# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_kmem.c

FreeBSD SPL memory allocation and kmem cache compatibility layer.

Key behavior:
- `zfs_kmem_alloc()`/`zfs_kmem_free()` wrap FreeBSD malloc/free using `M_SOLARIS`, with optional debug tracking.
- `kmem_size()` reports capped kernel memory size initialized from VM counters.
- `kmem_cache_create()` maps caches to UMA zones in kernel builds, or size-backed allocations otherwise.
- `kmem_cache_alloc()`/`kmem_cache_free()` run constructors/destructors and use UMA when available.
- Reaping hooks call UMA reclaim in kernel builds and no-op in non-kernel builds.
- `calloc()` is provided as `kmem_zalloc()`.
- `kmem_vasprintf()` allocates formatted strings from kmem.
- `spl_kmem_cache_inuse()` and `spl_kmem_cache_entry_size()` query UMA zone state.
- `spl_kmem_cache_set_move()` is stubbed but asserts a non-null callback.

`KMEM_DEBUG` has tracking scaffolding but is explicitly unsupported near the UMA internals section.
