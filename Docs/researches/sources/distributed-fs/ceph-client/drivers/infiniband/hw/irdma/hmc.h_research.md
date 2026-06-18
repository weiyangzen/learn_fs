# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hmc.h

## Purpose
`hmc.h` defines the HMC object model used by the IRDMA control plane. It gives names, constants, SD/PD table structures, create/delete request structures, and function prototypes for programming host memory backing for queues, MRs, PBLEs, timers, and other hardware objects.

## Important APIs, types, and functions
Important constants include SD/PD geometry such as `IRDMA_HMC_MAX_BP_COUNT`, `IRDMA_HMC_PD_CNT_IN_SD`, `IRDMA_HMC_DIRECT_BP_SIZE`, `IRDMA_HMC_PAGED_BP_SIZE`, and `IRDMA_HMC_MAX_SD_COUNT`. `enum irdma_hmc_rsrc_type` enumerates object classes, with `IRDMA_HMC_IW_MAX` as the table size. `struct irdma_hmc_info` owns the object table and SD table; `struct irdma_hmc_sd_entry`, `struct irdma_hmc_pd_table`, and `struct irdma_hmc_pd_entry` describe the host-side mirror of hardware descriptors.

## Control flow, state, and persistence
The header itself has no control flow but defines the state persisted across control initialization and runtime allocations: object counts/bases/sizes, function id, SD entries, PD tables, and cached SD indexes used to batch CQP programming. Create/delete info structures carry one operation's range, object type, selected SD entry type, and counts of SDs to add or delete.

## Dependencies and integration points
It includes `defs.h` and refers to `struct irdma_hw`, `struct irdma_sc_dev`, DMA memory wrappers from `osdep.h`, and CQP-facing update structures. It is consumed by `hmc.c`, `hw.c`, `pble.c`, and lower-level control code that configures FPM values.

## Risks and test signals
The main risk is contract drift: constants and enum order must match firmware/hardware FPM layouts and CQP encodings. Tests should verify table sizes, SD/PD geometry assumptions, object enum count handling, and that all code using `sd_indexes` respects `IRDMA_HMC_MAX_SD_COUNT`.
