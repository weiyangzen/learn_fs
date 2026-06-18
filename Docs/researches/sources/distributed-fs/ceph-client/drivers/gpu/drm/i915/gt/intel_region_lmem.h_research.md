<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.h

Purpose: declares the GT local-memory setup entry point.

Important API: `intel_gt_setup_lmem(struct intel_gt *gt)` returns an `intel_memory_region` for DGFX local memory or an error pointer when unavailable.

Control flow: GT probe calls this after GT/uncore PCI resources are ready and stores the returned memory region for GEM/TTM allocation.

State and persistence: the returned region owns LMEM allocator and IO mapping state until destroyed by the memory-region core.

Dependencies and integration points: forward-declares `struct intel_gt`; the return type is `struct intel_memory_region` from the wider i915 memory subsystem.

Risks: callers must handle `ERR_PTR(-ENODEV/-ENXIO/-EIO)` on platforms without valid LMEM.

Test signals: DGFX and integrated-platform probe coverage and LMEM allocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.h -->
