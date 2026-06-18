# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gtt.c

Purpose: provides mock global and per-process GTT address-space operations for i915 selftests where page-table programming should be inert.

Important APIs/functions: `mock_ppgtt()` allocates a fake `i915_ppgtt` with a near-`U64_MAX` address-space size and no-op insert/clear/cleanup operations. `mock_init_ggtt()` populates a supplied GT GGTT with fake GMADR/mappable sizes, no-op bind/insert ops, and address-space initialization. `mock_fini_ggtt()` finalizes the GGTT address space. Internal no-op bind/unbind functions either do nothing or, for PPGTT, mark `vma_res->bound_flags`.

Control flow and state: PPGTT allocation initializes VM fields, DMA device, page-table allocation callbacks, and vma ops. GGTT initialization sets `is_ggtt`, resource bounds, total size, callbacks, and then calls `i915_address_space_init()`.

Dependencies and integration: depends on i915 VM/GTT abstractions, page-table DMA allocation helpers, and GT/GGTT structures. Used by mock GEM device construction and lower-level VM tests.

Risks: the mock implementation does not validate real PTE programming, aperture constraints, cache attributes, or hardware global binding. PPGTT `mock_bind_ppgtt()` asserts that global bind flags are not used.

Test signals: VM/GEM tests should observe address-space lifecycle and bound flag changes without hardware MMIO. Failures usually appear as `GEM_BUG_ON`, refcount, or address-space cleanup warnings.
