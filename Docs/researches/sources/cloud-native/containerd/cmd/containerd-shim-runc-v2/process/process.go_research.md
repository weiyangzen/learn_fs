# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/process.go

## Purpose
Defines the common shim-side `Process` interface implemented by init and exec process types.

## Important APIs, Control Flow, And State
The interface covers identity, PID, exit status/time, stdin closer, stdio metadata, status, wait, resize, start, delete, kill, and `SetExited`. It establishes the contract used by `runc.Container` and task service without embedding runc-specific concrete types. No control flow or persistence exists in this file; it is a type boundary.

## Dependencies And Integration
Depends on `context`, `io`, `time`, `console`, and containerd `stdio`. It is implemented by `Init` and `Exec`, stored in container process maps, and driven by ttrpc task service methods.

## Risks And Test Signals
Risks are interface drift and inconsistent semantics between init and exec implementations. Compile-time assertions or targeted tests should ensure both concrete process types satisfy the interface and agree on wait/delete/status behavior.
