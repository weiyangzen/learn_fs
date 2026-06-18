# sources/distributed-fs/lizardfs/src/chunkserver/network_stats.h

## Purpose
`network_stats.h` declares shared atomic network/stat counters and the drain API used by the chunkserver network subsystem.

## Important APIs, Types, and Functions
The header declares extern atomics for bytes in/out, high-level read/write operation counts, and maximum observed job count. `networkStats` drains these into output pointers.

## Control Flow
Worker code updates the extern counters directly. Monitoring/chart code calls `networkStats` to obtain interval deltas and reset counters.

## State and Persistence Behavior
The header declares runtime-only process counters. They are not persisted and are reset through exchange in the implementation.

## Dependencies and Integration Points
It depends on platform, integer, and atomic headers. It is included by worker/main network code and any chart/stat collector.

## Risks and Edge Cases
Direct extern counter access makes it easy for future code to update the wrong metric or bypass desired aggregation rules. Drain semantics require a single logical consumer.

## Test Signals
Compile tests should ensure exactly one definition exists. Stats tests should verify counter increments in worker read/write paths become visible through `networkStats`.
