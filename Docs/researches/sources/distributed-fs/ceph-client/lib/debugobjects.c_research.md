# sources/distributed-fs/ceph-client/lib/debugobjects.c

## Purpose
Implements the kernel generic object lifetime debugger. Subsystems register object addresses and descriptor callbacks so debugobjects can catch invalid init, activate, deactivate, destroy, free, and active-state transitions.

## APIs, Types, and Functions
Core exported APIs are `debug_object_init()`, `debug_object_init_on_stack()`, `debug_object_activate()`, `debug_object_deactivate()`, `debug_object_destroy()`, `debug_object_free()`, `debug_object_assert_init()`, and `debug_object_active_state()`. With `CONFIG_DEBUG_OBJECTS_FREE`, `debug_check_no_obj_freed()` scans address ranges being freed. Boot APIs include `debug_objects_early_init()` and `debug_objects_mem_init()`.

Important internal types are `struct debug_bucket`, `struct pool_stats`, and `struct obj_pool`. The file manages a page-chunk-hashed `obj_hash`, a static boot pool, per-CPU object pools, a global pool, a deferred free pool, a dedicated `debug_objects_cache`, warning/fixup/stat counters, early params `debug_objects` and `no_debug_objects`, and optional debugfs stats.

## Control Flow
Initialization first sets up hash bucket locks and seeds `pool_boot` with static objects. Later `debug_objects_mem_init()` runs an optional selftest, creates the dedicated slab cache, allocates dynamic batches, replaces active static debug objects, adjusts pool thresholds by CPU count, and enables the static key for cache-backed allocation.

Runtime operations hash the target object address by page chunk, lock the bucket, find or allocate a `struct debug_obj`, validate the requested transition, update state when legal, or snapshot the object and print/fix up outside the bucket lock when illegal. Pool management moves objects in fixed batches between per-CPU, global, and free pools. A delayed work item rate-limits freeing surplus objects back to slab. OOM disables debugobjects and drains tracked objects to avoid cascading failures.

## State and Persistence
The subsystem is stateful for the life of the kernel. It persists tracked object records in hash buckets, pool occupancy, per-object `state` and `astate`, global enablement, stats counters, and delayed-work state. It does not persist across reboot. The state machine distinguishes none, initialized, inactive, active, destroyed, and not-available states.

## Dependencies and Integration Points
Depends on CPU hotplug, debugfs, hash lists, kmemleak/slab, scheduler/task-stack helpers, seq_file, static keys, raw spinlocks, delayed work, early params, and descriptor callbacks from object-owning subsystems. It integrates with timers, work items, RCU-like objects, and other facilities that opt into debug object tracking.

## Risks and Test Signals
Risks include false positives from missing annotations, missed reports when OOM disables the subsystem, lock-order problems during pool refill, per-CPU pool accounting bugs, recursion if debug object allocations are themselves debugged, and expensive scans under `CONFIG_DEBUG_OBJECTS_FREE`. Test signals include `CONFIG_DEBUG_OBJECTS_SELFTEST`, debugfs `debug_objects/stats`, lockdep coverage of pool locks, CPU hotplug tests, forced OOM/fallback tests, and subsystem-specific lifetime misuse tests that verify descriptor fixups and warnings.
