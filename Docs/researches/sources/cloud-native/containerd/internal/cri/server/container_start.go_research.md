# sources/cloud-native/containerd/internal/cri/server/container_start.go

## Purpose
This file implements CRI `StartContainer`, including normal task start, checkpoint restore, IO/log setup, status transition, NRI lifecycle hooks, exit monitoring, and log writer creation.

## Important APIs, Types, and Functions
Key functions are `StartContainer`, `setContainerStarting`, `resetContainerStarting`, and `createContainerLoggers`. It uses containerd `NewTask`, `Restore`, `Task.Wait`, `Task.Start`, `startContainerExitMonitor`, NRI hooks, `updateContainerIOOwner`, and CRI loggers.

## Control Flow, State, and Persistence
Start looks up container metadata/info, sets `Starting`, checks sandbox readiness, creates log-backed IO, and either restores a checkpoint or creates a new task. On failure it writes exit status metadata with error reason/message and resets `Starting`. On success it records PID/start time, starts an exit monitor, sends a started event, and calls post-start hooks. Restore mode also deletes checkpoint artifacts after success. Log creation opens the CRI log path when configured and wires stdout/stderr, or discards output if logging is disabled.

## Dependencies and Integration Points
It integrates container store status, sandbox store readiness, runtime handler/path/endpoints, user namespace IO ownership, streaming/fifo IO, checkpoint restore metadata, NRI, tracing, metrics, and CRI eventing.

## Risks and Test Signals
Risks include races with remove, leaked tasks on start failure, incorrect failed-start state, log file leaks, restore artifact cleanup errors, and invalid target PID namespaces. `container_start_test.go` covers the `Starting` guard; Linux/other platform files cover IO owner options.
