## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_hwconfig.c

Purpose: retrieves the GuC-provided hardware configuration KLV table, stores it in `gt->info.hwconfig`, and frees it at teardown.

Important APIs, types, and functions:
- `__guc_action_get_hwconfig()` sends `INTEL_GUC_ACTION_GET_HWCONFIG` over MMIO with a GGTT address/size. `-ENXIO` is mapped to `-ENOENT`.
- `guc_hwconfig_discover_size()` queries with zero offset/size and stores the returned blob size.
- `guc_hwconfig_fill_buffer()` allocates a temporary GuC-mapped VMA, asks GuC to write the table into it, copies it into host memory, then releases the VMA.
- `has_table()` gates supported platforms: Alder Lake-P except ADL-P-N and graphics IP >= 12.55.
- `intel_gt_init_hwconfig()` initializes only when UC uses GuC; `intel_gt_fini_hwconfig()` frees `ptr` and clears size.

Control flow:
- Init skips unsupported platforms or non-GuC mode.
- Size discovery must return a positive size.
- Host memory is allocated with `kmalloc()`, a temporary GGTT buffer receives firmware data, and success persists the copied table in `gt->info.hwconfig`.
- On fill failure, fini is called to release partial state.

State and persistence:
- The retrieved KLV blob persists in `gt->info.hwconfig.ptr` with byte count `size` until `intel_gt_fini_hwconfig()`.

Dependencies and integration points:
- Uses GuC MMIO send path, GuC VMA allocation/mapping, GGTT offset helpers, i915 memcpy, and generic `intel_hwconfig` storage consumed by other GT discovery code.

Risks:
- Platform gating must match firmware availability. Querying unsupported firmware returns errors.
- The firmware-returned size is trusted for allocation and transfer; zero size is rejected.
- Data is copied from a temporary VMA without parsing here, so downstream users must validate KLV contents/lengths.

Test signals:
- Boot on supported and unsupported platforms and verify init returns expected values.
- Validate KLV table presence/size and downstream feature queries.
- Fault injection for VMA allocation, host allocation, zero-size discovery, and GuC action failure.
