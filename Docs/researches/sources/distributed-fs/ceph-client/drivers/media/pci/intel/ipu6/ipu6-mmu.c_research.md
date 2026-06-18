# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-mmu.c

## Purpose
`ipu6-mmu.c` implements the IPU6 internal MMU page-table manager and hardware programming layer used by ISYS and PSYS auxiliary devices. It builds a two-level 32-bit IOVA page table, maps/unmaps pages for the custom IPU6 DMA layer, initializes hardware TLB stream registers, invalidates TLBs, and allocates a trash buffer used by MMU v2 invalidation workarounds.

## Important APIs, Types, And Functions
Exported APIs are `ipu6_mmu_init()`, `ipu6_mmu_cleanup()`, `ipu6_mmu_hw_init()`, `ipu6_mmu_hw_cleanup()`, `ipu6_mmu_map()`, `ipu6_mmu_unmap()`, and `ipu6_mmu_iova_to_phys()`. Internal helpers allocate dummy pages/L2 tables/L1 tables, map L2 pages, unmap ranges, invalidate TLBs, and allocate/destroy the trash-buffer IOVA range.

## Control Flow
`ipu6_mmu_init()` copies hardware variant descriptors, assigns register bases, creates `struct ipu6_mmu`, allocates the shared DMA mapping object, and builds dummy page-table state. `ipu6_mmu_hw_init()` writes the L1 page-table base and info bits into each MMU hardware block, configures L1/L2 stream block start registers, allocates the trash page/range if needed, and marks the MMU ready. `ipu6_mmu_map()` validates alignment and calls `l2_map()`, which allocates an L2 page table on first use, maps it for DMA, installs it in L1, fills L2 PTEs, and flushes cache lines. Unmap replaces entries with the dummy-page PTE. Hardware cleanup marks the MMU not ready; full cleanup unmaps/free tables and IOVA metadata.

## State And Persistence
The page table, dummy page, dummy L2 table, trash-page mapping, and IOVA allocator are in-memory and device-lifetime only. `ready_lock` guards whether invalidation can hit hardware; `mmu_info->lock` serializes table updates.

## Dependencies And Integration Points
The code depends on DMA mapping, Linux IOVA allocator, IPU6 hardware variant data from `ipu6.c`, register offsets from `ipu6-platform-regs.h`, and `ipu6-dma` users that call map/unmap.

## Risks And Test Signals
`l2_unmap()` logs unmapped L1 entries but continues without reducing `size`, which could loop through later L1 entries and end with a size warning; invalid unmap callers deserve testing. `ipu6_mmu_iova_to_phys()` assumes the L2 table pointer exists and can fault for dummy L1 regions. Cleanup manually frees `dummy_l2_pt` without `free_dummy_l2_pt()`, so DMA unmap symmetry should be checked. Tests should cover aligned/unaligned map/unmap, cross-L1 mappings, low-memory L2 allocation failures, trash-buffer allocation failure unwind, repeated runtime PM hardware init/cleanup, and DMA API debug.
