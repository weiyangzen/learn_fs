# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom-debug.c

## Purpose
Qualcomm debug support for the Arm SMMU driver. It adds TBU registration, TBU halt/resume control, hardware address-translation probing through ATOS/ECATS registers, enhanced fault diagnostics, and Qualcomm-specific TLB sync timeout logging. It is compiled behind `CONFIG_ARM_SMMU_QCOM_DEBUG`; otherwise the header exposes no-op stubs.

## Important APIs, Types, And Functions
`struct qcom_tbu` tracks each translation buffer unit with its device, SMMU DT node, stream-ID range, clock, interconnect path, MMIO base, halt spinlock, and nested `halt_count`. Global state is `tbu_list`, protected by `tbu_list_lock`, plus global `atos_lock` to serialize ATOS transactions. `qcom_tbu_probe()` parses `qcom,stream-id-range`, maps the TBU registers, gets optional clock/interconnect resources, and appends the TBU to the global list. `qcom_smmu_tlb_sync_debug()` reads secure Qualcomm implementation registers through SCM after a TLB sync timeout and rate-limits logging. `qcom_find_tbu()` resolves a fault SID to a TBU. `qcom_tbu_halt()`/`qcom_tbu_resume()` stop and restart TBU traffic, including stalled-fault cleanup. `qcom_tbu_trigger_atos()` performs the hardware translation attempt. `qcom_smmu_context_fault()` replaces the generic context fault path when the Qualcomm debug impl is selected.

## Control Flow
On TBU probe, DT links each TBU to a parent SMMU node and SID range. During a Qualcomm context fault, the handler reads `FSR`, `FSYNR0`, `FAR`, and `CBFRSYNRA`, reports the fault to the IOMMU core, and if the normal client path did not handle it, compares software page-table walk output with ATOS hardware translation. ATOS flow enables interconnect bandwidth and clocks, halts the TBU, temporarily disables context fault interrupt/reporting bits, clears pending faults, serializes through `atos_lock`, writes SID/IOVA/AXUSER/transaction trigger registers, polls for completion or PAR fault/timeout, restores context SCTLR, resumes the TBU, disables resources, and returns a physical address or zero.

## State And Persistence
The file keeps only runtime kernel state: the global TBU list, per-TBU halt count, locks, and hardware register state while operations run. There is no disk persistence. Correctness depends on always unwinding clocks/interconnect votes and restoring SMMU context control state after debug operations.

## Dependencies And Integration Points
It depends on `arm-smmu.h` register helpers and `arm_smmu_domain`, the Qualcomm wrapper in `arm-smmu-qcom.h`, SCM IO reads, interconnect bandwidth APIs, runtime clocks, DT phandles, and IOMMU fault reporting. `arm-smmu-qcom.c` installs `qcom_smmu_context_fault()` and `qcom_smmu_tlb_sync_debug()` through `struct arm_smmu_impl` when debug support is enabled.

## Risks
The debug path manipulates live fault state, SCTLR fault bits, TBU halt control, clocks, and interconnect votes from IRQ/threaded IRQ context. Bugs could deadlock the TBU, hide faults, leave context interrupts disabled, or return misleading physical translations. The `icc_set_bw()` error path returns an integer as `phys_addr_t`, so callers must treat nonzero carefully. Global `atos_lock` avoids concurrent ATOS register races but can serialize all debug translations. Probe has no remove path to unlink TBUs from `tbu_list`, so it assumes devm lifetime and platform-device lifetime are sufficient.

## Test Signals
Exercise `CONFIG_ARM_SMMU_QCOM_DEBUG` builds, DT TBU binding parsing, missing TBU behavior, TLB sync timeout logging, fault handling with and without registered TBUs, ATOS success/fault/timeout cases, nested halt/resume counting, and fault handler return values for `report_iommu_fault()` results `0`, `-EBUSY`, `-EAGAIN`, and `-ENOSYS`.
