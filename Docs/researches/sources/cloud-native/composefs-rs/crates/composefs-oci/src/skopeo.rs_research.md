# sources/cloud-native/composefs-rs/crates/composefs-oci/src/skopeo.rs

## Purpose
This module is the OCI image pull path for `composefs-oci`. It opens an image reference through `containers-image-proxy`/skopeo, fetches manifests, configs, and blobs, imports layer content into a composefs `Repository`, and records config and manifest splitstreams with named references to their dependent layers. It also contains the local OCI layout fast path and the delta artifact path.

## Important APIs, Types, and Functions
`PullResult<ObjectID>` carries manifest digest/verity and config digest/verity, with `into_config()` and `into_manifest()` compatibility helpers. The content type constants identify splitstreams: `TAR_LAYER_CONTENT_TYPE`, `OCI_CONFIG_CONTENT_TYPE`, `OCI_MANIFEST_CONTENT_TYPE`, and `OCI_BLOB_CONTENT_TYPE`. `ImageOp` owns the repository, proxy, opened image, reporter, and transport. `ImageOp::new()` validates write access, applies containers-storage-specific skopeo/podman handling, and opens the image. `ensure_layer()` imports or reuses a layer. `ensure_config_with_layers()` imports or reuses config and all referenced layers. `pull()` stores the manifest and detects delta artifacts. `ProxyBlobReader` adapts skopeo blob access for delta import. Public entry points are `pull_image()` and backward-compatible `pull()`.

## Control Flow
`pull_image()` first ensures the repo is writable and parses `imgref`. `oci:` references bypass skopeo and call `oci_layout::import_oci_layout`; all other transports construct `ImageOp` and call `pull()`. `ImageOp::pull()` fetches raw OCI manifest bytes, parses them, dispatches delta artifacts to `pull_delta()`, otherwise imports config and layers, then writes a manifest splitstream if missing. `ensure_config_with_layers()` first checks for an existing config splitstream; on cache hit it reads named layer refs back from the config stream. On miss it downloads the config, extracts diff IDs, sorts layer downloads by descending size, limits concurrency with `available_parallelism()`, imports layers in parallel, then writes a config splitstream with named refs keyed by diff ID. `ensure_layer()` checks the repository for an existing layer stream. Missing tar layers are downloaded, progress-wrapped, decompressed, and passed to `import_tar_async`; non-tar artifact blobs are stored raw and wrapped in an `OCI_BLOB_CONTENT_TYPE` stream. After pull, `pull_image()` calls `ensure_oci_composefs_erofs()` for container images and tags artifacts directly.

## State and Persistence
Persistent state is the composefs repository: objects, stream IDs, stream content IDs, named stream references, image tags, and generated EROFS references. Layer content IDs are derived from diff IDs, config content IDs from config digests, and manifest content IDs from manifest digests. Cache hits short-circuit network and storage work. Delta blobs are temporarily copied to repo tmpfiles before apply.

## Dependencies and Integration Points
This file integrates `containers-image-proxy`, skopeo/podman, `tokio`, composefs repository APIs, `layer` import helpers, OCI image tagging/manifests, delta import, progress reporting, and OCI layout import. It handles transport quirks for rootless `containers-storage:` and digest references.

## Risks
Correctness depends on proxy driver futures being awaited so skopeo validates content. Parallel layer sorting returns task indexes from sorted order, but final layer refs are reconstructed by diff ID, which avoids order corruption unless duplicate diff IDs appear. Existing config streams must contain all named layer refs or cache hit reconstruction fails. Non-tar artifacts intentionally skip tar import and EROFS generation. Rootless containers-storage behavior relies on external podman/skopeo availability.

## Test Signals
No tests live in this file, but behavior is covered indirectly by OCI image construction, layout import, layer import, manifest/tagging, delta, and repository tests elsewhere. The main test indicators are cache reuse, config named-ref reconstruction, non-tar artifact handling, local OCI layout fast path, delta import, and rootless containers-storage reference normalization.
