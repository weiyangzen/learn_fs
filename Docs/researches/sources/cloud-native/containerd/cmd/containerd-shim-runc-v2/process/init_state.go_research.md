# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/init_state.go

## Purpose
Defines the init process lifecycle state machine, including normal created/running/stopped states and checkpoint-created restore state.

## Important APIs, Control Flow, And State
`initState` declares lifecycle methods. `createdState` permits start, delete, update, kill, and exec, while rejecting pause/resume/checkpoint. `createdCheckpointState` starts from runc restore options and transitions similarly after restore. Running state supports pause, checkpoint, update, exec, kill, and stop transition; stopped state permits delete and rejects active operations. Each state calls underlying `Init` methods and switches `p.initState` on legal transitions. State persistence is in the `Init` object; runc state changes occur through delegated operations.

## Dependencies And Integration
Uses go-runc restore options, protobuf Any for updates, log/error helpers, and state-name utilities. It coordinates with `Init.Create`, checkpoint/restore paths, and reaper-driven `SetExited`.

## Risks And Test Signals
Risks include illegal transition bugs, restore-specific console/IO setup failures, and operation availability differing from containerd API expectations. Tests should cover transition matrix, created checkpoint start, pause/resume/checkpoint legality, update in created/running, and set-exited behavior.
