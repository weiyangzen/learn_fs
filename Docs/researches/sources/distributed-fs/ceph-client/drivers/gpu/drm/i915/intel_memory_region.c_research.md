# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_memory_region.c

Purpose: creates, probes, validates, looks up, reports, and destroys i915 memory regions such as system, local, and stolen memory.

Important APIs/functions: exports `intel_memory_region_lookup`, `intel_memory_region_by_type`, `intel_memory_type_is_local`, `intel_memory_region_reserve`, `intel_memory_region_debug`, `intel_memory_type_str`, `intel_memory_region_create`, `intel_memory_region_set_name`, `intel_memory_region_avail`, `intel_memory_region_destroy`, `intel_memory_regions_hw_probe`, and `intel_memory_regions_driver_release`. Internal helpers perform optional IO memory tests.

Control flow: hardware probe walks `i915->mm.regions` capability bits, maps region IDs to UAPI classes/instances, creates the correct backend (`ttm_system`, shmem, stolen local/system), stores successful regions, and logs sizes. Creation initializes resources, object lists, backend ops, optional backend init, and memtest. Release fetches and destroys all registered regions.

State and persistence: each `struct intel_memory_region` stores resource ranges, IO aperture, min page size, total size, type/instance/id, names, object list lock, range-manager flag, and backend-private pointer. It is runtime-only and tied to driver lifetime.

Dependencies and integration: depends on GEM backends, stolen memory setup, TTM buddy manager, DRM printers, i915 parameters, IO mapping, and UAPI memory classes. Object allocation and migration code query these regions.

Risks: memtest writes to IO memory and is gated by debug or module params; failures abort region creation. Destroy refuses to free leaked regions if backend release reports busy, preventing use-after-free but leaking intentionally. Wrong capability maps can expose missing or invalid memory regions.

Test signals: `CONFIG_DRM_I915_SELFTEST` includes memory-region and mock-region tests; runtime debug output, memtest failures, local-memory availability queries, and probe/remove paths provide additional signals.
