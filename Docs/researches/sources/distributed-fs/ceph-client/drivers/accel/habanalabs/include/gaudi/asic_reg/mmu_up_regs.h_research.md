# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mmu_up_regs.h

## Purpose

`mmu_up_regs.h` is a compact auto-generated register map for the Gaudi upper MMU block, marked as prototype `MMU`. It exports 25 `mmMMU_UP_*` address constants from `mmMMU_UP_MMU_ENABLE` at `0xC1100C` to `mmMMU_UP_MMU_BYPASS` at `0xC1106C`. The file names MMU enablement, ordering, feature, interrupt, fault-capture, RAZWI, credit, and bypass registers.

## Important APIs, types, and functions

There are no functions or types. The important macro groups are:

- Control/configuration: `MMU_ENABLE`, `FORCE_ORDERING`, `FEATURE_ENABLE`, `VA_ORDERING_MASK_31_7`, `VA_ORDERING_MASK_49_32`, `LOG2_DDR_SIZE`, `SCRAMBLER`, `MMU_BYPASS`.
- Initialization/status: `MEM_INIT_BUSY`, `SLICE_CREDIT`, `PIPE_CREDIT`, `DBG_MEM_WRAP_RM`.
- Interrupt and SPI handling: `SPI_MASK`, `SPI_CAUSE`, `SPI_INTERRUPT_CLR`, `SPI_INTERRUPT_MASK`, `SPI_CAUSE_CLR`.
- Fault capture: `PAGE_ERROR_CAPTURE`, `PAGE_ERROR_CAPTURE_VA`, `ACCESS_ERROR_CAPTURE`, `ACCESS_ERROR_CAPTURE_VA`.
- RAZWI tracking: `RAZWI_WRITE_VLD`, `RAZWI_WRITE_ID`, `RAZWI_READ_VLD`, `RAZWI_READ_ID`.

## Control flow

The header has no direct control flow. In `gaudi.c`, MMU initialization writes `mmMMU_UP_MMU_ENABLE` to enable translation and `mmMMU_UP_SPI_MASK` to configure MMU interrupt masking after STLB/cache setup. Later error handling reads `RAZWI_WRITE_VLD` and `RAZWI_READ_VLD`, decodes initiator IDs from `RAZWI_*_ID`, clears valid bits, and reads page/access capture registers to report faults and call the page-fault handler. This makes the header part of both initialization and asynchronous fault-reporting paths.

## State and persistence behavior

The macros are build-time constants. The hardware registers hold persistent device state until changed or reset: MMU enable/bypass status, ordering masks, interrupt cause/mask, captured fault virtual addresses, RAZWI initiator IDs, and credit counters. Fault-capture registers are latch-like: the driver reads valid bits, reports the captured address, then clears capture state by writing zero to the capture register or valid register.

## Dependencies and integration points

`gaudi_regs.h` includes this header. `gaudi.c` integrates it with STLB setup, cache invalidation, page-fault handling (`hl_handle_page_fault()`), RAZWI reporting, event masks, and engine-id mapping. Some field masks used with these addresses, such as page/access capture valid and VA high-bit masks, come from companion generated mask headers included through the broader Gaudi register set rather than from this address-only file.

## Risks

MMU register errors are high impact: a wrong enable or bypass address can disable address translation guarantees, and wrong capture addresses can hide or misreport memory faults. Fault handlers rely on clear-on-write behavior and valid bits; if the address map or masks diverge, stale faults may repeat or real faults may be dropped. RAZWI initiator decoding depends on the ID registers matching the hardware format, so address mistakes can misidentify engines and mislead recovery/debug work.

## Test signals

Useful tests include Gaudi MMU initialization, cache invalidation, page-fault injection, access-error injection, RAZWI read/write injection, interrupt mask/cause handling, and validation that captured virtual addresses are reported with correct high and low bits. Static build checks should verify `gaudi.c` still resolves all `mmMMU_UP_*` and companion `MMU_UP_*_MASK` macros.
