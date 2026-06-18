<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_inspect.go -->
# sources/cloud-native/moby/daemon/images/image_inspect.go

Purpose: constructs the API image inspect response from legacy image, layer, and reference state.

Important APIs and control flow: `ImageInspect` resolves the image with optional platform, gets layer size and graphdriver metadata, reads last-updated time, splits references into tags and digests, derives fallback comment from history, converts container config to Docker OCI image config, and returns both modern inspect fields and deprecated legacy fields. `getLayerSizeAndMetadata` loads the rootfs chain layer, reads size and metadata, and releases it.

State and persistence: reads image store, reference store, layer store, and image last-updated metadata. No state is written.

Dependencies and integration: used by image inspect API and depends on storage driver metadata, `containerConfigToDockerOCIImageConfig`, and platform-aware `GetImage`.

Risks: corrupt or missing layer metadata fails the inspect request. Deprecated fields are still populated for compatibility, so config shape changes affect older clients.

Test signals: no direct tests in this subset; image inspect API tests provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_inspect.go -->
