# Research: sources/cloud-native/containerd/client/process.go

## Purpose
Defines the public `Process` abstraction for exec processes and implements the client-side wrapper that talks to the task service for lifecycle, IO, terminal, wait, and status operations.

## Important APIs, Control Flow, And State
`Process`, `ExitStatus`, and `process` cover ID, PID, start, kill, wait, delete, IO close, resize, IO access, and status. `Start` sends `StartRequest` with `ExecID`, records the PID, and closes/cancels IO on failure. `Kill`, `CloseIO`, `Resize`, and `Status` delegate to task service requests with gRPC error conversion. `Wait` starts a goroutine and returns a one-shot channel carrying either exit code/time or an error with `UnknownExitStatus`. `Delete` runs deletion options, rejects running/paused states, deletes the exec process, and then cancels/waits/closes IO. State is local PID/IO fields plus remote shim task state.

## Dependencies And Integration
Uses task service protobufs, `cio`, tracing, protobuf timestamp conversion, `errdefs`, and `errgrpc`. It is returned by `Task.Exec` and `Task.LoadProcess`.

## Risks And Test Signals
Risks include leaked IO on start/delete errors, waits blocked by caller context, state races between status and delete, and signal/exec ID confusion. Tests should cover start failure cleanup, wait error paths, delete preconditions, IO close stdin behavior, resize requests, and status mapping.
