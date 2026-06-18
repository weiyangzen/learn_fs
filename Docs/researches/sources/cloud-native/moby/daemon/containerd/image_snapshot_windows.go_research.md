<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot_windows.go -->
# sources/cloud-native/moby/daemon/containerd/image_snapshot_windows.go

Purpose: provides Windows stubs for snapshot remap/unremap helpers that are meaningful on Unix user-namespace setups.

Important APIs and flow: defines the same `remapSuffix` constant and no-op `copyAndUnremapRootFS`, `remapSnapshot`, and `unremapRootFS` methods so cross-platform callers compile.

State and persistence: no state is changed on Windows by these functions.

Dependencies and integration: keeps `image_snapshot.go` portable while Windows layer-folder handling lives in `service_windows.go`.

Risks: because these are no-ops, any future Windows feature that expects ownership remapping must not silently rely on these methods. Behavior is intentionally platform divergent.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot_windows.go -->
