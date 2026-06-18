# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/exec_state.go

## Purpose
Defines the state machine for shim exec processes.

## Important APIs, Control Flow, And State
The exec state interface and concrete states model created, running, stopped, and deleted exec lifecycles. Created can start, kill, delete, and transition; running can kill and becomes stopped on exit; stopped permits delete; deleted rejects operations. State methods delegate to underlying `Exec` helpers for runc actions and enforce legal transitions. Persistence is not direct, but state transitions determine when wait channels close, exit status is recorded, and runc delete/IO cleanup can run.

## Dependencies And Integration
Uses context, errors, and state-name utilities. It is embedded in `Exec` and driven by shim service calls and reaper exit events.

## Risks And Test Signals
Risks include invalid transitions panicking or returning inconsistent errors, deletion allowed too early, and exit races with start. Tests should cover every transition, set-exited behavior from each live state, and operation rejection by stopped/deleted states.
