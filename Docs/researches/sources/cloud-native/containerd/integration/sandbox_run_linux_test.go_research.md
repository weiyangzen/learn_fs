# sources/cloud-native/containerd/integration/sandbox_run_linux_test.go

## Purpose

`sandbox_run_linux_test.go` contains a Linux regression test for sandbox controller behavior when sandbox removal has a shim `Delete` failpoint.

## Important APIs, Types, and Functions

- `TestPodSandboxController_ShouldBackoffExitEventWhenFail` injects a one-shot shim `Delete` error, runs a sandbox, stops it, and removes it.

## Control Flow

The test creates a pod sandbox config for the failpoint namespace, annotates the shim `Delete` method with `1*error(retry)`, starts the sandbox through the failpoint runtime handler, stops it, and removes it. Successful remove despite the injected delete error validates that the controller backs off or tolerates the transient failure path correctly.

## State and Persistence Behavior

It focuses on transient sandbox lifecycle state, failpoint annotations, and cleanup event ordering rather than long-lived persistence.

## Dependencies and Integration Points

It relies on the Linux sandbox controller, CRI runtime service, failpoint runtime handler, and common sandbox config helpers.

## Risks and Edge Cases

This is a narrow regression test. Its value depends on the failpoint shim honoring the one-shot `Delete` error and on controller cleanup logic preserving enough state to retry/remove successfully.

## Test Signals

Failure points to sandbox controller backoff, shim delete retry, or cleanup event ordering regressions.
