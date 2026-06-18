# sources/cloud-native/containerd/internal/cri/io/helpers_windows.go

## Purpose

This Windows helper implements CRI local pipe opening with Windows named pipes.

## Important APIs, Types, and Functions

`pipe` wraps a `net.Listener`, accepted `net.Conn`, accept error, and waitgroup. `openPipe` creates a `winio.ListenPipe`, starts an accept goroutine, closes the pipe on context cancellation, and returns the wrapper. `Read`, `Write`, and `Close` wait for the accept goroutine and then operate on the accepted connection or return the accept error.

## Control Flow

Opening returns before a client connects. First read/write blocks until `Accept` completes. Cancellation closes the listener, which unblocks accept. `Close` closes the listener, waits for accept completion, and closes the connection if one exists.

## State and Persistence Behavior

The state is an OS named-pipe listener and possibly one accepted connection. There is no filesystem directory state beyond the named-pipe namespace.

## Dependencies and Integration Points

It uses `github.com/Microsoft/go-winio` and satisfies the `openPipe` contract consumed by `helpers.go`.

## Risks and Edge Cases

Only one accepted connection is represented. `conErr` is written by the accept goroutine and read after `Wait`, which is safe by synchronization. Close before connect returns the accept error. The `flag` and `perm` parameters are ignored because Windows named pipe APIs do not map directly to Unix flags.

## Test Signals

Windows tests should cover delayed client connect, cancellation before connect, read/write after connect, and close behavior when accept fails.
