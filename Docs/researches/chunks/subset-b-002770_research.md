# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 28257-30631

## Scope

This chunk covers a large middle slice of the generated AMD MMHUB 1.7 shift/mask header. It begins in the `MMEA5_DSM_CNTL2` field group and continues through `VM_CONTEXT10_CNTL`. The range is entirely preprocessor data: `#define` constants for register-field shifts and masks, plus generated address-block comments. It contains no C functions, structs, enums, storage, locks, allocation, or executable control flow.

The register families in this slice cover:

- `MMEA5_*` error injection, EDC/RAS, clock-control, miscellaneous request blocking, address-decoder selection, and always-on link-manager fields.
- `MC_VM_MX_L1_*` L1 TLB status and L1 performance-counter fields.
- `PCTL0_*` MMHUB deep-sleep, power-gating ignore, per-slice busy/allow, and UTCL2/slice miscellaneous fields.
- `ATC_L2_*` ATC L2 request/cache controls, cache data/debug access, clock gating, light sleep, DSM error injection, and ATC performance-counter fields.
- `L2TLB_*` and `UTC_GPUVA_VMID_TRANSLATION_ASSIST_*` L2 TLB status, translation-assist request/response, and L2TLB performance counters.
- `VM_L2_*`, `VML2_*`, and `UTCL2_*` VM L2 cache, invalidation, protection fault, identity aperture, bank/class selection, parity, clock gating, ECC/EDC, and VM L2 performance-counter fields.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT10_CNTL`, where the chunk ends partway through the repeated VM context control register family.

## Purpose

`mmhub_1_7_sh_mask.h` is a generated hardware bitfield map for the AMDGPU MMHUB 1.7 block. This chunk gives symbolic shift and mask constants used by SOC15 register helpers to read, modify, and interpret MMHUB registers without hard-coded bit numbers.

The matching offset header identifies register addresses (`reg...` constants). This shift/mask header identifies the bit layout inside those registers (`REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`). The constants are consumed by macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD`, which depend on the generated naming convention.

For MMHUB 1.7 specifically, this slice supports three main driver surfaces:

- GPUVM and GART setup: VM L2 cache setup, L1/L2 invalidation behavior, VM context enablement, page-table depth/block size, retry-fault policy, and default-page fault routing.
- RAS and diagnostics: MMEA5 EDC counters, error-status fields, ECC/EDC controls, parity status, and fatal/interrupt behavior.
- Power/performance management: clock-gating and light-sleep fields, deep-sleep controls, per-slice power/deep-sleep gating, and performance-counter selector/result fields.

## Important APIs, Types, And Data

The exported "API" is the macro namespace. Important groups include:

- `MMEA5_DSM_CNTL2`, `MMEA5_DSM_CNTL2A`, and empty `MMEA5_DSM_CNTL2B` marker: error-injection enable, delay-selection, and injection-delay fields for command, data, tag, page, DRAM, GMI, and IO memory paths.
- `MMEA5_CGTT_CLK_CTRL`, `MMEA5_EDC_MODE`, `MMEA5_ERR_STATUS`, `MMEA5_MISC2`, `MMEA5_ADDRDEC_SELECT`, `MMEA5_EDC_CNT3`, and `MMEA5_MISC_AON`: clock/test gating, EDC mode, fatal/error status, request blocking, address decoder channel selection, DED count fields, and link-manager hysteresis controls.
- `MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS`: `BUSY` and `FOUND_PARITY_ERRORS` status fields for eight L1 TLB instances.
- `MC_VM_MX_L1_PERFCOUNTER0_CFG` through `MC_VM_MX_L1_PERFCOUNTER3_CFG`, `MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, `MC_VM_MX_L1_PERFCOUNTER_LO`, and `MC_VM_MX_L1_PERFCOUNTER_HI`: L1 perf event selection, mode, enable/clear, result selection, triggers, low/high counter values, and compare fields.
- `PCTL0_CTRL`, `PCTL0_MMHUB_DEEPSLEEP_*`, `PCTL0_PG_IGNORE_DEEPSLEEP*`, `PCTL0_SLICE{0..5}_CFG_DAGB_BUSY`, `PCTL0_SLICE{0..5}_CFG_DS_ALLOW*`, `PCTL0_UTCL2_MISC`, and `PCTL0_SLICE{0..5}_MISC`: power controller masks for deep-sleep entry, idle/busy sources, power-gating masks, slice-level DAGB status, and per-slice memory power state.
- `ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CNTL3`, `ATC_L2_CNTL4`, `ATC_L2_STATUS`, `ATC_L2_STATUS2`, `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, `ATC_L2_CGTT_CLK_CTRL`, `ATC_L2_CACHE_*_DSM_*`, `ATC_L2_MM_GROUP_RT_CLASSES`, and ATC L2 perf-counter macros: ATC request depth, cache bank/update/VMID policy, translation reset/wait, busy/status, clock gating, light sleep, data SRAM error injection, real-time class mapping, and performance monitoring.
- `L2TLB_TLB0_STATUS`, `UTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*`, and `UTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_*`: L2 TLB parity/busy state and assisted GPUVA/VMID translation request/response fields including VMID, pasid/vmfid, permission flags, PTE address, ready/valid, and fault response metadata.
- `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, `VM_L2_STATUS`, `VM_DUMMY_PAGE_FAULT_*`, `VM_L2_PROTECTION_FAULT_*`, identity-aperture address registers, `VM_L2_BANK_SELECT_RESERVED_CID*`, `VM_L2_CACHE_PARITY_CNTL`, `VM_L2_CGTT_*`, `VML2_*_ECC_*`, `UTCL2_*_ECC_*`, `UTCL2_EDC_MODE`, and `UTCL2_EDC_CONFIG`: VM L2 cache enablement, fragment processing, invalidation, cache sizing/banking, protection-fault controls/status/default routing, identity mapping, reserved client ID banking, parity/ECC injection and status, and EDC mode.
- `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG`, result-control, low, and high fields: VM L2 performance-counter selection and result access.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT10_CNTL`: repeated context-control fields for enabling contexts, configuring page-table depth/block size, retry behavior, and per-fault interrupt/default-page policy for range, dummy page, PDE0, valid, read, write, and execute protection faults.

There are no local types. The important external type relationships are indirect: `struct amdgpu_device`, `struct amdgpu_vmhub`, `struct ras_err_data`, `struct soc15_ras_field_entry`, and `struct soc15_reg_entry` in the AMDGPU driver consume these macros through register helper APIs.

## Control Flow

This header has no runtime control flow. Runtime behavior appears when AMDGPU MMHUB code includes the header and expands the macros in register read/modify/write sequences.

The primary local consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`:

1. `mmhub_v1_7_gart_enable()` sequences GART setup, aperture setup, TLB setup, cache setup, snoop override, system-domain enablement, identity-aperture disable, VMID configuration, and invalidation programming.
2. `mmhub_v1_7_init_cache_regs()` reads and writes `regVM_L2_CNTL`, `regVM_L2_CNTL2`, `regVM_L2_CNTL3`, and `regVM_L2_CNTL4`, using fields from this chunk to enable VM L2 cache, enable fragment processing, invalidate L1/L2 state, select bank/fragment values, and adjust physical PDE/PTE request policy for XGMI-connected-to-CPU systems.
3. `mmhub_v1_7_enable_system_domain()` programs `VM_CONTEXT0_CNTL` fields for VMID0 using `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, and retry-fault policy.
4. `mmhub_v1_7_setup_vmid_config()` loops over VMIDs 1 through 15 using offsets from the companion offset header and `VM_CONTEXT1_CNTL` field names. Because the context control registers are layout-compatible, `REG_SET_FIELD(..., VM_CONTEXT1_CNTL, ...)` is used for each offset in the repeated context range.
5. `mmhub_v1_7_set_fault_enable_default()` uses `VM_L2_PROTECTION_FAULT_CNTL` fields to toggle default-page handling for range, PDE, translate-further, NACK, dummy, valid, read, write, and execute faults; when default handling is disabled it sets crash-on-fault fields.
6. `mmhub_v1_7_init_system_aperture_regs()` writes `VM_L2_PROTECTION_FAULT_DEFAULT_ADDR_LO32/HI32` and updates `VM_L2_PROTECTION_FAULT_CNTL2__ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
7. Clock-gating helpers read/write `ATC_L2_MISC_CG__ENABLE_MASK` and `ATC_L2_MISC_CG__MEM_LS_ENABLE_MASK` to report and control MMHUB medium-grain clock gating and memory light sleep.
8. RAS helpers read MMEA EDC count registers, extract SEC/DED counts with `SOC15_REG_FIELD` metadata, check `MMEA*_ERR_STATUS` status fields via `REG_GET_FIELD`, and set `CLEAR_ERROR_STATUS` to reset hardware error status.

The perf-counter, PCTL0, translation-assist, ECC/EDC injection, and many debug/cache-data fields in this chunk are generated register definitions that may be used by diagnostics, firmware-facing flows, debug tooling, or future driver paths even when not directly touched by the current `mmhub_v1_7.c` setup path.

## State And Persistence Behavior

The macros are compile-time constants and do not own state. The registers they describe are persistent hardware state inside MMHUB until changed by driver writes, firmware, reset, suspend/resume restore, or GPU reset.

- VM L2 cache and invalidation fields persist after GART enable. Incorrect `VM_L2_CNTL*` values can affect address translation, cache residency, L1/L2 invalidation propagation, and page-table walk behavior for all MMHUB clients.
- VM context control fields persist per VMID. They define whether a context is active, how many page-table levels are walked, what page-table block size is used, whether retry faults are generated, and whether specific faults interrupt or resolve to the default page.
- Protection-fault status and address registers capture hardware fault state. Status fields such as VMID, client ID, fault type, RWX bits, and more-faults indicators are read by fault/RAS paths; default-address and fault-policy registers control where failed transactions are redirected.
- MMEA5 EDC/RAS counters and status registers accumulate hardware error evidence. Driver RAS paths read count registers to update corrected/uncorrected totals and write zero or `CLEAR_ERROR_STATUS` to reset the hardware view.
- ECC/EDC index/control/status registers for VML2, VML2 walker, and UTCL2 are stateful debug/RAS controls. Error-injection enable and status bits are especially sensitive because they can intentionally create correctable or uncorrectable events.
- Clock gating, deep sleep, memory light sleep, and PCTL slice controls persist as power-management policy. These fields affect whether MMHUB/ATC/UTCL2/slice logic can idle, gate clocks, or enter memory low-power states.
- Performance-counter configuration and result-selection fields persist while counters run. A profiling path must clear/configure/select counters carefully or it can observe stale results from prior measurements.

There is no disk persistence, allocation lifetime, refcounting, or software synchronization in the header. Serialization and ordering are the responsibility of the MMIO callers, usually under AMDGPU device initialization, reset, clockgating, VM, or RAS sequencing.

## Dependencies

This chunk depends on the generated MMHUB 1.7 register specification and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`, which supplies the matching `reg...` register addresses and `_BASE_IDX` constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, the primary MMHUB 1.7 consumer for GART setup, VM L2 setup, VM context setup, clock gating, and RAS handling.
- SOC15 register helper macros including `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_ENTRY_OFFSET`, `SOC15_REG_FIELD`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- AMDGPU state in `struct amdgpu_device`, especially `adev->gmc`, `adev->vm_manager`, `adev->vmhub[AMDGPU_MMHUB0(0)]`, `adev->cg_flags`, `adev->dummy_page_addr`, and RAS support state.
- RAS support code in `amdgpu_ras.h` and SOC15 RAS field descriptors, which rely on the shift/mask values for correct SEC/DED extraction and status clearing.

The generated macro naming convention is itself a dependency. `REG_SET_FIELD(tmp, VM_L2_CNTL, ENABLE_L2_CACHE, 1)` expands by concatenating `VM_L2_CNTL__ENABLE_L2_CACHE_MASK` and `VM_L2_CNTL__ENABLE_L2_CACHE__SHIFT`; a spelling or prefix mismatch compiles only if a wrong same-named macro exists elsewhere, or fails at build time.

## Integration Points

- MMHUB GART enable/disable: `mmhub_v1_7_gart_enable()` and `mmhub_v1_7_gart_disable()` use these fields to enable or disable VM contexts, L1 TLB, advanced driver model, VM L2 cache, invalidation, and context fault routing.
- VM fault handling: `mmhub_v1_7_set_fault_enable_default()` and the hub initialization fields `vm_l2_pro_fault_status` and `vm_l2_pro_fault_cntl` integrate this header with AMDGPU fault reporting, retry policy, default-page handling, and crash-on-fault behavior.
- VMID setup: `VM_CONTEXT0_CNTL` and `VM_CONTEXT1_CNTL` field layouts configure VMID0 and VMIDs 1-15. This chunk covers context 0-10 field definitions directly, while the file continues the repeated family after the chunk for later VMIDs.
- Clock and power gating: `ATC_L2_MISC_CG` masks integrate with `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS`. PCTL0 fields describe the lower-level deep-sleep and slice gating controls that hardware or debug/power paths use around those policies.
- RAS count/status integration: `mmhub_v1_7_ras_fields`, `mmhub_v1_7_edc_cnt_regs`, and `mmhub_v1_7_ea_err_status_regs` use MMEA5 fields in this chunk for SEC/DED accounting and external-agent error status checks.
- Performance monitoring: L1, ATC L2, L2TLB, and VM L2 performance-counter macros provide selector/result layouts for MMHUB profiling and hardware debug. Their integration is through generic register access rather than a high-level C abstraction in this file.
- Translation assist and ATS/ATC behavior: `UTC_GPUVA_VMID_TRANSLATION_ASSIST_*` and `ATC_L2_*` fields describe interfaces between MMHUB address translation, ATC cache behavior, and VMID/GPUVA translation assistance.
- ECC/EDC and error injection: `VML2_MEM_ECC_*`, `VML2_WALKER_MEM_ECC_*`, `UTCL2_MEM_ECC_*`, `UTCL2_EDC_*`, and DSM controls integrate with RAS validation, hardware self-test, and debug flows that intentionally inject or observe memory-protection errors.

## Risks

- Bitfield drift is the central risk. These masks can compile cleanly while targeting the wrong bits if the generated header is out of sync with the MMHUB 1.7 register database.
- The chunk starts and ends mid-family. It begins after earlier `MMEA5_DSM_CNTL2` fields and ends partway through `VM_CONTEXT10_CNTL`; reconciliation must merge adjacent chunks to describe the full source file without treating this slice as complete for those families.
- Repeated VM context registers are easy to misuse. Context 1 field names are used with offset arithmetic for VMIDs 1-15; the repeated field layouts must remain identical, and `hub->ctx_distance` must match the offset header.
- VM L2 and invalidation fields are high-blast-radius. Incorrect cache enablement, bank selection, fragment size, or invalidate bits can create stale GPUVM translations, page-table walk failures, data corruption symptoms, or GPU hangs.
- Fault policy changes can mask or amplify bugs. Enabling default-page handling can hide invalid accesses; disabling it and enabling crash-on-fault can turn recoverable faults into device resets or process failures.
- RAS extraction depends on exact masks and shifts. Wrong MMEA5 EDC count fields can misreport corrected versus uncorrected errors, clear the wrong status, or miss fatal external-agent response errors.
- Error-injection and ECC/EDC controls are dangerous if exposed outside controlled diagnostics. Accidentally enabling injection can create artificial RAS events, poison status counters, or trigger recovery paths.
- Clock-gating and deep-sleep fields can cause intermittent failures if misprogrammed. Timing-sensitive hangs may appear only under idle, suspend/resume, or low-power transitions.
- Cross-generation copying is risky. Similar register names exist in GMC, DCN, later MMHUB, and earlier MMHUB headers, but bit positions and supported fields differ by ASIC generation.

## Test Signals

- Build AMDGPU with MMHUB 1.7 support and warnings enabled. This catches missing or misspelled generated macros used by `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD`.
- Generated-header validation should compare every shift and mask in this line range against the authoritative MMHUB 1.7 register source and verify that corresponding offsets exist in `mmhub_1_7_offset.h`.
- MMHUB 1.7 boot smoke should exercise GART enable, VMID setup, VM L2 cache setup, TLB setup, invalidation programming, and GART disable without VM fault storms, register-access warnings, or GPU reset.
- GPUVM stress should create multiple processes/VMIDs, update and invalidate page tables repeatedly, exercise XNACK/retry-fault behavior, evict and remap buffers, and verify no stale translations after invalidation.
- Fault-policy tests should toggle default-page handling and validate expected behavior for invalid, read, write, execute, dummy-page, PDE, range, and retry/no-retry faults.
- RAS tests should read MMEA5 EDC counters, inject or simulate SEC/DED events where supported, verify corrected/uncorrected counts, verify status warnings for `SDP_RDRSP_STATUS`, `SDP_WRRSP_STATUS`, and data parity, and verify counter/status reset paths.
- Power-management tests should toggle medium-grain clock gating and memory light sleep, then run memory/VM workloads across idle, suspend/resume, and GPU reset to catch ATC/PCTL low-power regressions.
- Perf-counter diagnostics should configure L1, ATC L2, L2TLB, and VM L2 counters, clear/select results, and confirm monotonic or expected event counts under controlled address-translation workloads.
- ECC/EDC and DSM debug validation should confirm injection controls are disabled during normal boot and only enabled in controlled RAS/debug tests, with status bits clearing as documented.
