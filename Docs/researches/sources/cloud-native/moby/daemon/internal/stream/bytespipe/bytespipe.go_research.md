# sources/cloud-native/moby/daemon/internal/stream/bytespipe/bytespipe.go

## Purpose
Implements a blocking in-memory `io.ReadWriteCloser` for daemon stream fan-out. It buffers bytes in pooled fixed buffers, supports backpressure, and allows readers to drain data once.

## Important APIs, Types, And Functions
`BytesPipe` has a mutex, condition variable, buffer list, buffered byte count, close error, and read-block flag. `New` initializes a minimum-capacity buffer. `Write` appends across fixed buffers, doubles buffer capacity up to `maxCap`, and blocks while buffered data is at or above `blockThreshold`. `Read` waits for data or close, drains buffers, returns buffers to pools, and wakes writers. `CloseWithError` and `Close` set the terminal read error.

## Control Flow
Writers loop until all input is copied or close/error occurs. When allocation would happen with too much buffered data, the writer waits and wakes a blocked reader if present. Readers wait only while empty and open, then copy as much as the caller buffer can hold and return emptied fixed buffers to capacity-keyed pools.

## State And Persistence
State is in memory. Buffer pools persist process-wide by capacity and may retain allocations after peak stream load. Closed pipes return `ErrClosed` to writers and the configured close error to readers.

## Dependencies And Integration Points
Used by `stream.Config.StdoutPipe` and `StderrPipe` as per-consumer pipes behind unbuffered broadcasters. It integrates with `io.Copy` paths in attach and container I/O.

## Risks And Test Signals
Backpressure and condition-variable ordering are deadlock-sensitive. `readBlock` is used only as a wake-up hint. Tests cover sequential reads/writes, a deadlock regression around `blockThreshold`, random chunk checksums, and benchmarks for allocation/performance.
