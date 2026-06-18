# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mmu_regs.h

## Purpose

`mmu_regs.h` provides generated MMIO offsets for the Goya MMU control block. It names the registers used to configure translation enablement, ordering, features, address scrambling, busy status, SPI status, and page/access fault capture.

## Important APIs, types, and data

The file defines only `mmMMU_*` offset macros. The register window starts at `0x480000` with `INPUT_FIFO_THRESHOLD`, then includes `MMU_ENABLE`, `FORCE_ORDERING`, `FEATURE_ENABLE`, VA ordering masks, `LOG2_DDR_SIZE`, `SCRAMBLER`, `MEM_INIT_BUSY`, `SPI_MASK`, `SPI_CAUSE`, `PAGE_ERROR_CAPTURE`, `PAGE_ERROR_CAPTURE_VA`, `ACCESS_ERROR_CAPTURE`, and `ACCESS_ERROR_CAPTURE_VA` through `0x480040`.

There are no functions, structs, or field masks in this file; field definitions live in `mmu_masks.h`.

## Control flow

The header is declarative. Goya MMU initialization code writes these offsets in a hardware-defined sequence to configure thresholds/features/ordering/scrambler and then enable translation. Fault paths read the capture registers, combine high/low VA pieces using `mmu_masks.h`, log the fault, and clear capture state. Reset paths may reinitialize the whole window.

## State and persistence behavior

The addressed registers hold global MMU state for the device. Configuration affects all clients using translated memory, including MME queue managers and tensor accesses. Fault-capture registers retain latched addresses until handled. The header itself has no persistent state.

## Dependencies and integration points

It pairs with `mmu_masks.h` and common HabanaLabs MMU code. Goya-specific `goyaP.h` reserves page-table, default-page, and MMU cache-management regions; common code manages page tables and address translation. MME and QMAN ASID/MMBP programming relies on this MMU block being configured correctly.

## Risks and edge cases

Using offsets without the matching masks can write reserved bits. Enabling the MMU before page tables, default pages, or client ASIDs are ready can break all translated accesses. Fault capture requires valid-bit checks and correct high/low address reconstruction. Since this is a single global block, mistakes affect unrelated accelerator engines, not only MME.

## Test signals

Validation should include successful Goya probe with MMU enabled, page-table setup and teardown, debugfs MMU queries, deliberate page/access fault injection with accurate VA reporting, and MME/DMA/TPC workloads that prove translated clients remain functional after reset and under load.
