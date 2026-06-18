# subset-b-000041 research

Grouped research report for composefs-rs library files. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fs.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/fs.rs

## Purpose
This module is the main bridge between live Linux filesystem trees and composefs in-memory trees. It can scan a directory into `FileSystem<ObjectID>`, store or compute fs-verity digests for external file content, apply container-specific xattr filtering and OCI transformations, and write a composefs tree back to a directory. It also defines the `ObjectStore` abstraction and the C-compatible `FlatDigestStore`.

## Important APIs, Types, and Functions
`ObjectStore<ObjectID>` abstracts `ensure_object_from_fd()` and `write_semaphore()` so filesystem reading can target either `Repository<ObjectID>` or other object layouts. `FlatDigestStore` implements a flat `<store>/xx/rest-of-digest` layout compatible with C `mkcomposefs --digest-store`. `write_to_path()` recursively materializes a `FileSystem` into a target directory using `write_directory_contents()`, `write_directory()`, `write_leaf()`, and `set_file_contents()`.

The scan path uses `FilesystemScanner`, `FileDevIno`, `PendingFile`, and `ChannelHandler`. `PendingFile::Inline` holds small content at or below `INLINE_CONTENT_MAX_V0`; `PendingFile::External` records `(dev, ino)` and size for later fs-verity resolution. `HardlinkBehavior` controls whether shared source inodes are deduplicated into shared `LeafId`s or broken into independent leaves. `ReadFilesystemOpts` exposes a custom object store, semaphore, and hardlink mode. Public readers are `read_filesystem()`, `read_filesystem_with_opts()`, `read_filesystem_filtered()`, `read_container_root()`, and `read_file()`.

## Control Flow
Writing walks the root directory, creates directories and special files with `rustix`, writes inline data through `O_TMPFILE` when supported, and copies external object content out of the repository. Reading starts a blocking scanner task and an async stream of large-file work items. The scanner opens each inode with `NOFOLLOW`, reads stat and xattrs, recurses into directories, reads small regular files inline, captures symlinks and device metadata, and sends large regular file descriptors through a bounded Tokio channel. The async side gates work with a semaphore, spawns blocking digest/store tasks, collects `TaskResult::Verity` results by `FileDevIno`, waits for the scan result, then maps `PendingFile` to final `RegularFile<ObjectID>`.

`FlatDigestStore::ensure_object_from_fd()` copies the input fd into an anonymous tmpfile, reopens it read-only, enables fs-verity when possible, measures the kernel digest or computes a userspace fallback when `insecure` allows it, creates the digest prefix directory, and atomically links the tmpfile into its final content-addressed path. Duplicate objects are accepted via `EEXIST`.

## State and Persistence Behavior
The scanner keeps transient in-memory state: a hardlink map and leaf vector. Persistent side effects occur when an object store is supplied: repositories or flat digest stores receive content-addressed files, and `write_to_path()` creates files, directories, symlinks, and device nodes in the output tree. `FlatDigestStore` uses anonymous tmpfiles plus `linkat` for atomic publication and avoids in-memory buffering for object copies. Xattrs are read into `BTreeMap`s; `read_container_root()` filters to the container allowlist and then calls OCI tree transforms.

## Dependencies and Integration Points
This file integrates `rustix` fd-based filesystem operations, Tokio `Semaphore`, `JoinSet`, and streams, `Repository`, `generic_tree`, `tree`, `fsverity`, and utility helpers such as `proc_self_fd()` and `reopen_tmpfile_ro()`. It relies on `FsVerityHashValue` and `FsVerityHasher` for generic hash support. It feeds composefs image generation through `FileSystem<ObjectID>` and supports C compatibility through `FlatDigestStore`.

## Risks and Edge Cases
The write path for external files reads the entire object into memory, and the comment notes this should become streaming or reflink-aware. Small-file reading calls `read()` once into spare capacity, so short reads on regular files are a risk unless upstream assumptions hold. `read_xattrs()` uses fixed 64 KiB buffers, so unusually large xattr lists or values may fail. The async scanner can silently ignore channel send failures after cancellation, which is acceptable for early error paths but makes root-cause context depend on the async side. `FlatDigestStore` has an `insecure` fallback that computes userspace hashes without kernel immutability guarantees. Hardlink mode changes image semantics and compatibility.

## Test Signals
Unit tests cover `set_file_contents()` and flat digest store layout, content preservation, and idempotent duplicate storage. Broader behavior is indirectly covered by tests in `generic_tree`, `fsverity`, repository, and image generation paths. Useful additional tests would exercise partial reads, xattr buffer overflow behavior, hardlink `Tracked` versus `Break`, cancellation while scanning, and write-back of external large files without allocating the full file.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/digest.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/digest.rs

## Purpose
This module implements userspace fs-verity digest computation. It builds the Merkle tree root hash and then hashes the fs-verity descriptor fields so callers can compute the same digest the kernel reports, even when kernel fs-verity is unavailable.

## Important APIs, Types, and Functions
`FsVerityLayer<H, LG_BLKSZ>` wraps a hash context for one Merkle tree layer and tracks remaining bytes in the current block. `FsVerityHasher<H, LG_BLKSZ>` is the public incremental hasher with `BLOCK_SIZE`, `hash()`, `new()`, `add_block()`, and `digest()`. It is generic over `FsVerityHashValue`, so SHA-256 and SHA-512 share the same logic.

## Control Flow
`hash()` slices an input buffer into block-sized chunks and feeds `add_block()`. `add_block()` hashes a data block padded to the fs-verity block size, increments `n_bytes`, and propagates completed child hashes upward through `layers`. If a prior root value exists and more data arrives, that value is converted into a new upper layer before processing continues. `root_hash()` finalizes pending layers, using the all-zero `EMPTY` value for the empty-file case. `digest()` serializes the fs-verity descriptor fields manually in little-endian order, appends the Merkle root, pads the root hash field to 64 bytes, adds zero salt and reserved bytes, and returns the final hash.

## State and Persistence Behavior
All state is in memory: `layers`, cached `value`, and `n_bytes`. Calling `digest()` mutates the hasher by finalizing/caching the root. No file descriptors or persistent stores are touched. Correctness depends on callers feeding full blocks except for the final chunk.

## Dependencies and Integration Points
The module depends on `sha2::Digest` and the local `FsVerityHashValue` trait. It is used by `fsverity::compute_verity()`, fallback measurement paths, filesystem scanning without a store, and flat digest store insecure fallback. It mirrors kernel descriptor construction rather than relying on a packed struct.

## Risks and Edge Cases
`add_block()` trusts caller chunking and does not reject oversized or mid-stream short blocks, so misuse can produce non-kernel-equivalent digests. The descriptor serialization must stay aligned with Linux fs-verity rules; future support for salt or non-4096 block sizes would require careful changes. `root_hash()` mutates internal state, so repeated `digest()` calls are intended to be stable but should remain tested.

## Test Signals
Tests assert known SHA-256 and SHA-512 fs-verity digests for `hello world`. Cross-checks against the kernel for many sizes live in `fsverity/mod.rs`, giving stronger end-to-end confidence over Merkle boundary cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/digest.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/hashvalue.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/hashvalue.rs

## Purpose
This module defines the fs-verity hash value contract, concrete SHA-256 and SHA-512 value types, and algorithm identifiers. It centralizes digest parsing, formatting, object-store pathname conversion, serde support, and kernel algorithm IDs.

## Important APIs, Types, and Functions
`FsVerityHashValue` requires cloneable, hashable, zerocopy-compatible, sendable digest value types with an associated `Digest`, `ALGORITHM`, and `EMPTY`. Provided helpers include `from_hex()`, `from_object_dir_and_basename()`, `from_object_pathname()`, `to_object_pathname()`, `to_object_dir()`, `to_hex()`, and `to_id()`. `Sha256HashValue` and `Sha512HashValue` are repr(C) byte wrappers with `From<Output<_>>` conversions. `Algorithm` covers SHA-256 and SHA-512 with a log2 block size, plus `for_hash()`, `hash_name()`, `kernel_id()`, `lg_blocksize()`, `is_compatible()`, `FromStr`, `Display`, and serde implementations. `AlgorithmParseError` documents all parse failures.

## Control Flow
Hex parsing decodes into a zero-initialized value buffer. Object path parsing accepts trailing `xx/rest` pathnames so higher-level prefixes can be ignored. Algorithm parsing requires the `fsverity-` prefix, splits at the last dash, validates the block size against `DEFAULT_LG_BLOCKSIZE`, and maps the hash name to a variant. Serialization stores the same string that `Display` emits.

## State and Persistence Behavior
These types carry value state only. They do not access the filesystem. The object pathname format is a persistence contract because repositories and flat digest stores use the first byte as a directory and remaining bytes as the basename.

## Dependencies and Integration Points
The module depends on `hex`, `sha2`, `serde`, and `zerocopy`. It is imported by fs-verity ioctl wrappers, userspace digest computation, repository object layout, dump/image parsing, and mount verification options. `kernel_id()` couples these values to Linux `FS_VERITY_HASH_ALGORITHM_*` IDs.

## Risks and Edge Cases
`from_object_pathname()` intentionally ignores leading path components, which is useful for repository paths but unsuitable where callers need strict path validation. `is_compatible()` compares enum discriminants only, so it distinguishes hash family but not block size; this is currently acceptable because only block size 12 is supported. New algorithms or block sizes would need updates across descriptor construction, ioctl wrappers, tests, and parsing.

## Test Signals
Generic tests validate empty hash formatting, debug output, `to_id()`, invalid hex cases, object basename and pathname parsing, SHA-256/SHA-512 instantiations, algorithm round-trips, error variants, equality, and compatibility checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/hashvalue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/ioctl.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/ioctl.rs

## Purpose
This module is the low-level adapter between composefs-rs generic hash types and the `composefs-ioctls` fs-verity API. It hides kernel ioctl details behind typed enable and measure functions.

## Important APIs, Types, and Functions
It re-exports `EnableVerityError` and `MeasureVerityError`. `fs_ioc_enable_verity<H>()` calls the underlying enable ioctl using `H::ALGORITHM.kernel_id()` and a 4096 byte block size. `fs_ioc_measure_verity<H>()` dispatches on the kernel hash ID, requests either a 32-byte or 64-byte digest, and converts the returned byte array into the caller's `FsVerityHashValue` type.

## Control Flow
Enable flow is direct: convert `impl AsFd` to a borrowed fd and call `composefs_ioctls::fsverity::fs_ioc_enable_verity`. Measurement matches the algorithm ID. ID 1 reads `[u8; 32]`, ID 2 reads `[u8; 64]`, and any other ID is considered unreachable because the local `Algorithm` type only exposes SHA-256 and SHA-512.

## State and Persistence Behavior
`fs_ioc_enable_verity()` changes kernel filesystem state by enabling fs-verity on the target file. `fs_ioc_measure_verity()` is read-only but relies on kernel state and validates digest size/algorithm through the lower crate. The module stores no state of its own.

## Dependencies and Integration Points
This file depends on `composefs-ioctls`, `std::os::fd::AsFd`, and `FsVerityHashValue`. It is private to the `fsverity` module, whose public functions add retry, copy, optional, fallback, and comparison semantics around these raw calls.

## Risks and Edge Cases
The hardcoded 4096 block size must match `DEFAULT_LG_BLOCKSIZE` and userspace digest construction. `H::read_from_bytes(...).expect("size mismatch")` is safe for current concrete hash sizes but would panic if a future `FsVerityHashValue` had inconsistent size and kernel ID. Tests requiring `/dev/shm` are environment-sensitive and gated by `test_with`.

## Test Signals
Tests cover missing verity on a temporary file, unsupported filesystem behavior on `/dev/shm`, and enabling on unsupported filesystems. Deeper bad-fd behavior is delegated to the lower `composefs-ioctls` crate because this crate forbids unsafe code.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/ioctl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/mod.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/mod.rs

## Purpose
This is the public fs-verity facade. It exports hash value types and userspace hashing, wraps kernel enable/measure ioctls, handles transient enable failures, provides copy-on-enable fallback, offers optional/software-fallback measurement, and compares measured digests to expected values.

## Important APIs, Types, and Functions
Public exports include `FsVerityHasher`, `Algorithm`, `AlgorithmParseError`, `DEFAULT_LG_BLOCKSIZE`, `FsVerityHashValue`, `Sha256HashValue`, `Sha512HashValue`, `EnableVerityError`, and `MeasureVerityError`. `CompareVerityError` distinguishes measurement failures from digest mismatches. Main functions are `compute_verity()`, `enable_verity_raw()`, `enable_verity_with_retry()`, `enable_verity_maybe_copy()`, `measure_verity()`, `measure_verity_opt()`, `measure_verity_with_fallback()`, `has_verity()`, and `ensure_verity_equal()`.

## Control Flow
`compute_verity()` delegates to the userspace hasher. `enable_verity_raw()` calls the ioctl wrapper. `enable_verity_with_retry()` retries `FileOpenedForWrite` up to three attempts with 1 ms sleeps, covering inherited write fds during concurrent forks. `enable_verity_maybe_copy()` first tries the original fd and, on persistent `FileOpenedForWrite`, calls `enable_verity_on_copy()`. That helper clones and rewinds the source, creates an `O_TMPFILE` in the supplied directory, copies bytes, opens a read-only fd through `/proc/self/fd`, drops the writable fd, and loops until enabling verity succeeds on the copy.

Measurement flows are layered. `measure_verity()` calls the raw ioctl. `measure_verity_opt()` converts missing or unsupported verity into `Ok(None)`. `measure_verity_with_fallback()` first tries kernel measurement and then streams the file through `FsVerityHasher` when the kernel cannot provide a digest. `ensure_verity_equal()` measures and compares, returning a structured mismatch with expected/found hex strings.

## State and Persistence Behavior
Enabling verity mutates file metadata and makes the file immutable under kernel fs-verity semantics. The copy path creates an anonymous tmpfile and returns it to the caller, who must link or otherwise persist it if needed. Measurement and fallback hashing do not persist state. Retry behavior is time-dependent but bounded.

## Dependencies and Integration Points
This module integrates the local `digest`, `hashvalue`, and `ioctl` submodules with `rustix` open/openat, standard file I/O, and `proc_self_fd()`. It is used by repository object storage, flat digest storage, filesystem scanning, and verification/mount logic. The private `has_verity()` dispatches based on runtime `Algorithm`.

## Risks and Edge Cases
`enable_verity_on_copy()` loops until enable succeeds; if a filesystem repeatedly creates problematic tmpfiles or environmental conditions persist, that can spin. The copy path intentionally does not sync copied contents, leaving durability to callers. `measure_verity_with_fallback()` accepts `impl AsFd + Read`, so callers must pass a readable object positioned at the beginning or otherwise understand the current read position. Optional measurement hides unsupported filesystems as `None`, which is correct for fallback paths but not for strict security checks.

## Test Signals
Tests cover missing verity, simple enable/measure/compare, digest mismatch reporting, concurrent fork retry behavior, unsupported filesystems, wrong hash algorithm and digest size errors, kernel/userspace cross-checks over many size edge cases, direct enable without copy, and forced copy when the fd is read-write.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/generic_tree.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/generic_tree.rs

## Purpose
This module defines a generic metadata-rich filesystem tree where regular file content is caller-defined. It is the reusable tree model underneath composefs image construction, scanning, dump parsing, OCI transforms, and hardlink representation.

## Important APIs, Types, and Functions
Core types are `Stat`, `LeafId`, `LeafContent<T>`, `Leaf<T>`, `Directory<T>`, `Inode<T>`, `ImageError`, `FileSystem<T>`, and `DirectoryRef<'a, T>`. `Stat::uninitialized()` provides placeholder root metadata for incremental builds. `Directory` offers lookup, traversal, split, insert, merge, remove, pop, clear, hardlink remapping, top-level filtering, and newest-mtime discovery. `FileSystem` offers construction, root stat replacement, leaf allocation, OCI transforms, stat iteration, xattr filtering, regular-content mapping, compaction, nlink counts, fsck validation, and leaf access. `DirectoryRef` pairs a directory reference with the filesystem leaves table for ergonomic read-only operations.

## Control Flow
Directory traversal uses `Path::components()` and rejects prefixes, `.`, and `..` for image safety. `split()` and `split_mut()` locate the parent directory and basename for path-based operations. `merge()` preserves existing directory entries when a directory overlays a directory but replaces non-directory content. Hardlinks are represented by multiple `Inode::Leaf` entries pointing at one `LeafId`. `try_map_regular()` maps each leaf table entry exactly once and retypes the directory tree without changing indices. `compact()` counts references, builds an old-to-new `LeafId` map, drains live leaves into a new vector, remaps tree references, and debug-checks consistency.

OCI-related flow is explicit: `transform_for_oci()` copies root metadata from `/usr` and canonicalizes `/run`. `add_overlay_whiteouts()` creates root entries `00` through `ff` as character devices unless already present, inheriting root uid/gid/mtime and only `security.selinux` xattr for C format compatibility.

## State and Persistence Behavior
All state is in memory. Directory entries are `BTreeMap`s, giving deterministic ordering. The leaves vector is the authoritative storage for non-directory metadata and content; tree nodes reference it by index. Methods like `remove()` and `clear()` can orphan leaves until `compact()` is called, while `fsck()` detects such orphans. Xattrs are stored per `Stat` as `BTreeMap<Box<OsStr>, Box<[u8]>>`.

## Dependencies and Integration Points
This module depends only on standard collections/path types and `thiserror`. Other modules alias or wrap it as `tree`, serialize it to EROFS/dump formats, scan into it from `fs.rs`, and transform it for OCI consistency. It deliberately does not know about fs-verity object IDs except through generic `T`.

## Risks and Edge Cases
`Inode::stat()` and `FileSystem::leaf()` index directly and can panic if the tree is invalid; callers should use `fsck()` when consuming untrusted trees. `Directory::remap_leaf()` panics on invalid entries and is intended for internal hardlink surgery. Removing entries without compacting can leave orphan leaves that affect iteration and validation. `copy_root_metadata_from_usr()` and `canonicalize_run()` require `/usr` for standard OCI flows, so minimal filesystems without `/usr` will error. The whiteout helper mutates the root namespace heavily and must remain aligned with C compatibility rules.

## Test Signals
Tests cover directory insertion, lookup, error variants, file access, removal, merge semantics, clear, newest mtime, sorted entries, root metadata copying, missing `/usr`, xattr filtering, `/run` canonicalization, regular-content mapping, hardlink sharing, error propagation, OCI transform, Send/Sync, compaction, nlink counts, mutable stat iteration, and overlay whiteout behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/generic_tree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/lib.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/lib.rs

## Purpose
This is the crate root for composefs library bindings and utilities. It declares the public module surface, enforces safety/lint policy, and defines format-level constants shared by scanners, parsers, image writers, and streaming code.

## Important APIs, Types, and Functions
The crate exposes modules including `dumpfile`, `dumpfile_parse`, `erofs`, `filesystem_ops`, `fs`, `fsverity`, `mount`, `mountcompat`, `progress`, `repository`, `splitstream`, `tree`, `util`, and `generic_tree`. It re-exports `repository::ImageNotFound` and conditionally exposes `test`. Public constants are `INLINE_CONTENT_MAX_V0`, `MAX_INLINE_CONTENT`, and `SYMLINK_MAX`. The hidden `shared_internals::IO_BUF_CAPACITY` sets a 64 KiB streaming buffer size.

## Control Flow
There is no runtime control flow in this file beyond module loading. Its most important behavior is compile-time: `#![forbid(unsafe_code)]` applies crate-wide, and non-test builds deny direct stdout/stderr printing through Clippy except where locally allowed.

## State and Persistence Behavior
The constants define persistent format behavior. `INLINE_CONTENT_MAX_V0` controls whether files are embedded inline or stored externally with fs-verity-backed object references; changing it is explicitly a format break. `MAX_INLINE_CONTENT` is a parsing safety bound for untrusted input and intentionally exceeds the current writer threshold. `SYMLINK_MAX` enforces an XFS-compatible symlink target limit.

## Dependencies and Integration Points
Every other public module is rooted here. `fs.rs` uses `INLINE_CONTENT_MAX_V0` and `shared_internals::IO_BUF_CAPACITY`; parsers use `MAX_INLINE_CONTENT`; symlink validators use `SYMLINK_MAX`; repository users rely on the `ImageNotFound` re-export.

## Risks and Edge Cases
Changing exported module names or constants can break downstream APIs or image compatibility. The crate-level print lint has a documented exception in `mount::FsHandle::drop()` where kernel diagnostics are only available during drop. Hidden internals are not stable API, but cross-crate workspace users may still come to depend on them.

## Test Signals
This file has no direct tests. Its guarantees are exercised by compilation of the whole crate and by downstream module tests that depend on constants and module visibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/mount.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/mount.rs

## Purpose
This module implements composefs mounting through the modern Linux mount API. It creates detached EROFS mounts from image files, configures overlayfs with composefs data layers and fs-verity options, and exposes a final mount fd that callers can attach with `move_mount`.

## Important APIs, Types, and Functions
`FsHandle` owns a filesystem context fd from `fsopen()` and implements `AsFd`. `mount_at()` moves a detached mount to a target path. `erofs_mount()` prepares an image and mounts it read-only as EROFS. `MountOptions` stores optional overlay upper/work dirs and read-write mode, with `set_overlay()` and `set_read_write()`. `composefs_fsmount()` builds the EROFS lower mount, opens an overlayfs context, configures source/metacopy/redirect_dir/verity/upper/work/lower/data options, creates the filesystem, and returns an `fsmount()` fd.

## Control Flow
The EROFS path calls `make_erofs_mountable()`, configures `ro` and `source=/proc/self/fd/N`, runs `fsconfig_create()`, then `fsmount()`. Composefs mounting first calls `prepare_mount()` on the EROFS mount for kernel compatibility. It configures overlayfs source as `composefs:{name}`, enables metacopy and redirect_dir, optionally requires verity, optionally supplies upperdir and workdir, sets lower and data fds through compatibility helpers, finalizes the config, and chooses read-only mount attributes unless `read_write` is set.

## State and Persistence Behavior
Mount operations create kernel mount state, not repository files. `mount_at()` attaches a detached mount into the namespace. `FsHandle::drop()` drains kernel diagnostic messages from the fs context fd and prints them to stderr as a local lint exception.

## Dependencies and Integration Points
This module depends on `rustix::mount`, `rustix::path`, `mountcompat` helpers for kernel-version differences, and `proc_self_fd()`. It is the runtime consumer of EROFS image outputs and repository object directories and integrates with overlayfs fs-verity enforcement through the `verity=require` option.

## Risks and Edge Cases
The modern mount API requires sufficiently new kernels and privileges; compatibility helpers cover some but not all environment constraints. `FsHandle::drop()` printing can surprise library users but is justified for otherwise lost kernel diagnostics. `MountOptions::set_read_write(true)` only makes sense with a writable overlay; without upper/work dirs, kernel config may fail. `enable_verity` must match object-store integrity expectations or composefs mounts may reject data.

## Test Signals
No direct tests appear in this file. Confidence comes from integration or privileged tests elsewhere. Useful test coverage would mock or isolate fsconfig sequences, validate option emission under feature flags, and exercise read-only/read-write overlay combinations on supported kernels.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/mount.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/mountcompat.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/mountcompat.rs

## Purpose
This module isolates Linux kernel compatibility differences for composefs mounting. It provides alternate implementations for overlayfs fd options, detached mount preparation, and EROFS image mountability based on Cargo features for pre-6.15 and RHEL9-like kernels.

## Important APIs, Types, and Functions
Public helpers are `overlayfs_set_fd()`, `overlayfs_set_lower_and_data_fds()`, `make_erofs_mountable()`, and `prepare_mount()`. Default builds pass fds directly via `fsconfig_set_fd()`, pass EROFS image fds through unchanged, and leave detached mounts as-is. With `pre-6.15`, overlay layer options use string `/proc/self/fd` paths and `prepare_mount()` returns a temporary mounted directory fd through `tmpmount::TmpMount`. With `rhel9`, `make_erofs_mountable()` calls `loopify()`.

## Control Flow
Feature flags select entire implementations at compile time. The pre-6.15 lower/data path constructs either `/proc/self/fd/lower` or `/proc/self/fd/lower::/proc/self/fd/data` and sets `lowerdir`. `TmpMount::mount()` creates a temporary directory, moves the detached mount there, opens it with `O_PATH|O_DIRECTORY|O_CLOEXEC`, and returns a guard object. Dropping the guard detaches the mount. RHEL9 loop support delegates to `composefs_ioctls::loop_device::loopify()`.

## State and Persistence Behavior
Default helpers create no extra persistent state. The pre-6.15 temp mount path temporarily mutates the mount namespace and creates a temporary directory that is cleaned on drop. The RHEL9 path creates loop device state managed by the lower helper. String-based `/proc/self/fd` options rely on the referenced fds staying open through fsconfig.

## Dependencies and Integration Points
`mount.rs` calls these helpers rather than branching on kernel features itself. The module depends on `rustix` mount/fs APIs, `tempfile` for temp mountpoints under `pre-6.15`, and `composefs-ioctls` loop helpers under `rhel9`. It also uses `crate::util::proc_self_fd()` for fd path conversion.

## Risks and Edge Cases
Feature selection must match target kernel behavior. The comments note overlayfs `fsconfig_set_fd()` support differences around Linux 6.13 and detached mount limitations before 6.15. Temp mounts depend on `Drop` for cleanup; leaked guards can leave mounts until process exit or manual cleanup. `/proc/self/fd` string options are sensitive to fd lifetime and namespace behavior.

## Test Signals
There are no direct unit tests. Practical validation requires feature-matrix integration tests on representative kernels: modern, pre-6.15, and RHEL9. Tests should verify temp mount cleanup and loop-device release.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/mountcompat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/progress.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/progress.rs

## Purpose
This module defines a small progress-reporting abstraction for pull and download operations. It lets library code emit structured events without depending on a specific UI and provides an async reader wrapper that reports byte progress out of the hot I/O path.

## Important APIs, Types, and Functions
`ComponentId` identifies a layer, object, or stream and supports `as_str()`, `into_inner()`, `From<S>`, `Display`, `Eq`, and `Hash`. `ProgressUnit` distinguishes bytes from item counts. `ProgressEvent` variants are `Started`, `Progress`, `Skipped`, `Done`, and `Message`. `ProgressReporter` is the `Send + Sync` trait implemented by renderers. `NullReporter` discards events, and `SharedReporter` is `Arc<dyn ProgressReporter>`. `ProgressRead<R>` wraps an `AsyncRead` and exposes `new()` plus an `AsyncRead` implementation. Test support provides `RecordingReporter`.

## Control Flow
Callers emit lifecycle events to a reporter. For byte streams, `ProgressRead::new()` creates a Tokio watch channel initialized to zero and returns both the wrapped reader and a driver future. Each successful `poll_read()` computes the newly filled byte count and updates the watch value with `send_modify()`. The driver awaits watch changes and emits `ProgressEvent::Progress` with the component id and total. The driver completes when the reader is dropped and the watch sender closes.

## State and Persistence Behavior
Progress state is in memory only. `ProgressRead` keeps the wrapped reader and a watch sender containing cumulative bytes. Slow renderers do not backpressure reads because watch channels coalesce intermediate values. `RecordingReporter` stores events behind a `Mutex` for test inspection.

## Dependencies and Integration Points
The module depends on Tokio `AsyncRead` and `watch`, `Arc`, and standard task/pin traits. It is intended for higher-level pull/download paths and UI crates such as `cfsctl` renderers. Placement before decompressors is documented so fetched bytes match compressed transfer totals.

## Risks and Edge Cases
A caller must run the driver future concurrently; otherwise no `ProgressEvent::Progress` events are emitted even though byte counts update. Watch coalescing means renderers may not observe every intermediate count, only monotonic snapshots. Zero-length streams emit no progress events because the watch value never changes. If a read returns `Ok(())` with zero bytes before EOF semantics are complete, no progress is sent.

## Test Signals
Tests cover `NullReporter`, `ComponentId` conversion/display/hash behavior, `ProgressEvent` debug and clone behavior, `RecordingReporter` ordering and thread safety, `ProgressUnit`, non-empty `ProgressRead` progress emission, zero-length no-event behavior, and single-byte event count.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/progress.rs -->
