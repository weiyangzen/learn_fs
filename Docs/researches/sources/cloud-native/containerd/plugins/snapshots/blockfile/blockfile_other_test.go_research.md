# sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_other_test.go

## Purpose
This platform-specific test helper skips blockfile snapshotter tests on Windows and Darwin.

## Important APIs, Types, And Functions
`setupSnapshotter` calls `t.Skip("No support for loopback mounts")` and returns nil values.

## Control Flow
The function is selected by `windows || darwin` build tags and prevents tests from attempting unsupported loopback mounts.

## State And Persistence
No state is created.

## Dependencies And Integration Points
It pairs with the Linux loop setup helper and feeds `blockfile_test.go`.

## Risks
Platform coverage for blockfile behavior is intentionally absent on these systems.

## Test Signals
The test signal is a clean skip rather than failure on unsupported platforms.
