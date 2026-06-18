# sources/distributed-fs/ceph-client/drivers/of/of_reserved_mem.c

## Purpose
`of_reserved_mem.c` discovers, reserves, allocates, initializes, and assigns devicetree `/reserved-memory` regions. It supports static `reg` regions, dynamic `size` plus `alloc-ranges` regions, `no-map`, compatible-specific callbacks, and device assignment through `memory-region`.

## Important APIs, types, and functions
Boot APIs include `fdt_scan_reserved_mem()` and `fdt_scan_reserved_mem_late()`. Runtime exports include `of_reserved_mem_device_init_by_idx()`, `of_reserved_mem_device_init_by_name()`, `of_reserved_mem_device_release()`, `of_reserved_mem_lookup()`, `of_reserved_mem_region_to_resource()`, `of_reserved_mem_region_to_resource_byname()`, and `of_reserved_mem_region_count()`. Internal helpers include `early_init_dt_alloc_reserved_memory_arch()`, `__reserved_mem_reserve_reg()`, `__reserved_mem_alloc_size()`, `fdt_fixup_reserved_mem_node()`, `fdt_validate_reserved_mem_node()`, and `__reserved_mem_init_node()`.

## Control flow and state
Early scan checks `/reserved-memory` cell counts and `ranges`, reserves static `reg` regions first, saves dynamic-size nodes, then allocates dynamic regions after static reservations to avoid overlap. Dynamic allocation honors alignment, `alloc-ranges`, and `no-map`, and can choose bottom-up or top-down based on nearby existing reservations. Late scan allocates a right-sized `reserved_mem` array, initializes static regions, and checks overlaps.

Compatible-specific reserved-memory ops are discovered from `__reservedmem_of_table` and can validate, fix up FDT nodes, initialize region data, and attach/release devices. Device assignments are tracked in `of_rmem_assigned_device_list` under a mutex so release can call matching `device_release` callbacks.

## Dependencies and integration
The file integrates with libfdt, memblock, kmemleak, reserved-memory driver tables, OF phandle parsing, resource APIs, and DMA setup in `device.c` for restricted pools.

## Risks and test signals
Risks include overlap, bad root cell counts, array overflow beyond `MAX_RESERVED_REGIONS`, failed memblock reservations, `no-map` conflicts with already reserved memory, callback failure rollback, and device assignment leaks. Signals are reserved-memory boot logs, overlap warnings, memblock maps, resource conversion tests, and driver-specific reserved-memory behavior.
