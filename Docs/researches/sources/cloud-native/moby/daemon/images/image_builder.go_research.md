<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_builder.go -->
# sources/cloud-native/moby/daemon/images/image_builder.go

Purpose: provides legacy builder access to images and layers, including pull-on-demand, readonly layers, temporary writable layers, and image creation.

Important APIs and control flow: `roLayer` wraps a referenced layer and releases it exactly once. `rwLayer` mounts a temporary RW layer, exposes its root, commits its tar stream as a new readonly layer, and releases/unmounts it. `newROLayerForImage` holds a layer-store reference for an image rootfs. `pullForBuilder` normalizes refs, resolves auth, pulls, then tolerates a special platform-mismatch warning case. `GetImageAndReleasableLayer` implements builder `FROM` logic, including scratch handling, no-pull/force-pull behavior, OS checks, and final layer acquisition. `CreateImage` writes config JSON, parent links, and built-locally metadata.

State and persistence: creates and releases layer-store references, temporary RW layers, new image-store records, parent metadata, and built-locally flags. Pulling may update the image/reference/content stores.

Dependencies and integration: connects legacy builder interfaces to `ImageService`, registry auth resolution, distribution pull, layer store, streamformatter progress output, and OCI platform checks.

Risks: every `GetImageAndReleasableLayer` caller must release the returned layer or leak layer references. RW layer `Commit` registers tar content but leaves empty-layer optimization as a TODO. Platform mismatch handling intentionally emits a warning and suppresses an error in a known manifest/config inconsistency case.

Test signals: no direct unit tests here; behavior is covered by Dockerfile build and pull integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_builder.go -->
