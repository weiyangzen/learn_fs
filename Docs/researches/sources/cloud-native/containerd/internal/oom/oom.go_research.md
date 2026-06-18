# sources/cloud-native/containerd/internal/oom/oom.go

## Purpose
Defines the Linux OOM watcher interface used to monitor cgroup v2 out-of-memory events for containers.

## Important APIs, Types, And Functions
`EventFunc` is a callback receiving a container ID. `Interface` exposes `Add(containerID, pid, fn)` and `Stop(containerID)`.

## Control Flow
Implementations start monitoring the cgroup for a process PID and invoke callbacks when `oom_kill` events increase.

## State And Persistence
Interface only; implementation state is in `watcher.go`.

## Dependencies And Integration Points
Linux build tag. Integrates CRI/container lifecycle monitoring with cgroup v2 memory events.

## Risks
The interface still takes a PID because cgroups v2 package does not expose the cgroup path directly, as noted by TODO.

## Test Signals
`watcher_test.go` validates the concrete implementation under root/cgroup-v2 conditions.
