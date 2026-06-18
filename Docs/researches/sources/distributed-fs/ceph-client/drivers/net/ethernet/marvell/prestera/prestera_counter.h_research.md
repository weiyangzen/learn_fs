# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_counter.h

## Purpose
`prestera_counter.h` declares the public counter manager API used by Prestera ACL and other offload subsystems.

## Important APIs, Types, and Definitions
It defines `struct prestera_counter_stats` with packet and byte counters, forward-declares switch/counter/block types, and declares init/fini, counter get/put, and stats get functions.

## Control Flow
No runtime flow exists in the header. Callers initialize the manager on switch setup, request counters by hardware client, attach returned block/id pairs to offloaded objects, read stats, and put counters during teardown.

## State and Persistence
The opaque `prestera_counter` persists on `prestera_switch`. `prestera_counter_block` and counter IDs are opaque handles whose lifecycle is controlled by get/put. Stats are returned as packet/byte snapshots from cached polling state.

## Dependencies and Integration Points
The header depends only on Linux integer types and is included by ACL interfaces and the counter implementation. `prestera_acl.h` embeds counter block pointers and counter IDs in ACL action state.

## Risks and Edge Cases
Because block internals are opaque, callers must not infer readiness or lifetime; they must call `prestera_counter_put()` exactly once for successful `get()`. Stats can be zero before a poll has populated a newly allocated counter.

## Test Signals
Compile ACL/count-action users, test get/put symmetry, stats reads before and after polling, and switch fini warnings when counters remain allocated.
