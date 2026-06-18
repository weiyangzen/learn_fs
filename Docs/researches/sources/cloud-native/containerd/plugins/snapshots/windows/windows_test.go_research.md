<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/windows_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/windows_test.go

## Purpose
Runs the generic snapshotter compliance suite against the Windows WCOW snapshotter.

## Important APIs, Types, And Functions
`newSnapshotter` constructs `NewWindowsSnapshotter` and returns a close function. `TestWindows` invokes `testsuite.SnapshotterSuite`.

## Control Flow
The test requires root/admin privileges, creates snapshotters under suite-provided roots, and lets the shared suite exercise snapshot lifecycle operations.

## State And Persistence
Uses temporary suite roots and closes each snapshotter after use.

## Dependencies And Integration Points
Depends on Windows build tags, `pkg/testutil.RequiresRoot`, and the shared snapshotter testsuite.

## Risks And Edge Cases
The generic suite does not necessarily cover all WCOW-specific hcsshim conversion, UVM scratch, or custom scratch size behavior.

## Test Signals
Provides baseline snapshotter API compatibility for the Windows implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/windows_test.go -->
