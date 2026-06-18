# sources/distributed-fs/ceph-client/include/linux/cgroup_dmem.h

## Purpose

`cgroup_dmem.h` declares device-memory cgroup accounting hooks for registering memory regions, charging/uncharging allocations, and choosing eviction targets when a cgroup limit is hit.

## Important APIs, Types, and Functions

Opaque types are `dmem_cgroup_region` and `dmem_cgroup_pool_state`. Enabled APIs are `dmem_cgroup_register_region()`, `dmem_cgroup_unregister_region()`, `dmem_cgroup_try_charge()`, `dmem_cgroup_uncharge()`, `dmem_cgroup_state_evict_valuable()`, and `dmem_cgroup_pool_state_put()`. Disabled stubs return success or neutral values.

## Control Flow

Device-memory providers register a region, try-charge a size before allocation, optionally receive pool/limit-pool state for eviction decisions, uncharge on free, and release pool-state references.

## State and Persistence Behavior

Implementation state is opaque and per cgroup/device-memory pool. The disabled path stores no state and sets returned pool pointers to NULL.

## Dependencies and Integration Points

It depends on types and lockless lists. It integrates with the cgroup subsystem when `CONFIG_CGROUP_DMEM` is enabled and with device drivers managing nonstandard/device memory.

## Risks and Edge Cases

Callers must handle enabled and disabled configurations identically. On disabled builds, `dmem_cgroup_state_evict_valuable()` returns true, so eviction policy must not assume real accounting. Returned pool references require matching put calls only when non-NULL.

## Test Signals

Build with and without `CONFIG_CGROUP_DMEM`, test charge/uncharge balance, region unregister with outstanding pools, limit-pool eviction decisions including low-protection hits, and disabled-stub behavior.
