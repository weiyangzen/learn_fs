# sources/distributed-fs/ceph-client/mm/execmem.c

## Purpose
`execmem.c` implements the executable-memory allocator used for module text and other kernel executable ranges. It abstracts architecture-provided executable memory ranges, falls back to vmalloc space when no architecture setup is supplied, supports KASAN module shadow allocation, and optionally maintains a read-only-executable cache that can be temporarily made writable for text updates.

## Important APIs, types, and functions
Global state is `execmem_info`, a `struct execmem_info` containing per-`enum execmem_type` ranges, and `default_execmem_info`. `execmem_alloc()` allocates page-aligned memory for a type. `execmem_alloc_rw()` allocates and then forces it writable/non-executable for patching. `execmem_free()` frees through the ROX cache when possible, otherwise `vfree()`. `execmem_is_rox()` reports whether a type uses the ROX cache. `execmem_vmap()` reserves module-data virtual space.

The optional `CONFIG_ARCH_HAS_EXECMEM_ROX` cache uses `struct execmem_cache` with a mutex, `busy_areas` and `free_areas` maple trees, and a pending-free counter. Helpers include `execmem_cache_alloc_locked()`, `execmem_cache_populate_alloc()`, `__execmem_cache_free()`, delayed `execmem_cache_free_slow()`, and `execmem_cache_clean()`. Permission helpers are `execmem_force_rw()`, `execmem_restore_rox()`, and `execmem_set_direct_map_valid()`.

## Control flow
Initialization calls weak `execmem_arch_setup()`. If it returns `NULL`, the default range spans `VMALLOC_START` to `VMALLOC_END`, uses `PAGE_KERNEL_EXEC`, and has alignment 1. `execmem_validate()` requires the default range to have nonzero alignment, start, end, and page protection, and strips unsupported `EXECMEM_ROX_CACHE` flags when the architecture lacks ROX cache support. `execmem_init_missing()` copies the default range into missing type-specific ranges, except module data uses `PAGE_KERNEL`.

`execmem_alloc()` aligns size, selects the requested range, and either uses `execmem_cache_alloc()` for ROX-cache ranges or `execmem_vmalloc()` directly. The vmalloc path tries the primary range then a fallback range, applies KASAN shadow allocation if requested, and returns a tag-reset pointer. The ROX cache first tries to carve a suitable span from `free_areas`. If none exists, it allocates a PMD-sized or exact vmalloc block, fills it with trapping instructions, marks it ROX, adds the whole block to `free_areas`, and carves out the requested allocation atomically under the mutex.

Freeing a cached allocation finds its `busy_areas` entry. Fast free makes the range writable/NX, fills trapping instructions, restores ROX permissions, merges it into `free_areas`, removes it from `busy_areas`, and schedules cleanup. If fast free cannot allocate maple-tree metadata with `__GFP_NORETRY`, it marks the busy entry with `PENDING_FREE_MASK` and schedules delayed work. Cleanup returns PMD-aligned free ranges to the direct map and `vfree()`s them.

## State and persistence
`execmem_info` becomes read-only after init. Cached memory persists in the maple-tree free list after individual frees so later executable allocations can reuse it without repeated vmalloc/direct-map churn. Busy entries persist until `execmem_free()`. Pending-free state is encoded in the low bit range made available by page alignment. Workqueue items perform asynchronous retry and cleanup.

## Dependencies and integration points
The allocator depends on vmalloc internals, maple trees, memory permission APIs (`set_memory_nx/rw/rox`, `set_direct_map_valid_noflush()`), KASAN module shadow support, architecture TLB/cache behavior, module loader ranges, and text-patching helpers such as `execmem_fill_trapping_insns()`. Architecture code can override `execmem_arch_setup()` and choose late initialization through `CONFIG_ARCH_WANTS_EXECMEM_LATE`.

## Risks and test signals
Key risks are permission transitions that briefly expose writable executable memory, direct-map alias validity, maple-tree range merge/split bugs, delayed-free starvation, and incorrect architecture range definitions. `within_range()` range checks and fallback handling are security-sensitive because executable memory must remain inside intended regions. Test signals include module load/unload under KASAN, BPF/kprobe/ftrace/text-patching users, ROX permission tests, memory hotplug/direct-map checks, and fault injection around maple-tree allocation during free. Warnings from `execmem_validate()` indicate module loading may fail.
