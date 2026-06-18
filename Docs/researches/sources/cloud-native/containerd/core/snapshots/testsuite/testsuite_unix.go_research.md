# sources/cloud-native/containerd/core/snapshots/testsuite/testsuite_unix.go

## Purpose
This Unix-only helper normalizes process umask for the snapshotter conformance suite.

## Important APIs, Types, and Functions
`clearMask` calls `syscall.Umask(0)` and returns a closure that restores the previous mask.

## Control Flow
`SnapshotterSuite` calls `clearMask` before registering tests and defers the returned restore function. All tests then run with a zero umask so mode assertions are not altered by the caller environment.

## State and Persistence
The only state is process-global umask. It is restored at suite exit.

## Dependencies and Integration Points
The file is selected by `//go:build !windows` and is paired with the Windows no-op implementation.

## Risks
Umask is process-wide, while tests run in parallel. The suite changes it around test registration, but any concurrent test in the same process could theoretically observe the temporary value.

## Test Signals
Supports mode-sensitive tests such as root permission and directory permission checks.
