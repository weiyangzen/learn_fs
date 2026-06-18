# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 19950-22457

## Scope And Purpose

This chunk is a generated AMD DCN 3.1.2 register shift/mask header slice. It contains only preprocessor constants for memory-mapped display-controller register fields: `__SHIFT` macros give bit positions, `_MASK` macros give raw 32-bit field masks, and comments delimit register groups and hardware `addressBlock` sections. There are no functions, structs, enums, loops, branches, allocations, locks, or in-memory state in this range.

The purpose of the range is to define the field layout ABI used by AMDGPU Display Core code when programming DCN 3.1.2 DPP-related hardware. The matching `dcn_3_1_2_offset.h` header provides register addresses; this header provides the bit fields used by register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related macros after resource construction binds the generated addresses, shifts, and masks into DPP objects.

The slice has partial logical boundaries. It starts in the middle of DPP2 color-management shaper RAM B region definitions, at `CM2_CM_SHAPER_RAMB_REGION_10_11`; the preceding DPP2 shaper setup and earlier RAM B regions are in the previous chunk. It ends inside DPP3 perfmon definitions, after most `DC_PERFMON14_PERFCOUNTER_STATE` masks; the remaining `DC_PERFMON14` perfmon registers continue in a later chunk.

This specific chunk contains 2,117 `#define` lines across 368 generated register groups. The main hardware surface is the tail of DPP2 CM shaper/3DLUT, all DPP2 top and perfmon13 fields, most DPP3 CNVC/DSCL/CM/DPP top fields, and the beginning of DPP3 perfmon14.

## Register Blocks Covered

The initial DPP2 color-management tail covers:

- `CM2_CM_SHAPER_RAMB_REGION_10_11` through `CM2_CM_SHAPER_RAMB_REGION_32_33`, completing later RAM B shaper piecewise-linear region descriptors with LUT offsets and segment counts.
- `CM2_CM_MEM_PWR_CTRL2` and `CM2_CM_MEM_PWR_STATUS2` for shaper and HDR 3D LUT memory force/disable/state fields.
- `CM2_CM_3DLUT_MODE`, `CM2_CM_3DLUT_INDEX`, `CM2_CM_3DLUT_DATA`, `CM2_CM_3DLUT_DATA_30BIT`, `CM2_CM_3DLUT_READ_WRITE_CONTROL`, output normalization, per-channel output offset/scale, and CM test debug index/data fields.

The `dce_dc_dpp2_dispdec_dpp_top_dispdec` block covers `DPP_TOP2` control/status and diagnostics:

- `DPP_TOP2_DPP_CONTROL` for DPP clock enable, multiple DPPCLK/DISPCLK gate-disable controls, and test clock selection.
- `DPP_TOP2_DPP_SOFT_RESET` for CNVC, DSCL, CM, and OBUF soft reset bits.
- `DPP_TOP2_DPP_CRC_VAL_R_G`, `DPP_TOP2_DPP_CRC_VAL_B_A`, and `DPP_TOP2_DPP_CRC_CTRL` for DPP CRC readback and one-shot/continuous CRC selection.
- `DPP_TOP2_HOST_READ_CONTROL` for host-read rate limiting.

The `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` block covers a full `DC_PERFMON13` surface for DPP2. It defines counter event selection, counted-value type, hardware stop/count-off controls, counter states for eight counters, perfmon run/enable/clear controls, threshold/interrupt state and acknowledge fields, and low/high counter readbacks.

The DPP3 converter configuration block, `dce_dc_dpp3_dispdec_cnvc_cfg_dispdec`, covers:

- Surface pixel format and alpha-plane enable.
- `FORMAT_CONTROL` fields for CNVC bypass, alpha enable, expansion, truncation, clipping, 16-bit conversion, MSB alignment, positive clamp, and RGB crossbar selection.
- Floating-point conversion bias/scale for R/G/B.
- Color keyer control and low/high thresholds for alpha, red, green, and blue.
- Two-bit alpha LUT entries.
- Pre-dealpha, pre-degamma, pre-realpha, pre-CSC mode, coefficient format, and A/B pre-CSC coefficient matrices.

The DPP3 cursor converter block, `dce_dc_dpp3_dispdec_cnvc_cur_dispdec`, covers cursor0 mode, expansion, enable, pixel-inversion, alpha modulation, ROM enable, two cursor colors, and cursor FP scale/bias.

The DPP3 scaler block, `dce_dc_dpp3_dispdec_dscl_dispdec`, covers:

- Scaler coefficient RAM tap select/data windows.
- Scaler mode and tap controls, including luma/chroma taps, chroma coefficient mode, coefficient RAM selection, 4:2:0 processing, and alpha-luma mode.
- DSCL 2-tap sharpness/hardcoded coefficient controls.
- Manual replicate, horizontal/vertical luma and chroma scale ratios, and initial filter phases.
- Black color, update/autocal, overscan, OTG blanking windows, recout start/size, MPC size, and line-buffer data/memory controls.
- DSCL LUT memory power controls/status and OBUF control/memory power controls.

The DPP3 color-management block, `dce_dc_dpp3_dispdec_cm_dispdec`, is the largest part of the chunk. It covers:

- CM bypass, post-CSC A/B mode and coefficient matrices, gamut-remap A/B mode and coefficient matrices, fixed bias fields, dealpha, coefficient format, and HDR multiplier.
- GAMCOR control, indexed LUT access, LUT write/read controls, RAM A/B start/base/slope/end/offset, and region descriptors for regions 0 through 33.
- BLNDGAM control, indexed LUT access, LUT controls, RAM A/B start/base/slope/end/offset, and region descriptors for regions 0 through 33.
- Shaper control, offset/scale fields, indexed LUT access, write enable/select, RAM A/B start/end controls, and region descriptors for regions 0 through 33.
- Memory-power controls/status for GAMCOR, BLNDGAM, shaper, and HDR 3D LUT memories.
- 3D LUT mode, size, current mode, index/data paths, 30-bit data path, read/write control, output normalization, per-channel output offset/scale, and test debug index/data.

The `dce_dc_dpp3_dispdec_dpp_top_dispdec` block mirrors the DPP2 top fields for instance 3: clock/gating controls, soft resets, CRC values/control, and host-read rate control.

The final block begins `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` for `DC_PERFMON14`. This chunk includes `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, and most of `PERFCOUNTER_STATE`. Later `DC_PERFMON14` perfmon control, threshold/interrupt, and counter readback definitions are outside this assigned range.

## Important APIs, Types, And Macros

The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's low bit within the 32-bit register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask before shifting or after register readback masking, depending on the helper macro.
- `// addressBlock: ...` comments identify the generated hardware register aperture.
- `//<REGISTER>` comments group the fields belonging to a single register.

Important instance prefixes in this chunk are `CM2`, `DPP_TOP2`, `DC_PERFMON13`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, `CM3`, `DPP_TOP3`, and `DC_PERFMON14`. The prefix is part of the generated symbol and encodes the hardware instance. A wrong prefix can compile if a similarly named field exists for another instance, but it targets the wrong register instance when bound through register-list macros.

The primary consumer path for these macros is `display/dc/resource/dcn31/dcn31_resource.c`. That file includes `dcn/dcn_3_1_2_offset.h` and `dcn/dcn_3_1_2_sh_mask.h`, builds `dpp_regs[]` with `DPP_REG_LIST_DCN30(id)`, and initializes `tf_shift`/`tf_mask` with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`. `dcn31_dpp_create()` then passes the selected per-instance addresses plus the shared shift/mask tables into `dpp3_construct()`.

The DPP register-list and field-list definitions live in `display/dc/dpp/dcn30/dcn30_dpp.h`. DCN31 reuses this DCN30 DPP hardware object shape. `DPP_REG_LIST_DCN30_COMMON(id)` names the CNVC, cursor, DSCL, CM, and DPP top registers for each instance. `DPP_REG_LIST_SH_MASK_DCN30_COMMON()` and `DPP_REG_LIST_SH_MASK_DCN30_UPDATED()` map canonical field names in `struct dcn3_dpp_shift` and `struct dcn3_dpp_mask` to generated instance-0 macro names; resource construction pairs those common shifts/masks with instance-specific addresses for DPP0 through DPP3.

Runtime code that consumes the resulting DPP object includes the DCN10/DCN20/DCN30 DPP scaler and color-management implementations. Examples include CNVC format programming, cursor programming, DPP clock enable/disable, DSCL tap/ratio/recout setup, line-buffer memory setup, DSCL memory-power sequencing, CSC/gamut-remap programming, GAMCOR/BLNDGAM/shaper PWL LUT programming through index/data windows, and CM memory-power controls.

## Functional Field Groups

CNVC format fields define how source pixels enter the DPP. Pixel format, alpha-plane enable, alpha expansion, format expansion/truncation, component clipping, positive clamp, 16-bit conversion, MSB alignment, and RGB crossbar fields are the low-level representation of plane format choices made by higher-level DRM/AMDGPU display code. The floating-point bias/scale registers and pre-degamma/dealpha/realpha controls further adapt incoming plane data before scaling and color processing.

Pre-CSC and post-CSC fields expose banked color-space conversion matrices. Each coefficient register packs two coefficients, and both A and B banks are present for pre-CSC and post-CSC paths. Mode and current-mode fields let driver code select or observe which matrix bank is active. Correct bank selection matters when changing color matrices on a live pipe.

DSCL fields program scaling geometry and filter behavior. The chunk includes both luma and chroma scale ratios, initial phases, tap counts, coefficient RAM access, 2-tap sharpness controls, 4:2:0 mode selection, recout geometry, MPC size, overscan, OTG blank windows, and line-buffer format/memory parameters. These fields translate plane scaling, viewport, chroma-siting, and line-buffer decisions into hardware state.

The CM GAMCOR, BLNDGAM, and shaper LUT blocks are piecewise-linear LUT engines. They use a repeated pattern: control/current-mode fields, an index register, a data register, a LUT control or write-enable register, per-channel start/end/base/slope/offset registers, and region descriptors that pack two regions per register. Region descriptors use 9-bit LUT offsets and segment-count fields for regions 0 through 33. The DPP2 portion completes the later shaper RAM B region descriptors; the DPP3 portion includes full GAMCOR, BLNDGAM, and shaper RAM A/B definitions.

The 3D LUT fields define a stateful indexed RAM interface. `CM_3DLUT_MODE` selects mode and size and exposes current mode, `CM_3DLUT_INDEX` selects the entry, `CM_3DLUT_DATA` packs two 16-bit data values, `CM_3DLUT_DATA_30BIT` exposes a 30-bit access path, and `CM_3DLUT_READ_WRITE_CONTROL` selects write enable mask, RAM bank, 30-bit enable, and read selection. Output normalization and per-channel offset/scale fields shape the 3D LUT output.

Memory-power fields gate or report internal DPP memories. `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_MEM_PWR_CTRL2`, and `CM_MEM_PWR_STATUS2` cover GAMCOR, BLNDGAM, shaper, and HDR 3D LUT memory force/disable/state. DSCL and OBUF memory-power fields cover scaler LUT and output-buffer memories. These fields are not just diagnostics; setting force/disable bits can make dependent LUT or scaler access invalid until memory state is restored.

DPP top fields are instance-level control and diagnostic fields. Clock-enable and gate-disable fields decide whether the DPP subblock is active or gated. Soft-reset fields reset CNVC, DSCL, CM, and OBUF subblocks. CRC fields configure one-shot or continuous DPP CRC capture and read back R/G/B/A signatures. Host-read rate control throttles host-side reads from the DPP block.

Perfmon fields define hardware profiling controls. `DC_PERFMON13` is complete in this chunk and `DC_PERFMON14` starts at the end. Counter controls select events, counted-value type, increment mode, hardware stop behavior, run enable mode, interrupt enable, active state, and counter selection. State and cvalue fields expose counter status and threshold/interrupt conditions, while low/high registers expose the sampled count value.

## Control Flow And State Behavior

This header has no executable control flow. Runtime behavior appears when DCN31 resource setup binds generated offsets and masks into DPP objects, and later DPP code uses those objects to access MMIO registers. A normal path is:

1. `dcn31_resource.c` includes `dcn_3_1_2_offset.h` and this shift/mask header.
2. `dpp_regs[inst]` selects the instance-specific register addresses, for example DPP2 or DPP3.
3. `tf_shift` and `tf_mask` provide canonical field positions and masks through the DCN30 DPP field-list macros.
4. DPP code calls register helpers to set or read fields; the helper combines the chosen address with the relevant shift/mask.
5. Hardware persists, latches, consumes, or updates the register-backed state according to the block's semantics.

Most fields in this range represent hardware state rather than software state. Format, scaler, CSC, gamut, gamma, shaper, 3D LUT, CRC, and memory-power controls persist in hardware registers until reprogrammed, reset, power-gated, or overwritten by firmware/hardware mechanisms. Status fields such as current mode, memory-power state, CRC values, perfmon active state, and counter state are volatile hardware readbacks.

Several register groups are explicitly stateful. LUT and 3D LUT programming uses index/data windows, write masks, RAM bank selectors, and current-mode readbacks. A valid mask with a stale index or wrong bank can write correct-looking data to the wrong LUT bank. CRC and perfmon fields are interval-sensitive; clear/ack, enable, one-shot/continuous, event selection, threshold, and readout ordering determine what a readback means.

Soft reset, ACK/clear, and memory-power fields have side effects. They should not be treated as ordinary durable configuration bits. Writing a soft-reset field can reset subblock state, writing clear/ack fields can drop latched diagnostic events, and forcing memory power down can make subsequent LUT or coefficient writes unreliable.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`. Offset macros and shift/mask macros are generated as a pair; address drift or field-layout drift can compile but program wrong bits.

The main include sites in this tree are:

- `display/dc/resource/dcn31/dcn31_resource.c`, which constructs DPP0 through DPP3 objects and binds the DCN 3.1.2 generated masks and shifts.
- `display/dc/irq/dcn31/irq_service_dcn31.c`, which includes the same generated header set for DCN31 interrupt-service register definitions.
- `display/dmub/src/dmub_dcn31.c`, which includes the generated header set for DMUB/DCN31 register access.

The DPP-specific consumer definitions are in `display/dc/dpp/dcn30/dcn30_dpp.h` and the inherited DPP implementations under `display/dc/dpp/dcn10`, `display/dc/dpp/dcn20`, and `display/dc/dpp/dcn30`. The fields in this chunk support:

- Plane format and converter programming through CNVC/CNVC_CUR fields.
- Scaling and line-buffer setup through DSCL fields.
- Color-management programming through CM CSC, gamut, GAMCOR, BLNDGAM, shaper, and 3D LUT fields.
- Power-management sequencing for CM, DSCL, and OBUF memories.
- DPP clocking, soft reset, CRC diagnostics, and host-read throttling.
- Perfmon diagnostics for DPP2 and DPP3.

Higher-level display integration comes from DRM plane state, atomic modeset/resource validation, color-management properties, scaling ratio calculations, cursor state, power management, CRC/debugfs workflows, and hardware performance diagnostics. This generated header is the low-level endpoint those paths use to encode the requested hardware state.

## Risks And Maintenance Notes

Generated numeric drift is the primary risk. A wrong shift or mask can corrupt adjacent fields in MMIO registers, which may show up as bad color output, failed scaling, cursor artifacts, incorrect CRCs, broken 3D LUT programming, unreliable perfmon data, or power-management failures rather than an immediate crash.

Instance-prefix mistakes are high risk because this chunk contains repeated DPP2 and DPP3 surfaces. Using `CM2` versus `CM3`, `DPP_TOP2` versus `DPP_TOP3`, or `DC_PERFMON13` versus `DC_PERFMON14` incorrectly can target a different pipe's hardware. Shared DPP code relies on resource construction to pair common field tables with the correct instance addresses.

The range is split across logical blocks. The DPP2 shaper RAM B definitions are only the tail, and `DC_PERFMON14` is incomplete. Merge/reconciliation should combine neighboring chunk documents before presenting a complete per-file register map for DPP2 shaper or DPP3 perfmon.

LUT programming is ordering-sensitive. GAMCOR, BLNDGAM, shaper, and 3D LUT paths use bank selectors, current-mode readbacks, index/data windows, color write masks, and region descriptors. Updating a visible bank before all data and regions are programmed can cause transient or persistent color corruption.

Scaler and CNVC format fields are tightly coupled to plane state. Wrong tap counts, chroma modes, scale ratios, initial phases, line-buffer memory configuration, or format crossbar settings can produce artifacts only on specific pixel formats, scaling ratios, rotation/chroma cases, or cursor/alpha combinations.

Memory-power controls can invalidate dependent programming. Forcing shaper, HDR 3D LUT, GAMCOR, BLNDGAM, DSCL LUT, or OBUF memories into low-power states while the block is active can cause lost LUT contents, failed register waits, or display corruption around blanking, suspend/resume, hotplug, or plane reconfiguration.

CRC and perfmon fields are diagnostics with stateful clear/enable/read ordering. Generic read/modify/write code must preserve unrelated bits and avoid accidentally acknowledging or masking events. Tests that do not reset counters, clear pending one-shot state, or select the intended source can report misleading data even if the masks are correct.

Soft-reset and clock-gating fields affect whole DPP subblocks. Resetting CNVC, DSCL, CM, or OBUF while an active pipe depends on them can drop programmed state. Disabling clocks or forcing gate behavior can make subsequent register access unreliable unless sequencing matches hardware requirements.

## Test Signals

Build-time validation should catch missing or renamed generated macros in `dcn31_resource.c` and `dcn30_dpp.h`, especially through `DPP_REG_LIST_DCN30(id)`, `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)`, and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`.

Generated-header consistency checks should verify that every field has the expected `_SHIFT` and `_MASK`, masks fit in 32 bits, fields do not overlap unexpectedly within a register, and repeated DPP2/DPP3 register groups match the ASIC specification.

Modeset and plane tests should exercise DPP2 and DPP3 with varied pixel formats, alpha-plane state, format expansion/truncation, color keying, cursor formats, pre-dealpha/realpha, and pre-degamma paths. Useful symptoms are correct color channels, alpha behavior, cursor appearance, and no unexpected converter bypass.

Scaler tests should cover upscaling, downscaling, bypass, 4:2:0 luma/chroma handling, chroma coefficient mode, tap-count changes, coefficient RAM programming, overscan, recout size/start, MPC size, and line-buffer memory configuration.

Color-management tests should program post-CSC, gamut remap, GAMCOR, BLNDGAM, shaper, HDR multiplier, and 3D LUT paths on DPP3 and the DPP2 shaper/3D LUT tail where applicable. High-signal checks include color-ramp output, LUT bank switching, current-mode readback, region descriptor correctness, and no visible transient during atomic updates.

Power-management tests should exercise suspend/resume, runtime power transitions, display blank/unblank, stream reconfiguration, and plane disable/enable around CM, DSCL, shaper, HDR 3D LUT, GAMCOR, BLNDGAM, and OBUF memory-power fields. Expected signals are successful register waits, restored LUT contents where required, and no corruption after resume.

DPP CRC tests should enable one-shot and continuous CRC on DPP2 and DPP3, vary CRC source/pixel/cursor/420/stereo/interlace selection where supported, read R/G/B/A values, and verify pending bits and masks behave as expected.

Perfmon tests should configure `DC_PERFMON13` for DPP2 and the available `DC_PERFMON14` counter-control/state fields for DPP3, select known events, start/stop counters, read low/high values, trigger threshold interrupts where available, and verify clear/ack behavior without losing unrelated counter state.

## Chunk-Specific Summary

Lines 19950-22457 are generated DCN 3.1.2 register metadata for DPP color, scaler, converter, top-level control, CRC, memory-power, 3D LUT, and perfmon programming. The chunk completes the DPP2 shaper/3D LUT tail, fully covers DPP2 top and perfmon13, covers most DPP3 CNVC/CNVC_CUR/DSCL/CM/DPP_TOP fields, and starts DPP3 perfmon14. Correctness depends on exact generated mask/shift values, correct instance binding through DCN31 resource construction, careful LUT/index/bank sequencing, and hardware validation across modeset, scaling, color management, CRC, perfmon, reset, and power-management workflows.
