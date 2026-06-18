# sources/distributed-fs/lizardfs/src/chunkserver/masterconn.h

## Purpose
`masterconn.h` declares the small public surface of the master connection module.

## Important APIs, Types, and Functions
`masterconn_stats(uint64_t *bin, uint64_t *bout, uint32_t *maxjobscnt)` drains byte and max-job counters. `masterconn_init()` initializes config, singleton connection state, event-loop hooks, and starts connecting. `masterconn_init_threads()` creates the background job pool used for master-directed HDD and replication work.

## Control Flow
Startup calls `masterconn_init` during normal module initialization and `masterconn_init_threads` during late/thread initialization. Runtime behavior is then event-loop driven inside the implementation.

## State and Persistence Behavior
The header itself has no state. The implementation maintains connection and job-pool runtime state and causes persistent chunk changes by scheduling HDD operations.

## Dependencies and Integration Points
It includes only platform and integer headers. `init.h` references both init functions. Stats consumers can call `masterconn_stats` for charts/monitoring.

## Risks and Edge Cases
The API hides most lifecycle details, so call order matters: `masterconn_init_threads` assumes normal initialization has prepared the singleton/config. Stats are drain-and-reset, so multiple consumers would race semantically.

## Test Signals
Startup tests should assert `masterconn_init` precedes `masterconn_init_threads`. Stats tests should verify drain/reset behavior through the implementation.
