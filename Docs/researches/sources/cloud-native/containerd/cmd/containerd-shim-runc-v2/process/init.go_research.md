# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/init.go

## Purpose
Implements shim-side init process management for a runc container, including create, restore, start, wait, delete, pause/resume, kill, update, checkpoint, exec, and IO cleanup.

## Important APIs, Control Flow, And State
`Init` stores process state, wait channel, bundle/work dirs, console/platform, runc handle, IO handles, rootfs path, option flags, PID, status, and timestamps. `Create` sets up terminal socket or pipe IO, handles checkpoint restore state, calls runc create, opens stdin, wires console/pipe copying, and records PID from `init.pid`. `Start`, `Delete`, `Pause`, `Resume`, `Kill`, `Update`, `Checkpoint`, and `Exec` delegate through `initState` to enforce lifecycle. `setExited` records exit time/status, shuts down console, and releases waiters. `delete` drains IO, deletes runc state, closes pipes, and recursively unmounts rootfs. Persistent state includes runc state under root, bundle files, mounted rootfs, pid files, checkpoint data, and generated exec specs.

## Dependencies And Integration
Uses go-runc, containerd mount and stdio helpers, console/fifo IO, OCI specs, protobuf Any, Unix syscalls, and state implementations. It is owned by `runc.Container` and task service.

## Risks And Test Signals
Risks include create/restore cleanup gaps, IO goroutine leaks, rootfs unmount failures, start/exit ordering races, checkpoint side effects, and PID file errors. Tests should cover create terminal/nonterminal, checkpoint restore, lifecycle transitions, IO drain timeout, unmount error propagation, and concurrent start/exit behavior.
