<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/native/native_test.go

## Purpose
Runs the generic containerd snapshotter compliance suite against the native snapshotter.

## Important APIs, Types, And Functions
`newSnapshotter` constructs `native.NewSnapshotter` and returns a close function. `TestNative` gates the suite by OS and root privileges.

## Control Flow
Windows is skipped because the native snapshotter is not implemented there. On other systems the test requires root and invokes `testsuite.SnapshotterSuite(t, "Native", newSnapshotter)`.

## State And Persistence
Uses temporary roots provided by the suite and closes the snapshotter after each test case.

## Dependencies And Integration Points
Depends on `snapshots/testsuite` and `pkg/testutil.RequiresRoot`, making this a conformance bridge rather than bespoke assertions.

## Risks And Edge Cases
The suite may not stress native-specific full-copy performance or xattr-copy behavior. Root and mount availability determine whether tests run.

## Test Signals
Signals broad snapshotter API compatibility: prepare/view/commit/remove/walk/mounts/usage behavior through the shared suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/native/native_test.go -->
