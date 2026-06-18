# sources/cloud-native/containerd/integration/runtime_handler_test.go

## Purpose

`runtime_handler_test.go` verifies that a sandbox created with the configured runtime handler reports that handler consistently through CRI status and list APIs.

## Important APIs, Types, and Functions

- `TestRuntimeHandler` creates a sandbox via `PodSandboxConfigWithCleanup`, then checks `PodSandboxStatus.RuntimeHandler` and `ListPodSandbox[0].RuntimeHandler`.

## Control Flow

The test logs whether the global `--runtime-handler` flag is empty or explicit, creates a sandbox, fetches status and list results, and asserts the returned runtime handler equals the requested flag value.

## State and Persistence Behavior

It relies on CRI sandbox metadata storing the runtime handler for subsequent status/list retrieval. Cleanup is handled by the sandbox helper.

## Dependencies and Integration Points

The test uses integration-wide `runtimeHandler` flag, CRI runtime service, and Kubernetes CRI filter/status types.

## Risks and Edge Cases

It assumes the newly created sandbox is the first entry in `ListPodSandbox`, so pre-existing sandboxes could make the list assertion fragile. The test covers reporting, not actual runtime implementation differences.

## Test Signals

Failure signals a regression in CRI runtime handler persistence or response population.
