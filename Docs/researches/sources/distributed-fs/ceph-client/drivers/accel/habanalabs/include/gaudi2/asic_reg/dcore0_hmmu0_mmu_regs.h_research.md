<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_regs.h

## Purpose
`dcore0_hmmu0_mmu_regs.h` is the generated address map for the DCORE0 HMMU0 MMU control bank. It defines 107 `mmDCORE0_HMMU0_MMU_*` addresses in the 0x408000C-0x4080324 range for MMU enable/features, ordering, fault capture, interrupts, bypass, page-size and credit setup, secure/privileged DDR ranges, illegal address capture, RAZWI capture, and source-count reporting.

## Important APIs, types, and functions
The file exports address constants only. Core registers include `MMU_ENABLE`, `FORCE_ORDERING`, `FEATURE_ENABLE`, VA ordering masks, `LOG2_DDR_SIZE`, `SCRAMBLER`, `MEM_INIT_BUSY`, `SPI_SEI_MASK/CAUSE`, page and access error capture/address/valid registers, interrupt clear/mask, debug memory wrap, SPI cause clear, pipe credit, bypass, static multi-page size, separate-cache controls, total slice credit, fault/access id registers, DDR range enable, 8 secure min/max 64-bit range pairs, 8 privileged min/max 64-bit range pairs, illegal read/write address pairs, RAZWI valid/id/address registers, and `MMU_SRC_NUM`.

## Control flow
There is no logic in the header. Initialization writes range and feature registers before enabling translation. Runtime fault handling reads capture/id/address registers, decodes them using the mask header, clears interrupts, and may reconfigure or reset the MMU. Debug and recovery code read busy, credit, and source-count registers to decide whether the MMU can be safely reprogrammed.

## State and persistence behavior
The MMU bank stores critical persistent translation and protection state. Translation enable, bypass, ranges, features, credits, and masks affect all downstream memory access until changed. Error captures are latched diagnostics that must be consumed before clear/reset.

## Dependencies and integration points
This address map integrates with `dcore0_hmmu0_mmu_masks.h`, STLB programming, page-table management, device memory allocation, security setup, and interrupt/error handling in the Gaudi2 driver.

## Risks and edge cases
The largest risks are using the wrong DCORE/HMMU instance address, enabling bypass accidentally, programming only one half of a 64-bit range/address, and clearing latched MMU faults before the driver records VA/source/id details. Generated address drift would break memory protection in ways that may surface as unrelated engine faults.

## Test signals
Validation should include MMU initialization, memory mapping/unmapping, page-fault injection, access violation capture, secure/privileged range checks, RAZWI logging, STLB invalidation coupling, and reset paths that prove translation/protection state is reloaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_regs.h -->
