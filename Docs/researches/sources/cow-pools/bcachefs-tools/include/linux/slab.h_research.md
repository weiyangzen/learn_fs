# File Research: sources/cow-pools/bcachefs-tools/include/linux/slab.h

Implements the userspace allocation compatibility layer: `kmalloc`, `kzalloc`, realloc/array helpers, page allocation/free helpers, vmalloc wrappers, `kmemdup`, minimal `kmem_cache`, and `vmalloc_exec`.

Allocators use `posix_memalign`, `aligned_alloc`, `malloc_usable_size`, `mprotect`, and shrinker retries. Overflow checks are present in array helpers. `vmap()` is unimplemented and returns `NULL`.
