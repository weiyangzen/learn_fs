# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/pble.c

## Purpose
`pble.c` manages PBLE backing memory carved from the HMC PBLE object space. It creates PBLE chunks using direct or paged SDs, tracks free PBLE ranges with bitmaps, allocates level-1 or level-2 PBLE lists, and returns PBLEs during MR/AEQ teardown.

## Important APIs, types, and functions
Exported functions include `irdma_hmc_init_pble`, `irdma_destroy_pble_prm`, `irdma_get_pble`, and `irdma_free_pble`. Internal helpers include `get_sd_pd_idx`, `add_sd_direct`, `add_bp_pages`, `irdma_get_type`, `add_pble_prm`, `get_lvl1_pble`, `get_lvl2_pble`, `free_lvl2`, and `get_lvl1_lvl2_pble`.

## Control flow, state, and persistence
Initialization aligns the PBLE FPM base to 4 KiB, records unallocated PBLE count and next FPM address, initializes mutex/spinlock/list state, and adds the first PBLE PRM chunk. `add_pble_prm` chooses direct SD when a full SD-aligned 2 MiB region is available, otherwise paged SD, registers the chunk with the PRM bitmap, advances `next_fpm_addr`, decrements `unallocated_pble`, programs the SD when required, and links the chunk. Allocation first tries existing free PBLEs, then adds SD chunks as needed, creating level-1 lists or level-2 root/leaf lists. State persists in `irdma_hmc_pble_rsrc` counters, chunk list, PRM bitmaps, and HMC SD/PD entries.

## Dependencies and integration points
The file depends on HMC APIs from `hmc.c`, PBLE bitmap helpers declared in `pble.h` and implemented elsewhere, DMA/vmalloc page mapping for paged chunks, and CQP SD programming. `hw.c` initializes PBLE resources after CEQs and before AEQ creation; AEQ virtual mapping can allocate PBLEs from this pool.

## Risks and test signals
Risks include allocation underflow/overflow around FPM alignment, direct-versus-paged fallback mistakes, bitmap leaks after level-2 partial failure, locking imbalance between mutex and PRM spinlock helpers, and programming SDs before `valid` is coherent. Tests should cover exact 512-PBLE boundaries, unaligned PBLE base, level-1 and level-2 allocation/free, forced direct allocation failure fallback, Gen3 direct mode rules, and destroy with mixed chunk types.
