# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu.h

## Purpose
Shared private header for the Arm SMMU v1/v2 driver family. It defines architectural register offsets, bitfields, constants, core data structures, io-pgtable register conversion helpers, MMIO access wrappers, implementation hook contracts, and exported helpers used by implementation-specific files.

## Important APIs, Types, And Functions
The header enumerates global, stream mapping, context bank, fault, TLB, ATS, TCR, TTBR, MAIR, CBAR/CBA2R, and SCTLR registers. Important structures include `arm_smmu_device`, `arm_smmu_domain`, `arm_smmu_cfg`, `arm_smmu_cb`, `arm_smmu_smr`, `arm_smmu_s2cr`, `arm_smmu_master_cfg`, `arm_smmu_impl`, and `arm_smmu_context_fault_info`. Helpers `arm_smmu_lpae_tcr()`, `arm_smmu_lpae_tcr2()`, and `arm_smmu_lpae_vtcr()` translate io-pgtable config into SMMU register values. `arm_smmu_readl/writel/readq/writeq()` route register accesses through implementation overrides when present. Macros define GR0, GR1, and context-bank page addressing.

## Control Flow
This header does not run control flow itself, but it shapes the core driver's flow. `arm-smmu.c` uses it to probe features, initialize context banks, program stream routing, issue TLB invalidations, and decode faults. Qualcomm and Nvidia implementation files use `arm_smmu_impl` hooks and exported prototypes to customize behavior without duplicating the generic driver.

## State And Persistence
It defines volatile runtime state only. `arm_smmu_device` persists for platform-device lifetime and contains feature bits, register base, context and stream maps, IRQs, clocks, and IOMMU registration state. `arm_smmu_domain` persists for IOMMU domain lifetime and contains selected stage, config, locks, and io-pgtable ops. No disk persistence exists.

## Dependencies And Integration Points
The header depends on kernel bitfield, device, I/O, clock, IOMMU, io-pgtable, IRQ, mutex, and spinlock APIs. It exposes prototypes for generic, Nvidia, and Qualcomm impl init/module hooks and shared functions such as `arm_smmu_write_context_bank()`, `arm_mmu500_reset()`, and context fault info helpers.

## Risks
Register definitions are architectural contracts; wrong masks or duplicate definitions can corrupt hardware programming. `arm_smmu_lpae_tcr()` handles TTBR1 quirks by shifting TCR fields and disabling TTBR0, so changes can break GPU split page tables. Implementation override paths mean every access helper must preserve semantics for both generic and vendor-mediated register spaces. Fixed maxima such as `ARM_SMMU_MAX_CBS` and 32-bit stall users in vendor code must remain compatible.

## Test Signals
Compile all `arm-smmu` variants, including vendor impls. Run sparse/build coverage for 32-bit and 64-bit, big endian, AArch32 short descriptor, and TTBR1 quirk configurations. Hardware tests should verify register programming through generic and overridden MMIO accessors, context-bank setup, fault decoding, and TLB operations.
