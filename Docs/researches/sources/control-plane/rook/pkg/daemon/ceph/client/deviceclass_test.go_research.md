# sources/control-plane/rook/pkg/daemon/ceph/client/deviceclass_test.go

Purpose: validates device-class OSD lookup.

Important test case: `TestGetDeviceClassOSDs` configures a mock executor for `ceph osd crush class ls-osd ssd` and `hdd`, expecting `[0,1,2]` for `ssd` and `[]` for `hdd`. It asserts both parsed result slices.

Control flow and dependencies: the test relies on `NewCephCommand()` placing command-specific args first and standard flags after them. It uses `AdminTestClusterInfo()` and `exectest.MockExecutor`.

Risks and coverage gaps: only the OSD lookup function is tested. There is no coverage for `GetDeviceClasses()`, command failures, invalid JSON, or device class names requiring special handling. The mock branches by fixed arg indexes, so it would catch changes in command construction order.
