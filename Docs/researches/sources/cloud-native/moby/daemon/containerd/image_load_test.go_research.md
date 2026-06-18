<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_load_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_load_test.go

Purpose: validates `LoadImage` platform filtering behavior for OCI/Docker archives loaded into the containerd image service.

Important APIs and flow: `TestImageLoad` creates single-platform, multi-platform, empty-index, and partial-content image archives with `specialimage`, tars them, and calls `imgSvc.LoadImage` with requested platform lists. `verifyImagePlatforms` inspects loaded images with manifest output and confirms the requested platforms appear.

State and persistence: uses a temporary labeled content store and fake image service. The `cleanup` helper removes image records through `ImageDelete` and deletes all content after each scenario to isolate cases.

Dependencies and integration: exercises archive import/load code outside this subset, then validates via `Images`/`ImageInspect` paths in this subset. It uses `platforms.Default` override to emulate daemon-native platform decisions.

Risks and gaps: the implementation under test is not in this work item, but the tests reveal expected containerd-store semantics: requested platforms must exist in the index and have required content, while all requested platforms can be retained. One platform constant is spelled `riskv64`, which is intentional test data but could hide typo-related expectations.

Test signals: covers empty index not-found, wrong single-platform request, all/single platform load from a multi-platform image, absent platform, and platform descriptor present with missing blobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_load_test.go -->
