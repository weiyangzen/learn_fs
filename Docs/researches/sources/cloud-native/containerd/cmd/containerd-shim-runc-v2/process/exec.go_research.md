# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/exec.go

## Purpose
Implements shim-side exec process handling for additional processes inside an existing runc container.

## Important APIs, Control Flow, And State
`Exec` stores ID, PID, status, timestamps, stdio, IO pipes, console, and wait channel. Creation decodes the process spec, sets up terminal or pipe IO, writes the exec process JSON into the bundle, invokes runc `exec`, wires console or pipe copying, opens stdin when provided, and records PID. Lifecycle methods start/wait/delete/kill/resize/status mirror `Process`. On exit it records status/time, shuts down console, closes wait channel, and later deletion drains IO and removes resources. Persistent state includes the generated exec spec file and runc process state; local state is protected by mutexes.

## Dependencies And Integration
Uses go-runc, typeurl/protobuf specs, stdio/console/fifo IO utilities, process state helpers, and the parent `Init.exec` path. It is exposed through `runc.Container.Exec` and task service `Exec`/`Start`.

## Risks And Test Signals
Risks include IO leaks on partial exec creation, invalid process spec unmarshaling, console handoff timeouts, PID file read failures, and deleting before stopped. Tests should cover terminal and nonterminal execs, start errors, wait behavior, kill behavior, IO cleanup, and duplicate exec IDs through container reservation.
