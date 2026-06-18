# sources/cloud-native/containerd/internal/cri/server/podsandbox/controller_test.go

## Purpose

This test file supplies a minimal controller fixture and verifies controller status translation for an in-memory pod sandbox.

## Important APIs, Types, and Functions

`newControllerService` builds a `Controller` with test config, real OS abstraction, and a fresh store. `Test_Status` saves a `PodSandbox` with a known ID and `StateReady`, calls `Status`, and asserts the returned `ControllerStatus` carries the sandbox ID and string state.

## Control Flow

The test constructs a sandbox object directly rather than starting a real containerd task. It exercises the store lookup and status conversion path in `Controller.Status`.

## State and Persistence Behavior

Only the in-memory `Store` is mutated. No containerd metadata, leases, snapshots, or files are involved.

## Dependencies and Integration Points

The fixture depends on CRI config, the OS interface, the podsandbox `types` package, and sandbox store status constants.

## Risks and Test Signals

The signal is narrow but useful: status calls work for cached sandboxes. It does not cover verbose status, not-found errors, task inspection, or plugin initialization.
