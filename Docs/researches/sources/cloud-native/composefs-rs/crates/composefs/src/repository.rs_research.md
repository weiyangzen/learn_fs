# sources/cloud-native/composefs-rs/crates/composefs/src/repository.rs

## Purpose

`repository.rs` implements the core composefs content-addressable repository abstraction. A repository stores immutable file objects under `objects/`, EROFS composefs images under `images/`, splitstreams under `streams/`, and named references under `images/refs/` and `streams/refs/` as garbage-collection roots. Objects are keyed by fs-verity digest and arranged as `objects/XX/<remaining-hex>`.

The module owns repository initialization, metadata/version validation, object import and verification, stream/image registration, mounting, garbage collection, consistency checking, and migration of older repositories that lack `meta.json`.

## Important APIs, Types, and Functions

- `Repository<ObjectID: FsVerityHashValue>` is the primary handle. It stores the repository fd, lazily opened objects fd, lazy Tokio write semaphore, insecure-mode flag, open-time `RepoMetadata`, optional per-session EROFS format override, and test-only old splitstream-header switch.
- `RepositoryConfig` configures `init_path`: fs-verity algorithm, `FormatConfig`, and an insecure flag. Defaults are SHA-256, default EROFS format, and secure fs-verity-required mode.
- `RepoMetadata` is serialized as `meta.json` and stores `version`, `algorithm`, `features`, and `erofs_formats`. It provides JSON roundtrip helpers, compatibility checks, and backward-compatible derivation of V1/V2 EROFS settings.
- `FeatureFlags` and `FeatureCheck` model compatible, read-only-compatible, and incompatible feature sets. Unknown incompatible features reject open; unknown read-only-compatible features report `ReadOnly`.
- `RepositoryOpenError` distinguishes missing metadata, old-format repos, invalid metadata, algorithm mismatch, unsupported format version, feature incompatibility, and I/O errors.
- `ObjectStoreMethod` reports whether file import used reflink, hardlink, copy, or deduplication.
- `ImportContext` caches source/destination device pairs where reflink is unsupported to avoid repeated `FICLONE` probes during bulk imports.
- `GcResult`, `FsckError`, and `FsckResult` are public reporting types for garbage collection and repository integrity checks.

Key module-level helpers include `read_repo_algorithm`, `read_repo_metadata`, `write_repo_metadata`, `reset_metadata`, `user_path`, `system_path`, `infer_repo_algorithm`, `ensure_dir_and_openat`, and `ensure_dir_at`.

## Repository Open, Initialization, and Metadata Flow

`Repository::init_path` creates the repository directory, builds `RepoMetadata` from `RepositoryConfig`, writes `meta.json`, then reopens via `open_path`. Initialization is idempotent only if existing metadata exactly matches the requested configuration; mismatched algorithm or EROFS format configuration fails.

`write_repo_metadata` writes `meta.json` atomically using `O_TMPFILE` plus `linkat` when available, falling back to `O_EXCL` file creation. In secure mode it enables fs-verity on `meta.json`; later open uses that as the signal that repository objects must have fs-verity.

`open_path` opens the root directory, takes a shared `flock`, reads and probes `meta.json`, validates version/features/algorithm against `ObjectID`, and sets `insecure` based on whether metadata has fs-verity. `Drop` unlocks the repository fd.

`open_upgrade` handles old-format repositories that have `objects/` but no `meta.json`. It infers the algorithm from object filename lengths, probes object fs-verity, writes new metadata, and then opens normally. Empty old `objects/` cannot be upgraded because the algorithm is unknowable.

The metadata compatibility model has two EROFS compatibility paths: modern repos persist the complete `FormatConfig` in `erofs_formats`; older metadata without that field defaults to V2 unless the legacy `v1_erofs` read-only-compatible flag is present.

## Object Storage Control Flow

`ensure_object` computes an fs-verity digest in userspace, then delegates to `store_object_with_id`. Existing object files are opened and verified with `ensure_verity_equal`; missing objects are written into tmpfiles, reopened read-only, fs-verity-enabled when possible, verified, and linked into `objects/XX/...`.

`ensure_object_from_fd` streams from an owned fd into an object tmpfile. In insecure mode it computes the verity digest while copying to avoid another read; in secure mode it copies, enables fs-verity, measures the kernel digest, and links.

`ensure_object_from_file` and `ensure_object_from_file_zerocopy` optimize existing-file imports:

- First try reflink to an object tmpfile using `ioctl_ficlone`; unsupported source/destination device pairs are remembered in `ImportContext`.
- Then try hardlinking the source file directly after enabling fs-verity on the source. This requires `CAP_DAC_READ_SEARCH` for `AT_EMPTY_PATH`.
- Finally, if allowed, copy into a tmpfile.

`finalize_object_tmpfile` is the common secure finalization path: reopen as read-only, enable fs-verity or accept insecure fallback on unsupported filesystems, measure or compute digest, deduplicate by statting the object path, create the parent prefix directory, and link the tmpfile into place.

`open_object` verifies the object digest unless insecure mode allows missing or unsupported fs-verity. `read_object` loads object contents into memory.

## Streams, Images, Mounting, and References

Streams are content identifiers under `streams/<identifier>` symlinked to object paths. `create_stream` returns a `SplitStreamWriter` carrying a `WritableRepo` token. `write_stream` finalizes the splitstream, calls `sync()`, then exposes the stream symlink and optional `streams/refs/<name>` symlink. That ordering is a crash-consistency barrier: linked data is durable before the named stream becomes discoverable.

`register_stream` performs the same publication sequence for already-stored splitstream objects. `write_stream_async` uses `done_async` and `sync_async` for parallel object-storage workflows.

`has_stream`, `has_named_stream`, `name_stream`, `ensure_stream`, `open_stream`, and `merge_splitstream` provide lookup, ref creation, lazy creation, reading, and materialization of splitstreams.

Images are stored as normal objects plus `images/<object-hex>` symlinks. `write_image` stores image data and optionally creates `images/refs/<name>`. `import_image` reads from a `Read` into memory before writing. `open_image` handles named refs and hex image names, verifying fs-verity when required and returning whether the mount should request verity.

`mount_with_options`, `mount`, and `mount_at` integrate with `composefs_fsmount` and `mount_at`, passing the image fd, objects directory fd, verity decision, and `MountOptions`.

`symlink_impl` creates repository-relative symlinks, ensures intermediate directories, and atomically replaces targets through `replace_symlinkat`.

## Garbage Collection

`gc` first checks writability and upgrades to an exclusive `flock`; `gc_dry_run` uses a shared lock and reports without deleting. Both call `gc_impl`.

`gc_impl` builds a live object set by:

- Reading image roots from `images/refs` plus `additional_roots` matching first-level image entries.
- Adding image objects and all object IDs referenced by each EROFS image via `erofs::reader::collect_objects`.
- Reading stream roots from `streams/refs` plus `additional_roots` matching first-level stream entries.
- Walking each live splitstream with `walk_streams`, adding direct object refs and resolving named stream refs by object ID through a map of all stream entries.

After liveness is computed, GC scans every `objects/00` through `objects/ff` directory and unlinks unreferenced files, accumulating count and byte totals. It then removes broken symlinks in `images/`, `streams/`, and their recursive `refs/` trees. Actual GC downgrades the lock back to shared before returning.

The GC assumptions are explicitly narrow: category first-level entries should be symlinks to objects, refs should point to first-level entries, and some of these assumptions are marked for future fsck coverage.

## Fsck

`fsck` performs full structural and object verification; `fsck_metadata_only` skips per-object digest verification. Both call `fsck_inner`.

The check phases are:

1. Re-read `meta.json` and validate metadata compatibility.
2. For full fsck, verify objects in parallel by object prefix directory using `tokio::task::spawn_blocking` bounded by `available_parallelism`.
3. Validate `streams/` first-level symlinks, splitstream headers, object refs, named refs, and recursive `streams/refs`.
4. Validate `images/` first-level symlinks, parse EROFS image data with composefs-specific validation, verify referenced objects, and check recursive `images/refs`.

Object fsck parses the path-derived expected digest, opens the object file, measures fs-verity, or computes the digest in userspace when insecure. Missing verity in secure mode is reported as `ObjectVerityMissing`; digest mismatch is `ObjectDigestMismatch`.

`FsckResult::Display` emits a compact human-readable status for metadata, objects, streams, images, broken links, missing objects, and structured errors.

## State and Persistence Behavior

Persistent repository state is almost entirely filesystem state:

- `meta.json` records repository format, algorithm, feature flags, and EROFS format configuration.
- `objects/XX/name` files are immutable content-addressed data blobs.
- `streams/<id>` and `images/<hash>` are relative symlinks to object files.
- `streams/refs/...` and `images/refs/...` are relative symlinks that act as GC roots.

The module avoids per-object `fsync` for performance. Instead, stream publication explicitly calls `syncfs` before creating stream-visible symlinks, and callers are expected to call `sync` or `sync_async` after bulk object/image operations. Metadata initialization syncs the tmpfile or fallback created file before linking or enabling verity.

The repository lock is advisory and process-scoped through `flock`: normal open holds shared lock; GC requires exclusive lock; dry-run GC uses shared lock. Writability is checked with both `fstatvfs` for read-only mounts and `faccessat(W_OK)` for permissions.

## Dependencies and Integration Points

Internal crate dependencies:

- `crate::fsverity` supplies digest types, fs-verity measurement/enabling, userspace computation, and verification.
- `crate::splitstream` supplies `SplitStreamReader` and `SplitStreamWriter`.
- `crate::erofs::format` stores image format configuration; `crate::erofs::reader` collects object IDs from EROFS images.
- `crate::mount` mounts composefs images using object storage.
- `crate::util` supplies errno filtering, `/proc/self/fd` paths, tmpfile reopening, and atomic symlink replacement.
- `crate::shared_internals::IO_BUF_CAPACITY` sizes streaming buffers.

External dependencies include `rustix` for `openat`, `mkdirat`, `linkat`, `readlinkat`, `statat`, `flock`, `syncfs`, `fstatvfs`, and capability-sensitive operations; `tokio` for async blocking tasks and semaphores; `once_cell` for lazy fd/semaphore initialization; `anyhow` and `fn_error_context` for contextual errors; `serde`/`serde_json` for metadata and fsck reporting; and `log` for debug/trace diagnostics.

The module is generic over `ObjectID`, so callers must choose SHA-256 or SHA-512 repository types matching metadata. `read_repo_algorithm` and `infer_repo_algorithm` exist specifically to help frontends choose that type before opening.

## Risks and Edge Cases

- `FeatureCheck::ReadOnly` is returned by metadata compatibility checks, but `open_path` currently accepts the value without storing read-only state on `Repository`; write paths rely on filesystem writability, not unknown ro-compat feature enforcement.
- Insecure mode deliberately permits operation without kernel fs-verity. This is necessary for tmpfs/overlayfs/tests but shifts integrity to userspace digest computation and weakens runtime verification.
- Hardlink import mutates source files by enabling fs-verity in place and requires `CAP_DAC_READ_SEARCH`; it is intended for trusted immutable image data.
- Many operations rely on relative symlink topology. Invalid symlink shapes are partly handled by fsck, but GC comments still call out assumptions that are not fully validated before collection.
- `import_image` and `write_image` buffer entire images in memory.
- `syncfs` is coarse-grained and syncs the whole filesystem backing the repository; it is simple but can be expensive.
- Object replacement races are mostly handled through link/dedup behavior, but some TODOs note that a newly appearing object after `EEXIST` is not always remeasured.
- The `set_erofs_version` override narrows a multi-format repo to one in-memory format for the session and does not persist; callers must understand that it does not rewrite `meta.json`.

## Test Signals

The in-file test module is broad and mostly uses insecure temporary repositories for portability. Covered behaviors include:

- GC removing or preserving streams/images based on explicit additional roots, refs, overlapping objects, nested stream named refs, and object-ID-based stream matching when table names differ.
- `ensure_object_from_file` storing, reading back, and deduplicating repeated imports with `ObjectStoreMethod`.
- Full fsck on empty and healthy repositories.
- Fsck detection of corrupted objects, broken stream/image symlinks, missing stream object refs, non-symlink entries in streams/images, broken recursive refs, unexpected files under refs, invalid object filenames, corrupted splitstreams, missing named-ref objects, missing EROFS image object refs, corrupt EROFS image data, and V1 image parsing.
- Metadata fsck for valid and corrupt `meta.json`.
- `open_path` errors for missing metadata, old-format repos, and algorithm mismatch.
- feature flag JSON shape, unknown incompatible/ro-compatible/compatible behavior, and metadata JSON roundtrips.
- V1/V2/dual EROFS format metadata behavior, `v1_erofs` compatibility flag placement, idempotent init, mismatched re-init failure, and dual-format image commit with named ref pointing to the primary V1 image.
- `open_upgrade` for SHA-256 and SHA-512 old-format repos, type mismatch failure, empty-object inference failure, and no-op upgrade on already initialized repos.

No tests in this file directly exercise secure fs-verity on a real verity-capable filesystem, capability-dependent hardlink import success, mount behavior, concurrent GC/open interactions beyond flock calls, or enforcement of unknown read-only-compatible features.
