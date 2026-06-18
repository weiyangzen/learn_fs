# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-kmem.c

Read completely: 630 lines.

This implements general SPL `kmem_*` allocation wrappers on Linux, including formatted string allocation, contiguous-vs-virtual allocation policy, optional debug accounting, and optional allocation tracking.

Key responsibilities:
- Exposes `spl_kmem_alloc_warn` and `spl_kmem_alloc_max` tunables.
- Provides `kmem_asprintf()`, `kmem_vasprintf()`, `kmem_strdup()`, and `kmem_strfree()`.
- Implements `spl_kvmalloc()` with kmalloc-first and vmalloc fallback behavior.
- Implements `spl_kmem_alloc_impl()` and `spl_kmem_free_impl()` behind public `spl_kmem_alloc()`, `spl_kmem_zalloc()`, and `spl_kmem_free()`.
- Supports optional `DEBUG_KMEM` byte accounting and `DEBUG_KMEM_TRACKING` per-allocation leak tracking.

Important implementation details:
- Large non-`KM_VMEM` allocations above `spl_kmem_alloc_warn` log a warning and stack trace.
- Non-vmem allocations above `spl_kmem_alloc_max` fail quickly; vmem allocations may use `spl_vmalloc()`.
- `KM_SLEEP` allocations loop until success unless the allocator is allowed to fail after retry flags and scheduling.
- `spl_kvmalloc()` avoids vmalloc fallback for non-reclaim allocations because the fallback can sleep.
- Debug tracking stores allocation address, size, caller function, and line in a hash/list structure, then reports leaks on module unload.

Dependencies and interactions:
- Used by almost every Linux SPL/OpenZFS subsystem that expects Illumos `kmem_alloc` semantics.
- Depends on Linux kmalloc/kvmalloc/vfree, SPL vmem, converted GFP flags, and optional debug build macros.

Reliability notes:
- The file deliberately discourages large contiguous `kmem_alloc()` usage because of Linux fragmentation and latency.
- Leak tracking is powerful but explicitly high overhead and intended for debug builds only.
