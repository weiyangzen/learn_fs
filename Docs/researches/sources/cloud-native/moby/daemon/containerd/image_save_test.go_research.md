<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_save_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_save_test.go

Purpose: validates multi-platform shallow export behavior for the containerd-backed image service.

Important APIs and flow: `TestImageMultiplatformSaveShallowWithNative` creates an index where native and another platform are present and one platform is missing, then verifies `ExportImage` succeeds for default/native/present platforms and fails for a missing platform. `TestImageMultiplatformSaveShallowWithoutNative` creates an index where native is missing, verifies requested native/nonexistent platforms fail, requested present platforms succeed, and mixed present+missing behavior depends on whether the missing entry is native. One default export case is skipped pending a CLI issue.

State and persistence: temporary blob directories plus fake image service/image store; no registry or long-lived state.

Dependencies and integration: exercises export implementation outside this work item but relies on platform matching and present-content traversal behavior shared with image manifest/list/push paths.

Risks and gaps: skipped default-without-native scenario records unresolved behavior. Tests use fake stores and do not inspect tar contents, only success/error.

Test signals: important for shallow multi-platform images where an index references platforms not locally available.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_save_test.go -->
