# sources/distributed-fs/ceph-client/mm/failslab.c

## Purpose
`failslab.c` implements slab allocator fault injection. It lets tests force selected `kmem_cache` allocations to fail so slab-user error handling can be validated.

## Important APIs, types, and functions
The global `failslab` object holds `struct fault_attr attr`, `ignore_gfp_reclaim`, and `cache_filter`. `should_failslab()` is the allocator-facing decision function and returns `-ENOMEM` or 0; it is enabled for errno-style error injection. `setup_failslab()` parses `failslab=` boot options. `failslab_debugfs_init()` creates debugfs controls for the generic fault attributes plus `ignore-gfp-wait` and `cache-filter`.

## Control flow
`should_failslab()` immediately skips the bootstrap `kmem_cache`, `__GFP_NOFAIL` allocations, direct-reclaim allocations when the filter is enabled, and caches not marked `SLAB_FAILSLAB` when `cache_filter` is true. It maps `__GFP_NOWARN` to `FAULT_NOWARN` and calls `should_fail_ex()` using `s->object_size` as the size argument. A true fault-injection decision becomes `-ENOMEM`.

## State and persistence
All policy state is global and runtime mutable through debugfs when configured. The injection decision does not persist per-cache or per-object state. `cache_filter` allows tests to restrict failures to caches explicitly opted in by `SLAB_FAILSLAB`.

## Dependencies and integration points
This file depends on slab internals (`struct kmem_cache`, `kmem_cache`, `SLAB_FAILSLAB`), common fault-injection policy, boot parameter parsing, debugfs, and error injection. It is called from slab allocation paths before an object is returned to callers.

## Risks and test signals
Faulting bootstrap, nofail, or reclaim-sensitive allocations could destabilize the system, so those paths are guarded. The main test signals are boot parameter parsing, debugfs control visibility, expected `-ENOMEM` from targeted cache allocations, absence of allocation warnings under `__GFP_NOWARN`, and cache-filter behavior that only fails `SLAB_FAILSLAB` caches when enabled.
