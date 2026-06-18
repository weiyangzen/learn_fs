# sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu_hw-8xxx.h

## Purpose
`msm_iommu_hw-8xxx.h` is the register-definition and bitfield access layer for Qualcomm 8xxx-generation MSM IOMMU hardware. It provides read/write helpers, field setters/getters, page-table descriptor constants, register offsets, masks, and shifts consumed by `msm_iommu.c`.

## Important APIs, Types, and Functions
The header is macro-only. Generic primitives are `GET_GLOBAL_REG`, `GET_CTX_REG`, `SET_GLOBAL_REG`, `SET_CTX_REG`, numbered register wrappers, `GET_FIELD`, and `SET_FIELD`. Higher-level macros cover global registers (`M2VCBR_N`, `CBACR_N`, `CR`, `ESR`, `IDR`, TLB test/invalidate registers), context registers (`SCTLR`, `ACTLR`, `CONTEXTIDR`, `TTBR0/1`, `TTBCR`, `PAR`, `FSR`, `FAR`, `FSYNR0/1`, `PRRR`, `NMRR`, TLB invalidation and V2P registers), and field-specific setters/getters such as `SET_M`, `SET_TRE`, `SET_CONTEXTIDR_ASID`, `GET_FSR`, `GET_FAULT`, and `SET_TLBIVA`.

It also defines page-table descriptor constants for first-level and second-level ARM v7 mappings, memory/cache policy values, `CTX_SHIFT`, and masks/shifts for every exposed field.

## Control Flow and State
The macros perform direct MMIO reads/writes and read-modify-write operations. State is entirely hardware register state at the supplied base address and context index. `SET_FIELD()` reads the current register, clears a shifted mask, and writes the updated value; callers must provide any required serialization.

## Dependencies and Integration Points
The header depends on Linux MMIO primitives `readl()` and `writel()`. It is integrated by `msm_iommu.c` for reset, context programming, MID routing, TLB invalidation, fault decoding, and PAR translation. The field layout must match the APQ8064/MSM 8xxx hardware manual.

## Risks and Test Signals
Risks include macro argument ordering mistakes, read-modify-write races if used without locking, typo-prone field names, inconsistent names such as `TLBLCKR`/`TLBLKCR`, and silent corruption if masks or shifts are wrong. Test signals include compile-time coverage of all macros used by the driver, boot-time context reset/programming, fault register decode sanity, TLB invalidation side effects, and hardware validation against known register dumps.
