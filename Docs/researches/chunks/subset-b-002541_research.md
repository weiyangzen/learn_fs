# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 37499-39973

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for 32-bit register packing and decoding. There are no functions, structs, enums, global variables, includes, allocations, locks, callbacks, loops, or branches in this range.

The selected lines cover a large RLC and RLCS register-map span. The range begins in the tail of `RLC_CLK_COUNT_REFCLK_MSB` and then defines fields for RLC clock counters, multiple RLC doorbell endpoints, graphics power gating, clock gating, GPM/SRM control, UTCL1 fault/status reporting, shader profiler/SPP state, residency counters, graphics interrupt-handler client status, RLC Xtensa-style control/interrupt vectors, CPAXI doorbell monitoring, SMU/RLC command mailboxes, IMU bootload controls, and the start of the `gc_rlcsdec` address block. It ends at the first shift macro for `RLC_RLCS_GPM_LEGACY_INT_DISABLE`; that register's masks continue in the adjacent following chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 11.0.3 graphics IP block and is not Ceph filesystem logic.

## Purpose

`gc_11_0_3_sh_mask.h` supplies bit layouts for GC 11.0.3 registers. AMDGPU code pairs these field definitions with register address macros from the companion `gc_11_0_3_offset.h` header, then uses helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to manipulate MMIO registers without hard-coded bit positions.

This chunk's purpose is to describe the RLC control-plane surface:

- RLC clock measurement and capture fields for GFXCLK, REFCLK, GPU clock counters, SPM clock counters, and capture-valid/status bits.
- Doorbell range/control/status/data windows for several RLC clients: `RLC_RLCG`, `RLC_RLCV`, `RLC_RLCP`, and `RLC_XT`, plus CPAXI doorbell monitor control/status/data fields.
- Graphics power-gating, clock-gating, light-sleep/deep-sleep, WGP power status, dynamic/static WGP power-gating masks, per-WGP limits, power-brake controls, memory sleep, and residency counters.
- GPM and SRM command/control surfaces, including thread priorities/enables, GPM general scratch registers, SRM index-control address/data slots, SRM command status, SRM GPM command/abort fields, and RLC save/restore helper registers.
- UTCL1 translation control and diagnostics for GPM threads and SPM, including XNACK redo timers, drop/bypass/invalidate/fragment-limit/force-snoop controls, busy/stall indicators, translated request error VMID, and split error addresses.
- RLC shader profiling/SPP fields for profile enablement, SSF capture, thresholds, inflight reads, global shader ID selection, private counters, PBB override information, CAM access, and SPP reset/stall/status.
- RLC interrupt and fault monitoring, including FED status, graphics IH client buffers, PACE interrupts, legacy GPM interrupts, CP status invalidation, firewall violation, FED/EDC event clears, and GRBM idle/busy interrupt control.
- RLC firmware/embedded-controller handshakes, including SMU safe-mode mailboxes, RLCV command, SMU messages/arguments, IMU bootload address/size/misc/reset-vector fields, bootload status, bootload ID status bitmaps, and IMU voltage-change controls.
- The RLCS decoder block for exception/auxiliary register addresses, clock/deep-sleep controls, GPM state, aborted power-down sequence reporting, IOV command/status fields, WGP reads, CP/SPM interrupt information, DSM trigger, GRBM soft reset, and KMD log scratch fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register addresses live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` with names such as `regRLC_PG_CNTL`, `regRLC_RLCG_DOORBELL_CNTL`, `regRLC_SMU_SAFE_MODE`, `regRLC_IMU_MISC`, `regRLC_RLCS_GPM_STAT`, and `regRLC_RLCS_GRBM_SOFT_RESET`.

Major macro families in this slice are:

- Clock and residency: `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, `RLC_GPU_CLOCK_32`, `RLC_CAPTURE_GPU_CLOCK_COUNT_*`, `RLC_GPU_CLOCK_COUNT_*`, `RLC_GPU_CLOCK_COUNT_SPM_*`, and `RLC_*_RESIDENCY_{CNTR_CTRL,EVENT_CNTR,REF_CNTR}`. Control fields include run/reset/sample, enable/reset/ack/overflow, event select for PCC, and full-width event/reference counter data.
- Power and clock gating: `RLC_PG_CNTL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_CGCG_CGLS_CTRL_3D`, `RLC_CGCG_RAMP_CTRL_3D`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_PG_DELAY`, `RLC_PG_DELAY_3`, `RLC_WGP_STATUS`, `RLC_PG_ALWAYS_ON_WGP_MASK`, `RLC_MAX_PG_WGP`, `RLC_AUTO_PG_CTRL`, `RLC_STATIC_PG_STATUS`, `RLC_MEM_SLP_CNTL`, `RLC_RLCS_SOC_DS_CNTL`, `RLC_RLCS_GFX_DS_CNTL`, `RLC_RLCS_GFX_DS_ALLOW_MASK_CNTL`, `RLC_RLCS_POWER_BRAKE_CNTL`, and `RLC_RLCS_POWER_BRAKE_CNTL_TH1`.
- Doorbells and monitoring: `RLC_RLCG_DOORBELL_*`, `RLC_RLCV_DOORBELL_*`, `RLC_RLCP_DOORBELL_*`, `RLC_XT_DOORBELL_*`, and `RLC_CPAXI_DOORBELL_MON_*`. These expose lower/upper range fields, per-doorbell modes, doorbell ID and ID enable bits, per-doorbell valid bits, and low/high captured data words.
- GPM/SRM and scratch state: `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, `RLC_GPM_GENERAL_0..16`, `RLC_GPM_INT_DISABLE_TH0`, `RLC_GPM_INT_FORCE_TH0`, `RLC_GPM_INT_STAT_TH0`, `RLC_GPR_REG1/2`, `RLC_SRM_CNTL`, `RLC_SRM_GPM_COMMAND_STATUS`, `RLC_SRM_INDEX_CNTL_ADDR_0..7`, `RLC_SRM_INDEX_CNTL_DATA_0..7`, `RLC_SRM_STAT`, `RLC_SRM_GPM_COMMAND`, and `RLC_SRM_GPM_ABORT`.
- UTCL1 and translation errors: `RLC_GPM_UTCL1_CNTL_0..2`, `RLC_SPM_UTCL1_CNTL`, `RLC_UTCL1_STATUS`, `RLC_UTCL1_STATUS_2`, `RLC_SPM_UTCL1_ERROR_1/2`, and `RLC_GPM_UTCL1_TH0/TH1/TH2_ERROR_1/2`. These cover XNACK retry tuning, cache/TLB invalidation-style controls, fault/retry/PRT identifiers, busy/stall indicators, translated request error classes, VMID, and address fragments.
- SPP and profiling: `RLC_SPP_CTRL`, `RLC_SPP_SHADER_PROFILE_EN`, `RLC_SPP_SSF_CAPTURE_EN`, `RLC_SPP_SSF_THRESHOLD_*`, `RLC_SPP_INFLIGHT_RD_*`, `RLC_SPP_PROF_INFO_*`, `RLC_SPP_GLOBAL_SH_ID`, `RLC_SPP_GLOBAL_SH_ID_VALID`, `RLC_SPP_STATUS`, `RLC_SPP_PVT_STAT_*`, `RLC_SPP_PVT_LEVEL_MAX`, `RLC_SPP_STALL_STATE_UPDATE`, `RLC_SPP_PBB_INFO`, `RLC_SPP_RESET`, `RLC_SPP_CAM_*`, and `RLC_SPP_CAM_EXT_*`.
- Interrupt/fault/status: `RLC_RLCS_FED_STATUS_0/1`, `RLC_PACE_INT_STAT`, `RLC_PACE_INT_DISABLE`, `RLC_FIREWALL_VIOLATION`, `RLC_CP_STAT_INVAL_STAT`, `RLC_CP_STAT_INVAL_CTRL`, `RLC_GFX_IH_CLIENT_CTRL`, `RLC_GFX_IH_ARBITER_STAT`, `RLC_GFX_IH_CLIENT_SE_STAT_L/H`, `RLC_GFX_IH_CLIENT_SDMA_STAT`, `RLC_GFX_IH_CLIENT_OTHER_STAT`, `RLC_RLCS_IH_SEMAPHORE`, `RLC_RLCS_IH_COOKIE_SEMAPHORE`, `RLC_RLCS_CP_INT_CTRL_*`, `RLC_RLCS_CP_INT_INFO_*`, `RLC_RLCS_SPM_INT_CTRL`, `RLC_RLCS_SPM_INT_INFO_*`, `RLC_RLCS_EDC_INT_CNTL`, and `RLC_RLCS_GPM_LEGACY_INT_STAT`.
- Firmware, IMU, and RLCS decoder: `SMU_RLC_RESPONSE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_SMU_MESSAGE*`, `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_1..5`, `RLC_IMU_BOOTLOAD_ADDR_HI/LO`, `RLC_IMU_BOOTLOAD_SIZE`, `RLC_IMU_MISC`, `RLC_IMU_RESET_VECTOR`, `RLC_RLCS_EXCEPTION_REG_1..4`, `RLC_RLCS_CGCG_REQUEST/STATUS`, `RLC_GPM_STAT`, `RLC_RLCS_GPM_STAT`, `RLC_RLCS_ABORTED_PD_SEQUENCE`, `RLC_RLCS_DIDT_FORCE_STALL`, `RLC_RLCS_IOV_*`, `RLC_RLCS_WGP_*`, `RLC_RLCS_GRBM_*`, `RLC_RLCS_BOOTLOAD_STATUS`, `RLC_RLCS_BOOTLOAD_ID_STATUS1/2`, `RLC_RLCS_IMU_VIDCHG_CNTL`, `RLC_RLCS_KMD_LOG_CNTL1/2`, and related auxiliary registers.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.0.3 register headers for the active ASIC generation.
2. Use a matching register address macro from `gc_11_0_3_offset.h`.
3. Read an existing register value, prepare a write value, or decode a debug/status snapshot.
4. Use the `__SHIFT` and `__MASK` pairs, normally through register field helpers, to set or extract a field.
5. Issue the MMIO read/write or consume the decoded result in RLC bring-up, power management, firmware boot, doorbell setup, hang recovery, perf/debug plumbing, or virtualization/error handling.

For power-management flows, driver code reads or updates fields such as `RLC_PG_CNTL__GFX_POWER_GATING_ENABLE_MASK`, `RLC_PG_CNTL__SMU_HANDSHAKE_DISABLE_MASK`, `RLC_MEM_SLP_CNTL__RLC_MEM_LS_EN_MASK`, residency counter enables, and RLC/RLCS GPM status bits while enabling/disabling RLC-managed power features or waiting for power transitions. For boot flows, driver code polls `RLC_RLCS_BOOTLOAD_STATUS` fields such as bootload completion and uses IMU address/size/reset-vector fields around firmware loading. For interrupt and fault flows, code snapshots FED/IH/UTCL1/firewall/GRBM/CP/SPM fields and may write clear or disable masks. The header does not encode required sequencing, timeouts, posting reads, clear-on-write behavior, or reset delays.

## State And Persistence Behavior

The macros are stateless and persist nothing. They describe state owned by GPU hardware, firmware, and AMDGPU's runtime register programming.

RLC power-control fields are persistent hardware configuration until overwritten, reset, or lost through a relevant power state. `RLC_PG_CNTL`, clock-gating controls, WGP masks, memory sleep controls, deep-sleep allow masks, and power-brake controls directly affect whether graphics blocks can be power-gated, clock-gated, slowed down, or held active. Incorrect values can leave the graphics engine powered when it should idle, gate clocks while work is active, or block the SMU/RLC handshake path.

Doorbell range/control/data registers define live notification routing for multiple RLC clients. Range fields use aligned lower/upper address fragments, while control fields select per-doorbell modes and optional doorbell IDs. Captured data registers and valid bits are diagnostic state that can remain latched until cleared or overwritten by hardware. Misprogrammed ranges or IDs can route notifications to the wrong RLC client or make firmware appear unresponsive.

GPM/SRM general registers, KMD log controls, scratch-style data fields, auxiliary register address fields, SRM index-control slots, and R2I controls are generic RLC-owned state. Some are used by firmware command engines, profiling support, diagnostics, or save/restore paths. Because they are full-width or address-like fields, preserving ownership boundaries matters: host code should not assume unused-looking scratch registers are free unless the RLC firmware interface documents them.

UTCL1 status and error registers represent live or sticky memory-translation events for SPM and GPM threads. Fault, retry, PRT, VMID, UTCL1 ID, and translated address fragments are diagnostic state used to attribute translation failures. These fields may be volatile during ongoing traffic and may require a documented clear sequence outside this header.

SPP/profiling registers maintain profiler mode, selected shader IDs, thresholds, capture enablement, private level counters, CAM access, and reset/stall state. These settings can perturb profiling or debug collection if left configured across suspend/resume, GPU reset, or context transitions.

Residency counters and GPU clock counters accumulate event/reference data while enabled. Their reset/enable acknowledgements and overflow bits indicate hardware state transitions. The header cannot express counter latching or atomic high/low read requirements, so consumers must follow the hardware programming sequence when sampling.

Firmware and IMU registers are high-risk state. Bootload address/size, reset vector, safe-mode commands, SMU command/argument mailboxes, bootload status, bootload ID status, and voltage-change request/ack bits participate in firmware control and power/voltage transitions. Stale or malformed values can hang RLC boot, wedge SMU communication, or report the wrong firmware-load state.

Reserved fields appear throughout this generated map. Runtime read-modify-write code should preserve reserved bits unless the hardware sequence explicitly requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register family remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies the matching `reg...` addresses and base indices for the fields defined here.
- AMDGPU register helpers and SOC15 accessors provide the actual field packing/extraction and MMIO access.
- `drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c` and neighboring generation files use the same RLC field families for RLC power gating, SMU handshake disablement, bootload polling, memory sleep, and graphics bring-up/teardown flows.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.h` defines RLC firmware-related identifiers, including SPP/CAM firmware ID concepts that correspond to profiler and RLC firmware state exposed in this chunk.
- Power-management, reset, suspend/resume, GPU hang recovery, debugfs/register-dump, RAS/fault reporting, SR-IOV/IOV handling, KFD/compute interaction, and shader profiling paths all integrate with this register surface.

Practical integration points include enabling/disabling RLC-managed GFX power gating, configuring SMU handshake behavior, validating RLC bootload completion, programming RLC memory sleep, collecting residency statistics, routing and validating RLC doorbells, reporting UTCL1 translation faults, using SPP profiling controls, clearing graphics IH/RLC legacy interrupts, commanding SRM/GPM save/restore operations, and decoding RLCS GRBM idle/busy or soft-reset state during reset recovery.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bit or decode misleading power/fault state.
- This chunk starts and ends mid-family. It begins after the `RLC_CLK_COUNT_REFCLK_MSB` register comment and ends before the masks for `RLC_RLCS_GPM_LEGACY_INT_DISABLE`; final file-level research must merge adjacent chunks for those partial families.
- Many register families are structurally repeated: RLCG/RLCV/RLCP/XT doorbells, GPM UTCL1 thread controls/errors, residency counter controls, graphics IH client status per SE/SDMA group, and bootload ID bitmaps. Single-bit generator mistakes in one repeated family can create client-specific failures that are hard to spot.
- Address and range fields often omit alignment bits or split addresses across low/high registers. Treating masked fields as raw byte addresses can program plausible but wrong doorbell ranges, IMU bootload locations, exception/auxiliary addresses, or UTCL1 error addresses.
- RLC power-gating and clock-gating fields have side effects. Incorrect `RLC_PG_CNTL`, deep-sleep allow masks, WGP power masks, memory sleep controls, or power-brake fields can cause GPU hangs, missed idle transitions, high idle power, or failed resume.
- Doorbell control and CPAXI monitor fields affect live notification paths. Misdecoded doorbell IDs, modes, or match-clear behavior can make firmware commands look lost or can clear diagnostic evidence too early.
- Interrupt and fault status fields may be sticky or write-one-to-clear depending on the register. The shift/mask header cannot express clear semantics, so blindly writing masks can drop evidence or fail to clear an interrupt.
- UTCL1 and FED status fields are high-value diagnostics for memory and fabric failures. Misattributing VMID, UTCL1 ID, SDMA/FED source, or translated address bits can send debugging toward the wrong process or engine.
- Firmware/IMU mailboxes are sequencing-sensitive. Polling the wrong bootload bit, using the wrong size mask, or writing safe-mode/voltage-change fields without the expected handshake can wedge firmware bring-up.
- Counter sampling is race-prone. GPU clock and residency high/low or event/reference counters need hardware-defined latching behavior; masks alone do not make reads atomic.
- Reserved fields are large in several registers. Full-register writes that do not preserve reserved bits can change undocumented ASIC or firmware behavior.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware/runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_11_0_3_sh_mask.h`, especially GC 11 RLC, GFX, power-management, reset, debug, profiling, and firmware paths.
- Mechanical comparison against AMD's authoritative GC 11.0.3 register database to verify every `__SHIFT` and `__MASK` value in lines 37499-39973.
- Cross-check that every complete register family in this chunk has a matching address macro in `gc_11_0_3_offset.h`; note that a `gc_11_0_3_default.h` file was not present in this checkout.
- Static shift/mask sanity checks: masks align with shifts, full-width data fields use `0xFFFFFFFFL`, repeated doorbell/residency/UTCL1/IH families remain structurally consistent, and reserved masks cover the intended unused bits without overlapping named fields.
- RLC boot tests that load firmware and poll `RLC_RLCS_BOOTLOAD_STATUS`, `RLC_RLCS_BOOTLOAD_ID_STATUS1/2`, IMU bootload address/size, and reset-vector fields without timeout.
- Power-management tests that enable and disable GFX power gating, memory light sleep/deep sleep, SMU handshake behavior, clock-gating ramps, WGP power transitions, power-brake events, and residency counters across suspend/resume and GPU reset.
- Doorbell tests that validate RLCG/RLCV/RLCP/XT doorbell range, ID, valid, and captured-data fields under firmware command traffic and CPAXI monitor match/clear scenarios.
- Fault-injection or stress tests that trigger UTCL1 translated request errors, FED errors, firewall violations, graphics IH buffer overflow/protocol errors, CP/SPM interrupts, and GRBM idle/busy interrupt paths, then confirm decoded VMID/source/address/status fields are coherent.
- Shader profiling/SPP tests that toggle profile enablement, shader ID selection, SSF capture thresholds, CAM access, PVT counters, stall-state update, and reset fields while verifying expected profiler output.
- Hang/debug dump tests that collect RLC GPM/RLCS GPM status, GRBM idle/busy state, soft reset fields, CP invalidation status, KMD logs, and legacy interrupts during known idle, busy, reset, and fault conditions.
- Runtime warning signals include RLC boot timeouts, failed SMU safe-mode handshakes, GPU reset loops, high idle power, doorbell command loss, stuck residency counters, incorrect IH/fault attribution, impossible GPM status combinations, failed memory sleep restore, or shader profiling data that remains stale after reset.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002541`. It covers lines 37499-39973 of `gc_11_0_3_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial clock-count and `RLC_RLCS_GPM_LEGACY_INT_DISABLE` families and to place these RLC/RLCS definitions in the full GC 11.0.3 register map.
