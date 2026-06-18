# sources/cloud-native/containerd/integration/container_io_leak_linux_test.go

## Purpose

This Linux integration test checks that a failed container start does not leak pipe file descriptors in the shim. It targets cleanup behavior after `runc` start failure, especially when the configured process command cannot be found.

## Important APIs, Types, And Functions

- `TestContainerIOLeakAfterStartFailed` creates a container with a nonexistent command and checks shim pipe count after start failure.
- `numPipe` shells out to `lsof -p <shimPid> | grep pipe` and counts matching lines.
- The test reuses `getShimPid` from the TTY leak test and `connectToShim`/`shimPid` from the issue 7496 helpers.

## Control Flow

The test skips non-runc `RUNC_FLAVOR` values because it is specifically probing runc shim behavior. It starts a sandbox, ensures BusyBox exists, creates a container whose command is `something-that-doesnt-exist`, records the shim PID before start, expects `StartContainer` to fail, and then asserts that `numPipe(pid)` is zero.

## State And Persistence Behavior

No durable state is intentionally changed. The state under test is the shim process file descriptor table after a failed `StartContainer`. Sandbox cleanup is provided by `PodSandboxConfigWithCleanup`.

## Dependencies And Integration Points

The test depends on Linux, runc, `lsof`, a running shim, CRI `CreateContainer`/`StartContainer`, and the ttrpc shim connection helpers. It observes containerd indirectly through host process inspection.

## Risks And Edge Cases

`lsof` availability and permissions are host-dependent. Counting grep output can miss pipes if `lsof` format changes. The test assumes the shim remains alive after the failed start long enough to inspect it.

## Test Signals

Passing indicates failed start cleanup closes exec/stdio pipes in the shim instead of leaving descriptors pinned.
