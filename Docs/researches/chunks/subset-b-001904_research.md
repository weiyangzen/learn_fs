# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 17420-19930

## Purpose

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains no executable C logic; it exports preprocessor constants that describe hardware register bit positions (`__SHIFT`) and masks (`_MASK`) for the display pipe processor (DPP), color management, scaler, perfmon, and related DPP instance blocks. Runtime code pairs these constants with addresses from `dcn_3_1_6_offset.h` and then uses the AMD display register helpers to program MMIO fields.

The requested range covers 2,511 source lines with 2,113 `#define` entries and 386 generated register/address-block comments. It starts in the middle of `CM1_CM_GAMCOR_RAMA_REGION_18_19`, covers the rest of the DPP1 color-management/gamma-correction tail, DPP1 top/perfmon metadata, DPP2 converter/cursor/scaler/color-management metadata, and ends inside `CM2_CM_BLNDGAM_LUT_CONTROL`. Adjacent chunks are required for the beginning of DPP1 gamma correction and the rest of DPP2 blend-gamma RAM metadata.

Although this file lives under a local `ceph-client` source mirror, the content is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, branches, or direct register reads/writes in this range. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- Address-block comments such as `// addressBlock: dce_dc_dpp2_dispdec_cm_dispdec`: generated grouping metadata that identifies the hardware block owning the following register fields.

Major register families in this chunk:

- `CM1_CM_GAMCOR_RAMA/RAMB_*`: tail of DPP1 gamma-correction programmable transfer-function RAM A/B fields. These define region start/end, start slope, start base, offsets, and 34 exponential region descriptors for blue/green/red channels.
- `CM1_CM_BLNDGAM_*`: DPP1 blend/output gamma control, LUT index/data/control fields, RAM A/B PWL region setup, offsets, and region descriptors.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, `CM1_CM_BIAS_*`, `CM1_CM_SHAPER_*`, and `CM1_CM_3DLUT_*`: DPP1 HDR multiplier, dealpha, coefficient format, shaper LUT, 3D LUT, output normalization/offset, memory-power, and debug fields.
- `DPP_TOP1_*`: DPP1 top-level clock enable/gating, soft reset, DPP CRC values/control, and host-read rate control fields.
- `DC_PERFMON12_*`: DPP1 display perfmon counter selection, counter state, run/clear/freeze/interrupt controls, current/high/low counter values, and interrupt/status fields.
- `CNVC_CFG2_*` and `CNVC_CUR2_*`: DPP2 converter surface pixel format, numeric format, alpha/keyer, pre-dealpha, pre-CSC matrices, pre-degamma, pre-realpha, cursor format/colors, and cursor FP scale/bias fields.
- `DSCL2_*`: DPP2 scaler coefficient RAM, scaler mode/taps/ratios/init values, recout/MPC/blanking geometry, line-buffer format and partitioning, memory power, output-buffer control, and status fields.
- `CM2_CM_*`: DPP2 color-management control, post-CSC and gamut-remap matrices, bias, gamma-correction control/LUT/RAM A/B, memory power, dealpha, coefficient format, shaper LUT, 3D LUT, debug, and the beginning of blend-gamma control/LUT fields.

Representative field patterns include 16-bit paired matrix coefficients, 13- or 14-bit geometry fields, 18-bit PWL base/slope/start values, 9-bit LUT offsets, 3-bit segment counts, 27-bit scaler ratios, per-channel color RAM selectors, current/active mode readback fields, memory-power force/disable/state fields, and write/ack/status bits for perfmon and LUT programming.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMD display code:

1. DCN316 resource code includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h`.
2. `dcn316_resource.c` builds `dpp_regs[]` with `DPP_REG_LIST_DCN30(id)` for DPP instances 0 through 3, and builds `tf_shift`/`tf_mask` with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`.
3. `dcn31_dpp_create()` passes the per-instance register addresses and shared shift/mask tables into `dpp3_construct()`.
4. DPP implementation code in the DCN10/DCN20/DCN30 family then calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and multi-field variants to program scaler setup, color matrices, gamma/shaper/3D LUTs, blend gamma, memory power, clock/reset control, cursor format, and diagnostic readback.

The macros do not encode ordering rules. Consumers must still sequence update locks, scaler programming, color pipeline updates, LUT host selection, RAM A/B double buffering, memory-power transitions, clock gating, reset, perfmon clear/enable/readback, and CRC operations correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed display hardware state. The represented state includes:

- DPP1 and DPP2 color pipeline state: bypass/update bits, post-CSC and gamut-remap matrices, bias, HDR multiplier, dealpha, coefficient format, gamma-correction modes, blend-gamma modes, shaper state, 3D LUT mode/index/data/format, and output normalization/offset.
- PWL/LUT state for gamma correction, blend gamma, and shaper RAMs: active/select/current modes, LUT indexes/data, color write masks, host selection, region starts, slopes, bases, offsets, and exponential region descriptors.
- DPP top state: clock enable/gating controls, soft reset bits, CRC source/mode/control, CRC values, and host-read rate control.
- DPP1 perfmon state: counter event selection, counted value type, counter run/stop selectors, active/state bits, report count, current values, high/low values, interrupt enable/status/ack, and counter interrupt status/ack.
- DPP2 converter/cursor/scaler state: pixel format, expansion/alpha/keyer settings, pre-CSC/pre-degamma/pre-realpha, cursor control/color/scale/bias, scaler mode/taps/ratios/init values, overscan/blanking/recout/MPC geometry, line-buffer partitioning, output-buffer mode, and scaler/output-buffer memory power.

Persistence is hardware-defined. Configuration fields usually retain values until a modeset, plane update, power gating, suspend/resume, or ASIC reset. Status/current/pending/ack/readback fields may be live, sticky, self-clearing, read-only, or write-one-to-clear depending on the register. This generated header only supplies bit layout; it does not express access type, side effects, double-buffering rules, or reset defaults.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies matching MMIO register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the generated DCN 3.1.6 headers and expands DPP register, shift, and mask lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, where `DPP_REG_LIST_DCN30` and `DPP_REG_LIST_SH_MASK_DCN30` map generic DPP fields onto generated register names.
- DPP implementation files in the DCN10/DCN20/DCN30 family, which use the resulting tables through register helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which also includes the DCN 3.1.6 generated headers for firmware-service register tables.

Important consumers and integration points:

- DPP construction creates up to four DPP instances on DCN 3.1.6. This chunk specifically covers instance-1 tail fields and instance-2 DPP/CNVC/DSCL/CM fields, so array instance mapping is critical.
- Color-management code uses `CM_GAMCOR`, `CM_BLNDGAM`, `CM_SHAPER`, `CM_3DLUT`, matrix, bias, dealpha, and HDR multiplier fields to implement DRM/AMDGPU color operations, HDR transfer functions, 3D LUT features, and plane/output gamma behavior.
- Scaler code uses `DSCL2_*` fields for manual scaler setup, line-buffer allocation, coefficient RAM programming, recout geometry, chroma/luma scaling, and memory-power handling.
- Cursor/converter paths use `CNVC_CFG2_*` and `CNVC_CUR2_*` fields for format conversion, alpha/keying, cursor format, cursor colors, and fixed-point cursor scale/bias.
- Diagnostics use `DPP_TOP1_DPP_CRC_*` and `DC_PERFMON12_*` for CRC and display perfmon validation.
- Resource capability setup in `dcn316_resource.c` advertises DPP color capabilities such as gamma correction, post CSC, hardware 3D LUT, output gamma RAM, and related color-management behavior that ultimately depends on these field definitions being correct.

## Risks And Edge Cases

- Generated-header drift is the central risk. These macros are untyped constants, so an incorrect shift or mask can compile cleanly while programming the wrong MMIO bits.
- The chunk boundary is artificial. Line 17420 is only the tail of a `CM1_CM_GAMCOR_RAMA` region register, and line 19930 stops inside `CM2_CM_BLNDGAM_LUT_CONTROL`; adjacent chunks are needed for complete DPP1 gamma and DPP2 blend-gamma coverage.
- Repeated DPP instance prefixes are copy-sensitive. `CM1`/`DPP_TOP1`/`DC_PERFMON12` and `CNVC_CFG2`/`DSCL2`/`CM2` describe different hardware instances; a valid-looking mask with the wrong prefix can drive the wrong pipe.
- Color pipeline fields are visually high impact. Wrong masks for CSC/gamut matrices, bias, coefficient format, degamma/gamma/blend/shaper/3D LUT, or HDR multiplier can cause color shifts, banding, broken HDR, bad alpha handling, or incorrect protected color-management state without crashing the kernel.
- PWL region fields are dense and repetitive. Off-by-one region descriptors, bad segment counts, wrong LUT offsets, or swapped channel fields can produce subtle transfer-function errors that only show under specific gamma/HDR/LUT configurations.
- LUT programming is double-buffered and selection-sensitive. Incorrect host-select, RAM A/B select, mode-current, write-color-mask, index, or data masks can update the inactive RAM, the wrong channel, or a partially visible LUT.
- Scaler and line-buffer fields are timing-sensitive. Bad tap counts, ratios, init fractions, recout size, line-buffer partitions, blanking geometry, or memory-power fields can create underflow, corrupted scaling, blank planes, or mode-specific failures.
- Clock, reset, memory-power, CRC, and perfmon fields may have side effects. Writes while a block is gated, reset, scanning out, or in a pending update can be ignored or disruptive. Status/ack fields may require exact clear/read order.
- Some current/status fields reflect hardware state rather than requested state. Tests that only write requested fields without checking current fields may miss failed updates or stale hardware state.

## Test Signals

Useful validation combines generated-header consistency checks with display behavior:

- Build AMDGPU/DC with DCN316 support. Missing or renamed macros should fail in `dcn316_resource.c`, `dcn30_dpp.h`, DCN30 DPP implementation files, and DMUB DCN316 code.
- Mechanically verify that every visible `__SHIFT` macro in lines 17420-19930 has the expected companion `_MASK` macro for the same field where the generated schema defines one.
- Diff this slice against AMD's authoritative DCN 3.1.6 register database and nearby generated DCN headers where hardware compatibility is expected.
- Exercise systems with enough active pipes to use DPP instances 1 and 2, including primary planes, overlays, scaling, cursor, SDR/HDR transitions, color-management updates, suspend/resume, and rapid atomic commits.
- Validate color paths with post-CSC, gamut remap, bias, HDR multiplier, gamma correction, blend gamma, shaper LUT, and 3D LUT programming. Signals include correct visual output, expected register dumps, no stale update-pending/current-mode state, and no channel swaps.
- Test LUT RAM A/B switching by updating gamma/blend/shaper LUTs while scanning out, then confirming that host selection, active selection, current mode, and per-channel data behave as expected.
- Run scaler stress modes: upscaling, downscaling, chroma formats, interleaved/alpha paths, large recout sizes, overscan, multiple displays, bandwidth-limited memory clocks, and memory low-power transitions. Watch for underflow, blanking, corruption, or bad line-buffer partitioning.
- Validate DPP CRC and `DC_PERFMON12` flows by clearing, selecting, enabling, freezing, reading, and acknowledging counters/status in the documented order; stale or impossible counter values are strong signals of field mismatch.
- Monitor kernel logs and display traces for DPP reset/gating problems, CM update-pending stalls, scaler memory-power state mismatches, LUT write failures, cursor/color-key artifacts, HDR/color regressions, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DPP1 gamma-correction RAM A region tables, including the start of `CM1_CM_GAMCOR_RAMA_REGION_18_19`. The next chunk continues `CM2_CM_BLNDGAM_LUT_CONTROL` and should cover DPP2 blend-gamma RAM A/B region setup after the two fields visible at the end of this range. The final per-file report should merge adjacent chunks before making complete statements about all DPP instances, all gamma/blend/shaper RAMs, or the full DCN 3.1.6 shift/mask namespace.
