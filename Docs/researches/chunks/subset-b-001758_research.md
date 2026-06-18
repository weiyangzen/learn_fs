# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 17357-19868

Chunk: `subset-b-001758`
Covered source range: lines 17357-19868 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h`

## Purpose

This chunk is a generated AMD DCN 3.0.2 register shift/mask header section. It does not implement runtime logic; it publishes C preprocessor constants that describe bit positions and masks for display hardware registers. Driver code combines these constants with matching register-address macros from `dcn_3_0_2_offset.h` and register helper macros such as `REG_SET`, `REG_UPDATE`, and field-table builders to program AMDGPU display blocks.

The range is concentrated on Display Pipe Processor color-management and related DPP instance-2 metadata:

- the tail of `CM1` blend-gamma RAM-B region programming and the rest of `CM1` HDR multiplier, memory power, dealpha, coefficient format, shaper LUT, shaper RAM-A/RAM-B, 3D LUT, and test/debug fields;
- `DC_PERFMON12` performance-counter control, state, monitor control, compare-value interrupt, and counter readout fields;
- `DPP_TOP2`, `CNVC_CFG2`, `CNVC_CUR2`, and `DSCL2` fields for DPP instance 2 control, conversion, cursor, scaler, line-buffer, and output-buffer state;
- the beginning and bulk of the `CM2` color-management block, including post-CSC, gamut-remap, gamma-correction RAM-A/RAM-B, blend-gamma RAM-A/RAM-B, shaper, memory-power, 3D-LUT, and shaper RAM-A fields;
- the first fields of `CM2_CM_SHAPER_RAMB_END_CNTL_B`, with the matching continuation in the next chunk.

Although the repository path includes `ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem behavior, distributed storage state, networking path, or persistence semantics beyond compiled kernel constants used by the GPU display driver.

## Important APIs, Types, And Macros

There are no functions, structs, typedefs, enums, global variables, or callable APIs in this chunk. Its public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit shift for encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.

Important macro families in this range include:

- `CM1_CM_BLNDGAM_RAMB_REGION_24_25` through `CM1_CM_BLNDGAM_RAMB_REGION_32_33`: tail of DPP1 blend gamma RAM-B region descriptors. Each region-pair register encodes two piecewise-linear region LUT offsets and segment counts with offsets at bits 0 and 16, segment counts at bits 12 and 28, 9-bit LUT-offset masks, and 3-bit segment-count masks.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_STATUS`, `CM1_CM_MEM_PWR_CTRL2`, and `CM1_CM_MEM_PWR_STATUS2`: CM1 HDR multiplier and memory power force/disable/status fields for gamma-correction, blend-gamma, shaper, and 3D-LUT memories.
- `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, `CM1_CM_SHAPER_*`, and `CM1_CM_3DLUT_*`: CM1 dealpha enable/ablend, coefficient-format selectors, shaper LUT mode/current mode, shaper offsets/scales, shaper LUT index/data/write selection, RAM-A/RAM-B shaper region programming, 3D-LUT mode/current mode/index/data/read-write control, output normalization, and output RGB offsets.
- `CM1_CM_TEST_DEBUG_INDEX` and `CM1_CM_TEST_DEBUG_DATA`: indexed CM test/debug readback and write data selectors.
- `DC_PERFMON12_PERFCOUNTER_*` and `DC_PERFMON12_PERFMON_*`: performance event select, value select, counter increment/run/restart/interrupt controls, counter state machine, compare-value interrupt status/clear/mode/mask/select, and high/low counter readouts.
- `DPP_TOP2_DPP_CONTROL`, `DPP_TOP2_DPP_SOFT_RESET`, `DPP_TOP2_DPP_CRC_*`, and `DPP_TOP2_HOST_READ_CONTROL`: DPP2 enable, clock-gate disable, output muxing, soft reset, CRC values/control, and host readback mode.
- `CNVC_CFG2_*`: DPP2 converter and pre-color-stage fields for surface pixel format and alpha-plane enable, format bypass/alpha/expansion/crossbar/clamping, floating-point conversion bias/scale, color/luma keying, 2-bit alpha LUT, pre-dealpha/pre-realpha, pre-CSC mode/current mode, A/B pre-CSC coefficient matrices, coefficient format, and pre-degamma mode/select.
- `CNVC_CUR2_CURSOR0_*`: cursor enable, mode, 2x magnify, expansion, alpha, position readback mode, color entries, and floating-point cursor scale/bias.
- `DSCL2_*`: DPP2 scaler coefficient RAM access, scaler mode/taps/control, manual replication, luma/chroma horizontal and vertical scale ratios and initial phases, black color, update-autocal state, overscan, OTG blanking, recout/MPC sizing, line-buffer format, memory control/status, FIFO status, v-counter, and output-buffer controls.
- `CM2_CM_CONTROL`, `CM2_CM_POST_CSC_*`, `CM2_CM_GAMUT_REMAP_*`, and `CM2_CM_BIAS_*`: DPP2 color-management bypass/update-pending state, post-CSC mode/current mode, A/B post-CSC matrices, gamut-remap mode/current mode, A/B gamut-remap matrices, and bias channels.
- `CM2_CM_GAMCOR_*` and `CM2_CM_BLNDGAM_*`: DPP2 gamma-correction and blend-gamma mode/select/current/PWL controls, LUT index/data/control, RAM-A/RAM-B start/end/slope/base/offset descriptors, and 34-region paired region descriptors.
- `CM2_CM_HDR_MULT_COEF`, `CM2_CM_MEM_PWR_*`, `CM2_CM_DEALPHA`, `CM2_CM_COEF_FORMAT`, `CM2_CM_SHAPER_*`, and `CM2_CM_3DLUT_*`: DPP2 equivalents of CM1 HDR, memory power, dealpha, coefficient format, shaper, and 3D-LUT fields.

The chunk is boundary-split. It begins in the middle of the `CM1_CM_BLNDGAM_RAMB_REGION_24_25` macro group: the first line in this chunk is the mask for region 24's LUT offset, while the comment and shift macros are in the previous chunk. It ends at the first two shift macros for `CM2_CM_SHAPER_RAMB_END_CNTL_B`; its masks and the G/R RAM-B end-control fields continue in the next chunk.

## Control Flow

This header has no runtime control flow. Each line is a compile-time constant consumed by generated register tables and read/modify/write helper paths.

Typical consumer control flow is:

1. Display code builds a software state for a DPP pipe: pixel conversion, pre-CSC, scaler ratios, cursor state, line-buffer format, color transforms, gamma curves, shaper curves, 3D LUTs, memory power state, diagnostics, or perf counters.
2. The relevant DCN generation header maps logical fields to instance-prefixed register names using shift/mask constants from this file and addresses from `dcn_3_0_2_offset.h`.
3. Register helper macros clear the target `_MASK`, shift the input by the matching `__SHIFT`, and write or update the hardware register.
4. Hardware latches the state according to the target block: immediate write, update lock, mode/current handoff, vertical update, LUT write sequence, memory-power transition, or readback/status polling.

Several field groups indicate sequenced state rather than simple configuration. `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `*_UPDATE_PENDING`, `*_MEM_PWR_STATE`, `*_MEM_PWR_STATUS`, `*_SOFT_RESET`, `*_CRC_*`, `*_PERFCOUNTER_STATE`, `*_PERFMON_CVALUE_INT_*`, `*_LUT_INDEX`, `*_LUT_DATA`, and `*_LUT_WRITE_*` fields are normally used in ordered programming flows with polling, readback, or explicit handoff points.

## State And Persistence Behavior

The header itself is stateless and persists nothing. The state described by these constants lives in DCN 3.0.2 display hardware registers and in compiled driver register-field tables.

Hardware state represented by this chunk includes:

- color pipeline state: CM bypass/update-pending, dealpha, coefficient formats, post-CSC matrices, gamut-remap matrices, bias, HDR multiplier, gamma-correction and blend-gamma modes, and current-mode readbacks;
- LUT state: gamma-correction RAM-A/RAM-B, blend-gamma RAM-A/RAM-B, shaper RAM-A/RAM-B, 3D LUT index/data, 30-bit 3D LUT data, 3D LUT output normalization and offsets, and LUT write/read color selection controls;
- converter and cursor state: source pixel format, alpha-plane enable, format expansion, channel crossbar, clamp behavior, pre-dealpha/realpha, pre-degamma, pre-CSC matrices, color keying, alpha LUT, cursor enable/mode/magnification/alpha, cursor colors, and cursor scale/bias;
- scaler and line-buffer state: coefficient RAM contents, tap counts, luma/chroma ratios and phases, overscan, recout/MPC size, line-buffer format, memory partitions, request/data FIFO status, memory power state, and output-buffer controls;
- diagnostics and monitoring state: DPP CRC capture, host-read control, CM test/debug indexed registers, and `DC_PERFMON12` event selection, counter state, interrupt compare values, and high/low counter values;
- power/reset state: DPP soft reset, CM and DSCL memory power force/disable/status bits, and clock-gate disable controls.

Most configuration fields persist until a modeset, atomic commit, LUT/color update, suspend/resume, GPU reset, display block reset, or runtime power transition reprograms them. Status fields and interrupt/comparison bits are transient and may be level-sensitive, latched, write-one-to-clear, or readback-only depending on the hardware register specification. The mask header does not encode access type or required ordering.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.2 register database. The constants are meaningful only with the matching register address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`

Practical integration points are AMDGPU Display Core and DRM/KMS color, plane, and diagnostics paths:

- DPP resource construction and generation-specific register tables include DCN `*_sh_mask.h` and `*_offset.h` headers to populate field masks/shifts for DPP, scaler, input pixel processor, and color-management helpers.
- Color-management code maps DRM color properties, degamma/regamma, CTM/CSC, shaper LUT, 3D LUT, and HDR multiplier state into CM and CNVC fields. The user-facing 3D LUT properties in `amdgpu_dm_color.c`, `amdgpu_dm_plane.c`, and `amdgpu_mode.h` ultimately rely on generated field metadata like these when the hardware path supports the block.
- DPP/scaler programming uses `DSCL2_*`, `CNVC_CFG2_*`, and `DPP_TOP2_*` fields to translate plane state into converter, scaling, line-buffer, viewport, CRC, and output sizing registers.
- Power-management and reset paths use `*_MEM_PWR_CTRL`, `*_MEM_PWR_STATUS`, `*_MEM_PWR_CTRL2`, `*_MEM_PWR_STATUS2`, `DPP_TOP2_DPP_SOFT_RESET`, `DSCL2_DSCL_MEM_PWR_*`, and `DSCL2_OBUF_MEM_PWR_CTRL` to sequence block memories and resets.
- Diagnostics and performance paths use `DPP_TOP2_DPP_CRC_*`, `CM*_CM_TEST_DEBUG_*`, and `DC_PERFMON12_*` to validate output, inspect internal state, count events, and compare counter thresholds.

The field layout also aligns with later-generation MPC/DPP shaper and 3D-LUT programming patterns. For example, DCN3.2 MPC code programs shaper RAM-A/RAM-B start/end/region registers with the same conceptual fields: per-channel start points, end bases, region LUT offsets, segment counts, LUT index/data, and RAM select/write masks. That makes the repeated DCN 3.0.2 CM1/CM2 shaper fields integration-sensitive even though this file contains only raw macros.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped integer macros; an incorrect mask, shift, register prefix, or field pairing can compile successfully while corrupting a neighboring field or programming the wrong display pipe.

High-risk areas include:

- Repeated instance prefixes. `CM1` and `CM2` fields are structurally similar but target different DPP instances. Mixing prefixes can update the wrong pipe's color or LUT state while leaving the intended pipe unchanged.
- Boundary-split macro groups. This chunk is incomplete for `CM1_CM_BLNDGAM_RAMB_REGION_24_25` at the start and `CM2_CM_SHAPER_RAMB_END_CNTL_B` at the end. Chunk-local mask/shift-pair checks must account for adjacent chunks; the final file merge should verify complete pairs.
- LUT programming order. Gamma, blend-gamma, shaper, and 3D LUT fields require correct index/data/write-enable sequencing and correct RAM-A/RAM-B selection. Wrong `*_LUT_WRITE_SEL`, color mask, index width, data mask, or region segment count can cause banding, bad colors, stale LUTs, or partial updates.
- Color-matrix and coefficient formats. CSC, gamut-remap, bias, coefficient-format, pre-CSC, and format-conversion fields are dense and repetitive. Bad shifts or signedness assumptions can alter color range, HDR/SDR mapping, channel order, or fixed-point interpretation.
- Mode/current handoff. Fields with both requested and current values, such as `*_MODE` and `*_MODE_CURRENT`, can be misread as writable state or sampled too early. Consumers must respect hardware update timing rather than assuming immediate current-mode changes.
- Memory power and reset sequencing. Forcing or disabling CM, shaper, 3D-LUT, DSCL, or OBUF memory while the block is active can blank output or lose LUT state. Status fields should be polled using the proper block sequence.
- Scaler and line-buffer programming. Ratio, phase, tap, overscan, recout, MPC size, and line-buffer memory fields must match plane and timing state. Incorrect masks can produce cropping, unstable scaling, underflow, or corrupted scanout.
- Interrupt/perfmon semantics. `DC_PERFMON12` compare interrupt fields and counter run/restart controls must be updated in the expected order. Confusing status, clear, mask, and mode fields can miss performance events or leave interrupts asserted.
- High-bit masks. Constants such as `0xFFFF0000L` and `0x70000000L` should be handled through existing fixed-width register helpers, not ad hoc signed arithmetic.

## Test Signals

Useful validation signals are mostly build, generated-header, and hardware-behavior oriented:

- Kernel build coverage for DCN 3.0.2 display code that includes `dcn_3_0_2_sh_mask.h`; missing or renamed field macros should fail compilation.
- Generated-register-map comparison against AMD's authoritative DCN 3.0.2 database, verifying every shift/mask in lines 17357-19868 and reconciling boundary-split fields with adjacent chunks.
- Static checks that every non-boundary `_MASK` has a matching `__SHIFT`, repeated `CM1`/`CM2` register layouts stay intentionally identical where expected, and every register has a matching address macro in `dcn_3_0_2_offset.h`.
- DRM/KMS modeset and atomic plane tests covering DPP2 converter formats, alpha-plane handling, cursor modes, pre-CSC, scaler ratios/phases/taps, recout/MPC sizing, and line-buffer behavior.
- Color-management tests for post-CSC, gamut remap, bias, coefficient formats, HDR multiplier, gamma-correction LUTs, blend-gamma LUTs, shaper LUTs, 3D LUT programming, RAM-A/RAM-B switching, and current-mode readback.
- Visual and CRC tests using `DPP_TOP2_DPP_CRC_*` and CM test/debug registers to detect wrong color transforms, channel swaps, LUT corruption, scaling errors, or stale register programming.
- Power-management and reset tests across suspend/resume, runtime display power transitions, GPU reset, pipe disable/enable, and LUT reprogramming after CM/DSCL memory power changes.
- Performance-counter tests that configure `DC_PERFMON12`, start/stop counters, read high/low values, trigger compare interrupts, and verify clear/mask behavior without disturbing adjacent control fields.

Regression symptoms from incorrect constants include blank or corrupted scanout, wrong colors, banding, failed HDR or 3D-LUT validation, bad cursor blending, scaler artifacts, underflows, stuck update-pending/current-mode state, failed CRC checks, missed perfmon interrupts, or display failures after power transitions.

## Cross-Chunk Notes

This is chunk 8 of 26 for the large generated `dcn_3_0_2_sh_mask.h` file. Earlier chunks define the beginning of the DCN 3.0.2 register map and the preceding CM1 blend-gamma groups. Later chunks complete `CM2_CM_SHAPER_RAMB_END_CNTL_B`, continue the remaining CM2 shaper RAM-B region fields, and proceed through subsequent DCN display blocks. The final per-file document should treat this source as generated hardware ABI metadata and merge these notes with adjacent chunks before drawing conclusions about complete per-register definitions.
