<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/inspect_test.go -->
# sources/cloud-native/moby/daemon/inspect_test.go

Purpose: unit tests for minimal container inspect data construction and missing RW-layer handling.

Important APIs and control flow: `TestGetInspectData` constructs a minimal container and daemon link index/config store, then verifies `getInspectData` does not error. `TestContainerInspect` skips snapshotter mode, verifies a live container without `RWLayer` errors, then marks it dead and verifies the missing layer is tolerated.

State and persistence: creates in-memory daemon/container structs only.

Dependencies and integration: uses daemon container/network structs, config store, exec store, and `gotest.tools` assertions. It validates behavior in `containerInspect`.

Risks: tests do not exercise network endpoint copying, graphdriver metadata success, size paths, or exec inspect. Snapshotter mode is skipped for the RW-layer expectations.

Test signals: direct coverage for critical missing-RW-layer branch behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/inspect_test.go -->
