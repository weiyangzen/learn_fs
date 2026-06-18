# sources/cloud-native/containerd/internal/cri/io/exec_io.go

## Purpose

This file provides stdio handling for CRI exec sessions. Unlike `ContainerIO`, exec IO is short-lived and connects one client-facing set of streams directly to an exec process’s stdin/stdout/stderr over FIFOs or sandbox streaming endpoints.

## Important APIs, Types, and Functions

`ExecIO` implements `cio.IO` and holds an ID, `cio.FIFOSet`, opened `stdioStream`, and `wgCloser`. `NewFifoExecIO` creates named FIFOs under an IO root. `NewStreamExecIO` creates stable streaming URLs using the exec ID. `Config` exposes the `cio.Config`. `Attach` copies stdin and output and returns a done channel. `Cancel`, `Wait`, and `Close` control cancellation, waitgroups, and FIFO closure.

## Control Flow

Both constructors build a FIFO set, open it with `newStdioStream`, and return the configured object. `Attach` wraps stdin so it can interrupt `io.Copy`; on stdin completion it closes process stdin when `StdinOnce` is set and non-TTY, otherwise closes output readers to end the session. Each selected output starts a goroutine that copies from exec stdout/stderr into the client writer, closes both ends, closes stdin wrapper if present, and marks both the exec closer waitgroup and local attach waitgroup done. A background goroutine closes the returned `done` channel when all requested streams finish.

## State and Persistence Behavior

State is limited to open FIFOs/streams and goroutine synchronization. Exec stream IDs are deterministic from exec ID and stream type for reconnectable streaming. No CRI store state is persisted here.

## Dependencies and Integration Points

It shares helpers with container IO, uses `pkg/cio`, `pkg/ioutil`, and containerd logging. CRI exec server code constructs `ExecIO` for each exec request and passes `AttachOptions` from streaming server callbacks.

## Risks and Edge Cases

TTY mode omits stderr. If stdin ends first and `StdinOnce` is false, output streams are closed to prevent hanging sessions. Copy errors are logged but not returned through the done channel, so callers need other signals for failures. Close ordering matters to avoid blocked FIFO writers/readers.

## Test Signals

Tests should exercise stdin-only, stdout/stderr, TTY, cancellation, `StdinOnce`, stream close ordering, and `Close` on partially opened IO.
