# sources/cloud-native/containerd/internal/cri/io/helpers_unix.go

## Purpose

This non-Windows helper implements CRI local pipe opening with Unix FIFOs.

## Important APIs, Types, and Functions

`openPipe(ctx, fn, flag, perm)` delegates directly to `fifo.OpenFifo`, returning an `io.ReadWriteCloser`.

## Control Flow

The caller supplies the context, path, open flags, and permissions. `fifo.OpenFifo` handles FIFO creation/open and context cancellation. There is no additional state or retry logic.

## State and Persistence Behavior

The FIFO path may be created on disk with the requested permissions. The open handle is returned to callers and later closed by `wgCloser` or FIFO set cleanup.

## Dependencies and Integration Points

It is selected by `//go:build !windows` and integrates with `helpers.go` for local FIFO mode on Linux, Darwin, and other Unix-like targets.

## Risks and Edge Cases

Open flags must be chosen correctly by callers for stdin versus output. Cancellation behavior depends on `containerd/fifo`. File permissions are set to `0700` by current callers.

## Test Signals

Unit or integration tests can open read/write FIFO pairs, cancel the context during open, and verify close releases blocked readers/writers.
