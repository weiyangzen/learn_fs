# sources/cloud-native/containerd/integration/sandbox_clean_remove_test.go

## Purpose

`sandbox_clean_remove_test.go` is a Linux integration suite for sandbox cleanup edge cases involving CNI IPAM checkpoints, closed network namespaces, and nil CNI results.

## Important APIs, Types, and Functions

- `TestSandboxRemoveWithoutIPLeakage` verifies host-local IP allocation remains while a dead sandbox is only stopped/not-ready and is released when the sandbox is removed.
- `TestSandboxStopWithNilCNIResult` verifies `StopPodSandbox` succeeds when CNI setup never completed and `CNIResult` is nil, even if CNI `Del` fails.

## Control Flow

The IP leakage test verifies host-local CNI config, runs a sandbox, extracts IP and network namespace from verbose sandbox info, checks `/var/lib/cni` checkpoint files, kills the sandbox process, unmounts/removes netns, waits for NOTREADY, stops/removes the sandbox, and asserts the IP checkpoint disappears. The nil-CNI test injects failpoints to delay CNI Add and fail Del, kills containerd during CNI Add, restarts, finds the leftover not-ready sandbox by label, confirms `CNIResult` is nil, and stops/removes it.

## State and Persistence Behavior

The tests inspect persisted CNI checkpoint files, sandbox verbose info, `NetNSClosed`, `CNIResult`, netns path, and CRI sandbox state across daemon restart.

## Dependencies and Integration Points

They depend on Linux CNI host-local IPAM, `SandboxInfo`, `KillPid`, `unix.Unmount`, failpoint helpers, process environment scanning, and CRI runtime service.

## Risks and Edge Cases

The first test skips unless host-local IPAM is configured. It walks `/var/lib/cni`, manipulates namespaces, and kills sandbox processes, so host permissions and cleanup are critical. The second test relies on failpoint CNI binary process detection through `CNI_ARGS`.

## Test Signals

Failures indicate IPAM leak regressions, incorrect netns-closed handling, or overly strict CNI teardown errors when setup never produced a CNI result.
