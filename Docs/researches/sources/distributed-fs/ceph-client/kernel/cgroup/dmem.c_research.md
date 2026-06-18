# sources/distributed-fs/ceph-client/kernel/cgroup/dmem.c

## Purpose

`dmem.c` implements a device-memory cgroup controller. It lets device subsystems register named memory regions and charge per-cgroup usage against hierarchical `min`, `low`, and `max` limits using `page_counter`.

## Important APIs, Types, and Functions

Core types are `struct dmem_cgroup_region`, `struct dmemcg_state`, and `struct dmem_cgroup_pool_state`. Exported APIs include `dmem_cgroup_register_region()`, `dmem_cgroup_unregister_region()`, `dmem_cgroup_try_charge()`, `dmem_cgroup_uncharge()`, `dmem_cgroup_pool_state_put()`, and `dmem_cgroup_state_evict_valuable()`.

The controller uses a global `dmemcg_lock`, an RCU-protected `dmem_cgroup_regions` list, region `kref`s, pool `refcount_t`s, and css lifecycle callbacks `dmemcs_alloc()`, `dmemcs_offline()`, and `dmemcs_free()`.

## Control Flow and State

Devices first call `dmem_cgroup_register_region()` with a size and formatted name. Per-cgroup pools are created lazily by `get_cg_pool_unlocked()` and `get_cg_pool_locked()`, recursively ensuring ancestors have pools and that `page_counter.parent` links are initialized. Charges call `dmem_cgroup_try_charge()`, which pins the current dmem css, gets or creates a pool for the region, and uses `page_counter_try_charge()`. On limit failure it can return the limiting pool for eviction decisions. Uncharge paths drop page-counter usage, css references, and pool references.

Limit writes parse `region value` lines for `min`, `low`, and `max`, where `max` maps to `PAGE_COUNTER_MAX`. Reads iterate registered regions and show capacity, current, min, low, or max. Offline css resets all limits to unlimited-style defaults; freeing a css removes its pools from both css and region lists.

## Dependencies and Integration Points

The file depends on cgroup core, `linux/cgroup_dmem.h`, RCU list traversal, global spin locking, `page_counter`, parser helpers, css references, and external device-memory callers that manage region lifetime and call charge/uncharge symmetrically.

## Risks and Edge Cases

Lifetime is subtle: a region can unregister while pools still exist, so lookups rely on RCU plus `kref_get_unless_zero()`, and pool freeing is deferred through RCU. Pool initialization is recursive and can allocate outside the spinlock on `-ENOMEM`, so partial initialization paths need stress coverage. Charge failure returns `-EAGAIN` and may hand out a referenced limiting pool that callers must release. Eviction decisions depend on calculated effective min/low protections and ancestor relationships.

## Test Signals

Tests should cover region register/unregister while cgroups exist, repeated concurrent charges and uncharges, max-limit failures, `ret_limit_pool` release, min/low eviction behavior with and without `ignore_low`, multi-line limit writes, css offline reset, and RCU teardown under concurrent reads.
