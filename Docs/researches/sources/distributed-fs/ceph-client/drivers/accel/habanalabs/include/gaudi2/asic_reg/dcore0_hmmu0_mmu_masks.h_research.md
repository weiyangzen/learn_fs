<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_masks.h

## Purpose
`dcore0_hmmu0_mmu_masks.h` is the generated bitfield map for the DCORE0 HMMU0 MMU register bank. It defines 164 shift/mask macros for enabling/bypassing the MMU, ordering, feature controls, address-range protection, page/access fault capture, interrupts, memory initialization, credits, static page-size configuration, illegal-address/RAZWI capture, and source id reporting.

## Important APIs, types, and functions
Important fields include `MMU_ENABLE`, weak-ordering control, feature enables for translation/page-fault/access-error behavior, VA ordering masks, DDR size, scrambler, memory-init busy bits, SPI/SEI cause and mask fields, page-error and access-error capture plus valid bits, interrupt clear/mask bits for page faults, access errors, multi-hit, security violations, and RAZWI, bypass control, static multi-page-size bits, core separate cache range/slice credits, page/access id low/high fields, DDR range enable, 8 secure min/max 64-bit range pairs, 8 privileged min/max 64-bit range pairs, illegal read/write address capture, RAZWI valid/id/address fields, and MMU source count.

## Control flow
The header is not executable. MMU initialization uses these masks to program translation enable, page-size/static features, ordering, DDR range protection, security/privilege ranges, and interrupt masks. Fault handling decodes capture and valid bits, reports page/access/RAZWI/security errors, clears interrupt/cause registers, and may trigger device reset depending on severity.

## State and persistence behavior
The macros describe persistent MMU configuration and latched fault state. Enable/bypass, feature, range, ordering, credit, and interrupt-mask fields persist across all translations until reset or reprogramming. Fault address/id/cause fields persist until cleared and are crucial for diagnosing illegal memory access.

## Dependencies and integration points
This file integrates with `dcore0_hmmu0_mmu_regs.h`, Gaudi2 MMU initialization, page-table setup, security/privilege range programming, fault interrupt handlers, and STLB/cache invalidation code. It must match the address header and the HMMU/STLB hardware spec for the same ASIC revision.

## Risks and edge cases
Risks include enabling translation before ranges and page tables are valid, clearing fault capture before logging it, programming secure/privileged range halves inconsistently, using bypass during user traffic, and misinterpreting RAZWI/access/page fault id widths. Range arrays are repeated and vulnerable to index drift.

## Test signals
Test signals include MMU enable/disable, mapped and unmapped memory access, secure and privileged range violations, page fault and access error injection, RAZWI capture, interrupt clear/mask behavior, and reset paths that restore all protection ranges and feature bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_mmu_masks.h -->
