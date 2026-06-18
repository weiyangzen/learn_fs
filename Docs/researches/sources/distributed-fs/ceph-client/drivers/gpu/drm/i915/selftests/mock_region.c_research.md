# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_region.c

Purpose: implements mock i915 memory regions backed by TTM resources for selftests.

Important APIs/functions: `mock_region_create()` allocates a mock memory-region instance ID and calls `intel_memory_region_create()` with `mock_region_ops`. `mock_object_init()` initializes GEM objects in the mock region, validates size, records `bo_offset`, sets CPU/GTT read domains, disables cache coherency, and attaches the memory region. `mock_region_get_pages()` allocates a TTM resource and converts it to an `i915_refct_sgt`; `mock_region_put_pages()` releases the refcounted sg table and TTM resource. `mock_region_fini()` finalizes TTM and frees the IDA instance.

Control flow and state: region instances are assigned from `i915->selftest.mock_region_instances`, limited by available TTM private memory types. GEM object page state flows through `obj->mm.res`, `obj->mm.rsgt`, and `__i915_gem_object_set_pages()`.

Dependencies and integration: depends on GEM memory-region object APIs, TTM placement/resource helpers, scatterlists, and the i915 memory-region core. It is used by selftests that need memory-region behavior without physical local memory.

Risks: object size is checked only against total region size; offset/size overlap policy depends on lower TTM allocation. Failure paths must free `obj->mm.res` if sg conversion fails.

Test signals: expected tests allocate mock regions, create GEM objects, get/put pages, and see resources released with no IDA leaks or stale `rsgt` pointers.
