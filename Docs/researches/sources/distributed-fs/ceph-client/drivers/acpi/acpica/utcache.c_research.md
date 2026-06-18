# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcache.c

Purpose: `utcache.c` implements ACPICA's optional local fixed-size object cache when `ACPI_USE_LOCAL_CACHE` is enabled.

Important APIs/types/functions: `acpi_os_create_cache()` allocates an `acpi_memory_list` cache descriptor. `acpi_os_purge_cache()` frees all cached objects. `acpi_os_delete_cache()` purges then frees the cache descriptor. `acpi_os_release_object()` returns an object to the cache or frees it if full. `acpi_os_acquire_object()` obtains a cached object or allocates a zeroed one.

Control flow: Cache operations validate inputs, serialize list mutation with `ACPI_MTX_CACHES`, use descriptor pointer fields to link freed objects, poison cached objects with `0xCA`, mark them `ACPI_DESC_TYPE_CACHED`, and zero objects when reacquired. Allocation is performed after releasing the cache mutex to avoid deadlock with tracked allocation.

State and persistence behavior: Persistent cache state lives in `struct acpi_memory_list`: list head, object size, current/max depth, and optional allocation statistics. Cached objects persist in memory for reuse until purged or deleted.

Dependencies and integration points: It integrates with `utalloc.c` cache creation/deletion, ACPICA mutexes, allocation macros, descriptor metadata, and optional memory tracking.

Risks and test signals: Risks include list corruption through descriptor-pointer reuse, depth underflow on purge, starvation or deadlock if mutex handling changes, and stale object contents if zeroing is skipped. Tests should cover cache hit/miss, max-depth freeing, purge/delete with populated cache, concurrent acquire/release under stress, and descriptor type transitions cached-to-operand/state after callers initialize objects.
