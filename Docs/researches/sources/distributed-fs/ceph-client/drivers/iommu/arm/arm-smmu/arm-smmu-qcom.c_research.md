# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom.c

## Purpose
Qualcomm implementation layer for the generic Arm SMMU v1/v2 driver. It selects Qualcomm-specific `arm_smmu_impl` hooks, works around firmware and SoC quirks, programs implementation-defined ACTLR settings for selected clients, exposes private Adreno GPU callbacks, and registers the optional TBU debug platform driver.

## Important APIs, Types, And Functions
The core dispatch type is `struct qcom_smmu_match_data`, which points to a generic impl, an Adreno impl, client ACTLR match table, and optional debug register config. `qcom_smmu_impl_init()` matches DT or ACPI and wraps the generic `arm_smmu_device` into `struct qcom_smmu`. `qcom_smmu_tlb_sync()` overrides TLB sync polling and calls debug diagnostics on timeout. Adreno helpers include `qcom_adreno_smmu_get_fault_info()`, `qcom_adreno_smmu_set_stall()`, `qcom_adreno_smmu_set_ttbr0_cfg()`, PRR accessors, GPU SID detection, and context-bank allocation forcing the GPU to CB0. `qcom_smmu_cfg_probe()` trims bad context-bank counts, detects S2CR bypass write quirks, reserves a bypass context bank, and imports bootloader-programmed SMRs. `qcom_smmu_write_s2cr()` translates BYPASS/FAULT writes for affected firmware.

## Control Flow
During generic SMMU probe, `arm_smmu_impl_init()` calls into this file for Qualcomm-compatible nodes. `qcom_smmu_create()` defers until SCM is ready, reallocates the SMMU object to include Qualcomm fields, and installs the selected impl. Later, generic config probing calls the Qualcomm `cfg_probe`, context initialization calls Qualcomm ACTLR/GPU setup, S2CR writes flow through the quirk-aware writer, and TLB syncs use the Qualcomm poll wrapper. For Adreno SMMUs, GPU devices are identified by SID 0, receive context bank 0, may enable TTBR1 split page tables, and get an `adreno_smmu_priv` callback table allowing the GPU driver to inspect faults, toggle stall behavior, and switch TTBR0.

## State And Persistence
Persistent runtime state lives in `struct qcom_smmu`: match data, bypass quirk flag, reserved bypass CB index, and per-CB stall bitmap. Hardware state includes ACTLR, SCTLR, S2CR, CBAR, TTBR, PRR, and wait-for-safe settings. There is no disk persistence.

## Dependencies And Integration Points
This file integrates the generic `arm-smmu.c` implementation hooks, Qualcomm SCM (`qcom_scm_is_available()`, `qcom_scm_qsmmu500_wait_safe_toggle()`), Adreno private API (`linux/adreno-smmu-priv.h`), OF/ACPI matching, runtime PM, and optional debug helpers in `arm-smmu-qcom-debug.c`. It is selected by compatible strings such as `qcom,smmu-500`, SoC-specific SMMU-500 strings, and older `qcom,*-smmu-v2` entries.

## Risks
The bypass quirk deliberately rewrites S2CR semantics, so incorrect detection could either expose unintended bypass or fault valid devices. GPU split page-table handling requires precise ordering around TCR/TTBR writes. Stall toggling modifies SCTLR while the device may be active and relies on PM and `cb_lock`. ACTLR values are encoded in match data; incorrect client matching can cause performance or correctness issues. SCM unavailability defers probe, so boot ordering matters.

## Test Signals
Build with and without debug support and ACPI. Boot representative Qualcomm SoCs covering SMMUv2, SMMU-500, Adreno and non-Adreno nodes, bypass quirk detection, >128 SMR limiting, `sdm845` wait-safe reset, and ACTLR client programming. GPU tests should cover TTBR1 enablement, TTBR0 switching, stall toggling, PRR callbacks, and context fault threaded IRQ behavior.
