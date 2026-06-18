# sources/cloud-native/containerd/core/snapshots/testsuite/testsuite_windows.go

## Purpose
This Windows helper provides the same `clearMask` symbol as Unix builds without changing any process state.

## Important APIs, Types, and Functions
`clearMask` returns an empty restore closure.

## Control Flow
The snapshotter suite can call `clearMask` unconditionally while Windows builds avoid unsupported umask operations.

## State and Persistence
No state is read or written.

## Dependencies and Integration Points
This file is selected on Windows and complements the non-Windows implementation.

## Risks
Windows filesystem permission semantics differ from Unix, so tests depending on Unix modes are skipped or interpreted elsewhere.

## Test Signals
The helper keeps the suite buildable on Windows while preserving the shared suite API.
