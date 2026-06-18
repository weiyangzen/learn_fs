# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/arc_os.c

## Scope

FreeBSD ARC OS integration. It supplies platform memory sizing/availability helpers, registers the low-memory event handler, and exposes the FreeBSD-specific `zfs_arc_free_target` sysctl parameter.

## Main Interfaces

- `arc_available_memory()` computes reclaim pressure from free pages and, on some platforms, UMA heap availability.
- `arc_default_max()` computes default ARC max from physical memory.
- `arc_all_memory()` and `arc_free_memory()` report physical/free memory.
- `arc_memory_throttle()` is a FreeBSD no-op returning success.
- `arc_lowmem_init()` and `arc_lowmem_fini()` manage the `vm_lowmem` event handler.
- `arc_register_hotplug()` and `arc_unregister_hotplug()` are no-ops.

## State And Control Flow

`arc_free_target_init()` runs after pagedaemon/page counters are initialized and captures `vm_cnt.v_free_target` into `zfs_arc_free_target`. On low-memory events, `arc_lowmem()` prevents ARC growth, marks ARC warm, computes a shrink target from `arc_c`, `arc_c_min`, `arc_shrink_shift`, and current available memory, reduces target size, and only waits for eviction when invoked from `pageproc`.

## Dependencies

Uses FreeBSD `vm_cnt`, `freemem`, `physmem`, UMA availability APIs, eventhandlers, DTrace probes, and core ARC globals/functions from `arc_impl.h`.

## Correctness Notes

The low-memory callback avoids blocking arbitrary threads because they may hold ARC locks and deadlock with reclaim. The `pageproc` special case is allowed to wait for eviction and records indirect memory-pressure stats; other callers only request direct reclaim pressure.
