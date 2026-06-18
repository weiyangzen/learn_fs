# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 27101-29604

## Scope And Purpose

This chunk is a generated-style AMD DCN 3.1.4 register shift/mask header segment. It contains C preprocessor constants only: no functions, structs, enums, storage definitions, or executable control flow. The range covers lines 27101-29604 of `dcn_3_1_4_sh_mask.h` and defines 2116 macros: 1058 `__SHIFT` constants and 1058 matching `_MASK` constants across 371 register symbols.

The purpose of this chunk is to describe field layouts for part of the display pipe color-management and DPP programming surface. It starts mid-register-family in the `CM2` color-management shaper RAMA region definitions, completes the visible `CM2` shaper RAMB region and HDR 3D LUT/test-debug fields, then moves through DPP instance 3 blocks: `DC_PERFMON12`, `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and a large portion of `CM3`. The `CM3` range covers color matrix/remap controls, gamma-correction LUTs and piecewise-linear RAMs, blend gamma LUTs and RAMs, HDR multiplier and memory-power fields, dealpha/coefficient format, and most shaper LUT/RAM definitions through `CM3_CM_SHAPER_RAMB_REGION_28_29`.

Every field is represented as a pair:

- `REGISTER__FIELD__SHIFT`, the bit offset for the field.
- `REGISTER__FIELD_MASK`, the field mask already shifted into register position.

This is the ABI consumed by AMDGPU/DC display register helpers together with companion DCN 3.1.4 offset/address headers. The file gives no semantic values itself; it provides the bit positions that make typed display programming code target the correct hardware fields.

## Important Macro Families

The `CM2_CM_SHAPER_*` tail covers the second color-management block's shaper lookup-table segmentation. The visible RAMA and RAMB region registers use pairs of regions per register, with LUT offset fields at low and high halves and segment-count fields at bit positions `0xc` and `0x1c`. The RAMB control groups include per-channel start and end controls for B/G/R, using 18-bit start values, 7-bit start-segment values, 16-bit end values, and 14-bit end-base values. These fields are used when programming piecewise shaper curves before 3D LUT processing.

The `CM2_CM_MEM_PWR_CTRL2` and `CM2_CM_MEM_PWR_STATUS2` fields expose memory-power force/disable/state bits for shaper and HDR 3D LUT memories. The `CM2_CM_3DLUT_*` fields describe 3D LUT mode/size/current mode, 11-bit LUT index, 16-bit paired LUT data, optional 30-bit data mode, write masks, RAM selection, read selection, output normalization, per-channel output offset/scale, and test-debug index/data access.

The `DC_PERFMON12_*` block defines display performance-monitor fields for DPP2/perfmon address block instance 12. It includes event selection, counted-value selection, increment/run modes, hardware start/stop/control selection, interrupt enable/status/ack fields, eight counter-state fields, perfmon state/report count, clock enable, run start/stop selectors, 48-bit-ish value readout split through low/high/misc fields, and read-selection fields. Consumers use these fields for diagnostics and performance counter collection rather than normal modeset image programming.

The `DPP_TOP3_*` block covers DPP instance 3 top-level controls: DPP clock enable and clock-gating disables, test-clock selection, soft reset for CNVC/DSCL/CM/OBUF sub-blocks, CRC result readback for RGBA components, CRC control, and host-read control. These fields are integration points for pipe bring-up, reset, debug CRC validation, and low-level host read access.

The `CNVC_CFG3_*` block describes the DPP3 converter configuration path. It includes surface pixel format, format control, floating-point conversion bias/scale per channel, color keyer enable and per-channel key values, alpha 2-bit LUT, pre-dealpha, pre-CSC mode and matrix coefficients, alternate `B` pre-CSC coefficient registers, coefficient format, pre-degamma mode, and pre-realpha controls. These fields sit early in per-plane processing and determine how source pixels are interpreted and transformed before scaling/color management.

The `CNVC_CUR3_*` block covers cursor overlay controls for DPP3: cursor enable/format, 2x magnification, pitch, line-per-chunk, color0/color1 values, and floating-point scale/bias. These constants are used by cursor programming paths for DPP3 cursor composition.

The `DSCL3_*` block defines DPP3 scaler and line-buffer fields. It includes coefficient RAM tap select/data, scaler mode and tap controls, two-tap hardcoded/sharpness controls, manual replication, horizontal/vertical scale ratios and initial phases for luma and chroma including bottom-field values, black color, update pending, autocal pipe metadata, overscan, OTG blanking, recout and MPC dimensions, line-buffer format and partitioning, line-buffer vertical counters, DSCL/LB/LUT memory-power controls and state readbacks, OBUF bypass/full-buffer/hold controls, and OBUF memory-power fields.

The `CM3_CM_*` block is the largest part of this chunk. It defines:

- Core bypass/update state in `CM3_CM_CONTROL`.
- Post-CSC mode/current mode plus 3x4 coefficient matrices for normal and `B` banks.
- Gamut remap mode/current mode plus 3x4 coefficient matrices for normal and `B` banks.
- Bias controls for Cr/R and Y/G/Cb/B channels.
- Gamma-correction mode/select/PWL-disable/current fields, LUT index/data/control, and RAMA/RAMB start, slope, base, end, offset, and region segmentation fields.
- Blend-gamma mode/select/PWL-disable/current fields, LUT index/data/control, and parallel RAMA/RAMB piecewise-linear controls.
- HDR multiplier coefficient, CM memory-power control/status, dealpha, coefficient-format controls, shaper control, shaper offsets/scales, shaper LUT access, shaper LUT write mask, and most shaper RAMA/RAMB segmentation fields.

The repeated `RAMA`/`RAMB` region families encode 34 piecewise regions as packed pairs. The recurring masks show a 9-bit LUT offset (`0x000001FF` or `0x01FF0000`) and a 3-bit segment count (`0x00007000` or `0x70000000`) for each region. Start/end controls and offsets are separated by color channel, reflecting the per-channel PWL programming model.

## APIs, Types, And Functions

There are no callable APIs, C types, function bodies, or inline helpers in this chunk. The effective API is the generated macro naming convention used by AMD register helpers:

- The register symbol prefix, such as `DSCL3_SCL_MODE` or `CM3_CM_GAMCOR_CONTROL`, identifies a hardware register whose address is supplied by a companion `dcn_3_1_4_*offset*` or address header.
- The field name between the double underscores identifies the programmable or readable bitfield.
- The `__SHIFT` macro gives the insertion/extraction shift.
- The `_MASK` macro gives the pre-shifted bit mask.

Some field names themselves end in `MASK`, producing generated identifiers such as `CM2_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_WRITE_EN_MASK_MASK` and `CM3_CM_SHAPER_LUT_WRITE_EN_MASK__CM_SHAPER_LUT_WRITE_EN_MASK_MASK`. These names are awkward but intentional because the generator preserves the hardware field name and then appends the macro-role suffix.

## Control Flow

The header has no local runtime control flow. The implied control flow lives in display driver code that includes this header:

1. Select the DCN 3.1.4 register address for a DPP/CM/DSCL/CNVC/perfmon register.
2. Compose or read a 32-bit MMIO register value.
3. Clear a field with `REGISTER__FIELD_MASK`.
4. Insert a value shifted by `REGISTER__FIELD__SHIFT`.
5. Write the register or extract readback/status fields through AMDGPU/DC register access macros.

The field families imply several external programming sequences. A DPP pipe setup typically enables clocks and releases soft resets, programs CNVC pixel format and pre-CSC/color-key/cursor state, configures DSCL ratios/taps/recout/line-buffer state, then programs CM post-CSC, gamut remap, gamma, blend gamma, shaper, and optional HDR 3D LUT state in a carefully ordered update sequence. LUT and PWL programming flows normally select an index or RAM bank, write data and region descriptors, set write-enable masks, then switch modes or wait for current-mode/update-pending fields to reflect hardware state. Perfmon flows select events and counter modes, start counting, read low/high value registers, and clear/ack interrupt status.

## State And Persistence Behavior

The macros do not hold software state. They describe persistent hardware register state in the DCN display controller. Values written through these fields remain in the relevant DPP/CM/DSCL/CNVC/perfmon hardware registers until reset, power-gating, modeset reprogramming, or hardware state-machine side effects change them.

State domains visible in this chunk include:

- Per-pipe DPP3 top-level clock, reset, host-read, and CRC diagnostic state.
- DPP3 converter source format, floating-point conversion, pre-CSC, color-key, pre-dealpha/pre-realpha, and cursor state.
- DPP3 scaler ratios, taps, coefficient RAM contents, phase initialization, recout/MPC dimensions, overscan/blanking, line-buffer partitioning, update-pending state, and DSCL/OBUF memory-power state.
- CM2 shaper/HDR 3D LUT and CM3 gamma/blend-gamma/shaper/3D-color-management LUT programming state.
- CM3 matrix state for post-CSC and gamut remap, including alternate `B` coefficient banks and current-mode readbacks.
- Memory-power force/disable/status state for CM, shaper, HDR 3D LUT, DSCL LUT/LB groups, and OBUF memories.
- Perfmon event selection, run state, interrupt status/ack state, and counter readback state.

Many fields are mode-programming state, but others are hardware-observed status or handshake state. Examples include `*_MODE_CURRENT`, `CM_UPDATE_PENDING`, `SCL_UPDATE_PENDING`, memory-power `*_STATE`, CRC values, perfmon active/status bits, counter interrupt status/ack bits, and line-buffer vertical counters. Callers must treat these according to the hardware specification, especially for write-one-to-clear or readback-latched status fields.

## Dependencies And Integration Points

This chunk depends only on the C preprocessor, but it is useful only with AMDGPU/DCN register infrastructure:

- Companion DCN 3.1.4 register address/offset headers provide the MMIO addresses corresponding to these shift/mask macros.
- AMD display-core register helper macros combine register addresses, field masks, and shifts for `REG_SET`, `REG_UPDATE`, `REG_GET`, or generated table-style accessors.
- DPP/DPP3 resource construction and pipe programming code consumes `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and `CM3` fields for per-plane image processing.
- Color-management code consumes `CM*_CM_POST_CSC`, `CM*_CM_GAMUT_REMAP`, `CM*_CM_GAMCOR`, `CM*_CM_BLNDGAM`, `CM*_CM_SHAPER`, and `CM*_CM_3DLUT` fields when programming CSC matrices, transfer functions, gamma ramps, shaper LUTs, blend gamma, and HDR 3D LUTs.
- Scaling code consumes `DSCL3_*` fields for tap programming, scale ratios, initial phase, line-buffer memory, output size, and scaler update.
- Cursor code consumes `CNVC_CUR3_*` fields for cursor format, colors, pitch, magnification, and FP scale/bias.
- Debug and validation paths consume `DPP_TOP3_DPP_CRC_*`, `CM2_CM_TEST_DEBUG_*`, and `DC_PERFMON12_*` fields for CRC, test/debug access, and performance counters.
- Power-management and clock-gating code consumes memory-power and clock-gating fields to save power or force memories on for programming/debug.

The repeated instance prefixes are integration-critical. `CM2` belongs to one DPP/color-management instance, while `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and `CM3` belong to instance 3. Using the wrong instance prefix can silently program the wrong pipe.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Shift/mask constants compile as ordinary macros; if one value is wrong, callers can overwrite reserved bits or unrelated fields without compiler warnings. Symptoms would appear as incorrect color, broken scaling, missing cursor, failed LUT programming, black screens, power-gating issues, CRC mismatches, or invalid perfmon data.

Boundary risk is high for this chunk. It begins inside `CM2_CM_SHAPER_RAMA_REGION_2_3`, because the `REGION2` shift/mask entries and part of the `REGION3` entries are in the prior chunk. It also ends inside the `CM3_CM_SHAPER_RAMB_REGION_28_29` family, before the remaining mask entries and later shaper RAMB regions appear in the next chunk. The final per-file report must reconcile adjacent chunks before describing those register families as complete.

The repeated PWL region patterns are copy/generation-sensitive. Region pairs use fixed positions for low/high LUT offsets and segment counts; an off-by-one region number, swapped channel suffix, or mismatched RAMA/RAMB prefix would only affect particular gamma/shaper curve segments and may be visible only on specific color-management configurations.

Mode/current and update-pending fields are sequencing-sensitive. Programming CM matrices, gamut remap, gamma, blend gamma, shaper, and 3D LUT state requires callers to respect bank selection, write-enable masks, current-mode readbacks, and update handshakes. Incorrect ordering can leave stale LUTs or half-applied color transforms.

Memory-power fields can interact with programming. Forcing memories off or relying on power-gated RAM while writing DSCL coefficient RAM, line-buffer state, shaper RAMs, gamma RAMs, or HDR 3D LUT entries can cause writes to be lost or readbacks to look invalid. Status fields should be polled or managed through existing power sequencing.

Mask literal width is a C-integration risk. Many masks use `L` suffixes, including `0xFFFFFFFFL`, `0xFFFF0000L`, and high-bit masks. Callers should use unsigned 32-bit-safe intermediates through the existing register helpers rather than ad hoc signed arithmetic.

Perfmon and debug fields can perturb state if used carelessly. Counter control, interrupt ack, debug index/write-enable, CRC one-shot/continuous state, and host-read controls are meant for diagnostics. Accidental writes during normal modeset paths can hide real performance data or disturb debug/readback flows.

## Test Signals

Useful validation signals are mostly build, static-generation, and hardware integration checks:

- Build coverage for DCN 3.1.4 display code that includes `dcn_3_1_4_sh_mask.h` and instantiates register-field tables for DPP, DSCL, CNVC, cursor, CM, and perfmon blocks.
- Static checks that every `REGISTER__FIELD__SHIFT` in this range has the expected `REGISTER__FIELD_MASK`, masks align to shifts, and generated high/low packed fields do not overlap.
- Diff checks against AMD's authoritative DCN 3.1.4 register database or generated header source, especially around the partial chunk boundaries and repeated RAMA/RAMB region families.
- Modeset tests using DPP3 with scaling enabled/disabled, different pixel formats, chroma formats, pre-CSC, color keying, cursor formats, and recout/MPC sizes.
- Color-management tests covering post-CSC, gamut remap, gamma correction, blend gamma, shaper LUTs, HDR multiplier, HDR 3D LUT, 30-bit 3D LUT mode, alternate coefficient banks, and update-pending/current-mode transitions.
- LUT/RAM programming tests that write and read back gamma, blend-gamma, shaper, DSCL coefficient RAM, and 3D LUT entries across boundary indices and region pairs.
- Power-management tests that exercise CM, DSCL, line-buffer, OBUF, shaper, and HDR 3D LUT memory power states across suspend/resume, blanking, and pipe enable/disable.
- CRC/debug/perfmon tests that enable DPP3 CRC, read RGBA CRC values, configure `DC_PERFMON12` events/counters/interrupt ack paths, and verify counter values remain stable across normal display operation.

## Cross-Chunk Notes

This is chunk 12 of 26 for `dcn_3_1_4_sh_mask.h`. It should be merged with prior chunks for the start of `CM2` shaper/gamma/color-management definitions and with following chunks for the rest of `CM3_CM_SHAPER_RAMB_REGION_28_29`, later `CM3` fields, and subsequent DCN 3.1.4 register blocks. The final per-file document should present this as generated field metadata for the full DCN 3.1.4 display register set, not as an independently complete API module.
