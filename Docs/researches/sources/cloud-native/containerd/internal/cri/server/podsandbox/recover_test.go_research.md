# sources/cloud-native/containerd/internal/cri/server/podsandbox/recover_test.go

## Purpose

This test file validates pod sandbox recovery behavior with fake containerd container and task implementations.

## Important APIs, Types, and Functions

`fakeTask` implements the containerd task interface methods needed by recovery, including `Status`, `Wait`, `Pid`, and `Delete`. `fakeContainer` implements metadata, runtime info, task lookup, and extension access. `sandboxExtension` creates typed sandbox metadata extensions. `TestRecoverContainer` drives the controller recovery path through table cases.

## Control Flow

The test builds fake containers with different metadata/task/status combinations, calls `RecoverContainer`, and asserts recovered sandbox status, store contents, and error handling. Fakes return not-found and status values to simulate restart races.

## State and Persistence Behavior

The fake controller store is mutated by recovery. No real containerd, filesystem, or namespace state is used.

## Dependencies and Integration Points

It exercises typeurl metadata decoding, sandbox status reconstruction, task wait channel registration, and controller store save behavior.

## Risks and Test Signals

The tests catch regressions in restart reconstruction and not-found handling. They cannot validate real shim/task-service cleanup, netns filesystem state, or concurrent task deletion timing.
