# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mmu.c

## Purpose
This file implements the PowerVR SGX-side MMU page-directory and page-table manager used by the GMA500 driver. It allocates GPU page directories, maps physical page sequences or page arrays into GPU virtual addresses, invalidates mappings, manages hardware directory contexts, and performs cache/TLB flushes.

## Important APIs, Types, and Functions
The exported APIs are `psb_mmu_driver_init()`, `psb_mmu_driver_takedown()`, `psb_mmu_alloc_pd()`, `psb_mmu_free_pagedir()`, `psb_mmu_get_default_pd()`, `psb_mmu_set_pd_context()`, `psb_mmu_flush()`, `psb_mmu_insert_pfn_sequence()`, `psb_mmu_insert_pages()`, `psb_mmu_remove_pfn_sequence()`, and `psb_mmu_remove_pages()`. Internal helpers compute page-directory/table indexes, construct PTEs, allocate page tables, map/unmap them under lock, and flush PTE cache lines.

## Control Flow
Driver init allocates a default page directory, records BIF control state, clears faults, detects `clflush`, and initializes locking. A page directory allocates a PD page, dummy PT, dummy page, and a 1024-entry software PT pointer table. Insert paths walk the GPU VA range by PDE window, allocate PTs as needed, write PTEs, bump `pt->count`, flush modified PTEs when the PD is bound to hardware, and trigger an MMU flush. Remove paths invalidate PTEs, decrement counts, drop empty PTs, flush modified cache lines, then flush the hardware MMU.

## State and Persistence Behavior
Persistent state lives in `struct psb_mmu_driver` and each `struct psb_mmu_pd`: hardware context number, PD/PT pages, invalid PTE/PDE encodings, default PD, flush flags, saved BIF control, and optional MSVDX invalidation flag. Hardware-visible PD/PT pages are DMA32 pages. The code preserves ordering with a driver rwsem taken before the PT spinlock.

## Dependencies and Integration Points
The MMU is initialized from `psb_drv.c`, populated with stolen memory, and used by GEM/GTT paths. It writes SGX registers `PSB_CR_BIF_CTRL` and `PSB_CR_BIF_DIR_LIST_BASE*` through `PSB_RSGX32`/`PSB_WSGX32`. PTE bit definitions come from `psb_drv.h`; SGX register definitions come from `psb_reg.h`.

## Risks
Reference counts can underflow if remove calls do not match inserted mappings. The code assumes 1024 PDEs and 4 KiB pages. There are subtle cache-flush calculations using CPUID-derived line size and `kmap_atomic`; locking order must remain rwsem before spinlock. Tiled insertion/removal requires `num_pages` to divide by desired stride when `hw_tile_stride` is nonzero.

## Test Signals
Signals include successful driver load with stolen-memory mapping, no SGX MMU faults during modeset/GEM operation, correct cleanup of empty PTs, stable suspend/resume after MMU context rebinding, and no warnings from invalid stride inputs or allocation failures. Hardware TLB/cache flush registers should be touched after bound PD updates.
