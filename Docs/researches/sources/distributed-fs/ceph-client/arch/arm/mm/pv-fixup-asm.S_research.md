# sources/distributed-fs/ceph-client/arch/arm/mm/pv-fixup-asm.S

## Purpose
Safely remaps LPAE page tables by applying a physical-address delta to kernel, boot-data, level-1 table entries, and TTBRs. It is used for Keystone 2 physical address space remapping while running from identity-mapped code.

## Important APIs, Types, And Functions
Exports `lpae_pgtables_remap_asm`. Inputs are a 64-bit delta in `r1:r0` and page-table base in `r2`. It uses constants such as `_end`, `FDT_FIXED_BASE`, `KERNEL_OFFSET`, `SECTION_SHIFT`, `CR_M`, and LPAE table entry widths.

## Control Flow
The function saves registers, disables MMU/caches by clearing `CR_M`, updates L2 entries covering the kernel, updates two boot-data entries, updates four L1 entries, adjusts TTBR0 and TTBR1 by the same delta, flushes I-cache/BTB and TLBs, then restores the saved SCTLR to re-enable the MMU.

## State, Dependencies, And Integration
Persistent state changed is page-table physical addresses and CP15 TTBR/SCTLR state. Dependencies include LPAE page-table layout, identity mapping, `asm/cp15.h`, `asm/page.h`, and linker symbols. It integrates with platform physical-address virtualization/fixup code before normal virtual mappings are trusted.

## Risks And Test Signals
Risks are off-by-one L2 coverage, wrong 64-bit carry propagation, disabling MMU outside identity mapping, missing barriers, or stale TLBs. Test signals include Keystone 2 boot, high physical address boot, FDT fixed mapping access, and early page-table dump verification after fixup.
