<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.c

Purpose: discovers, sizes, maps, and creates the local-memory (`LMEM`) memory region for discrete Intel GPUs, including optional Resizable BAR adjustment, Flat CCS stolen-area exclusion, low-memory reservation, and TTM region initialization.

Important APIs and functions: public `intel_gt_setup_lmem()` delegates to `setup_lmem()`. Internal helpers include `_resize_bar()`, `i915_resize_lmem_bar()`, `region_lmem_init()`, `region_lmem_release()`, `get_legacy_lowmem_region()`, and `reserve_lowmem_region()`. The region ops use `intel_region_ttm_init/fini()` and `__i915_gem_ttm_object_init`.

Control flow: setup rejects non-DGFX or invalid LMEM BAR. For Flat CCS platforms it reads tile address range and CCS base MCR registers, computes usable LMEM before tile-stolen CCS memory, and warns if CCS base is missing; otherwise it reads GSMBASE. It may resize the LMEM PCI BAR on 64-bit systems, honoring `i915->params.lmem_bar_size` when supported. It applies optional module-parameter size limiting, computes IO aperture size, chooses minimum page size based on 64K-page support, creates an `INTEL_MEMORY_LOCAL` region with WC IO mapping and TTM backing, reserves DG1 legacy low 1 MiB when required, and reports reduced BAR aperture.

State and persistence: the returned `intel_memory_region` persists as GT local-memory allocator state. It owns a WC `io_mapping`, TTM region state, physical LMEM size, CPU-visible IO aperture, minimum page size, and reserved low-memory ranges.

Dependencies and integration points: depends on PCI BAR/rebar APIs, runtime PM/forcewake during BAR resize, uncore/MCR register reads, Flat CCS definitions, i915 memory region and TTM helpers, GEM LMEM object allocation, module parameters, and DGFX platform detection.

Risks: BAR resizing disables PCI memory decoding and must hold forcewake to avoid later forcewake ack timeouts. Incorrect Flat CCS subtraction can expose stolen CCS memory to normal allocations. Reduced BAR means CPU mapping covers less than total LMEM and callers must respect `io_size`. DG1 low-memory reservation prevents legacy conflicts. 32-bit builds cannot resize BAR. Invalid module parameter handling falls back to full LMEM if unsupported.

Test signals: DGFX probe on DG1/DG2/MTL, Flat CCS base/range validation, reduced/rebar BAR boot tests, module `lmem_size` and `lmem_bar_size` coverage, TTM allocation/free stress, IO mapping tests, and driver unload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.c -->
