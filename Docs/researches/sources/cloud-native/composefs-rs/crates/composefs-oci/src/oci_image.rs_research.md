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
