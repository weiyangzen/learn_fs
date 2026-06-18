# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram.c

## Purpose

`xe_vram.c` probes and describes local memory on discrete Xe devices. It discovers the PCI LMEM BAR, computes per-tile actual and usable VRAM sizes, handles flat CCS or GSM reserved regions, initializes per-tile and aggregate `xe_vram_region` descriptors, and exposes safe accessors for region fields.

## Important APIs, Types, and Functions

The main entry point is `xe_vram_probe(struct xe_device *xe)`. Region objects are allocated by `xe_vram_region_alloc()`. Field accessors are `xe_vram_region_io_start()`, `xe_vram_region_io_size()`, `xe_vram_region_dpa_base()`, `xe_vram_region_usable_size()`, and `xe_vram_region_actual_physical_size()`.

Internal helpers include `resource_is_valid()` for PCI BAR sanity, `determine_lmem_bar_size()` for BAR start/length and write-combining ioremap, `get_flat_ccs_offset()` for reading platform registers that describe flat CCS reservation, `tile_vram_size()` for tile size/offset/usable calculation, `vram_region_init()` for filling an `xe_vram_region`, `print_vram_region_info()` for boot logs, and `vram_fini()` for managed teardown of mappings.

## Control Flow and State

`xe_vram_probe()` exits immediately on non-dGFX devices. For dGFX it validates and maps the LMEM BAR, then iterates tiles. SR-IOV VF mode uses virtual LMEM sizes and cumulative offsets from `xe_tile_sriov_vf_lmem()`. DG1 uses the LMEM BAR length as tile size; other platforms read `SG_TILE_ADDR_RANGE`. Usable size is the offset to flat CCS or GSM, minus tile offset. Each tile region receives physical size, CPU-visible IO size limited by remaining BAR space, DPA base, BAR mapping pointer, and usable size. After per-tile initialization, an aggregate `xe->mem.vram` region is initialized with total physical and available usable size.

## Dependencies and Integration Points

This file depends on PCI BAR resources, DRM managed allocation, MMIO register reads, forcewake, MCR reads, GT/tile topology, SR-IOV VF helpers, and TTM VRAM manager region state. The resulting `xe_vram_region` objects feed memory placement, TTM VRAM managers, pagemap support, migration, and user-visible memory region reporting elsewhere in the driver.

## Risks and Edge Cases

Small BAR systems may expose less CPU-visible VRAM than usable device VRAM, so IO size and usable size must not be confused. Flat CCS platforms require forcewake and correct conversion from hardware view to software view; the code asserts no hole between CCS and GSM on Xe2+. BAR validation and zero IO-size checks prevent unusable configurations. Multi-tile accounting must decrement remaining IO size carefully to avoid mapping a tile beyond CPU-visible BAR space.

## Test Signals

KUnit can cover accessor behavior and `xe_vram_region_actual_physical_size()` is explicitly exported for KUnit. Platform tests should cover non-dGFX no-op, invalid BAR resources, small BAR logging, DG1 sizing, multi-tile offsets, SR-IOV VF virtual LMEM sizing, flat CCS offset calculation, forcewake timeout handling, and devm cleanup clearing mappings.
