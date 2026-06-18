<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_list_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_list_test.go

Purpose: tests image-list behavior, size accounting, manifest classification, identity cache usage, and shared-size calculation for containerd-backed images.

Important APIs and flow: `imagesFromIndex` adapts special-image descriptors into containerd image records. `BenchmarkImageList` populates many generated images and optional containers to measure list scalability with shared-size computation. `TestImageListCheckTotalSize` builds a two-platform image and asserts combined and per-manifest content sizes, including after deleting layer blobs. `TestImageListIdentityUsesCacheOnly` and `TestImageListIdentityIsManifestScoped` verify identity data is not computed live and is keyed by image/index manifest/platform. `TestImageList` covers single image, multi-platform image, empty index, config target, text/plain pseudo content, and missing multi-platform state. `TestComputeSharedSizeIncludesSharedContentBlobs` validates shared layer and shared content blob accounting.

State and persistence: uses temporary blob directories and fake image services. Several tests mutate content by deleting blobs or inserting identity cache entries.

Dependencies and integration: depends on `specialimage`, fake content stores, containerd namespaces, daemon container store fakes, and `imagebackend.ListOptions`.

Risks and gaps: fake snapshotter usage is zero, so unpacked-size behavior is not fully validated. Some assertions depend on special-image descriptor ordering. Filter coverage for label/reference/before/since/until is not in this file.

Test signals: strong regression signal for partial content and multi-platform list semantics; benchmark signal for concurrent summary implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_list_test.go -->
