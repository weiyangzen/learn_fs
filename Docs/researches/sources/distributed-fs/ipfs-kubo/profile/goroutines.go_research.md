<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/profile/goroutines.go -->
# sources/distributed-fs/ipfs-kubo/profile/goroutines.go

## Purpose

This helper writes all goroutine stacks without the 64 MiB truncation behavior of Go's standard pprof stack writer.

## Important APIs, Types, and Functions

`WriteAllGoroutineStacks` repeatedly calls `runtime.Stack(buf, true)`, doubling the buffer from 1 MiB until it fits, then writes the captured stack dump to an `io.Writer`.

## Control Flow, State, and Integration

The function allocates progressively larger buffers and returns the writer error. It does not persist data itself; callers decide where profile output goes.

## Dependencies, Risks, and Test Signals

Dependencies are `runtime` and `io`. Risks include large memory allocation in processes with enormous goroutine dumps and racing stack changes while sizing. Profile tests and operational profile collection validate that dumps are complete enough for debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/profile/goroutines.go -->
