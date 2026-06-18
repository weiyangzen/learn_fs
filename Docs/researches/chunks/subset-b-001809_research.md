# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 17439-19949

## Scope

This chunk is a generated DCN 3.1.2 register-field mask slice from `dcn_3_1_2_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` values for field bit positions, `_MASK` values for 32-bit register masks, and comment markers that name registers and hardware address blocks. There are no C functions, structs, enums, branches, loops, local variables, or in-memory data structures in this range.

The range contains 2,114 generated `#define` lines, split almost evenly between field shifts and field masks. It starts in the tail of DPP1 color-management (`CM1`) fields, then covers DPP1 top/perfmon fields, and then moves through the DPP2 converter, cursor, scaler, and color-management register surface. The chunk ends partway through the `CM2_CM_SHAPER_RAMB_REGION_10_11` definition, so the following chunk must complete the remaining DPP2 CM shaper RAMB region fields.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.2 display hardware. The companion `dcn_3_1_2_offset.h` header supplies register addresses; this mask header supplies the field positions and masks consumed by register helper macros to encode values, decode MMIO readbacks, and perform read/modify/write updates without hard-coding numeric bit positions in functional code.

Major hardware areas represented here:

- Tail of `CM1` color-management fields for dealpha, coefficient format, shaper control, shaper LUT programming, shaper RAM A/B regions, 3D LUT programming, CM memory power status/control, and test/debug index/data.
- `DPP_TOP1` display pipe processor top controls for DPP enablement, expansion mode, gamut remap selection, realpha/dealpha controls, DPP reset, CRC capture/readback, CRC window programming, and host-read gating.
- `DC_PERFMON12`, a DPP performance monitor block with counter selection, increment mode, run/stop state, counter report selection, clock enable, counter-value interrupt status/ack bits, and low/high counter readback fields.
- `CNVC_CFG2`, the DPP2 input conversion/configuration block, including source pixel format, format-control mode bits, floating-point bias/scale, color keying, alpha LUTs, pre-dealpha/re-alpha, pre-degamma, pre-CSC matrices, and coefficient format.
- `CNVC_CUR2`, the DPP2 cursor block, including cursor enable, mode, pitch, line-per-chunk, 2x magnify, expansion mode, color0/color1, and floating-point scale/bias controls.
- `DSCL2`, the DPP2 scaler and line-buffer block, including coefficient RAM access, scaler mode/taps, 2-tap and manual replication controls, horizontal/vertical scale ratios and initial phases, recout/MPC/OTG geometry, line-buffer format/memory controls, DSCL and OBUF memory power controls/status, and autocal/update bits.
- Beginning and main body of `CM2`, the DPP2 color-management block, including post-CSC, gamut remap, bias, gamma-correction LUTs and RAM A/B PWL regions, blend-gamma LUTs and RAM A/B PWL regions, HDR multiplier, memory power controls/status, dealpha, coefficient format, shaper LUTs, shaper RAM A, and partial shaper RAM B regions.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw bitmask within the register.
- `// addressBlock: ...` comments identify the hardware aperture for the following register group.
- `//<REGISTER>` comments group the generated shift/mask pairs for one register.

Important field families in this chunk:

- Color-management mode fields include `CM_CONTROL`, `CM_POST_CSC_CONTROL`, `CM_GAMUT_REMAP_CONTROL`, `CM_GAMCOR_CONTROL`, `CM_BLNDGAM_CONTROL`, `CM_DEALPHA`, `CM_COEF_FORMAT`, and `CM_SHAPER_CONTROL`. They select enable modes, current-mode readback fields, RAM A/B selection, PWL disable controls, and coefficient numeric formats.
- CSC and gamut remap matrices are packed into paired coefficient registers such as `CM2_CM_POST_CSC_C11_C12`, `CM2_CM_POST_CSC_C33_C34`, `CM2_CM_GAMUT_REMAP_C11_C12`, and their `B_` variants. Each carries two coefficient fields, usually with low and high 16-bit masks.
- Gamma, blend-gamma, and shaper LUT access uses indexed data windows: `*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, and `*_LUT_WRITE_EN_MASK` fields. These fields are the register-level doorbell for loading piecewise-linear transfer functions into hardware RAM.
- RAM A/B PWL regions use repeated start, end, base, slope, offset, and region-pair registers. Region-pair registers such as `CM2_CM_GAMCOR_RAMA_REGION_0_1` and `CM2_CM_BLNDGAM_RAMB_REGION_32_33` pack a LUT offset and segment count for two adjacent regions, while start/end registers set channel-specific bounds for red, green, and blue.
- 3D LUT fields in the tail of `CM1` include `CM1_CM_3DLUT_MODE`, `CM1_CM_3DLUT_INDEX`, `CM1_CM_3DLUT_DATA`, `CM1_CM_3DLUT_DATA_30BIT`, `CM1_CM_3DLUT_READ_WRITE_CONTROL`, output normalization, and per-channel output offsets. These fields drive the DPP color pipeline's 3D lookup stage.
- DPP top fields include enable/configuration bits (`DPP_CLOCK_ENABLE`, `DPP_PIPE_CLOCK_ENABLE`, expansion mode), CRC controls and readback (`DPP_CRC_*`), and soft reset/status. These are used for pipe bring-up, reset sequencing, and validation.
- Perfmon fields include counter event selection, readback selection, increment mode, counter state, run-enable selection, report count, clock enable, counter-value interrupt status/ack for counters 0-7, and low/high counter-value registers.
- CNVC fields define input conversion behavior: surface pixel format, alpha enable/source/override, 10-bit and 12-bit component formatting, truncation/rounding modes, clamp controls, fixed/floating conversion bias/scale, pre-degamma, pre-CSC matrix values, and keyer channels.
- Cursor fields define whether cursor0 is enabled, how cursor memory is interpreted, pitch/line chunking, magnification, expansion, and palette/color values.
- DSCL fields define coefficient RAM bank/tap access, scaler operating mode, horizontal/vertical tap count, chroma/luma scale ratios and initial phases, autocalculation controls, overscan, recout and MPC geometry, line-buffer format/memory behavior, and DSCL/OBUF power state.
- Memory-power fields split force/disable controls from status readbacks: CM shaper/HDR 3D LUT controls in `CM*_CM_MEM_PWR_CTRL2`, CM gamma/blend controls in `CM2_CM_MEM_PWR_CTRL`, DSCL scaler and line-buffer controls in `DSCL2_DSCL_MEM_PWR_CTRL`, and status fields that report actual memory power state.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when Display Core code combines these constants with register addresses from the matching offset header and register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or generated `SF`/`SRI` tables.

A typical usage pattern is:

1. Select the DCN 3.1.2 register address for the target DPP instance from `dcn_3_1_2_offset.h` or an instance table.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack a field value into a 32-bit register word or extract a field from an MMIO readback.
3. Perform an MMIO write, read, or read/modify/write through the AMDGPU display register abstraction.
4. Let the hardware retain, consume, update, or clear the register-backed state according to the block's semantics.

The state represented here is hardware state, not software-owned persistent state:

- Color pipeline configuration, CSC coefficients, gamut matrices, shaper/gamma/blend transfer curves, 3D LUT values, format controls, cursor format, scaler geometry, and line-buffer mode persist in display hardware registers or RAMs until reprogrammed, reset, or power-gated.
- Current-mode fields, perfmon counter state, CRC values, memory-power status, line-buffer counters, soft-reset done/status, and host-read status are volatile hardware readbacks.
- LUT index/data windows and RAM A/B region registers are programming interfaces for hardware RAMs. Their contents are durable only while the relevant block and memory remain powered and are not reset or reloaded.
- ACK, reset, update, and clear-style fields are side-effecting write paths. They should not be treated like ordinary durable configuration bits.
- Memory-power force/disable fields affect whether dependent LUT, scaler, line-buffer, or output-buffer state can be reliably accessed. Callers must sequence power and clock controls around register programming.

The masks do not encode ordering or synchronization. Correct driver code must still enforce hardware sequencing: hold appropriate update locks when changing live pipe state, program LUT RAM through the expected index/data/write-enable order, avoid reading CRC or perfmon counters before capture/report state is valid, wait for reset/power status where required, and avoid updating scaler or color pipeline registers at scan positions that would create visible corruption.

## Dependencies And Integration Points

This chunk integrates with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`, which supplies the matching `reg...` addresses and base indices for the register names defined here.
- Display Core register helpers and generated shift/mask tables that use `FD_SHIFT`, `FD_MASK`, `SF`, `SRI`, `SRI_ARR`, `REG_GET`, `REG_SET`, and `REG_UPDATE` style macros.
- `dcn31` resource construction, which includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h` for DCN 3.1 register programming. Resource creation wires DPP instances, scalers, color blocks, OPPs, timing generators, AUX/I2C blocks, and IRQ services into the DC resource pool.
- DPP and MPC color code that programs degamma, regamma, shaper LUTs, 3D LUTs, gamut remap matrices, HDR multiplier, blend gamma, and post-CSC using the CM/CNVC register sets represented here.
- Plane programming paths that configure DPP input format, alpha behavior, color keying, cursor format, scaler taps, scaling ratios, recout geometry, and line-buffer format for each active plane.
- CRC and diagnostics paths that use `DPP_TOP1_DPP_CRC_CTRL`, `DPP_TOP1_DPP_CRC_VAL_R_G`, and `DPP_TOP1_DPP_CRC_VAL_B_A` to validate DPP output.
- Performance-monitoring code that configures `DC_PERFMON12` counters and samples low/high counter values or counter-value interrupt status for DPP2-related events.
- Clock, reset, and power-management paths that touch DPP top soft reset, DSCL memory power, OBUF memory power, line-buffer memory controls, and CM LUT memory power fields during pipe enable/disable, suspend/resume, and idle transitions.

The integration contract is name and numeric consistency. A missing macro name generally causes a compile-time failure in a generated table or register helper use. A wrong numeric mask or shift can compile successfully while programming the wrong hardware bits.

## Risks And Maintenance Notes

- Numeric drift from the ASIC register specification is the primary risk. A stale mask or shift can corrupt display pipe programming, color conversion, scaler state, LUT programming, CRC behavior, perfmon events, or power transitions.
- The range is heavily instance-prefixed. Confusing `CM1` with `CM2`, `CNVC_CFG2` with other CNVC instances, `DSCL2` with another scaler, or `DPP_TOP1` with a different top block can target the wrong pipe or a mismatched register address.
- The chunk straddles instance boundaries. It starts with DPP1 CM tail fields and then moves to DPP2 blocks; consumers should not assume every definition in the slice belongs to the same DPP instance.
- The end of the chunk is incomplete for `CM2_CM_SHAPER_RAMB_REGION_*`. Any per-file or per-block summary must merge with the following chunk before claiming full CM2 shaper RAMB coverage.
- LUT and PWL programming is ordering-sensitive. Writing data without the correct index, RAM selection, write-enable mask, or region bounds can create broken transfer curves, color artifacts, or inconsistent RAM A/B state.
- Current-mode/readback fields are not control fields. Treating `*_MODE_CURRENT` or memory-power status bits as writable control fields can produce ineffective writes or hide sequencing bugs.
- CSC, gamut, and bias fields are raw fixed-point representations. The header does not validate coefficient range, sign interpretation, matrix order, or channel packing.
- DSCL scaler ratio, phase, tap, and autocal fields interact with viewport size, recout size, chroma sampling, and line-buffer allocation. Incorrect programming can cause underflow, cropping, corruption, or incorrect chroma alignment.
- Memory power controls can make later LUT, scaler, line-buffer, or output-buffer register accesses unreliable if blocks are forced off or disabled while still in use.
- Perfmon and CRC fields have read/clear/capture semantics. Generic read/modify/write code must avoid accidentally acknowledging events or sampling partially updated values.

## Test Signals

Useful validation signals for this chunk are compile-time checks, generated-header consistency checks, and hardware/display exercise:

- Build AMDGPU Display Core with DCN 3.1 support and verify all referenced generated register-field names resolve against `dcn_3_1_2_sh_mask.h`.
- Run generated-header validation that every field has matching `_SHIFT` and `_MASK` definitions, masks are 32-bit bounded, bitfields do not overlap unexpectedly within each register, and register prefixes line up with the companion offset header.
- Exercise modesetting on pipes that use DPP1 and DPP2, including plane enable/disable, pipe reset, DPP clock enable, host-read control, and suspend/resume.
- Validate DPP2 plane input formats across RGB/YUV, 8/10/12-bit formats, alpha modes, pre-dealpha/re-alpha, pre-degamma, pre-CSC, color keying, and cursor enable/magnify modes.
- Program scaler paths using DSCL2 with scaling up/down, luma/chroma ratios, tap changes, coefficient RAM updates, recout/MPC geometry changes, overscan, autocal, and line-buffer format changes.
- Program color-management paths using CM2 post-CSC, gamut remap, gamma-correction RAM A/B, blend-gamma RAM A/B, shaper RAM A/B, HDR multiplier, and 3D/shaper-related memory power controls.
- Use CRC diagnostics through `DPP_TOP1_DPP_CRC_CTRL` and read `DPP_CRC_VAL_R_G`/`DPP_CRC_VAL_B_A` to confirm capture windows, enable bits, and reset/continuous behavior.
- Configure `DC_PERFMON12`, sample counter low/high values, trigger counter-value interrupts, and verify status/ack bits clear without losing counter state.
- Test memory-power sequencing for DSCL, line buffer, OBUF, CM shaper, HDR 3D LUT, gamma, and blend-gamma memory around blank/unblank, idle optimization, runtime PM, and full suspend/resume.

## Chunk-Specific Summary

Lines 17439-19949 define a dense generated register-field surface for DCN 3.1.2 DPP color, conversion, scaler, cursor, CRC, perfmon, and memory-power blocks. The most important responsibilities in this slice are DPP2 plane input conversion, DSCL2 scaler programming, DPP1/DPP2 color-management LUT and matrix programming, hardware RAM region layout for shaper/gamma/blend transfer curves, and status/control fields for diagnostics and power management. Correctness depends on exact mask/shift values, instance-correct register use, proper LUT and power sequencing, and successful hardware behavior under modeset, color-management, scaling, cursor, CRC, perfmon, and suspend/resume workloads.
