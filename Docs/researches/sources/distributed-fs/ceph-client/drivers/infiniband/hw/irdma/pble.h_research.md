# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/pble.h

## Purpose
`pble.h` defines PBLE geometry, allocation levels, chunk metadata, PRM allocator state, HMC PBLE resource state, and prototypes for PBLE resource management.

## Important APIs, types, and functions
Important constants are `PBLE_SHIFT`, `PBLE_PER_PAGE`, `HMC_PAGED_BP_SHIFT`, `PBLE_512_SHIFT`, and `PBLE_INVALID_IDX`. Important types are `enum irdma_pble_level`, `enum irdma_alloc_type`, `struct irdma_pble_info`, `struct irdma_pble_level2`, `struct irdma_pble_alloc`, `struct irdma_chunk`, `struct irdma_pble_prm`, and `struct irdma_hmc_pble_rsrc`. Public prototypes cover initialization, destruction, allocation, free, PRM bitmap operations, locks, and paged memory helpers.

## Control flow, state, and persistence
The header itself has no flow, but its structures define the PBLE persistent state: chunk list and bitmaps, free/allocated PBLE counters, next FPM position, allocation statistics, level-1 and level-2 allocation descriptors, and direct/paged SD chunk type.

## Dependencies and integration points
It depends on HMC structures, DMA info, virtual memory wrappers, list heads, locks, and the control device. It is consumed by MR registration paths, AEQ virtual mapping, `hw.c`, and `pble.c`.

## Risks and test signals
Risks are geometry mismatch with HMC page size, level-2 root/leaf count mistakes, and stats/counter drift. Tests should validate allocation descriptors returned to MR code, free/reallocate behavior, PRM bitmap accounting, and chunk type cleanup.
