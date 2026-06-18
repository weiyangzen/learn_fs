# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/deleted_state.go

## Purpose
Defines the terminal deleted process state for the shim process state machine.

## Important APIs, Control Flow, And State
`deletedState` implements state methods by returning errors for operations that are invalid after deletion, such as start, delete, pause, resume, checkpoint, exec, kill, update, and status. It preserves the invariant that once an init process transitions to deleted it cannot be manipulated as a live runtime process. It carries no fields and persists no state.

## Dependencies And Integration
Part of the `initState` interface used by `Init`. It integrates with created/running/stopped state transitions and guards ttrpc task service operations indirectly through process methods.

## Risks And Test Signals
Risks include missing methods if `initState` evolves or unclear error semantics for callers. Tests should cover delete transition behavior and that every lifecycle operation rejects deleted processes.
