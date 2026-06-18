# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 30087-32527

## Scope

This chunk is a generated AMD GC 11.5.0 register shift/mask header segment. It contains C preprocessor constants only: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions for 32-bit graphics-core hardware registers. There are no functions, structs, enums, variables, callbacks, allocations, locks, or executable branches in the selected range.

The requested slice contains 2,164 `#define` entries: 1,090 shift definitions and 1,074 mask definitions across 268 visible register groups. The count mismatch is caused by chunk boundaries. The first requested line starts at the tail of `RLC_CGCG_RAMP_CTRL` with only mask definitions; the corresponding shift definitions are immediately before this chunk. The last requested line stops inside `GFX_ICG_GL2A_CTRL` after `CLIENT14_OVERRIDE__SHIFT`, before the remaining shift and mask entries for that register.

Although the repository path is under `ceph-client`, this source is AMDGPU DRM graphics hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_11_5_0_sh_mask.h` supplies symbolic bit layouts for GC 11.5.0 registers. Consumers pair these macros with register offsets from `gc_11_5_0_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15` to compose or decode register values.

This chunk is centered on RLC control/status and graphics power-control metadata:

- RLC clock-gating and power-gating controls: CGCG ramp masks at the boundary, dynamic/static WGP power-gating status/request registers, delay controls, always-on WGP mask, max powered-up WGP count, auto power-gating thresholds, and RLC memory light/deep-sleep controls.
- RLC SerDes and GPM/SRM access: SerDes read indices/data, target/busy masks for center hubs and shader engines, GPM general-purpose registers, GPR scratch registers, SRM command/status/index/data windows, SRM GPM command/abort controls, and save/restore copy command fields.
- RLC interrupt, error, and status groups: GPM interrupt disable/force/status, legacy interrupt disable bits, pace timer interrupt/status/disable/control, CP stat invalidation status/control, SPM/UTCL1/GPM UTCL1 status and error fields, R2I controls, GPM status, safe-mode status, and spare interrupt fields.
- RLC profiling and performance blocks: shader performance profiling (`RLC_SPP_*`) controls, shader-profile enable masks for shader engines and wave slots, SSF capture and thresholds, inflight readback, profile info, global shader IDs, PVT statistics, CAM access registers, SPM sample and MC/int controls, and SPM delay indirect address/data windows.
- RLC doorbells and embedded-controller interfaces: RLCP and XT doorbell ranges/control/status/data, CPAXI doorbell monitor fields, LX6/XT core status/interrupt/fault/reset-vector fields, XT interrupt vector force/clear/mux controls, and SMU/RLC command, response, argument, and safe-mode message registers.
- IMU boot and power-state metadata: IMU bootload address/size, throttle/early MGCG controls, and reset-vector bits for cold boot, VDDGFX, fast GFXOFF, and full GFXOFF exits.
- GC power decoder clock-gating controls: TCC disable masks and many CGTT/ICG override registers for SPI, PC, BCI, VGT, IA, WD, GS/NGG, PA, SC, SQ, SQG, ALU/TEX/LDS/SQ clocks, SP, SX, TA, TD, GDS, DB, CB, and the beginning of GL2A.

## Important APIs, Types, And Macros

There are no callable APIs or local C types. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- Matching offsets live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`.

Important register families in this chunk include:

- `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_WGP_STATUS`, `RLC_PG_ALWAYS_ON_WGP_MASK`, `RLC_MAX_PG_WGP`, `RLC_PG_DELAY`, `RLC_PG_DELAY_3`, and `RLC_AUTO_PG_CTRL`: WGP-level power gating, idle thresholds, propagation delays, memory sleep delay, and auto wake/save behavior.
- `RLC_SERDES_RD_INDEX`, `RLC_SERDES_RD_DATA_0..3`, `RLC_SERDES_MASK`, `RLC_SERDES_CTRL`, `RLC_SERDES_DATA`, and `RLC_SERDES_BUSY`: RLC SerDes read/write routing, broadcast, register address, target mask, read FIFO, and pending/busy indicators.
- `RLC_GPM_GENERAL_0..16`, `RLC_GPR_REG1`, `RLC_GPR_REG2`, `RLC_SRM_CNTL`, `RLC_SRM_GPM_COMMAND_STATUS`, `RLC_SRM_INDEX_CNTL_ADDR_0..7`, `RLC_SRM_INDEX_CNTL_DATA_0..7`, `RLC_SRM_STAT`, `RLC_SRM_GPM_COMMAND`, and `RLC_SRM_GPM_ABORT`: general-purpose mailboxes and SRM/GPM save-restore machinery.
- `RLC_GPM_UTCL1_CNTL_0`, `RLC_GPM_UTCL1_CNTL_1`, `RLC_SPM_UTCL1_CNTL`, `RLC_UTCL1_STATUS`, `RLC_UTCL1_STATUS_2`, `RLC_SPM_UTCL1_ERROR_*`, and `RLC_GPM_UTCL1_TH*_ERROR_*`: UTCL1 control, hit/miss/status, request, miss FIFO, translation, and fault/error information for RLC GPM/SPM paths.
- `RLC_CGCG_CGLS_CTRL_3D`, `RLC_CGCG_RAMP_CTRL_3D`, `RLC_MEM_SLP_CNTL`, `RLC_POWER_RESIDENCY_*`, `RLC_CLK_RESIDENCY_*`, `RLC_DS_RESIDENCY_*`, `RLC_ULV_RESIDENCY_*`, `RLC_PCC_RESIDENCY_*`, and `RLC_GENERAL_RESIDENCY_*`: clock gating, light sleep, deep sleep, residency event counters, reference counters, selector masks, enable bits, and counter-control fields.
- `RLC_PACE_INT_STAT`, `RLC_PACE_INT_DISABLE`, `RLC_PACE_TIMER_INT_0`, `RLC_PACE_TIMER_INT_1`, and `RLC_PACE_TIMER_CTRL`: RLC pacing interrupt flags, masking, timer periods, delayed-error fields, and timer enable/state.
- `RLC_SPP_CTRL`, `RLC_SPP_SHADER_PROFILE_EN`, `RLC_SPP_SSF_CAPTURE_EN`, `RLC_SPP_SSF_THRESHOLD_*`, `RLC_SPP_INFLIGHT_RD_*`, `RLC_SPP_PROF_INFO_*`, `RLC_SPP_GLOBAL_SH_ID*`, `RLC_SPP_STATUS`, `RLC_SPP_PVT_STAT_*`, `RLC_SPP_PVT_LEVEL_MAX`, `RLC_SPP_STALL_STATE_UPDATE`, `RLC_SPP_PBB_INFO`, `RLC_SPP_RESET`, `RLC_SPP_CAM_*`, and `RLC_SPP_CAM_EXT_*`: shader profiling, power profiling, scan/filter capture, private statistics, CAM windows, reset, and stall-update controls.
- `RLC_RLCP_DOORBELL_*`, `RLC_XT_DOORBELL_*`, and `RLC_CPAXI_DOORBELL_MON_*`: doorbell range sizing, enable/offset fields, source pointer selection, hit status, data readback, and CPAXI monitoring.
- `RLC_XT_CORE_STATUS`, `RLC_XT_CORE_INTERRUPT`, `RLC_XT_CORE_FAULT_INFO`, `RLC_XT_CORE_ALT_RESET_VEC`, `RLC_XT_INT_VEC_FORCE`, `RLC_XT_INT_VEC_CLEAR`, `RLC_XT_INT_VEC_MUX_SEL`, and `RLC_XT_INT_VEC_MUX_INT_SEL`: embedded XT/LX6 controller status, interrupt, fault, reset-vector, and interrupt-vector routing fields.
- `SMU_RLC_RESPONSE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_SMU_MESSAGE*`, `RLC_SMU_COMMAND`, and `RLC_SMU_ARGUMENT_1..5`: command/response and safe-mode interfaces between RLC, RLCV, and SMU firmware-controlled paths.
- `RLC_IMU_BOOTLOAD_ADDR_*`, `RLC_IMU_BOOTLOAD_SIZE`, `RLC_IMU_MISC`, and `RLC_IMU_RESET_VECTOR`: IMU firmware bootload address/size and reset-vector metadata.
- `CGTS_TCC_DISABLE`, `GFX_ICG_*`, `CGTT_*`, `SQ_*_CLK_CTRL`, `ICG_*`, `TA_CGTT_CTRL`, `DB_CGTT_CLK_CTRL_0`, and `GFX_ICG_CB_CTRL`: per-block clock gating, soft-stall/soft-override, register override, off-hysteresis, on-delay, perf-enable, and group override definitions.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. GC 11.5.0 code includes `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h`.
2. The caller chooses a register offset, usually through a `reg*` macro and SOC15 helper.
3. The caller builds or decodes a `u32` register value using `REG_SET_FIELD`, `REG_GET_FIELD`, direct masks, or direct shifts.
4. Ordered MMIO access, polling, firmware messaging, reset sequencing, and power-domain ownership are handled outside this header.

In this tree, the observed direct GC 11.5.0 include user is `drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which uses this generated namespace for VM hub setup and fault-status decoding. The RLC and clock-gating register names in this chunk also match broader AMDGPU GFX 11 patterns used by generic `gfx_v11_0.c` and newer GFX code: safe-mode entry/exit writes use `RLC_SAFE_MODE`-style `CMD` and `MESSAGE` fields, SPM VMID setup uses `RLC_SPM_MC_CNTL` fields, and clock-gating setup toggles RLC/CGTT/MGCG override fields around power-management transitions. Those generic files do not directly include this GC 11.5.0 header, but they show the intended semantic use of this register class.

The generated masks do not encode legal ordering, polling delays, write-one-to-clear semantics, self-clearing requests, read-only status, firmware-owned registers, SR-IOV restrictions, or power-domain accessibility. Those rules must come from the consuming code and hardware programming guide.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names hardware-visible state whose lifetime is controlled by the GPU, firmware, reset domains, power gating, and driver reinitialization.

Represented state includes:

- WGP power-gating state, request masks, always-on masks, maximum powered WGP count, auto power-gating thresholds, and RLC memory light/deep-sleep state.
- RLC SerDes routing and busy/read-pending state across center hubs and shader-engine targets.
- RLC GPM/SRM scratch, command, FIFO, auto-increment, and copy state used for register save/restore and firmware-managed data movement.
- RLC interrupt masks, forced interrupts, pace timers, spare interrupts, CP stat invalidation state, and interrupt-handler client status.
- UTCL1 status and fault/error state for GPM/SPM accesses, including request counters, miss FIFO status, fault IDs, and client/status flags.
- SPM/SPP profiling state, including enabled shader-engine/wave masks, sample counters, capture thresholds, inflight readback state, profile info, CAM data windows, and PVT statistics.
- Doorbell range, enable, offset, source, hit, and data state for RLCP and XT interfaces, plus CPAXI doorbell monitor readback.
- RLC/SMU/RLCV command and response mailboxes, safe-mode request/response bits, IMU bootload metadata, and IMU reset-vector bits used across boot and low-power exits.
- Power/clock-gating overrides for graphics pipeline blocks. Many fields named `SOFT_OVERRIDE`, `SOFT_STALL_OVERRIDE`, `GRP_OVERRIDES`, `REG_OVERRIDE`, `ON_DELAY`, and `OFF_HYSTERESIS` affect whether block-level clocks can gate, when gating occurs, and whether perf/debug logic forces clocks on.

Some registers are configuration that persists until reset or reprogramming; others are live status, counters, command triggers, firmware mailboxes, or sticky error/interrupt state. The macro names alone do not identify volatility or side effects. Reserved and `UNUSED` fields should be preserved on read-modify-write unless an ASIC programming table explicitly owns the full register value.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies matching register offsets and address-block placement. The shift/mask header must stay synchronized with that offset header and AMD's authoritative GC 11.5.0 register database.

Observed direct include user:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`

Semantic integration points for this chunk include:

- RLC firmware and microcontroller bring-up, including RLC/SMU/RLCV messaging, safe-mode transitions, IMU bootload state, and GFXOFF or VDDGFX exit handling.
- Runtime power management, clock gating, clock-stop controls, memory light/deep sleep, power residency counters, and block-specific clock-gating overrides.
- GPU reset, suspend/resume, and recovery paths that need to reinitialize RLC-managed state, doorbell ranges, safe-mode state, SPM/SPP profiling controls, and clock-gating overrides.
- Profiling and diagnostics through RLC SPM/SPP counters, shader-profile enable masks, PVT statistics, CAM windows, residency counters, GFX IH client status, and UTCL1 error/status registers.
- Firmware or low-level driver paths that use SRM/GPM register save/restore windows and GPM general-purpose mailboxes.
- Doorbell, CPAXI, and embedded-controller interrupt routing between host, RLC, RLCP, XT/LX6 controller logic, and SMU-owned firmware flows.
- Common AMDGPU register helper infrastructure for SOC15 addressing and field packing/unpacking.

Mixing this GC 11.5.0 mask header with another GC generation's offset header can compile but program the wrong hardware bits.

## Risks And Edge Cases

- Generated-header drift is high impact. A wrong shift or mask can silently alter firmware commands, power-state transitions, profiling setup, doorbell routing, or clock-gating behavior.
- The chunk boundaries are artificial. This slice begins with only `RLC_CGCG_RAMP_CTRL` masks and ends before `GFX_ICG_GL2A_CTRL` is complete; adjacent chunk documents are required before making complete file-level claims about those register groups.
- RLC safe-mode, SMU message, RLCV command, and SRM/GPM command fields are side-effect sensitive. Whole-register writes or stale command bits can trigger firmware actions, fail to enter/exit safe mode, or abort save/restore operations unexpectedly.
- Power-gating and clock-gating fields can create intermittent hangs or performance regressions rather than immediate build failures. Bad WGP masks, delay fields, CGCG/CGLS thresholds, memory sleep overrides, or block-level clock overrides can break idle entry/exit, GFXOFF, profiling, or reset recovery.
- Repeated register families are copy-sensitive: `RLC_SRM_INDEX_CNTL_ADDR/DATA_0..7`, `RLC_GPM_GENERAL_*`, `RLC_SPP_PVT_STAT_0..3`, RLCP/XT doorbell data pairs, and many `CGTT_*`/`GFX_ICG_*` controls must remain structurally consistent with their offsets.
- Status, interrupt, force, disable, and command registers sit near each other. The generated header does not distinguish read-only status, write-one-to-clear, mask-disable, force, self-clearing request, or sticky error behavior.
- Address and size fields may have implicit alignment or unit semantics, such as doorbell offsets starting above low bits, SRM command size/start offsets, IMU bootload size width, and delay counters measured in hardware-specific units.
- Profiling fields can perturb the workload under measurement. SPM/SPP enable masks, shader-profile wave selection, CAM access, SSF capture, and PVT statistics should be synchronized with profiling ownership and power-management state.
- Firmware ownership matters. RLC, SMU, IMU, and XT/LX6 controller registers may be invalid or unsafe to access when their firmware block is halted, power gated, in reset, or owned by another virtualization function.
- Reserved and `UNUSED` masks are present throughout the clock-gating and control registers. New code should preserve them unless writing validated golden-register values.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware integration tests:

- Build and preprocess GC 11.5.0 AMDGPU paths that include `gc_11_5_0_sh_mask.h`, especially `gfxhub_v11_5_0.c`, with common SOC15 register helpers enabled.
- Mechanically compare this chunk against the authoritative GC 11.5.0 register database. Verify that complete registers in the chunk have matching shift/mask pairs and that boundary exceptions are limited to `RLC_CGCG_RAMP_CTRL` and `GFX_ICG_GL2A_CTRL`.
- Cross-check every register group in this slice against `gc_11_5_0_offset.h` for corresponding `reg*` or `mm*` offsets and correct address-block placement.
- Run static mask sanity checks: each mask should align with its shift, full-width data fields should use `0xFFFFFFFFL`, repeated SRM/GPM, doorbell, SPP, residency-counter, and clock-control families should have regular layouts.
- Exercise GPU init, suspend/resume, runtime power management, GFXOFF entry/exit, GPU reset, and recovery on GC 11.5.0-class hardware. Watch for failed safe-mode polling, RLC/SMU command timeouts, invalid IMU boot/exit behavior, and clock-gating regressions.
- Validate RLC power-gating behavior with idle and busy graphics/compute workloads. Relevant signals include WGP power status/request bits, residency counters, RLC busy/status bits, and absence of hangs during power-state changes.
- Exercise SPM/SPP profiling and shader profiling controls. Expected signals are plausible sample counts/statistics, correct VMID or shader-engine selection, working CAM readback, and no lost workload progress while profiling is enabled.
- Test doorbell paths and embedded-controller interrupt routing where supported, checking RLCP/XT doorbell hit/status/data fields, CPAXI monitor data, and XT interrupt vector force/clear behavior under controlled diagnostics.
- Inspect UTCL1 and RLC error/status registers during induced fault or debug scenarios. Fault IDs, client IDs, miss FIFO flags, and CP stat invalidation status should decode consistently with expected conditions.
- Compare clock-gating register dumps against known-good golden-register or firmware-programmed values after init, after runtime power transitions, and after reset. Regression indicators include clocks stuck forced on, clocks gating during active work, unexpected perf counter disablement, or block-specific render/compute hangs.

## Cross-Chunk Notes

The previous chunk owns the start of `RLC_CGCG_RAMP_CTRL`; this chunk starts at its mask tail and then covers the bulk of RLC power, status, profiling, firmware-message, IMU, and doorbell metadata before entering the `gc_pwrdec` clock-gating block. The next chunk should complete `GFX_ICG_GL2A_CTRL` and continue later power/clock control register definitions. The merge lane should reconcile these boundaries before producing the final per-file research document.
