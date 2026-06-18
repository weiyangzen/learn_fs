# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-shrinker.c

Read completely: 78 lines.

This is a compatibility wrapper for registering and unregistering Linux shrinkers from SPL/OpenZFS code.

Key responsibilities:
- Allocates or receives a shrinker object depending on kernel API availability.
- Assigns count and scan callbacks plus seek cost.
- Registers the shrinker with the correct kernel API variant.
- Unregisters/frees the shrinker with the matching API.

Important implementation details:
- For kernels with `HAVE_SHRINKER_REGISTER`, `shrinker_alloc()` allocates the object and `shrinker_free()` unregisters/frees it.
- For older kernels, SPL allocates a `struct shrinker` with `kmem_zalloc()`, calls either `register_shrinker(shrinker, name)` or `register_shrinker(shrinker)`, then unregisters and `kmem_free()`s it.

Dependencies and interactions:
- Used by OpenZFS components that need memory reclaim callbacks while hiding Linux shrinker API churn.
- Depends on SPL kmem allocation and kernel feature macros.

Reliability notes:
- The wrapper returns `NULL` if allocation fails; callers must handle missing shrinker registration.
