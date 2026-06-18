# Research: subset-b-000037

Work item `subset-b-000037` covers the composefs OCI crate entrypoint and native OCI image/layout persistence paths.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/lib.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-oci/src/lib.rs

## Purpose

`lib.rs` is the public crate root for `composefs-oci`. It wires together the crate modules, re-exports the primary API surface, defines shared identifiers for OCI layer/config splitstreams, and implements the top-level pull/import/config-upgrade path used by callers that want OCI images represented as composefs splitstreams and optional mountable EROFS images.

The file is also the main compatibility bridge between OCI content addressing and composefs repository object identity. OCI digests such as `sha256:...` identify manifest/config/layer bytes, while `ObjectID: FsVerityHashValue` identifies the repository/fs-verity object or stream result. Most APIs preserve both values explicitly.

## Important APIs, Types, and Functions

- Module declarations: public modules include `boot`, `image`, `layer`, `oci_image`, `oci_layout`, `progress`, `skopeo`, and `tar`; `cstor` is behind the `containers-storage` feature; `delta` is crate-private.
- Re-exports: the crate exports `composefs`, `OciDigest`, `pull_image`, `OciImage`, image listing/tagging/referrer/fsck helpers, layer inspection helpers, and progress types.
- `IMAGE_REF_KEY` and `BOOT_IMAGE_REF_KEY` are named splitstream-ref keys embedded in OCI config splitstreams to keep generated EROFS images reachable through the OCI tag/config/manifest GC graph.
- `ImportStats` records per-import counts and bytes for copied, reflinked, hardlinked, already-present, and inlined data. `from_split_stream_stats` maps `composefs::splitstream::SplitStreamStats` object-store methods into this crate-level summary, and `merge` aggregates layer-level stats.
- `LocalFetchOpt` and `PullOptions` control whether `pull` uses the native `containers-storage` fast path, the zero-copy requirement, explicit storage roots, extra image stores, image-proxy config, and progress reporting.
- `PullResult<ObjectID>` returns manifest/config OCI digests plus their fs-verity object IDs and aggregate import stats.
- `OpenConfig<ObjectID>` returns a parsed `ImageConfiguration`, layer diff_id-to-verity refs, and optional EROFS/boot EROFS refs stripped out of the layer map.
- `layer_identifier(diff_id)` and `config_identifier(config)` generate stable repository stream content IDs: `oci-layer-{digest}` and `oci-config-{digest}`.
- `import_layer` converts an async tar stream into a composefs splitstream using `tar::split_async`, registers it by layer diff_id, and optionally names it.
- `pull` dispatches to `cstor::import_from_containers_storage` when enabled and requested for `containers-storage:` refs, otherwise to `skopeo::pull_image`.
- `sha256_output_to_digest`, `sha256_content_digest`, and private `hash_sha256` wrap SHA-256 content hashing into the OCI digest type.
- `extract_diff_ids` reads `rootfs.diff_ids` for normal image configs and falls back to manifest layer digests for non-standard artifact configs.
- `open_config`, `composefs_erofs_for_config`, `composefs_erofs_for_manifest`, `composefs_boot_erofs_for_config`, and `composefs_boot_erofs_for_manifest` are read-side helpers for config metadata and EROFS refs.
- `upgrade_repo` scans all tagged OCI refs and calls EROFS generation for container images that do not already carry `IMAGE_REF_KEY`.
- `write_config` and `write_config_raw` serialize or preserve raw config JSON, add deterministic named refs in config diff_id order, optionally attach EROFS refs, and write the config as a single-external-object splitstream.
- `ensure_oci_composefs_erofs` opens a container image, constructs a composefs filesystem from layers, commits an EROFS image, rewrites the config splitstream with `IMAGE_REF_KEY`, rewrites the manifest splitstream with the new config verity, and updates the tag when supplied.
- `ensure_oci_composefs_erofs_boot` is the boot feature variant; it applies `composefs_boot::BootOps::transform_for_boot` before committing and uses `BOOT_IMAGE_REF_KEY`.

## Control Flow

Layer import first checks `repo.has_stream("oci-layer-{diff_id}")` for idempotency. If the layer already exists, it can still add a requested name and returns zero stats. Otherwise, the tar stream is split into composefs splitstream form, written to the repository, registered under the content identifier, and returned with splitstream-derived stats.

Image pull starts by normalizing progress to a `SharedReporter`, defaulting to `NullReporter`. Under the `containers-storage` feature it short-circuits local refs through `cstor` if `local_fetch` is not disabled. That path can enforce zero-copy. All other inputs go to `skopeo::pull_image`; the proxy result is repackaged into the crate-level `PullResult`.

Config reading uses `oci_image::read_external_splitstream` to get raw bytes and named refs. When no trusted verity is supplied, `open_config` recomputes the SHA-256 digest and verifies it against the requested OCI digest. It removes `composefs.image` and `composefs.image.boot` from the returned layer map so callers do not confuse EROFS refs with OCI layer refs.

EROFS upgrade is a rewrite chain. `upgrade_repo` opens each tagged image, skips artifacts and images that already have an EROFS ref, then calls `ensure_oci_composefs_erofs`. That function builds the flattened filesystem from the current config/layer refs, commits it as an image object, reads the original raw config and manifest JSON bytes, rewrites only splitstream named refs, and retags the manifest stream. The raw JSON preservation is critical: config and manifest content digests remain the original OCI digests even though the composefs stream verity changes because named refs changed.

## State and Persistence Behavior

The persistent model is composefs streams plus named refs. Layers live at `oci-layer-{diff_id}`, configs at `oci-config-{config_digest}`, and manifests at the matching `oci-manifest-{manifest_digest}` implemented in `oci_image.rs`. Config splitstreams store the raw config JSON as an external object and named refs to each layer's stream/object ID in config-defined diff_id order. They may also carry `composefs.image` and `composefs.image.boot` refs to generated EROFS images, which makes those images reachable for GC as long as the config remains reachable.

`write_config_raw` intentionally parses the JSON only to recover ordered diff_ids; it writes the original byte buffer back as the external object. This lets non-canonical JSON survive upgrades and keeps the OCI digest stable. Manifest rewriting follows the same principle through `oci_image::rewrite_manifest`.

`ImportStats` is not persisted directly; it reports import-time object-store behavior. Idempotent import paths return default stats when a stream already exists, so callers should not interpret zero stats as zero-size content.

## Dependencies and Integration Points

This file depends heavily on `composefs::repository::Repository` for stream/object/image persistence, `composefs::fsverity::FsVerityHashValue` for generic object IDs, `containers_image_proxy::oci_spec::image` for OCI schema types, `sha2`/`hex` for digest generation, `indicatif` for human-byte formatting, `anyhow` for contextual errors, and optional `composefs_boot`/`cstor` behavior behind features.

Key internal integration points are `tar::split_async`, `image::create_filesystem`, `OciImage::open`, `oci_image::list_refs`, `oci_image::write_manifest`/`rewrite_manifest`, `skopeo::pull_image`, `oci_layout::import_oci_layout` through tests and pull routing elsewhere, and `progress` reporter types.

## Risks and Edge Cases

- The distinction between OCI digest and fs-verity `ObjectID` is essential. Passing an untrusted verity skips content digest recomputation in `open_config`, so callers must only supply trusted verity values.
- `write_config_raw` requires the refs map to contain every diff_id in the config. Missing refs fail with a detailed list of available keys.
- Config refs are deterministic only because they are written in config diff_id order; future changes that iterate the `HashMap` directly would change stream verity.
- EROFS upgrade rewrites config and manifest splitstreams even if content bytes are unchanged. Old splitstreams become garbage and need repository GC.
- `ensure_oci_composefs_erofs` creates a new EROFS image each call, relying on object deduplication for identical content rather than treating it as a strict no-op.
- Non-container artifacts are deliberately skipped by EROFS generation and upgrade.
- `pull` behavior differs by feature set: native containers-storage import exists only when compiled with `containers-storage`.

## Test Signals

The in-file test module exercises layer import dumpfile output, import stats and idempotent re-import, config write/open, config external-object storage, deterministic config verity across `HashMap` insertion orders, digest mismatch detection, EROFS ref embedding, EROFS generation and GC reachability, preservation of non-canonical config JSON during rewrite, `ImportStats` display formatting, multi-layer whiteout flattening, old-format splitstream compatibility, pre-EROFS repository upgrade, `upgrade_repo` idempotency, and OCI-layout progress behavior for started/done/skipped/null-reporter paths. These tests are strong regression signals for persistence format compatibility and GC reachability.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/oci_image.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-oci/src/oci_image.rs

## Purpose

`oci_image.rs` implements native OCI image and artifact storage inside a composefs repository. It defines the repository naming convention, opens stored OCI structures, manages tag refs as GC roots, stores manifests/configs/blobs as external-object splitstreams, tracks OCI referrers, runs OCI-aware fsck checks, and exposes layer inspection/reconstruction helpers.

The module supports both normal container images and OCI artifacts. Container images use `ImageConfig` configs and config-named layer refs keyed by diff_id. Artifacts can have arbitrary config media types and arbitrary layer/blob media types; their layer refs are keyed by manifest layer digests.

## Important APIs, Types, and Functions

- `OciRefNotFound` and `OciImageNotFound` are typed error markers for missing tags and missing manifest streams.
- `read_external_splitstream` is a central invariant checker: it opens a repository stream, requires exactly one external object reference, reads that object's raw bytes, and returns the stream's named refs.
- `OCI_REF_PREFIX` is `oci/`, the subdirectory under repository stream refs used for image tags.
- `OciImage<ObjectID>` stores manifest digest/verity, parsed manifest, config digest/verity, optional parsed image config, layer refs, optional EROFS refs, and exposes accessors such as `manifest_digest`, `config_verity`, `layer_refs`, `image_ref`, `architecture`, `labels`, `read_manifest_json`, and `read_config_json`.
- `OciImage::open` opens by manifest digest and optional trusted verity; `open_ref` resolves a tag then opens by digest/verity.
- `open_layer_fd` opens non-tar artifact layer content as a raw object fd and rejects tar media types.
- Tag APIs: `tag_image`, `untag_image`, `resolve_ref`, and `list_refs`.
- Listing APIs: `ImageInfo` and `list_images` summarize tagged images and referrer counts.
- Manifest APIs: `write_manifest`, crate-private `rewrite_manifest`, `has_manifest`, and `manifest_identifier`.
- Tag encoding helpers: `oci_ref_path`, `encode_tag`, and `decode_tag` make refs safe for filesystem paths by encoding `/` and `%`.
- Blob APIs: `blob_identifier`, `write_blob`, and `open_blob` support arbitrary OCI artifact blobs.
- Referrer APIs: `add_referrer`, `list_referrers`, `remove_referrer`, `remove_referrers_for_subject`, and `cleanup_dangling_referrers`.
- Fsck APIs: `OciFsckError`, `OciFsckResult`, `oci_fsck`, `oci_fsck_image`, and internal `fsck_single_image`.
- Layer inspection APIs: `LayerInfo`, `SplitstreamInfo`, `layer_info`, `layer_dumpfile`, and `layer_tar`.

## Control Flow

Opening an image starts with `manifest_identifier(digest)` and `read_external_splitstream`. If no verity was supplied, the raw manifest bytes are SHA-256 checked against the requested OCI digest. The manifest is parsed, its config digest is used to find the `config:{digest}` named ref in the manifest stream, and the config stream is opened by that verity. For normal images, the config JSON is parsed and the config stream's named refs become the layer map. For artifacts, the layer map is built by filtering manifest named refs to only the manifest layer digests. EROFS and boot EROFS refs are then removed from the layer map into dedicated fields.

Tagging validates only that the name does not start with `@`, then creates a stream ref under `refs/oci/{encoded-name}` to the manifest stream. Resolution reads the symlink, extracts the target `oci-manifest-{digest}` suffix, parses the digest, and looks up the current stream verity.

`write_manifest` is idempotent by content identifier. If a stream already exists, it may add a requested tag and returns the existing verity. Otherwise it serializes the manifest, verifies the caller-provided digest, creates an OCI manifest splitstream, adds a named ref to the config stream as `config:{config_digest}`, adds layer named refs, stores the JSON externally, and optionally tags the stream. `rewrite_manifest` always writes a new stream for the same content ID so named refs can be updated without changing manifest JSON bytes.

Artifact blob storage hashes raw bytes, stores them as a single external-object splitstream under `oci-blob-{digest}`, and verifies the hash on open when verity is not supplied.

Referrer indexing creates additional GC-root symlinks under `streams/refs/oci-referrers/{encoded-subject}/{encoded-artifact}` pointing to artifact manifest streams. Cleanup walks subject directories, checks `has_manifest(subject)`, removes all referrer symlinks for subjects whose manifest stream no longer exists, then removes empty subject directories.

Fsck first runs repository-level `repo.fsck()`, then checks tagged OCI refs. Each image is validated by reading and hashing the manifest, parsing it, checking the config named ref, reading and hashing config bytes, parsing normal image configs, checking every layer named ref and layer stream/object, checking composefs seal image annotations, or for artifacts checking manifest-layer refs and backing objects. `fsck_single_image` increments `images_corrupted` once per image even if multiple errors are appended.

Layer inspection opens the layer splitstream by `oci-layer-{diff_id}`, counts object refs, parses tar entries with `crate::tar::get_entry`, calculates external and inline sizes, emits dumpfile text, or merges the splitstream back into tar bytes.

## State and Persistence Behavior

OCI state is persisted as repository streams and symlinks:

- Manifest streams are named `oci-manifest-{digest}` and store raw manifest JSON as exactly one external object.
- Config streams are named `oci-config-{digest}` and store raw config JSON as exactly one external object.
- Tar layer streams are named `oci-layer-{diff_id}` and contain composefs splitstream tar representations.
- Arbitrary artifact blobs are named `oci-blob-{digest}` or wrapped under layer identifiers for non-tar layers, depending on the call path.
- Tags under `streams/refs/oci/` are GC roots.
- Referrers under `streams/refs/oci-referrers/` are also GC roots until explicitly cleaned.
- Named stream refs form the GC graph from manifest to config and from config or manifest to layer/blob streams. EROFS image refs embedded in config streams keep generated images reachable.

`read_external_splitstream` enforces the single-external-object convention for metadata/blob payloads. This matters for independent fs-verity of the raw JSON/blob bytes and for signature workflows.

## Dependencies and Integration Points

The module uses `composefs::repository::Repository` for object, stream, image, symlink, and fsck operations; `containers_image_proxy::oci_spec::image` for OCI manifest/config/descriptors/media types; `rustix` for low-level `openat`, `readlinkat`, and `unlinkat`; `serde::Serialize` for CLI/report structures; `anyhow` for contexts; and crate modules `layer`, `skopeo`, and the crate-level config/layer/digest helpers.

It is used by `lib.rs` for config opening, EROFS upgrade, manifest rewrite, tag listing, and public re-exports. It is also the persistence contract consumed by `oci_layout.rs`, `skopeo.rs`, image construction, GC, and CLI-style inspection paths.

## Risks and Edge Cases

- `read_external_splitstream` rejects metadata streams with zero or multiple external objects. That is a strong invariant but can reject older or malformed repositories.
- Supplying trusted verity to `OciImage::open` or `open_blob` skips content digest recomputation; callers must not supply untrusted verity.
- `write_manifest` deduplicates by content ID. If named refs need to change while JSON bytes do not, callers must use `rewrite_manifest`.
- Tag validation rejects only a leading `@`; other unusual characters are allowed after percent-encoding of `/` and `%`.
- `decode_tag` is single-pass to avoid decoding `%252F` into `/`, but unknown percent sequences are preserved literally.
- Referrer symlinks are GC roots, so orphaned referrers can keep artifacts alive until `cleanup_dangling_referrers` is run before GC.
- Artifact and container layer refs are keyed differently. Code that assumes `rootfs.diff_ids` for artifacts will miss refs.
- `layer_info` uses tar entry parsing and splitstream total size; malformed tar splitstreams or mismatched content types surface as errors.

## Test Signals

Tests cover identifier formatting, tag path encoding/decoding including property tests, SHA-256 digest helpers, blob round-trips/dedup/bad digest, manifest/blob external-object storage, OCI artifact round-trips with non-tar layers and OCI 1.1 empty config, `open_layer_fd` rejection of tar layers, non-tar layer GC reachability, multiple image listing/opening/tagging/untagging, ref resolution, invalid leading-`@` refs and fsck detection, digest open without tag, `has_manifest`, empty repository behavior, GC for tagged/untagged/shared/multi-tag images, dry-run GC, referrer add/list/remove/cleanup and GC interactions, healthy/corrupt fsck paths for images and artifacts, missing config refs, missing layer refs, missing streams, bad refs, and mixed healthy/corrupt image counts. The test suite gives broad coverage of persistence invariants and error classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/oci_image.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/oci_layout.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-oci/src/oci_layout.rs

## Purpose

`oci_layout.rs` implements the direct local OCI layout import path for `oci:`-style references. Instead of spawning skopeo through `containers-image-proxy`, it reads an OCI layout directory with `ocidir`, imports config/layers into the same composefs repository format used elsewhere, and emits progress events for layer import. It also detects delta artifacts in single-manifest layouts and delegates them to the crate delta importer before platform filtering.

## Important APIs, Types, and Functions

- `parse_oci_layout_ref(imgref)` splits a local layout reference into `(path, optional_tag)` using the last colon after the last slash as a tag separator.
- `resolve_manifest` calls `ocidir.open_image_this_platform(tag)` to select a manifest for the current platform.
- `import_oci_layout` is the public async entry point. It opens the layout, detects delta artifacts, resolves the manifest, imports config and layers, stores the manifest splitstream, and returns `(skopeo::PullResult<ObjectID>, ImportStats)`.
- `import_config_and_layers` imports or reuses the config stream, extracts ordered layer identifiers, imports layers concurrently, writes config named refs, and returns ordered layer refs plus stats.
- `import_layer_from_file` imports a single layout blob, emits progress events, decompresses tar layers or stores non-tar blobs, creates the layer/blob splitstream, and returns the stream verity plus stats.
- `OciDirBlobReader` implements `delta::DeltaBlobReader` over an `OciDir` by opening blob files under `blobs/{algorithm}/{digest}`.

## Control Flow

`import_oci_layout` begins by checking repository writability to provide a repository error before any source-layout error. It opens the layout via `cap_std` and `OciDir::open`. Before platform resolution, it reads the index when there is exactly one manifest and checks whether that manifest is a composefs delta artifact. Deltas lack normal platform data, so they are delegated early to `delta::import_delta`.

For normal images, it resolves the manifest for the host platform and emits a message with the layer count. `import_config_and_layers` handles the config and layers. When the config stream already exists, it reads the config splitstream and named refs, extracts diff_ids using the same config/artifact fallback as `lib.rs`, reconstructs ordered layer refs from the existing named refs, emits `Skipped` events for every cached layer, and returns zero stats. This fast path avoids opening layer blobs.

When the config is new, raw config bytes are read from the layout and diff_ids are extracted. Manifest layers are paired with diff_ids, sorted by descriptor size descending, and imported concurrently using `tokio::task::JoinSet` with a semaphore sized to `available_parallelism()`. Each task opens a layer blob file from the layout before spawning, then calls `import_layer_from_file`. Results are merged into a digest-to-verity map and then re-ordered back into config-defined diff_id order before writing the config stream.

Manifest storage mirrors the rest of the crate. If `oci-manifest-{digest}` already exists, it reuses the verity. Otherwise it creates a manifest splitstream, adds the `config:{digest}` named ref, adds layer refs in config-defined order, reads the raw manifest bytes from the layout, writes them as the external payload, and stores the stream without tagging.

`import_layer_from_file` checks for an existing `oci-layer-{diff_id}` stream first and emits `Skipped` when cached. For new layers it emits `Started`, wraps the file in `ProgressRead`, and runs the progress driver concurrently with the actual import. Tar media types are decompressed with `decompress_async` and passed to `import_tar_async`; the resulting stream is registered under the layer content ID. Non-tar media types are stored through `store_blob_async`, object-store-method stats are populated, a small `OCI_BLOB_CONTENT_TYPE` splitstream wrapper is written with a reference to the object, and `Done` is emitted with the stored size.

## State and Persistence Behavior

The import path writes the same repository structures used by registry/skopeo import: config streams under `oci-config-{digest}`, layer streams under `oci-layer-{diff_id}`, manifest streams under `oci-manifest-{digest}`, and single-object blob wrappers for non-tar artifacts. It preserves raw config and manifest bytes from the OCI layout rather than reserializing parsed OCI structures. It does not tag the manifest itself; callers that need refs must add them in the surrounding pull path.

Config named refs are written in diff_id order and are used as the cache boundary. If the config stream already exists, the function trusts its named refs to recover layer verities and does not re-import layers. Import stats only reflect new work in this function; cached config/layer paths return default stats.

Progress state is externalized through `SharedReporter` events: `Message`, `Started`, `Done`, and `Skipped`. `ProgressRead` reports compressed bytes read, matching descriptor sizes.

## Dependencies and Integration Points

The module depends on `ocidir` for OCI layout reading and platform resolution, `cap_std_ext::cap_std` for capability-based directory access, Tokio `Semaphore` and `JoinSet` for bounded async layer import, `available_parallelism` for concurrency sizing, `composefs::repository::Repository` for stream/object persistence, `containers_image_proxy::oci_spec::image` for descriptors and media types, and internal `layer`, `delta`, `progress`, `oci_image`, `skopeo`, and crate-level identifier/stat helpers.

It is the fast path equivalent of the skopeo proxy importer. Its output must remain compatible with `OciImage::open`, `open_config`, fsck, GC, and EROFS generation.

## Risks and Edge Cases

- `parse_oci_layout_ref` treats an empty suffix after a trailing colon as `Some("")`, which callers must handle consistently with `ocidir`.
- Platform resolution rejects layouts that do not match the current platform unless they are detected as single-manifest delta artifacts first.
- The cached-config path assumes config named refs are complete and correct; missing layer refs fail before manifest storage.
- Layer tasks open blob files before spawning. This keeps task bodies simple but can fail serially during task setup.
- Sorting layers by size improves throughput but requires reordering results back to diff_id order. The code uses a map and then rebuilds ordered refs, so duplicate diff_ids would collapse in the map.
- `available_parallelism()` errors propagate and can abort import before any layer tasks start.
- Progress `Done` for tar layers reports descriptor `layer_size` rather than decompressed bytes; this is intentional because progress tracks compressed bytes read.
- Non-tar blob stats use object-store method data from `store_blob_async`; inlined metadata for the wrapper stream is not counted as layer tar inline bytes.

## Test Signals

The local tests cover `parse_oci_layout_ref` across plain paths, tags, Windows-style paths, embedded colons, and empty tags. `test_wrong_platform_rejected` builds a minimal layout for a foreign architecture and verifies the direct import returns a platform-selection error. Additional integration tests in `lib.rs` construct local OCI layouts and verify that fresh imports emit `Started` and terminal progress events, cached reimports emit `Skipped`, and `NullReporter` does not panic.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/oci_layout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/progress.rs -->
# sources/cloud-native/composefs-rs/crates/composefs-oci/src/progress.rs

## Purpose

`progress.rs` is a compatibility shim. Progress types now live in the core `composefs` crate, and this module re-exports them so existing `composefs-oci` users can keep importing `crate::progress::*` while migrating to `composefs::progress`.

## Important APIs, Types, and Functions

- `pub use composefs::progress::*;` re-exports the production progress API, including reporter traits/types and helpers such as `ProgressEvent`, `ProgressReporter`, `SharedReporter`, `NullReporter`, `ComponentId`, `ProgressRead`, `ProgressUnit`, and any other upstream progress items.
- `#[cfg(any(test, feature = "test"))] pub use composefs::progress::test_support;` re-exports progress test support only for test builds or when the crate `test` feature is enabled.

There are no local structs, functions, or implementations in this file.

## Control Flow

The file has no runtime control flow. Compilation conditionally exposes `test_support`, then publicly re-exports everything from `composefs::progress`.

## State and Persistence Behavior

This module owns no state and performs no persistence. It affects API compatibility only.

## Dependencies and Integration Points

The only dependency is the workspace/core `composefs` crate. Internal modules such as `lib.rs` and `oci_layout.rs` import progress symbols through `crate::progress`, while the actual implementations are provided by `composefs::progress`. Tests in `lib.rs` use `crate::progress::test_support::RecordingReporter` through the gated re-export.

## Risks and Edge Cases

- This shim couples the `composefs-oci` progress API surface to `composefs::progress`; upstream renames or removals are immediately reflected here.
- `test_support` is not available in normal builds unless the `test` feature is enabled. Production code must not depend on it.
- Because this is a wildcard re-export, rustdoc and downstream imports may expose more items than the OCI crate explicitly needs.

## Test Signals

There are no local tests. Coverage comes from callers, especially the OCI layout progress integration tests in `lib.rs`, which import `NullReporter`, `ProgressEvent`, `SharedReporter`, and test support through `crate::progress`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs-oci/src/progress.rs -->
