# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_hw_counters.c

## Purpose
`rxe_hw_counters.c` exposes RXE software counters through the RDMA hardware-stats interface.

## Important APIs, types, and functions
`rxe_counter_descs[]` maps `enum rxe_counters` indexes to stat names such as sent/received packets, duplicate/out-of-sequence requests, RNR/sequence/retry errors, send errors, link-down events, and RDMA send/recv counts. `rxe_ib_get_hw_stats()` copies atomic64 counter values into `struct rdma_hw_stats`. `rxe_ib_alloc_hw_port_stats()` allocates the stats descriptor structure and asserts descriptor count matches `RXE_NUM_OF_COUNTERS`.

## Control flow
RDMA core stats allocation calls `rxe_ib_alloc_hw_port_stats()`. Stats reads call `rxe_ib_get_hw_stats()`, which validates port/stats arguments and snapshots every counter.

## State and persistence
Counter values live in `rxe_dev.stats_counters[]` and are incremented by RXE packet, requester, responder, completer, and net paths. Stats persist for the life of the RXE device.

## Dependencies and integration points
The file depends on RDMA core hw stats APIs and `rxe_hw_counters.h`. It is wired into RXE device ops elsewhere and consumed by userspace RDMA stats tooling.

## Risks
The descriptor array and enum must remain in exact order and length. Adding counters requires updating both files and all counter increments. The port validation rejects port 0; callers must pass the RXE port number.

## Test signals
Read RDMA hw stats after traffic, duplicate/out-of-order packet tests, retry/RNR failures, link down events, and module reload. Build should catch descriptor/enum length mismatch via `BUILD_BUG_ON`.
