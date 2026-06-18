# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom.h

## Purpose
Private Qualcomm header shared by the Qualcomm Arm SMMU implementation and debug files. It defines the Qualcomm wrapper state, debug register configuration metadata, match-data contract, and conditional debug entry points.

## Important APIs, Types, And Functions
`struct qcom_smmu` embeds `struct arm_smmu_device` as its first field so generic code can be converted with `container_of()`. Its fields store selected match data, the bypass quirk flag and bypass context bank, and the `stall_enabled` bitmap used by Adreno stall control. `enum qcom_smmu_impl_reg_offset` indexes implementation-defined debug registers for TBU power and sync progress. `struct qcom_smmu_config` holds the register-offset table. `struct qcom_smmu_match_data` binds SoC compatible entries to a normal impl, Adreno impl, optional client ACTLR table, and optional debug config. The header declares `qcom_smmu_context_fault()` and conditionally declares or stubs `qcom_smmu_tlb_sync_debug()` and `qcom_tbu_probe()`.

## Control Flow
`arm-smmu-qcom.c` allocates/wraps a generic SMMU as `struct qcom_smmu` and stores `qcom_smmu_match_data`. Debug code uses the config offsets only when present. The generic Arm SMMU driver reaches the Qualcomm implementation through `struct arm_smmu_impl`; this header is the type bridge for those hooks.

## State And Persistence
The header defines in-memory driver state only. It creates no storage and has no persistence. The embedded-struct layout is important because callers rely on safe conversion between `arm_smmu_device` and `qcom_smmu`.

## Dependencies And Integration Points
It depends on `arm-smmu.h` being included first for `struct arm_smmu_device`, `struct arm_smmu_impl`, and related declarations. It is consumed by both Qualcomm source files and indirectly by module init/exit registration paths.

## Risks
Any change to `struct qcom_smmu` embedding would break `container_of()` assumptions. `stall_enabled` is a 32-bit bitmap, so it assumes context-bank indices used for stall fit the bitmap. Stubbed debug functions return no diagnostics and `qcom_tbu_probe()` returns `-EINVAL` when debug is disabled; callers must keep that conditional behavior in mind.

## Test Signals
Compile both `CONFIG_ARM_SMMU_QCOM_DEBUG=y` and disabled variants. Check that all Qualcomm impl data initializers match the header shape and that debug-disabled builds still register the TBU platform driver path without unresolved symbols.
