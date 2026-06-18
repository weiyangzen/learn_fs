# sources/distributed-fs/ceph-client/drivers/infiniband/core/cache.c

## Purpose

`cache.c` maintains RDMA core caches for port attributes, P_Keys, subnet prefixes, port state, and GID table entries. It supports InfiniBand, RoCE, and iWARP behavior, handles default RoCE GIDs tied to net devices, exports lookup/query APIs to other RDMA components, and synchronizes cache updates before dispatching asynchronous events to clients.

## Important APIs, Types, And Functions

- `struct ib_pkey_cache` stores a cached P_Key table.
- `struct ib_gid_table` owns per-port GID entries, a mutex for writers, an IRQ-safe rwlock for table readers, and a bitmap of reserved default GID indices.
- `struct ib_gid_table_entry` wraps `struct ib_gid_attr`, refcounting, delete work, provider context, entry state, and a retained netdevice pointer for RCU-safe release.
- GID mutation APIs: `ib_cache_gid_add()`, `ib_cache_gid_del()`, `ib_cache_gid_del_all_netdev_gids()`, `ib_cache_gid_set_default_gid()`.
- GID lookup/query APIs: `rdma_find_gid_by_port()`, `rdma_find_gid_by_filter()`, `rdma_find_gid()`, `rdma_query_gid()`, `rdma_get_gid_attr()`, `rdma_query_gid_table()`, `rdma_put_gid_attr()`, `rdma_hold_gid_attr()`, `rdma_read_gid_hw_context()`, `rdma_read_gid_attr_ndev_rcu()`, `rdma_read_gid_l2_fields()`.
- P_Key and port cache APIs: `ib_get_cached_pkey()`, `ib_find_cached_pkey()`, `ib_get_cached_lmc()`, `ib_get_cached_port_state()`, `ib_get_cached_subnet_prefix()`.
- Lifecycle/event APIs: `ib_cache_setup_one()`, `ib_cache_cleanup_one()`, `ib_cache_release_one()`, and `ib_dispatch_event()`.

## Control Flow

GID setup allocates one `ib_gid_table` per port, reserves leading entries for supported RoCE default GID types, enables GID updates, and triggers a RoCE rescan. Initial cache setup then calls `ib_cache_update()` per port to query port attributes, load non-RoCE GIDs from the provider, and refresh P_Key tables.

GID add flow rejects zero GIDs, locks the table mutex, uses `find_gid()` to detect duplicates and locate an empty slot that matches default/non-default policy, fills device/index/port/gid fields in the attribute, and calls `add_modify_gid()`. For RoCE, `add_modify_gid()` calls provider `ops.add_gid()` before storing the entry. Successful changes dispatch `IB_EVENT_GID_CHANGE`.

GID delete flow locks the table mutex, finds a matching valid entry, marks it `PENDING_DEL`, clears the slot immediately for non-RoCE, calls provider `ops.del_gid()` if applicable, detaches any netdev pointer through RCU, drops the entry reference, and dispatches a GID change event.

Lookup flow uses the table rwlock. Functions that return `struct ib_gid_attr *` increment the entry kref under the read lock and require `rdma_put_gid_attr()` by the caller. Table scans skip invalid and pending-delete entries.

Event flow uses `ib_dispatch_event()` to allocate `ib_update_work` in atomic context and queue it to `ib_wq`. Cache-affecting events run `ib_cache_event_task()`, which refreshes the software cache before redispatching non-GID events to clients. Generic events are simply forwarded.

Cleanup flow disables GID updates, flushes the shared workqueue, deletes valid GID entries, flushes again for delayed GID free work, and later frees P_Key and GID table storage during release.

## State And Persistence

All state is in `ib_device->port_data[port].cache` and per-port GID table allocations. P_Key cache replacement is protected by `device->cache_lock`; old P_Key tables are freed after the write-side swap. GID entries use `kref` plus workqueue-delayed freeing so returned attributes can outlive deletion from the table. Netdevice references are held with `dev_hold()` and released using `call_rcu()` to protect readers of `attr.ndev`.

There is no durable persistence. The cache is reconstructed from provider queries, netdev/RoCE rescans, and asynchronous events.

## Dependencies And Integration Points

The file integrates with provider operations `query_gid`, `add_gid`, `del_gid`, `ib_query_port()`, and `ib_query_pkey()`. It relies on RDMA core capability helpers, RoCE netdev/GID helpers, Linux netdevice/VLAN APIs, RCU, workqueues, and RDMA security hooks (`ib_security_cache_change()`). Exported symbols are used by CM, CMA, verbs, uverbs, and providers needing source GID/P_Key/port-state information.

## Risks

- GID lifetime is subtle: readers must balance every returned `ib_gid_attr` with `rdma_put_gid_attr()`, and release paths warn on leaked refs.
- Writers require a sleepable context because provider `add_gid`/`del_gid` may sleep; using the mutation API from atomic context would be unsafe.
- RoCE GID deletion leaves slots pending until references drain, unlike non-RoCE immediate slot reuse. Incorrect assumptions can cause duplicate or stale entries.
- Netdevice pointers require RCU discipline. Callers of `rdma_read_gid_attr_ndev_rcu()` must hold an RCU read lock and handle `ERR_PTR`.
- `rdma_query_gid_table()` returns `-EINVAL` if `max_entries` is too small, so uverbs callers need a correct sizing/retry strategy.
- Cache update failures during initial setup trigger GID cleanup but leave correctness dependent on lifecycle ordering during device registration/removal.

## Test Signals

Useful signals include add/delete/find GID round trips for default and non-default RoCE GIDs, refcount leak warnings at release, correct `IB_EVENT_GID_CHANGE` dispatch, P_Key preference for full membership over partial membership, VLAN/source-MAC extraction for upper/lower netdev topologies, provider add/delete failure injection, and teardown tests that flush workqueue paths without use-after-free. Event tests should verify that cache state is updated before clients receive non-GID cache events.
