# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_gmch.c

## Purpose
This file adapts pre-Gen6 x86 GMCH GTT support from the shared `intel-gtt`/AGP backend into the i915 GGTT address-space interface.

## Important APIs, Types, and Functions
The public functions are `intel_ggtt_gmch_probe()`, `intel_ggtt_gmch_enable_hw()`, and `intel_ggtt_gmch_flush()`. GGTT operations are implemented by `gmch_ggtt_insert_page()`, `gmch_ggtt_insert_entries()`, `gmch_ggtt_read_entry()`, `gmch_ggtt_clear_range()`, `gmch_ggtt_invalidate()`, and `gmch_ggtt_remove()`. `needs_idle_maps()` detects the Ironlake mobile VT-d workaround.

## Control Flow
Probe calls `intel_gmch_probe()`, retrieves total GTT size and GMADR base with `intel_gmch_gtt_get()`, sets GGTT resources and allocation callbacks, optionally enables `do_idle_maps` for Gen5 mobile VT-d systems, and installs GMCH-backed VMA operations. Enabling hardware delegates to `intel_gmch_enable_gtt()`. Insert/clear/invalidate operations directly call the GMCH GTT helpers.

## State and Persistence Behavior
The function initializes persistent GGTT fields: `vm.total`, `gmadr`, `mappable_end`, operation callbacks, invalidation callback, and `do_idle_maps`. It does not own separate PTE memory; the backend manages hardware state through `intel-gtt`.

## Dependencies and Integration Points
It depends on x86 `intel-gtt`, AGP memory-type flags, PCI devices, i915 VT-d detection, and the generic i915 GGTT VMA ops. It is selected by `intel_ggtt.c` for platforms older than Gen6 and is stubbed on non-x86 through the header.

## Risks
Legacy GMCH paths are platform- and architecture-specific. Cache flag mapping to AGP types must match expectations for uncached versus cached mappings. The Gen5 mobile VT-d idle-map workaround affects performance but avoids unsafe unmaps. Probe failure semantics are inverted by `intel_gmch_probe()` returning false on failure, so error handling must stay clear.

## Test Signals
Boot and GEM/display operation on pre-Gen6 x86 platforms, GMADR/GTT size reporting, aperture mmap correctness, VT-d active Gen5 mobile stability, and clean GMCH remove/flush paths are the key signals.
