# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 14899-17419

## Scope

This chunk is part of the generated AMDGPU DCN 3.1.6 register shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, includes, or executable control flow. The covered range has 2,521 source lines, 2,111 `#define` lines, and 398 register/group comments.

The chunk starts mid-register in the DPP0 color-management block: line 14899 contains the mask definitions for `CM0_CM_POST_CSC_C11_C12`, while the corresponding shift definitions are in the previous chunk. It ends mid-color-management table at `CM1_CM_GAMCOR_RAMA_REGION_22_23`, before that register's field definitions are complete. The merge lane must combine adjacent chunks before making whole-file or whole-register claims.

## Purpose

The purpose of this range is to publish bitfield ABI for DCN 3.1.6 display pipe programming. Each macro pairs a hardware register and field with either its bit offset or its bit mask:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: mask for the same field.

Driver register helpers use these constants with the matching DCN 3.1.6 address header to pack, update, and extract fields in memory-mapped display registers. The covered hardware areas are:

- DPP0 color-management tail: post-CSC, gamut remap, color bias, gamma correction, blend gamma, HDR multiplier, color memory power state, shaper LUTs, 3D LUT controls, and CM debug index/data.
- DPP0 top-level and perfmon blocks: DPP enable/clock/soft reset, DPP CRC, host read control, and display performance counter control/status/value registers.
- DPP1 converter/scaler blocks: surface format conversion, pre-CSC, cursor colors, scaler coefficients and ratios, line-buffer and output-buffer memory power controls.
- DPP1 color-management start: CM1 control, post-CSC, gamut remap, bias, gamma-correction LUT controls, and the first portion of gamma RAM A region descriptors.

## Important Definitions

The public surface is macro-only. The most important groups in this chunk are:

- `CM0_CM_POST_CSC_*` and `CM1_CM_POST_CSC_*`: 16-bit coefficient and bias fields for post color-space conversion matrices. Control fields include requested and current post-CSC mode.
- `CM0_CM_GAMUT_REMAP_*` and `CM1_CM_GAMUT_REMAP_*`: gamut-remap matrix coefficients and mode/current-mode fields, again represented as paired 16-bit matrix entries.
- `CM*_CM_BIAS_CR_R` and `CM*_CM_BIAS_Y_G_CB_B`: channel bias fields for color-management math.
- `CM0_CM_GAMCOR_*`, `CM0_CM_BLNDGAM_*`, and `CM1_CM_GAMCOR_*`: gamma and blend-gamma control, LUT index/data/control, and RAM A/B piecewise-linear region descriptors. These include LUT index fields, 18-bit LUT data fields, per-channel start/end/base/slope/offset fields, and packed region descriptors containing LUT offsets and segment counts.
- `CM0_CM_SHAPER_*`: shaper scale, offset, LUT index/data/write enable, and RAM A/B region descriptor fields used before 3D LUT processing.
- `CM0_CM_3DLUT_*`: 3D LUT mode, index, data, 30-bit data path, read/write control, output normalization, and per-channel output offsets.
- `CM0_CM_MEM_PWR_CTRL`, `CM0_CM_MEM_PWR_STATUS`, `CM0_CM_MEM_PWR_CTRL2`, and `CM0_CM_MEM_PWR_STATUS2`: power-force, power-disable, power-mode, and power-state fields for color-management RAMs.
- `DPP_TOP0_DPP_*`: top-level DPP enable/clock gating/reset controls, CRC value/control fields, and host read control.
- `DC_PERFMON11_*`: performance counter control, state, perfmon enable, condition select, threshold, value, and high/low counter fields.
- `CNVC_CFG1_*`: DPP1 converter configuration for surface pixel format, clamp/expansion/alpha settings, floating-point bias/scale, color keyer thresholds, alpha LUT, pre-dealpha/pre-realpha, pre-CSC mode/matrix, and coefficient format.
- `CNVC_CUR1_CURSOR0_*`: cursor enable, mode, expansion, premultiplied alpha, color0/color1, and cursor floating-point scale/bias fields.
- `DSCL1_*`: DPP1 scaler coefficient RAM access, scale mode, tap counts, manual replicate, horizontal/vertical luma/chroma ratios and initial phases, black color, update/autocal, overscan, timing windows, recout/MPC sizes, line-buffer format/memory control/status, OBUF control, and OBUF memory power control.

## Control Flow and State

This header has no runtime branches or calls. Runtime behavior comes from code that includes the generated address and shift/mask headers, selects a DPP instance, and calls AMD display register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or field-table builders such as `TF_SF(...)`.

Typical use is:

1. The DPP, color, scaler, cursor, or perfmon code selects a generated register address for DCN 3.1.6.
2. A helper shifts a field value by `<REGISTER>__<FIELD>__SHIFT` and applies `<REGISTER>__<FIELD>_MASK`.
3. The helper writes the memory-mapped register, or reads it and extracts a field through the same constants.
4. Hardware latches the programmed value or exposes status/readback fields for later polling.

The chunk describes several persistent hardware states:

- Color pipeline state persists in post-CSC, gamut-remap, bias, gamma, blend-gamma, shaper, and 3D LUT registers until the driver reprograms them or the block is reset.
- LUT RAM programming is indexed and stateful. `*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, `*_RAMA_*`, and `*_RAMB_*` fields define a host-programmed table and piecewise-linear segmentation for multiple channels and banks.
- Double-buffer/current-mode style state appears in fields such as `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `CM_UPDATE_PENDING`, `DSCL_UPDATE_PENDING`, `DSCL_UPDATE_TAKEN`, and related scaler update bits.
- Memory power controls persist in DPP color, scaler line-buffer, and output-buffer memory power registers, with paired status fields exposing hardware state.
- Perfmon counters and DPP CRC/debug fields are readback-oriented state: software configures selection/enables, then reads captured values or status.

## Dependencies and Integration Points

This header depends on the generated AMD ASIC register naming contract. It is useful only with the matching DCN 3.1.6 register-address header and the AMD display register helper layer.

Important integration points:

- `drivers/gpu/drm/amd/display/dc/dpp/` headers define field lists with `TF_SF(...)` using the same register/field names. Those lists map generated `__SHIFT` and `_MASK` constants into typed DPP register structures for common color, scaler, and memory power code.
- DPP color management code consumes the CM, GAMCOR, BLNDGAM, SHAPER, and 3D LUT fields when programming color transforms, gamma curves, HDR multipliers, and LUT banks.
- DPP scaler code consumes `DSCL1_*` fields when configuring scaling ratios, taps, coefficient RAM, line-buffer format, viewport/recout sizing, and memory power behavior.
- Converter and cursor code consume `CNVC_CFG1_*` and `CNVC_CUR1_*` fields for pixel format, color keying, alpha handling, pre-CSC, cursor mode, and cursor colors.
- Diagnostics and validation paths consume DPP CRC, host read, test/debug, and `DC_PERFMON11_*` fields.

The `CM0`, `DPP_TOP0`, and `DC_PERFMON11` prefixes identify DPP0-side blocks, while `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and `CM1` identify corresponding DPP1-side converter, cursor, scaler, and color-management blocks. Shared suffixes allow common code to work across pipe instances while preserving per-instance register names.

## Risks and Edge Cases

- These constants are hardware ABI. A wrong shift or mask can silently write the wrong bits, producing incorrect color transforms, broken gamma/LUT programming, scaler artifacts, cursor corruption, failed memory power transitions, or misleading perfmon/CRC readings.
- The chunk boundaries are not semantic boundaries. `CM0_CM_POST_CSC_C11_C12` is missing its shift definitions here, and `CM1_CM_GAMCOR_RAMA_REGION_22_23` is incomplete at the end of the range.
- Many matrix and LUT fields are packed as two 16-bit halves, 18-bit LUT data values, 19-bit offsets, or 9-bit LUT offsets with 3-bit segment counts. Raw callers must rely on helper masking or validate values before packing to avoid truncation.
- Generated names with repeated suffixes, such as fields ending in `*_MASK_MASK`, are intentional when the hardware field itself is named `*_MASK`; reviewers should not simplify those identifiers locally.
- Current/pending/taken/status fields describe hardware handshakes but do not encode access semantics. Correct sequencing, polling, and write-one-to-clear behavior must come from driver code and hardware documentation.
- DPP0 and DPP1 blocks are similar but not fully represented in this single chunk. Absence of a matching `CM1` blend-gamma, shaper, or 3D LUT section here should be treated as a chunking artifact, not evidence that the full source lacks it.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation is compile-time, generated-structure, and hardware integration focused:

- AMDGPU/DC builds that include `dcn_3_1_6_sh_mask.h` should compile with no undefined register-field macros for DCN 3.1.6 DPP color, converter, cursor, scaler, perfmon, or top-level code.
- Generated consistency checks should verify that every field has a matching shift/mask pair, masks align with shifts and expected widths, and replicated CM0/CM1 or DPP0/DPP1 fields match where hardware blocks are replicated.
- Display validation should exercise SDR/HDR color pipelines, post-CSC, gamut remap, gamma correction, blend gamma, shaper LUT, and 3D LUT programming on affected DCN 3.1.6 hardware.
- Scaler tests should cover luma/chroma scaling ratios, tap programming, coefficient RAM writes, overscan/recout sizing, line-buffer formats, and OBUF/line-buffer memory power transitions.
- Cursor and converter tests should cover surface pixel formats, alpha/keying paths, pre-CSC, cursor color/mode programming, and cursor scale/bias.
- Diagnostics should observe DPP CRC values, perfmon counter state/value updates, CM debug index/data reads, and status transitions for `*_PENDING`, `*_TAKEN`, memory power state, and LUT/control current-mode fields.

## Chunk Notes for Merge Lane

- Prefix distribution in this range: `CM0` has 1,310 `#define` lines, `CM1` has 265, `CNVC` has 154, `DSCL1` has 200, `DC` perfmon has 126, and `DPP` top-level has 56.
- Address-block comments in this chunk are `dce_dc_dpp0_dispdec_dpp_top_dispdec`, `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`, `dce_dc_dpp1_dispdec_cnvc_cfg_dispdec`, `dce_dc_dpp1_dispdec_cnvc_cur_dispdec`, `dce_dc_dpp1_dispdec_dscl_dispdec`, and `dce_dc_dpp1_dispdec_cm_dispdec`.
- The final per-file research document should be produced later by the reconciliation lane after all chunks for `dcn_3_1_6_sh_mask.h` are available.
