# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 5163-7647

## Purpose

This chunk is generated AMD DCN 3.1.5 display register-address metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic register names to MMIO offsets plus a matching `<register>_BASE_IDX` selector. AMDGPU display code combines each offset with `DCN_BASE__INST0_SEG*` base constants to build runtime register tables for DCN315 hardware blocks.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver ASIC metadata and has no Ceph or distributed filesystem behavior.

The requested range covers 2,401 `#define` lines across 21 address-block markers or continuation regions. It starts in the middle of the `CM2` color-management block, continues through DPP2 and DPP3 display pipe register groups, includes the MPC/MPCC compositor and RMU color-LUT register space, and ends inside the first ABM0 backlight/ambient-light block. The major hardware surfaces are:

- Tail of `CM2` color management: gamma-correction RAM B region entries, blender gamma LUT programming, HDR multiplier, coefficient/dealpha controls, shaper LUTs, 3D LUTs, memory power, and debug index/data.
- DPP2 top and perfmon registers: DPP control, soft reset, CRC readback/control, host-read control, and `DC_PERFMON13`.
- DPP3 CNVC, cursor, scaler, color-management, top, and perfmon registers: pixel-format conversion, color keying, pre-CSC, DSCL filter/scaler/line-buffer controls, full `CM3` gamma/shaper/3DLUT programming, DPP top controls, and `DC_PERFMON14`.
- MPC register space: MPCC0 through MPCC3 blending/composition state, global MPC clock/reset/CRC/pending/vupdate-lock/DWB mux controls, `DC_PERFMON15`, out muxes, output CSC, output gamma/OGAM, and RMU0/RMU1 shaper plus 3DLUT registers.
- Start of `ABM0`: BL1 PWM/ABM backlight registers and the beginning of `DC_ABM1` ambient backlight management histogram/luma-statistics registers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, allocations, or direct persistence APIs in this line range. The public interface is the generated macro convention:

- `reg<block>_<register>` gives the register offset inside the selected DCN base segment.
- `reg<block>_<register>_BASE_IDX` gives the base-segment index used by local `BASE(reg..._BASE_IDX)` helper macros in DCN315 resource code.

Important macro families in this chunk:

- `regCM2_CM_*`: continuation of DPP pipe 2 color-management offsets. The chunk starts after earlier `CM2` post-CSC, gamut-remap, bias, and most gamma-correction definitions; this range includes the remaining gamma-correction RAM B region slots, blender gamma, HDR multiplier, memory power, dealpha/coefficient format, shaper RAM A/B, 3DLUT, and test debug registers. All have base index `2`.
- `regDPP_TOP2_*` and `regDC_PERFMON13_*`: DPP2 top-level control/CRC/host-read registers and DPP2 perfmon counter controls. All have base index `2`.
- `regCNVC_CFG3_*` and `regCNVC_CUR3_*`: DPP3 converter and cursor offsets for surface pixel format, format control, floating-point bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices, pre-degamma, pre-realpha, and cursor color/control state. All have base index `2`.
- `regDSCL3_*`: DPP3 scaler/filter offsets for coefficient RAM access, SCL/DSCL modes, tap control, manual replicate, horizontal/vertical ratios and initial phases for luma/chroma, black color, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format and memory control, counters, DSCL memory power, and output-buffer memory power. All have base index `2`.
- `regCM3_CM_*`: full DPP3 color-management offset set. It mirrors the CM2 pattern for control, post-CSC, gamut remap, bias, gamma-correction LUT and RAM A/B, blender-gamma LUT and RAM A/B, HDR multiplier, memory power, dealpha/coefficient format, shaper LUT and RAM A/B, 3DLUT, and test debug registers. All have base index `2`.
- `regDPP_TOP3_*` and `regDC_PERFMON14_*`: DPP3 top-level control/CRC/host-read registers and DPP3 perfmon counter controls. All have base index `2`.
- `regMPCC0_*` through `regMPCC3_*`: compositor pipe instances for top/bottom input selection, OPP routing, MPCC control, state-machine control, update-lock selection, top/bottom gain, background color, memory power, and status. These offsets use base index `3`.
- `regMPC_*`, `regADR_*`, `regCFG_*`, and `regCUR_*`: global MPC control, reset, CRC, perfmon event selection, bypass backgrounds, host-read, DPP/pending status, vupdate locks for four sets, DWB mux, and `DC_PERFMON15`. These offsets use base index `3`.
- `regMPC_OUT_MUX*_*`: output mux routing, status, alpha control, and selected-output readback for MPC output instances 0 through 3. These use base index `3`.
- `regMPC_OCSC_*` and `regMPC_OGAM_*`: MPC output color space conversion and output gamma/shaper/LUT registers, including output CSC A/B matrices, OGAM RAM A/B start/end/region registers, memory power, and test debug. These use base index `3`.
- `regMPC_RMU0_*` and `regMPC_RMU1_*`: RMU shaper and 3DLUT programming registers for two RMU instances. RMU0 is mostly in the middle of this chunk, while RMU1 is complete from shaper control through 3DLUT output offsets. These use base index `3`.
- `regABM0_BL1_PWM_*` and `regABM0_DC_ABM1_*`: beginning of ABM0 backlight and ambient backlight management offsets, including ambient/user/target/current/final/minimum duty cycle, PWM ABM control, update sample rate, register lock, ABM control, IPCSC coefficient selection, ACE offsets/thresholds, luma-stat readback, histogram sample/bin controls, and histogram result registers 1 through 5. These use base index `3`.

The companion `dcn_3_1_5_sh_mask.h` file supplies bit-field masks and shifts for many of these register names. Consumers normally use both headers through helper macros such as `SR`, `SRI`, `SRII`, `SRII_MPC_RMU`, `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

## Control Flow

This header has no runtime branches, loops, callbacks, or call graph. Control flow is supplied by AMDGPU display code that includes the generated offset and mask headers and expands register-list macros into typed register tables.

Typical runtime path:

1. DCN315 resource code includes `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`.
2. Local helper macros in `dcn315_resource.c` compute absolute addresses as `BASE(reg..._BASE_IDX) + reg...`.
3. Register-list macros such as `DPP_REG_LIST_DCN30(id)`, `ABM_DCN302_REG_LIST(id)`, `MPC_REG_LIST_DCN3_0(inst)`, `MPC_OUT_MUX_REG_LIST_DCN3_0(inst)`, and related mask/shift lists initialize per-block structs.
4. Runtime display code programs those structs through block-specific modules: DPP/CNVC/DSCL/CM code for pipe color and scaling, MPC/MPCC code for blending and routing, ABM code for backlight management, perfmon code for counters, and HWSS/resource sequencing code for modeset and power transitions.
5. DMUB DCN315 code also includes the same generated offset/mask headers to populate `dmub_srv_dcn315_regs` through `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, and field-list expansions, although the specific chunked CM/DPP/MPC/ABM registers are primarily consumed by DC resource and hardware block tables.

The offset macros do not encode hardware access ordering. Driver code must still sequence indexed LUT accesses, register locks, vupdate locks, memory power transitions, soft resets, and CRC/perfmon counter operation according to each block's hardware rules.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed GPU display state that lives in hardware until changed by the driver, reset by block/ASIC reset, or lost through power-gating/suspend/resume transitions.

State represented by the offsets includes:

- DPP pipe color state: post-CSC/gamut/bias configuration, gamma-correction RAM A/B, blender gamma RAM A/B, HDR multiplier, dealpha, coefficient format, shaper RAM A/B, 3DLUT index/data/control, memory power controls, and debug windows for CM2 and CM3.
- DPP top/scaler/converter state: DPP enable/control, soft reset, CRC control and values, host-read control, CNVC surface pixel format and color keying, cursor color/control, DSCL filter coefficients, scaling ratios, initial phases, line-buffer format, recout/MPC geometry, memory power, and output-buffer control.
- Perfmon state: DPP2 `DC_PERFMON13`, DPP3 `DC_PERFMON14`, and MPC `DC_PERFMON15` counter controls, run/configuration state, interrupt miscellaneous state, and high/low counter readback registers.
- MPCC/MPC composition state: per-MPCC top/bottom source selection, OPP routing, blending gains, background color, update-lock selection, memory power, MPCC status, global MPC clock/reset/CRC, pending statuses, vupdate lock sets, DWB muxing, output mux routing/status, output CSC coefficients, output gamma RAM, and MPC test debug windows.
- RMU state: two RMU shaper LUT/region programming blocks plus RMU 3DLUT index/data/read-write/out-normalization/out-offset registers.
- ABM state: PWM brightness request and status levels, minimum/final duty cycle, update cadence, register locking, ABM control, ACE contrast-enhancement parameters, luminance statistics, histogram sample controls, bin shifting, and initial histogram result registers.

Some registers are configuration registers, some are read-only or readback status, some are indexed data ports, some are register-lock or vupdate synchronization controls, and some likely have self-clearing or write-one-to-clear behavior. The generated offset header does not express those access classes; the paired mask header, hardware programming manuals, and consuming driver code provide that context.

## Dependencies And Integration Points

This chunk must remain consistent with the generated DCN 3.1.5 register database and its paired field-layout header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`

Key integration points:

- `dcn315_resource.c` defines `BASE`, `SR`, `SRI`, `SRII`, and `SRII_MPC_RMU` macros that token-paste these generated `reg...` symbols into absolute register addresses.
- `dcn315_resource.c` builds `dpp_regs[]` with `DPP_REG_LIST_DCN30(id)`, which consumes the DPP top, CNVC, DSCL, and CM register families represented here for pipe instances 2 and 3.
- `dcn315_resource.c` builds `abm_regs[]` with `ABM_DCN302_REG_LIST(id)` and `abm_shift`/`abm_mask` with `ABM_MASK_SH_LIST_DCN30()`, integrating ABM0 offsets from the end of this chunk with ABM hardware programming paths.
- `dcn315_resource.c` builds `mpc_regs` with `MPC_REG_LIST_DCN3_0()`, `MPC_OUT_MUX_REG_LIST_DCN3_0()`, and `MPC_DWB_MUX_REG_LIST_DCN3_0()`, integrating the MPCC, MPC global, output mux, and DWB mux offsets from this range. DCN315 defines `SRII_MPC_RMU`, but unlike adjacent DCN31/DCN314 resource files in this tree, this specific resource table does not visibly instantiate the `MPC_RMU_*` list in the searched excerpt.
- DPP color code uses the CM, shaper, gamma, and 3DLUT register tables to implement color transforms exposed through DC color-management state, including shaper LUTs and 3D LUTs.
- MPC/MPCC code uses composition and mux registers for plane blending, top/bottom tree wiring, OPP output routing, background colors, CRC, output CSC/gamma, and update-lock coordination.
- ABM/backlight code uses the ABM0 offsets to drive panel backlight PWM and ambient-backlight-management calculations.
- `dmub_dcn315.c` uses the same generated namespace for DCN315 DMUB register maps, keeping firmware-service register addressing in sync with the resource code's DCN base segments.

## Risks And Edge Cases

- Generated offset drift is the main risk. A wrong offset or base index compiles cleanly but can direct the driver to the wrong MMIO register, potentially corrupting color programming, scaler state, compositor routing, backlight state, or unrelated display hardware.
- This chunk has artificial boundaries. It starts in the middle of `CM2_CM_GAMCOR_RAMB_REGION_*`, so the complete CM2 gamma-correction context is in the previous chunk. It ends at `ABM0_DC_ABM1_HG_RESULT_5`, before the rest of the ABM0 histogram results and backlight-lock registers in the next chunk.
- Indexed LUT registers are sequencing-sensitive. `*_LUT_INDEX`, `*_LUT_DATA`, `*_3DLUT_INDEX`, `*_3DLUT_DATA`, `*_READ_WRITE_CONTROL`, and RAM A/B region registers must be programmed with the expected bank, index, and write-enable order. A bad offset can load the wrong bank or leave color transforms partially updated.
- Color pipeline offsets are high impact. Bad CM2/CM3 post-CSC, gamut-remap, shaper, gamma, blender-gamma, 3DLUT, or HDR multiplier addresses can cause wrong color output, banding, black screens, or failures that only appear with HDR, color-managed desktops, overlays, or multi-plane composition.
- DSCL/CNVC mistakes can break mode timing and format conversion. Incorrect scaling ratios, filter RAM access, line-buffer format, recout/MPC size, or pixel-format conversion offsets can cause underflow, corrupted scanout, clipped output, or failed plane validation symptoms.
- MPCC and MPC routing registers affect active composition. Wrong top/bottom selection, OPP ID, output mux, vupdate-lock, pending-status, or DWB mux offsets can misroute planes, leave updates stuck, break writeback, or produce inconsistent debug state.
- Memory power and soft-reset registers can disrupt live hardware if programmed while a pipe or compositor block is active. The header does not indicate which registers require disable, lock, or idle sequencing.
- Perfmon registers are diagnostic but stateful. Wrong counter control or interrupt-misc offsets can produce misleading performance data or leave counter interrupts/status bits stuck.
- ABM/PWM offsets are user-visible. A wrong duty-cycle, user-level, target-level, sample-rate, or lock offset can produce brightness jumps, ignored backlight requests, stalled ABM transitions, or incorrect luma histogram feedback.
- Base-index mismatches are as dangerous as offset mismatches. This range crosses base index `2` DPP blocks and base index `3` MPC/ABM blocks; using the wrong base segment would send otherwise-correct offsets into the wrong address aperture.

## Test Signals

Useful validation should combine generated-header consistency checks, build coverage, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail in `dcn315_resource.c`, `dmub_dcn315.c`, IRQ/GPIO DCN315 files, or shared DPP/MPC/ABM register-list expansions.
- Mechanically verify that every `reg...` definition in this range has a matching `_BASE_IDX` definition and that the expected base indices are preserved: DPP/CM/CNVC/DSCL/perfmon13/14 entries use `2`, while MPCC/MPC/RMU/ABM entries use `3`.
- Compare this offset range against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x headers where the same register families should remain compatible.
- Exercise DPP2/DPP3 color-management paths: post-CSC, gamut remap, degamma/gamma, blender gamma, shaper LUT, 3DLUT host loads, HDR multiplier, dealpha, memory power transitions, and debug readback.
- Exercise DPP3 scaling/conversion paths: pixel-format changes, color keying, cursor color/control, DSCL coefficient RAM loads, luma/chroma scaling ratios, overscan, line-buffer formats, recout/MPC sizing, CRC values, and host-read control.
- Exercise MPCC/MPC composition: multi-plane blending, MPCC top/bottom tree changes, OPP assignment, update locks, background color, output mux status, output CSC/gamma, DWB muxing, pending-status readback, and CRC selection/result readback.
- Exercise RMU shaper/3DLUT programming if enabled by the DCN315 resource configuration or later changes. Validate bank selection, index/data writes, 30-bit data paths, output normalization, and per-channel offsets.
- Exercise ABM/backlight behavior: user brightness changes, ambient-light updates, target/current/final duty-cycle reporting, sample-rate changes, group register locking, ACE configuration, luma-statistics readback, histogram bin controls, and histogram result readback beyond this chunk after merge.
- Exercise suspend/resume and display off/on transitions. Confirm that CM, DSCL, MPC, RMU, and ABM memory-power/status registers restore or reinitialize correctly without stale LUT banks, stuck locks, or incorrect PWM output.

## Cross-Chunk Notes

The previous chunk owns the start of the `CM2` color-management block, including the earlier gamma-correction register definitions that precede `regCM2_CM_GAMCOR_RAMB_REGION_8_9_BASE_IDX`. The next chunk owns the remainder of `ABM0_DC_ABM1_*`, including histogram results after result 5 and later ABM/backlight control registers. The final per-file research document should merge adjacent chunks before making complete claims about CM2 or ABM0 coverage.
