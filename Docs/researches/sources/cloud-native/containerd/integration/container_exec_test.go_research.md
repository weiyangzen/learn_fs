# sources/cloud-native/containerd/integration/container_exec_test.go

## Purpose

This integration test verifies CRI `ExecSync` IO draining behavior after an exec process exits while leaving background children alive. It targets a regression-prone container lifecycle edge where the exec command returns, but inherited stdout/stderr pipes may remain open and block CRI response completion.

## Important APIs, Types, And Functions

- `TestContainerDrainExecIOAfterExit` is the only test entry point.
- Shared helpers `PodSandboxConfigWithCleanup`, `ContainerConfig`, `WithCommand`, and `EnsureImageExists` create a long-lived BusyBox container.
- `runtimeService.ExecSync` drives the actual exec calls and checks timeout/error behavior.

## Control Flow

The test skips Windows because detached process behavior differs there. It creates a sandbox and a BusyBox container running `sleep 365d`, then starts the container. It first executes `sh -c "sleep 365d &"` with a five-second timeout and requires an error containing `failed to drain exec process`, proving CRI does not hang forever when IO remains open. It then executes `sleep 2s &` with a longer timeout and expects success, proving short-lived inherited IO can be drained before the timeout.

## State And Persistence Behavior

All state is transient: a sandbox, container, and exec processes. Cleanup removes and stops the container through deferred CRI calls. The behavioral state under test is not persisted data but shim/exec pipe lifecycle after exec command completion.

## Dependencies And Integration Points

The file depends on the CRI runtime service, the shared integration helper layer, and the configured BusyBox image from `integration/images`. It integrates with containerd shim exec handling and CRI timeout/error propagation.

## Risks And Edge Cases

The assertions are timing-sensitive and depend on shell background job behavior. A too-small timeout could become flaky on slow hosts, while a too-large timeout slows failure detection. The error-string check couples the test to CRI error wording.

## Test Signals

Passing confirms that stuck exec IO is surfaced as a timeout/error and that drainable short-lived background process IO completes successfully.
