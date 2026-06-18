# Research: sources/cloud-native/containerd/cmd/containerd-shim-runc-v2/process/io.go

## Purpose
Implements non-terminal shim IO setup and pluggable logging-binary IO for runc processes.

## Important APIs, Control Flow, And State
`processIO` wraps runc IO plus parsed stdio URI and copy mode. `createIO` chooses null IO, FIFO pipe IO, binary/binary-v2 logger IO, or file-backed stdout/stderr. `Copy` starts pipe copy goroutines through `copyPipes`. `copyPipes` opens FIFOs or files, handles stdout/stderr sharing with `countingWriteCloser`, copies stdout/stderr with pooled buffers, opens stdin nonblocking, and closes runc stdin on EOF. `NewBinaryIO` starts a logger process with extra file descriptors, waits for readiness (strict for `binary-v2`), and returns `binaryIO` which closes pipes and terminates the logger. State includes OS pipes/FIFOs/files, child logger processes, goroutines, and wait groups.

## Dependencies And Integration
Uses go-runc IO, containerd fifo, stdio URI conventions, namespace lookup, logging, OS pipes, exec, and helper utilities in `io_util.go`. It is used by init and exec creation.

## Risks And Test Signals
Risks include FIFO open deadlocks, logger readiness hangs/errors, shared stdout/stderr close ordering, file permission issues, and IO goroutine leaks. Tests should cover null/fifo/file/binary schemes, binary-v2 readiness, stdout-stderr same file behavior, stdin closure, and cleanup on partial errors.
