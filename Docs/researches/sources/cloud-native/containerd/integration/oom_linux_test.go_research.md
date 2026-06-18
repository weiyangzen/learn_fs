# sources/cloud-native/containerd/integration/oom_linux_test.go

## Purpose

This Linux test stress-validates OOM event monitoring across repeated concurrent container OOMs. It ensures containers killed by memory limits report exit code 137 and reason `OOMKilled`.

## Important APIs, Types, And Functions

- `TestOOMEventMonitor` is the only test.
- It uses `newCtrdProc` to start an isolated containerd binary from `buildDir`.
- `podTCtx.createContainer` starts containers with tight memory and swap limits.
- `Eventually` polls container status for OOM results.

## Control Flow

The test writes a temporary containerd config pointing runc runtime path to the build directory, starts containerd, pulls BusyBox, creates eight host-network pod sandboxes, and then runs ten rounds. In each round it concurrently starts one container per pod executing `dd if=/dev/zero of=/dev/null bs=20M` with 15 MiB memory/swap limits. Each goroutine waits for the container to exit with code 137 and reason `OOMKilled`, then removes it.

## State And Persistence Behavior

State is isolated to the temporary containerd root and repeated container metadata/task records. It deliberately creates OOM events and validates their translation into CRI container status.

## Dependencies And Integration Points

It depends on Linux memory cgroups, built containerd/shim binaries in `buildDir`, BusyBox `dd`, CRI status, and concurrent test helper behavior.

## Risks And Edge Cases

The workload is resource-intensive and timing-sensitive. Hosts without swap accounting or with different OOM behavior could fail. The use of `sync.WaitGroup.Go` requires the Go version/library support present in this source tree.

## Test Signals

Passing indicates containerd consistently monitors and reports OOMKilled events under repeated concurrent pressure.
