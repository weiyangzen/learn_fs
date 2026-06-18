# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/types.go

## Purpose
Defines configuration data structures passed into shim process creation, exec, and checkpoint operations.

## Important APIs, Control Flow, And State
`Mount` mirrors mount data needed by runc creation. `CreateConfig` carries container ID, bundle, runtime, rootfs mounts, stdio paths, checkpoint paths, parent checkpoint, terminal flag, and runtime options. `ExecConfig` carries exec ID, terminal/stdio fields, and process spec. `CheckpointConfig` carries CRIU work/path and option flags such as exit, TCP, external Unix sockets, terminal, file locks, and empty namespaces. These are pure data structs; runtime state changes happen in `Init`, `Exec`, and `runc.Container`.

## Dependencies And Integration
Uses protobuf `Any` for runtime options/spec data. The structs bridge task service requests to process implementation code.

## Risks And Test Signals
Risks include field mapping drift from task API requests and incomplete checkpoint option propagation. Tests should validate request-to-config conversion in `runc.Container` and option propagation into runc create/restore/checkpoint calls.
