# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 20297-22799

## Scope

This chunk covers generated shift and mask macros from the AMD GC 12.1.0 register mask header. The range starts in the tail of `RLC_GFX_IH_CLIENT_SE_STAT_H` mask definitions and ends inside the `GFX_IMU_SCRATCH_*` family at `GFX_IMU_SCRATCH_5`. The line boundaries are artificial, so adjacent chunks are required for the complete SE interrupt-client and IMU scratch-register families.

The covered range includes:

- RLC GFX interrupt-handler client status for SDMA, other/FED, UTCL2 22-beat status, and 22-beat arbiter grant status.
- RLC SPM indirect delay and block-enable mask address/data windows.
- RLC LX6 and XT core control/status, firmware status/version, core interrupt/fault/reset-vector, interrupt-vector force/clear/mux selection, doorbell monitor, XT doorbell range/control/status/data, and RLC memory light-sleep/deep-sleep controls.
- RLC safe-mode and command/message paths to RLCV, SMU, SRM/GPM, and IMU bootload state.
- The `CHIP_XCD_gfxip_xcc_gfx_cpwd_cpwd_rlcsdec` address block, including RLC_RLCS exception, fence, clock/deep-sleep, GPM status, bootload, interrupt, scratch/general, auxiliary, bootload-ID, GCR, UTCL2, IMU/RLC message, RAM, SDMA interrupt, memory-power, IH, FED, host-ack, and busy-handshake fields.
- The `CHIP_XCD_gfxip_xcc_gfx_cpwd_cpwd_pfvfdec_rlc` block, including PF/VF-safe RLC, SPM interrupt, CSIB, CP scheduler/EOF/spare interrupt, and VFI register-window fields.
- Power, PSP/security, CP PSP debug, and CH power/clock-gating blocks.
- The beginning of the `CHIP_XCD_gfxip_xcc_gfx_cpwd_gfx_imu_cpwd_gfx_imudec` block, covering `GFX_IMU_C2PMSG_0..47`, message flags, access-control registers, MP1/RLC mutexes, IMU/RLC command/data/status handshakes, SOC request window, VF control, and scratch registers `0..5`.

The chunk contains preprocessor constants only. It has no C functions, structs, variables, allocation, locking, or executable code.

## Purpose

This header section is the bitfield ABI between AMDGPU/KFD driver code and GC 12.1.0 graphics hardware. For each register field it defines the conventional generated names:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit field mask.

Driver code pairs these constants with matching address definitions from `gc_12_1_0_offset.h` and helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET`. The header itself does not describe sequencing, ownership, or reset values; those live in AMDGPU generation-specific code, firmware protocols, default headers, and hardware documentation.

## Important Macro Families

### RLC GFX IH, SPM, and Core-Debug Fields

The opening register families expose RLC-side interrupt-handler and streaming-performance-monitor status:

- `RLC_GFX_IH_CLIENT_SDMA_STAT` packs SDMA0 through SDMA3 buffer level, loading, protocol-error, overflow, and reserved bits into four 8-bit lanes.
- `RLC_GFX_IH_CLIENT_OTHER_STAT` reports UTCL2/PMM reserved state and FED buffer/error state.
- `RLC_GFX_IH_22BEAT_STAT` and `RLC_GFX_IH_ARBITER_STAT_22BEAT` expose UTCL2 22-beat buffer/error state plus current and last IH arbiter grants.
- `RLC_SPM_GLOBAL_DELAY_IND_*`, `RLC_SPM_SE_DELAY_IND_*`, `RLC_SPM_GLOBAL_BLK_EN_MASK_IND_*`, and `RLC_SPM_SE_BLK_EN_MASK_IND_*` are indirect address/data windows for SPM sampling delay and block-enable masks.

The `RLC_LX6_*` and `RLC_XT_*` groups expose firmware/core debug state. They include LX6 reset/runstall/debug enable, two-core busy and interrupt-pending status, full-width firmware status/version, XT wait/fatal/double-exception status, external interrupt and NMI bits, fault info, alternate reset vector, interrupt-vector force/clear bits for vector numbers 0 through 31, and mux selection fields. These are firmware-sensitive debug and control surfaces rather than ordinary queue programming fields.

`RLC_CPAXI_DOORBELL_MON_*` and `RLC_XT_DOORBELL_*` define a monitor and four data-bearing doorbell slots. `RLC_MEM_SLP_CNTL` controls RLC memory light-sleep/deep-sleep enablement, per-subblock overrides, busy override, and on/off delays.

### RLC Firmware, SMU, SRM, and IMU Bootload Handshakes

The chunk defines multiple command/message register layouts:

- `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, and `RLC_SAFE_MODE` share a `CMD`, 4-bit `MESSAGE`, and 4-bit `RESPONSE` layout.
- `RLC_RLCV_COMMAND`, `RLC_SMU_MESSAGE[_1/_2]`, `RLC_SMU_COMMAND`, and `RLC_SMU_ARGUMENT_1..5` provide command and argument payload fields.
- `RLC_SRM_GPM_COMMAND` carries operation, index-control, size, and start-offset fields, while `RLC_SRM_GPM_ABORT` exposes an abort bit.
- `RLC_IMU_BOOTLOAD_ADDR_HI/LO`, `RLC_IMU_BOOTLOAD_SIZE`, `RLC_IMU_MISC`, and `RLC_IMU_RESET_VECTOR` describe the RLC-to-IMU bootload address, size, throttle/early-MGCG options, and reset-vector exit fields.

These fields represent command protocols with hardware/firmware side effects. The masks are only the encoding layer; callers must still respect busy, response, and firmware ownership rules.

### RLC_RLCS Decode Block

The `RLC_RLCS` block is the largest portion of this chunk. It exposes the RLC slave/decode register surface used for firmware load, power management, diagnostics, interrupts, and fault handling.

Key groups include:

- `RLC_RLCS_EXCEPTION_REG_1..4` and `RLC_RLCS_AUXILIARY_REG_1..4`, with 18-bit register address fields.
- `RLC_RLCS_FENCE_CNTL`, `RLC_RLCS_CGCG_REQUEST`, and `RLC_RLCS_CGCG_STATUS`, controlling fence behavior and clock-gating request/status reporting.
- `RLC_RLCS_SOC_DS_CNTL`, `RLC_RLCS_GFX_DS_CNTL`, and `RLC_RLCS_GFX_DS_ALLOW_MASK_CNTL`, which gate deep-sleep allowance against RLC, CP, graphics power, non-3D power, IMU-disable, and SDMA0 through SDMA7 busy signals.
- `RLC_GPM_STAT`, `RLC_RLCS_GPM_STAT`, `RLC_RLCS_ABORTED_PD_SEQUENCE`, `RLC_RLCS_GPM_STAT_2`, `RLC_RLCS_GRBM_SOFT_RESET`, `RLC_RLCS_PG_CHANGE_STATUS`, and `RLC_RLCS_PG_CHANGE_READ`, which report RLC/GPM busy state, power/clock/light-sleep state, save/restore activity, WGP power transitions, aborted power-down, page/change events, and soft-reset state.
- `RLC_RLCS_IOV_CMD_STATUS`, `RLC_RLCS_IOV_CNTX_LOC_SIZE`, `RLC_RLCS_IOV_SCH_BLOCK`, and `RLC_RLCS_IOV_VM_BUSY_STATUS`, exposing SR-IOV command, context, scheduler, and VM-busy state.
- `RLC_RLCS_IH_SEMAPHORE`, `RLC_RLCS_IH_COOKIE_SEMAPHORE`, `RLC_RLCS_CP_INT_*`, `RLC_RLCS_SPM_INT_*`, and `RLC_RLCS_DSM_TRIG`, covering interrupt ownership, auto-ack/pending state, interrupt info payloads, and DSM trigger.
- `RLC_RLCS_BOOTLOAD_STATUS`, with fuse distribution, GFX init, GPM IRAM load/done, and `BOOTLOAD_COMPLETE` bits.
- `RLC_RLCS_GRBM_IDLE_BUSY_STAT`, `RLC_RLCS_GRBM_IDLE_BUSY_INT_CNTL`, and `RLC_RLCS_CMP_IDLE_CNTL`, which report/clear SDMA busy-change signals and compare-idle hysteresis state.
- `RLC_RLCS_GENERAL_0..16`, full-width scratch/data registers.
- `RLC_RLCS_BOOTLOAD_ID_STATUS1/2`, one-bit loaded indicators for bootload IDs 0 through 63.
- `RLC_RLCS_GCR_DATA_0..4` and `RLC_RLCS_GCR_STATUS`, carrying phase data/status.
- `RLC_RLCS_PERFMON_CLK_CNTL_UCODE`, `RLC_RLCS_UTCL2_CNTL`, and the IMU/RLC message data/control/cntl/status fields.
- `RLC_RLCS_IMU_RAM_*` and `RLC_RLCS_IMU_GFX_DOORBELL_FENCE`, exposing indexed IMU RAM address/data windows and doorbell-fence controls.
- `RLC_RLCS_SDMA_INT_CNTL_1/2`, `RLC_RLCS_SDMA_INT_STAT`, and `RLC_RLCS_SDMA_INT_INFO`, covering SDMA interrupt control and diagnostic payloads.
- `RLC_RLCS_GFX_MEM_POWER_CTRL_0..2` and `RLC_RLCS_IH_CTRL_1..3`/`RLC_RLCS_IH_STATUS`, describing graphics memory power control and IH control/status.
- `RLC_RLCS_FED_STATUS`, `RLC_RLCS_FED_RESP`, `RLC_RLCS_FED_INT_MASK`, `RLC_RLCS_MEM_FED`, `RLC_UTCL2_FED_STATUS_SNAP`, `RLC_SE0_FED_STATUS_SNAP`, `RLC_SE1_FED_STATUS_SNAP`, `RLC_CANE_FED_STATUS_SNAP`, `RLC_CONSOLIDATED_FED_STS`, and `RLC_HOST_FED_ACK`, which expose fatal-error-detection status, acknowledgements, masks, memory read/transaction errors, snapshots, consolidated status, and FLR-needed indication.
- `RLC_RLCS_SE_PWR_CTRL`, `RLC_RLCS_SB_RLC_ROM_STATUS`, `RLC_RLCS_SB_ROM_STATUS`, `RLC_RLCS_UTCL2_BUSY_CNTL`, and `RLC_RLCS_UTCL2_BUSY_STAT`, covering shader-engine power/reset control, ROM status, and UTCL2 busy request/ack handshake.

Observed integration in this tree includes `amdgpu/gfx_v12_1.c`, which reads `regRLC_RLCS_BOOTLOAD_STATUS` and checks `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`, and reads `regRLC_RLCS_FED_STATUS` to classify FED errors. Similar bootload polling exists in `gfx_v12_0.c` and older generation code.

### PF/VF RLC, SPM, CSIB, and VFI Fields

The `pfvfdec_rlc` block defines fields visible through the PF/VF RLC decode aperture:

- `RLC_SAFE_MODE` repeats the command/message/response safe-mode pattern.
- `RLC_SPM_SAMPLE_CNT`, `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, `RLC_SPM_INT_STATUS`, and `RLC_SPM_INT_INFO_1/2` expose SPM sample count, memory-client attributes, interrupt enable/status, and interrupt payload/ID.
- `RLC_CSIB_ADDR_LO/HI` and `RLC_CSIB_LENGTH` describe a command/status buffer address and length.
- `RLC_CP_SCHEDULERS`, `RLC_CP_EOF_INT`, and `RLC_CP_EOF_INT_CNTL` expose CP scheduler IDs and EOF interrupt state/control.
- `RLC_SPARE_INT_0..2` and `RLC_RLCV_SPARE_INT_1` provide spare interrupt payload, processing, complete, or interrupt bits.
- `RLC_VFI_CMD`, `RLC_VFI_STAT`, `RLC_VFI_GRBM_GFX_INDEX`, `RLC_VFI_GRBM_GFX_CNTL`, `RLC_VFI_ADDR`, and `RLC_VFI_DATA` are full-width virtual-function interface command/status and indirect register windows.

These definitions are especially sensitive to virtualization context. The same bitfield name may be compiled into PF, VF, or reset/error paths, but valid access depends on the register aperture and firmware policy.

### Power, Security, PSP, and Clock-Gating Fields

The chunk then enters several smaller decode blocks:

- `GRBMX_GLARB_BUSY_MASK` and `CGTT_*_CLK_CTRL` define busy masks, clock on-delay/off-hysteresis, performance/debug enables, soft-stall overrides, and clock override bits for IA, WD, CP, CPF, CPC, RLC, GCR, GC CAC, GRBM, and related CPWD blocks.
- `GFX_ICG_*`, `GC_EA_CPWD_ICG_CTRL`, `CC_GC_HBM_DISABLE`, `GRBMX_LPDDR_DISABLE_0/1`, `GLARBI_GLARBR_MGCG_OVERRIDE`, `ICG_GLARBA_CTRL`, and `ICG_GLARBC_CLK_CTRL` describe internal clock-gating and memory-interface disable/override state.
- `GC_EA_CPWD_SDP_SECLEVEL_NONIO_MAP0..3`, `GC_EA_CPWD_SDP_ERR_CTRL`, `GRBM_SRCID_CAM_*`, `GRBM_IOV_*`, `GRBM_SEC_CNTL`, `GRBM_CAM_*`, `RLC_REG_SEC_INT_STATUS`, `RLC_FWL_FIRST_VIOL_ADDR[_HI]`, and `RLC_UTC_BYPASS_CNTL` define security/trust-level maps, SDP parity/error injection controls, GRBM source-ID and remap CAMs, IOV range controls, firewall violation counters/addresses, and UTC bypass bits for RLC subclients.
- `CP_MES_DM_INDEX_*`, `CP_MEC_DM_INDEX_*`, `CP_GFX_RS64_DM_INDEX_*`, `CPG_PSP_DEBUG`, and `CPC_PSP_DEBUG` expose PSP-side CP data-memory index windows and debug override bits for privilege, GPA, ucode VF, MTYPE/TMZ, and secure-register handling.
- `CHI_CHR_MGCG_OVERRIDE`, `ICG_CHA_CTRL`, and `ICG_CHC_CLK_CTRL` define CH/CHA/CHC medium-grain and internal clock-gating overrides.

These fields connect RLC/GC operation with power management, security isolation, PSP/debug policy, and clock-gating behavior. They should be treated as platform bring-up and recovery controls, not generic debug knobs.

### GFX IMU Mailbox and Handshake Fields

The final portion starts the GFX IMU decode block:

- `GFX_IMU_C2PMSG_0..47` are 48 full-width client-to-platform mailbox payload registers.
- `GFX_IMU_MSG_FLAGS` exposes full-width mailbox/status flags.
- `GFX_IMU_C2PMSG_ACCESS_CTRL0` carries 3-bit access fields for mailboxes 0 through 7; `GFX_IMU_C2PMSG_ACCESS_CTRL1` groups access for mailbox ranges 8-15, 16-23, 24-31, 32-39, and 40-47.
- `GFX_IMU_PWRMGT_IRQ_CTRL` exposes a power-management IRQ request bit, and `GFX_IMU_MP1_MUTEX` exposes a 2-bit MP1 mutex.
- `GFX_IMU_RLC_DATA_0..4`, `GFX_IMU_RLC_CMD`, `GFX_IMU_RLC_MUTEX`, and `GFX_IMU_RLC_MSG_STATUS` define the IMU-to-RLC message data/command/mutex/status path, including busy, error, message-done, change-toggle, and done-toggle bits.
- `RLC_GFX_IMU_DATA_0` and `RLC_GFX_IMU_CMD` are the reverse RLC-to-IMU command path.
- `GFX_IMU_RLC_STATUS` reports power-domain active and RLC-alive state.
- `GFX_IMU_STATUS` reports GFXOFF allowance, FA/DCS allowance, a disable-GFXCLK-DS bit, and several generated TBD fields.
- `GFX_IMU_SOC_DATA`, `GFX_IMU_SOC_ADDR`, and `GFX_IMU_SOC_REQ` define a SOC access request window with busy, read/write, and error bits.
- `GFX_IMU_VF_CTRL` carries VF enable, VFID, and QoS fields.
- `GFX_IMU_SCRATCH_0..5` are full-width scratch/data registers; the family continues in the next chunk.

Direct consumers found in the source tree include `amdgpu/imu_v12_0.c`, `amdgpu/imu_v12_1.c`, and older IMU paths that write `regGFX_IMU_C2PMSG_ACCESS_CTRL0/1`, use `GFX_IMU_C2PMSG_16`, and store/read IMU firmware version data through `GFX_IMU_SCRATCH_*` registers. `amdgpu/gfx_v11_0.c` reads `regGFX_IMU_SCRATCH_0` into `adev->gfx.imu_fw_version`, and the same IMU mailbox/access-control pattern carries into GC 12 code.

## Control Flow and State Behavior

This header has no runtime control flow. Its effect is compile-time: C code uses the generated constants to compose writes and decode reads of 32-bit MMIO registers.

The state described by the chunk is hardware and firmware state. Important state classes include:

- Live RLC/IH buffer levels, loading, protocol-error, overflow, arbiter grant, SDMA busy, FED error, and UTCL2 busy/request/ack status.
- RLC SPM delay, block-enable, memory-client attributes, sample count, interrupt status, and interrupt payload state.
- RLC LX6/XT firmware status, busy/pending state, interrupt vectors, fault info, doorbell data, and memory sleep controls.
- Command/mailbox state for RLCV, SMU, SRM/GPM, RLC/IMU, IMU/SOC, MP1, and PF/VF VFI paths.
- Bootload and firmware-load state, including `RLC_RLCS_BOOTLOAD_STATUS`, `RLC_RLCS_BOOTLOAD_ID_STATUS1/2`, IMU bootload address/size/reset-vector fields, and IMU scratch registers.
- Power, clock-gating, deep-sleep, GFXOFF allowance, memory-power, shader-engine reset/clock, and clock-override state.
- Security and virtualization state, including trust-level maps, GRBM CAM/remap state, IOV ranges, firewall violation counters, VF/VFID/QoS, and PSP debug override bits.

Many fields are sticky status, write-one-clear, strobe, busy/ack, or toggle-protocol bits. Examples include RLC safe-mode command/response, SRM abort, CP/SPM interrupt acknowledge, GRBM idle/busy interrupt clear, DSM trigger, FED acknowledgements, host FED ack, UTCL2 busy ack, IMU/RLC message done/change toggles, and SOC request busy/error. The masks alone do not provide the required polling or timeout sequence.

## Dependencies and Integration Points

This generated header depends on matching GC 12.1.0 register-address and default-value headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` supplies the register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_default.h` supplies reset/default values where generated.
- AMDGPU SOC15 register helpers consume these field masks and shifts through `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related macros.

Observed or implied source-tree integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c` reads `regRLC_RLCS_BOOTLOAD_STATUS` and checks `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`, and reads `regRLC_RLCS_FED_STATUS` for FED error classification.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c` has analogous RLC bootload polling through `regRLC_RLCS_BOOTLOAD_STATUS`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.c` and `imu_v12_1.c` configure IMU mailbox access and firmware/RLC RAM flows using the same IMU register families that begin here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/*` maps `GFX_IMU` as an SMU feature on relevant platforms, making the IMU status/mailbox and power-management request fields part of the larger power-management contract.
- Debug, reset, SR-IOV, and fatal-error-recovery paths use the RLC_RLCS, FED, VFI, GRBM security, and firewall fields to diagnose hangs, acknowledge errors, or coordinate FLR/recovery.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write adjacent hardware control bits, causing firmware boot failure, GPU hangs, missed interrupts, bad power-state transitions, or broken security isolation.
- This chunk crosses many address blocks. Reusing similar names across RLC, RLC_RLCS, PF/VF RLC, PSP, and IMU contexts without the matching `reg...` offset can target the wrong aperture.
- Several fields are command or handshake bits, not durable configuration. Misusing safe-mode commands, SRM/GPM commands, interrupt acknowledgements, FED acks, IMU/RLC toggles, or SOC request busy bits can race firmware or leave hardware waiting for an acknowledgement.
- RLC_RLCS bootload and bootload-ID fields are bring-up critical. Incorrect interpretation of `BOOTLOAD_COMPLETE`, IRAM load/done, or ID-loaded bits can create false successful initialization or spurious timeout failures.
- Power and clock-gating fields must remain coordinated with SMU, RLC firmware, and reset paths. Forcing CGTT/ICG/MGCG overrides, deep-sleep allowances, memory power controls, or GFXCLK DS disable bits outside established sequencing can cause intermittent hangs or excess power draw.
- FED and firewall/security fields are recovery and isolation sensitive. Incorrect masks can hide fatal errors, acknowledge the wrong source, misreport FLR-needed state, or weaken GRBM/SDP/firewall protection.
- IMU mailbox and scratch registers are firmware protocol surfaces. Access-control, mutex, status-toggle, and scratch-field misuse can desynchronize IMU firmware startup or power-management messages.
- The chunk starts and ends mid-family. Final file-level research must merge adjacent chunks before making complete claims about `RLC_GFX_IH_CLIENT_SE_STAT_H` and `GFX_IMU_SCRATCH_*`.

## Test and Validation Signals

Useful validation is mostly build, bring-up, reset, and hardware-integration coverage:

- Build AMDGPU, KFD, and SMU code paths that include `gc/gc_12_1_0_sh_mask.h`; this catches missing or renamed macros.
- GFX 12.1 boot tests should reach `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE` without timeout and should report sane `RLC_RLCS_BOOTLOAD_ID_STATUS1/2` values after firmware load.
- RLC/FED recovery tests should exercise `RLC_RLCS_FED_STATUS`, `RLC_RLCS_FED_RESP`, `RLC_RLCS_FED_INT_MASK`, `RLC_CONSOLIDATED_FED_STS`, and `RLC_HOST_FED_ACK`, including SDMA, CP, UTCL2, SE, CANE, and AID sources.
- Interrupt validation should cover CP/SPM interrupt pending/ack/info fields, SDMA interrupt status/info, IH status/control, and RLC GFX IH client buffer overflow/protocol-error reporting.
- Power-management and suspend/resume tests should cover CGTT/ICG clock overrides, RLC memory sleep controls, SOC/GFX deep-sleep allow masks, GFXOFF/FA-DCS allowance, and IMU power-management IRQ behavior.
- IMU firmware tests should validate mailbox access-control programming, `GFX_IMU_C2PMSG_*` exchanges, RLC/IMU command/data/status toggles, MP1/RLC mutex behavior, SOC request busy/error handling, and scratch register version reporting.
- SR-IOV and FLR tests should cover PF/VF safe-mode/VFI windows, VF control fields, GRBM IOV ranges, firewall violation reporting, and `NEED_TO_APPLY_FLR` propagation.
- Register dumps from hung or recovered systems should include the RLC_RLCS bootload, GPM, GRBM idle/busy, FED, memory-power, UTCL2 busy, IMU/RLC status, and security/firewall registers with values that match expected field boundaries.

## Chunk Notes

This document covers only `subset-b-002600`, lines 20297-22799 of `gc_12_1_0_sh_mask.h`. It deliberately does not create a final per-file report; the merge/reconciliation lane should combine this with adjacent chunk documents to complete the generated GC 12.1.0 register map analysis.
