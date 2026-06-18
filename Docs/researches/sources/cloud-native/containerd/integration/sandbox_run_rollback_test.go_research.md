# sources/cloud-native/containerd/integration/sandbox_run_rollback_test.go

## Purpose

`sandbox_run_rollback_test.go` is a Linux failpoint-driven suite for `RunPodSandbox` rollback behavior across CNI setup failures, shim start/delete failures, restart persistence, and slow CNI operations.

## Important APIs, Types, and Functions

- Constants define failpoint runtime handler, failpoint CNI binary, shim annotation prefix, and CNI failpoint config annotation.
- Tests include `TestRunPodSandboxWithSetupCNIFailure`, `TestRunPodSandboxWithShimStartFailure`, `TestRunPodSandboxWithShimDeleteFailure`, `TestRunPodSandboxWithShimStartAndTeardownCNIFailure`, and `TestRunPodSandboxAndTeardownCNISlow`.
- `sbserverSandboxInfo` extracts verbose sandbox info from raw CRI status.
- `ensureCNIAddRunning` scans failpoint CNI process environments for the target pod name.
- `failpointConf`, `injectCNIFailpoint`, and `injectShimFailpoint` configure failure/delay injection through annotations and temporary JSON files.

## Control Flow

The tests build sandbox configs with labels and failpoint annotations, call `RunPodSandbox`, assert expected errors, list leftover sandboxes, verify NOTREADY state and metadata, optionally restart containerd, and then cleanup through `RemovePodSandbox` or stop/remove. Slow CNI tests run sandbox creation in a goroutine, wait until CNI Add is active, kill containerd with `SIGKILL`, then validate persisted partial sandbox state.

## State and Persistence Behavior

The suite intentionally leaves partial sandbox records when rollback cannot complete, then verifies those records survive restarts and retain metadata, IP/network info, netns path, and NOTREADY state. CNI failpoint configs are written to temporary files referenced by annotations.

## Dependencies and Integration Points

It integrates CRI runtime service, raw CRI status, internal pod sandbox info types, containerd failpoint parser, Linux process/env inspection helpers, daemon restart helpers, and the failpoint CNI/shim implementations.

## Risks and Edge Cases

These tests exercise race-prone failure windows. `SIGKILL` is used to avoid graceful shutdown side effects, and CNI process detection may be noisy if stale failpoint binaries run. Rollback semantics deliberately preserve records when deletion/teardown cannot be trusted.

## Test Signals

Failures identify regressions in sandbox rollback, partial-state persistence, restart recovery of failed sandboxes, or failpoint annotation validation.
