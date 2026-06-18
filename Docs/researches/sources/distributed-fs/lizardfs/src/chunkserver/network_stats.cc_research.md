# sources/distributed-fs/lizardfs/src/chunkserver/network_stats.cc

## Purpose
`network_stats.cc` defines global atomic counters for client/peer network traffic and high-level operation counts, plus a drain function for chart/status consumers.

## Important APIs, Types, and Functions
It defines `stats_bytesin`, `stats_bytesout`, `stats_hlopr`, `stats_hlopw`, and `stats_maxjobscnt`. `networkStats` atomically exchanges each counter with zero and writes the drained values to caller-provided pointers.

## Control Flow
Network worker code increments byte counters on socket reads/writes, increments high-level read/write operation counters on request start, and updates max job count during polling. Consumers call `networkStats` periodically to obtain deltas.

## State and Persistence Behavior
All state is in atomic process memory and is reset on each drain. There is no persistence.

## Dependencies and Integration Points
The file includes `network_stats.h`. `network_worker_thread.cc` and `network_main_thread.cc` use these counters; charts or monitoring code can call `networkStats`.

## Risks and Edge Cases
`stats_maxjobscnt` is updated racily in worker code and drained with exchange, so it is approximate. Drain-and-reset means multiple consumers would split counts. Atomic increments avoid data races but do not make multi-counter snapshots consistent.

## Test Signals
Unit tests can set counters and verify `networkStats` returns values and resets them. Stress tests can increment concurrently and verify no torn reads or crashes, accepting approximate max-job behavior.
