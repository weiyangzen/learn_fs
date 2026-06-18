# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_counter.c

## Purpose
`prestera_counter.c` manages Prestera hardware counter blocks for ACL and related offloads. It allocates counter IDs from hardware blocks by client, polls counter blocks asynchronously in bulk, exposes packet/byte stats, clears counters on read/free, and releases hardware blocks when unused.

## Important APIs, Types, and Functions
Public APIs are `prestera_counter_init()`, `prestera_counter_fini()`, `prestera_counter_get()`, `prestera_counter_put()`, and `prestera_counter_stats_get()`. Internal structures are `prestera_counter` and `prestera_counter_block`. Helpers manage block list lookup/add/get/put, IDR allocation, refcounts, ready/invalid flags, and delayed work polling via `prestera_counter_stats_work()`.

## Control Flow
Initialization creates a manager, block list, mutex, and schedules delayed polling. Counter allocation finds a non-full block for the client or gets a new hardware block, then allocates a cyclic counter ID. If allocation occurs while the block is updating, the counter flag is marked invalid so stale in-flight stats are cleared before use. Poll work triggers a hardware block snapshot, reschedules after a short delay to fetch bulk chunks, stores stats, marks invalid counters ready after clearing them, rotates to the next block, and schedules the next poll. Stats get returns zero until ready, then returns and clears cached stats.

## State and Persistence
Manager state includes block array, current index, total read count, and fetch-in-progress flag. Block state includes hardware block id/offset/count/client, IDR of allocated counters, refcount, mutex, cached stats array, per-counter ready flags, updating/full booleans. Hardware counter blocks persist until `prestera_counter_block_put()` releases them.

## Dependencies and Integration Points
The file depends on Prestera hardware counter APIs (`block_get/release`, `trigger`, `counters_get`, `abort`, `clear`), delayed work, mutexes, IDR, refcounts, and `prestera_acl.c` count actions/stat reads.

## Risks and Edge Cases
Delayed polling is asynchronous and can race allocation/free without correct block locks and refcounts. `prestera_counter_block_put()` frees `stats` but the shown code does not free `counter_flag`, which looks like a memory leak. `prestera_counter_is_ready()` reads flags without locking. Abort paths reset manager fetch state and rotate blocks, so repeated hardware errors can stall fresh stats. Stats are cleared on every read, providing delta-like behavior.

## Test Signals
Test allocation/free across multiple clients, block exhaustion and new block creation, allocation during an active update, stats polling over more than 256 counters, hardware trigger/fetch/abort failures, concurrent stats_get/put, ACL count action integration, module unload with no live blocks, and leak detection for block arrays/flags/stats.
