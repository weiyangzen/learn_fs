# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_gart.c

## Purpose

`radeon_gart.c` implements common internal GART management. The GART lets the GPU see scattered system pages as a contiguous GPU aperture. This file allocates and frees GART page tables in system RAM or VRAM, initializes dummy-page-backed page-entry arrays, binds/unbinds CPU pages into GPU page entries, and flushes the GPU TLB when table contents change.

## Important APIs, Types, and Functions

- `radeon_gart_table_ram_alloc()` and `radeon_gart_table_ram_free()` allocate coherent system-memory GART tables for older/internal-GART ASICs, with x86 cache attribute adjustments for selected IGP families.
- `radeon_gart_table_vram_alloc()`, `radeon_gart_table_vram_pin()`, `radeon_gart_table_vram_unpin()`, and `radeon_gart_table_vram_free()` manage VRAM-resident GART tables for PCIe/newer ASICs.
- `radeon_gart_bind()` maps pages/DMA addresses into the aperture and writes GPU page-table entries when the table is currently mapped.
- `radeon_gart_unbind()` replaces entries with the dummy page.
- `radeon_gart_init()` allocates the dummy page and software page/page-entry arrays.
- `radeon_gart_fini()` unbinds, frees arrays, clears readiness, and releases the dummy page.

## Control Flow

Initialization checks GPU page size compatibility, creates the dummy DMA page, computes CPU-page and GPU-page counts from `rdev->mc.gtt_size`, allocates `pages` and `pages_entry`, and fills all GPU entries with the dummy page. ASIC-specific code later allocates the actual hardware-visible page table in RAM or VRAM. When a VRAM table is pinned and mapped, the function restores all previously accumulated `pages_entry` values into hardware and flushes the TLB. Bind/unbind update software arrays first, optionally write the mapped table, issue a memory barrier, and flush the TLB.

## State and Persistence Behavior

Persistent GART state is in `rdev->gart`: `pages`, `pages_entry`, `num_cpu_pages`, `num_gpu_pages`, table BO or RAM pointer, table address, readiness, and table size. Entries may be updated before the table is mapped; `pages_entry` persists the intended state until pin time. The dummy page state is shared with `radeon_device.c`.

## Dependencies and Integration Points

The file depends on PCI DMA allocation, vmalloc/vcalloc, x86 `set_memory_uc/wb`, Radeon BO pin/kmap APIs, dummy page helpers, ASIC-specific `radeon_gart_get_page_entry()`, `radeon_gart_set_page()`, and `radeon_gart_tlb_flush()`. TTM calls `radeon_gart_bind()` for GTT-backed BOs.

## Risks and Edge Cases

- Bind/unbind require `rdev->gart.ready`; misuse emits WARN and fails or returns.
- Offset and page counts are not locally bounds-checked against array sizes, so callers must validate aperture ranges.
- Cache attribute changes are family-specific and must be balanced on free.
- VRAM table unpin ignores reserve failure and leaves state unchanged.
- The table can be temporarily unmapped, so software and hardware entries can diverge until repin restores them.

## Test Signals

Test GART init/fini, RAM-table and VRAM-table ASIC paths, bind/unbind of single and multi-GPU-page CPU pages, dummy-page fallback after unbind, TLB flush ordering, suspend/resume table repin, invalid uninitialized calls, cache attribute balance on x86 IGPs, and TTM GTT BO migration.
