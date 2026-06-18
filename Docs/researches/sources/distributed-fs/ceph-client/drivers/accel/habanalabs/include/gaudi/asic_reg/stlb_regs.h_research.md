# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/stlb_regs.h

## Purpose

`stlb_regs.h` is an auto-generated Gaudi ASIC register-address header for the shared second-level TLB/cache-management block labelled `STLB (Prototype: STLB)`. It exports `mmSTLB_*` MMIO offsets in the `0xC12010..0xC12084` range. The header is small, but it is central to MMU setup and TLB/cache invalidation flows in the Gaudi driver.

There are no functions, structures, inline helpers, or software variables in this file. Its purpose is to provide stable symbolic register names for the MMU code paths that initialize page-table cache management, configure hop behavior, trigger invalidations, and poll invalidation completion.

## Important APIs and Register Groups

The macro API includes:

- Cache invalidation producer registers: `mmSTLB_CACHE_INV`, `mmSTLB_CACHE_INV_BASE_39_8`, and `mmSTLB_CACHE_INV_BASE_49_40`.
- Feature/configuration controls: `mmSTLB_STLB_FEATURE_EN`, `mmSTLB_STLB_AXI_CACHE`, `mmSTLB_HOP_CONFIGURATION`, and `mmSTLB_MEM_READ_ARPROT`.
- Linked-list lookup controls: `mmSTLB_LINK_LIST_LOOKUP_MASK_49_32`, `mmSTLB_LINK_LIST_LOOKUP_MASK_31_0`, and `mmSTLB_LINK_LIST`.
- Full and set-based invalidation controls/status: `mmSTLB_INV_ALL_START`, `mmSTLB_INV_ALL_SET`, `mmSTLB_INV_PS`, `mmSTLB_INV_CONSUMER_INDEX`, `mmSTLB_INV_HIT_COUNT`, and `mmSTLB_INV_SET`.
- SRAM/cache-management controls: `mmSTLB_SRAM_INIT`, `mmSTLB_MEM_CACHE_INVALIDATION`, `mmSTLB_MEM_CACHE_INV_STATUS`, `mmSTLB_MEM_CACHE_BASE_38_7`, `mmSTLB_MEM_CACHE_BASE_49_39`, `mmSTLB_MEM_CACHE_CONFIG`, and `mmSTLB_MEM_L0_CACHE_CFG`.
- Threshold registers per hop level: `mmSTLB_SET_THRESHOLD_HOP4` down to `mmSTLB_SET_THRESHOLD_HOP0`.
- Multi-hit interrupt controls: `mmSTLB_MULTI_HIT_INTERRUPT_CLR` and `mmSTLB_MULTI_HIT_INTERRUPT_MASK`.

## Control Flow and State Behavior

The header itself has no control flow, but its registers are used by concrete MMU flows. In `gaudi_mmu_init()`, the driver programs `CACHE_INV_BASE_39_8` and `CACHE_INV_BASE_49_40` from `prop->mmu_cache_mng_addr`, enables memory cache invalidation with `MEM_CACHE_INVALIDATION`, calls `hl_mmu_invalidate_cache()`, enables the upstream MMU, writes `HOP_CONFIGURATION` with `0x30440`, and initializes `gaudi->mmu_cache_inv_pi` to `1`. The comment in the caller notes that hardware expects the first producer index after init to be `1`, with wraparound returning to `0`.

In `gaudi_mmu_invalidate_cache()`, the driver writes `INV_PS` to invalidate L0/L1, writes `CACHE_INV` with the incrementing `gaudi->mmu_cache_inv_pi`, writes `INV_PS` again, polls `INV_PS` until it clears, and then writes `INV_SET` to `0`. That makes the STLB register block part of the driver’s runtime MMU coherency mechanism, not only initial setup.

Goya code in the same driver tree also references several `mmSTLB_*` macros, showing that this register namespace is shared across more than one HabanaLabs ASIC family or generated include set in this source snapshot.

## Dependencies and Integration Points

The header integrates with:

- Gaudi MMU initialization and cache invalidation in `gaudi.c`.
- The common HabanaLabs MMU API, especially `hl_mmu_invalidate_cache()`.
- Device properties such as `mmu_cache_mng_addr`, `mmu_pgt_addr`, ASID count, and hop table sizing.
- Polling helpers such as `hl_poll_timeout()` and timeout constants selected for PLDM versus normal hardware.

Because the file only provides offsets, value encoding depends on other MMU/STLB field definitions and on hardware documentation. Runtime correctness also depends on driver-maintained state such as `gaudi->mmu_cache_inv_pi`.

## Risks and Test Signals

Incorrect STLB offsets can break address translation coherency, page-table cache invalidation, or MMU initialization. Failures may surface as device page faults, stale translations after mapping changes, initialization timeouts while polling `INV_PS`, or hard-to-reproduce memory corruption. The producer-index behavior around `mmu_cache_inv_pi` is a stateful integration point; if the `CACHE_INV` or `INV_PS` addresses are wrong, the driver may believe invalidation completed while hardware did not perform it.

Test signals include successful MMU initialization, successful cache invalidation under map/unmap workloads, no timeout from the `INV_PS` polling path, correct behavior in PLDM and hardware timeout modes, and absence of stale-translation faults during DMA/compute memory stress. Static validation should compare all `0xC120xx` offsets against the Gaudi register database and confirm this generated file remains synchronized with its matching field headers.
