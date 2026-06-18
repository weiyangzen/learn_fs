# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/alias_GUID.c

## Purpose
`alias_GUID.c` manages SR-IOV alias GUID assignment for mlx4 master devices. It tracks desired GUIDInfo records, sends SA GUIDInfo set/delete requests, updates caches from SMP responses, and notifies slaves when their GUID state changes.

## Important APIs, Types, And Functions
External entry points include `mlx4_ib_update_cache_on_guid_change()`, `mlx4_ib_notify_slaves_on_guid_change()`, `mlx4_ib_slave_alias_guid_event()`, `mlx4_ib_invalidate_all_guid_record()`, `mlx4_ib_init_alias_guid_work()`, `mlx4_ib_destroy_alias_guid_service()`, and `mlx4_ib_init_alias_guid_service()`. `aliasguid_query_handler()` handles SA responses. `invalidate_guid_record()`, `set_guid_rec()`, `set_required_record()`, `get_low_record_time_index()`, `get_next_record_to_update()`, and `alias_guid_work()` implement scheduling and retry logic.

## Control Flow
Initialization allocates/registers an SA client, initializes per-port records to delete values, optionally clears admin GUIDs for SM assignment, invalidates records, and creates ordered per-port workqueues. Invalidation marks records idle and queues work. Work selects the earliest due record, decides whether to set or delete based on pending GUID values, queries port state, sends an SA GUIDInfo request, and records callback context. The callback compares SM responses with required values, updates admin/cache data, applies exponential retry for declined entries, marks records set when complete, notifies slaves, and reschedules the next record.

## State And Persistence
Per-port alias GUID state lives in `dev->sriov.alias_guid.ports_guid[]`: records, GUID indexes, status, retry schedules, time-to-run, callbacks, state flags, and workqueue. Admin GUIDs stored through `mlx4_set_admin_guid()` provide persistence across subsequent requests as mediated by mlx4 core. The demux GUID cache is updated on GUIDInfo changes and used to decide slave notifications.

## Dependencies And Integration Points
This file depends on mlx4 master/SR-IOV helpers, IB SA GUIDInfo queries, IB MAD/SA data structures, port query state, slave port-state machinery, GUID change EQEs, workqueues, spinlocks, and the module parameter/flag controlling SM GUID assignment.

## Risks
The code has intricate locking across `going_down_lock` and `ag_work_lock`; teardown must cancel SA queries without racing callbacks. Retry scheduling uses seconds and boot-time nanoseconds, so time conversion mistakes can delay records. Slave notification depends on cache matching SM data; stale caches can suppress events. GUID record byte casts must preserve big-endian layout. Ordered per-port workqueues reduce concurrency but make stuck SA requests visible as delayed GUID propagation.

## Test Signals
Test master-only initialization, per-port workqueue creation failure unwind, port inactive rescheduling, SA set/delete success, declined GUID retry backoff, admin GUID persistence, cache update from SMP data, slave init/delete events, GUID invalidation on port management events, teardown with outstanding SA queries, and multi-slave/multi-port notification behavior.
