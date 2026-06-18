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
