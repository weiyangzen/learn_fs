# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 19931-22447

## Scope

This chunk is a generated AMD DCN 3.1.6 register field header segment. It contains only C preprocessor constants: `__SHIFT` and `_MASK` values for packed hardware register fields. There are no functions, structs, storage definitions, or executable control-flow blocks in the chunk. Runtime behavior comes from consumers that include this header with the matching `dcn_3_1_6_offset.h` register-address header and feed the constants into AMD display register helper macros.

The source path must remain tied to `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`; this is a partial chunk report for lines 19931-22447 only.

## Purpose

The chunk maps bit layouts for several display-pipe hardware blocks:

- Tail of DPP2 color-management blender gamma (`CM2_CM_BLNDGAM_*`) LUT, region, shaper, memory-power, 3D LUT, and debug fields.
- DPP2 top-level, host-read, CRC, and soft-reset fields (`DPP_TOP2_*`).
- DC perfmon block 13 fields (`DC_PERFMON13_*`) for counter control, counter state, value selection, manual/clear control, and high/low counter reads.
- DPP3 CNVC configuration and cursor fields (`CNVC_CFG3_*`, `CNVC_CUR3_*`) for pixel format, fixed-point conversion bias/scale, color keying, alpha LUT, pre-dealpha/pre-realpha, pre-CSC coefficients, and cursor color/control.
- DPP3 scaler/display scaler fields (`DSCL3_*`) for coefficient RAM, scaler modes, taps, ratios, recout/MPC sizes, line buffer state, memory power, and output buffer configuration.
- Start of DPP3 color-management fields (`CM3_CM_*`), including control, post-CSC, gamut remap, bias, gamma-correction LUTs, gamma-correction PWL region programming, blender-gamma control/LUTs, and the start of blender-gamma RAM B region programming.

The constants let shared DCN display code access hardware registers by symbolic field name instead of embedding numeric bit positions throughout the driver.

## Important APIs, Types, and Macro Contracts

This chunk does not define APIs in the function-call sense. Its public contract is the macro naming scheme:

- `REGISTER__FIELD__SHIFT` gives the right-shift amount for extracting or placing a field.
- `REGISTER__FIELD_MASK` gives the unshifted register mask for the same field.
- Register comments such as `//CM3_CM_BLNDGAM_RAMA_REGION_0_1` group the following field constants by hardware register.
- Prefixes encode instance/block identity. For example, `CM2_` is color management under DPP instance 2, `CM3_` is the DPP instance 3 color-management block, `DSCL3_` is scaler instance 3, and `DC_PERFMON13_` is perfmon instance 13.

The integration layer is visible in nearby consumers:

- `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes `dcn/dcn_3_1_6_offset.h` and this file, then initializes DPP shift and mask tables with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h` defines field-list macros and shift/mask table member lists for color-management fields such as `CM_BLNDGAM_RAMA_EXP_REGION*_LUT_OFFSET`, `CM_BLNDGAM_RAMB_EXP_REGION*_NUM_SEGMENTS`, `CM_3DLUT_*`, `CM_SHAPER_*`, and memory-power fields.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.c` uses register helpers such as `REG_GET` against fields like `CM_BLNDGAM_CONFIG_STATUS`, relying on the generated shift/mask tables populated from this header.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c` also includes this header for DCN316 DMUB-side register bit definitions.

## Register Groups in This Chunk

### CM2 Blender Gamma and Shaper Tail

Lines 19931-20376 complete the `CM2_CM_BLNDGAM_*` region that began before the chunk. The first visible entries finish `CM2_CM_BLNDGAM_LUT_CONTROL`, including write color mask, read color select, debug read, host select, and config mode fields. The section then defines:

- `CM2_CM_BLNDGAM_RAMA_*` start, slope, base, end, offset, and 34 region descriptors.
- `CM2_CM_BLNDGAM_RAMB_*` with the same double-buffered PWL region layout.
- Per-channel start/end fields for B, G, and R, generally with 18-bit or 19-bit value masks and segment selectors at shift `0x14`.
- Region-pair registers `REGION_0_1` through `REGION_32_33`, each packing two LUT offsets and two segment-count fields into one 32-bit register.

Lines 20377-20873 continue with CM2 color blocks: HDR multiplier coefficient, memory-power control/status, dealpha, coefficient format, shaper control/LUT/index/data, shaper RAM A/B region programming, second memory-power controls, 3D LUT mode/index/data/read-write control/out normalization/offsets, and test debug index/data.

These fields support the display color pipeline around programmable transfer functions: shaper LUT, blender gamma LUT, and 3D LUT. The hardware-visible state is register-resident, not persisted by this header.

### DPP2 Top and Perfmon

Lines 20874-20939 switch to `dce_dc_dpp2_dispdec_dpp_top_dispdec`. The defined fields cover DPP control, soft reset, CRC values/control, and host read control. These are top-level display-pipe control and diagnostics fields for instance 2.

Lines 20940-21076 switch to `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`. The `DC_PERFMON13_*` fields describe performance-counter setup: enable/reset/start modes, event selectors, perfmon state bits, selected counter value fields, and high/low counter registers. Runtime code can configure these counters to observe display hardware behavior.

### DPP3 CNVC, Cursor, and Scaler

Lines 21077-21243 define `CNVC_CFG3_*` fields. The converter configuration includes surface pixel format, format expansion and alpha enable bits, fixed-point conversion biases/scales, color-key control and per-channel key values, a 2-bit alpha LUT, pre-dealpha, pre-CSC mode and coefficient matrices, coefficient format, pre-degamma, and pre-realpha.

Lines 21244-21271 define `CNVC_CUR3_*` cursor fields: cursor enable/mode/2x magnify/control bits, cursor color entries, and cursor fixed-point scale/bias fields.

Lines 21272-21508 define `DSCL3_*` fields. They cover scaler coefficient RAM tap select/data, scaler mode, tap control, DSCL control, two-tap control, manual replicate, horizontal/vertical scale ratios and initial phases for luma/chroma, black color, update/autocal, extended overscan, OTG blanking, recout and MPC sizing, line-buffer data/memory control, vertical counter, scaler memory-power control/status, output buffer control, and output-buffer memory-power control.

These fields are central to display-pipe programming. A wrong shift or mask can change scaling, cursor rendering, color conversion, memory power, or diagnostics on a specific DPP instance.

### DPP3 Color Management

Lines 21509-22447 define the start and middle of `dce_dc_dpp3_dispdec_cm_dispdec`:

- `CM3_CM_CONTROL`, post-CSC control and coefficient matrix fields.
- Gamut remap control and coefficient matrix fields.
- Bias registers for chroma/red and luma/green/chroma-blue channels.
- `CM3_CM_GAMCOR_*` mode, LUT index/data/control, RAM A/B start/slope/base/end/offset, and 34 region descriptors.
- `CM3_CM_BLNDGAM_CONTROL`, LUT index/data/control, RAM A region programming through region `32_33`, and start of RAM B programming through `CM3_CM_BLNDGAM_RAMB_REGION_2_3`.

The gamma-correction and blender-gamma sections use highly repetitive double-buffered RAM A/RAM B layouts. Start registers carry a base value and a start segment, slope/base/end registers define the piecewise-linear curve endpoints, offset registers apply per-channel offsets, and region-pair registers assign LUT offsets plus segment counts for regions 0-33.

## Control Flow

There is no local control flow. The effective runtime flow is indirect:

1. DCN316 resource code includes this header and the matching offset header.
2. Field-list macros expand the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants into `tf_shift` and `tf_mask` tables for a DPP instance.
3. Register helper macros such as `REG_GET`, `REG_SET`, or equivalent AMD DC helpers use the register address, mask, and shift to read-modify-write 32-bit hardware registers.
4. Higher-level display code programs color transforms, scalers, cursors, power gates, diagnostics, and performance counters through those helpers.

The generated constants therefore influence control flow elsewhere only by determining which bits the helpers read or modify.

## State and Persistence

The header itself has no memory state and no persistent storage. It defines compile-time constants. The state affected by those constants lives in:

- Memory-mapped DCN display registers.
- Hardware LUT RAMs or indexed register windows reached through LUT index/data/control fields.
- Runtime C structs such as DPP shift/mask tables initialized from the macros.

Hardware register writes persist only as long as the display hardware, power state, and driver programming sequence preserve them. Power gating, reset, mode-set, or suspend/resume can clear or reprogram the underlying hardware state.

## Dependencies and Integration Points

Primary dependencies are generated alongside this file:

- `dcn_3_1_6_offset.h` for register addresses and base indices.
- `reg_helper.h` and AMD display `REG_*` helper macros for actual MMIO access.
- DPP/DCN field-list declarations such as `DPP_REG_LIST_SH_MASK_DCN30` and DPP shift/mask structs.
- DCN316 resource construction in `dcn316_resource.c`, which binds these generated values to the DC runtime for the ASIC family.
- DMUB DCN316 support, which includes this header where firmware-facing display microcontroller code needs the same bitfield definitions.

The source is a vendor-generated ASIC register description. Consistency with hardware documentation and companion generated headers is more important than local readability.

## Risks

- Generated header drift: if a mask/shift changes without the matching offset header, DPP field-list macros, or hardware generation, register helpers may silently program wrong bits.
- Instance mismatch: `CM2_`, `CM3_`, `DSCL3_`, and `DC_PERFMON13_` prefixes must match the intended display-pipe instance. Reusing the wrong instance constants can target the wrong register layout or table slot.
- Packed-field mistakes are high impact. Many region registers pack two LUT offsets and two segment counts into one 32-bit register. A single incorrect mask can corrupt the neighboring region.
- Power-management fields such as `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` are sensitive to sequencing. Incorrect masks can leave LUT/scaler memories forced on, disabled, or in an unexpected power state.
- The chunk boundary cuts through logical groups. It starts in the middle of `CM2_CM_BLNDGAM_LUT_CONTROL` and ends before the full `CM3_CM_BLNDGAM_RAMB_*` group is complete, so whole-file reconciliation must merge adjacent chunks before final conclusions about coverage.

## Test Signals

Useful validation signals for changes touching this chunk are mostly integration and hardware-facing:

- Compile coverage for AMDGPU DCN316 paths, proving field-list macros still find all expected shift/mask names.
- Static checks that every `*_SHIFT` used by DPP/DCN shift structs has the corresponding `_MASK`, and vice versa.
- Diff checks against AMD-generated upstream register headers for DCN 3.1.6.
- Runtime display smoke tests on DCN316 hardware: mode set, cursor enable/move, scaling, color-management/gamma changes, HDR/3D LUT paths, suspend/resume, and memory-power transitions.
- Debugfs or driver diagnostics that read DPP CRCs, perfmon counters, LUT state, and memory-power status can reveal bad masks that compile cleanly.

## Chunk Notes for Merge Lane

This is not a standalone per-file report. Merge/reconciliation should combine it with the surrounding chunks for `dcn_3_1_6_sh_mask.h`, especially the prior chunk that contains the beginning of the CM2 color-management block and the following chunk that completes `CM3_CM_BLNDGAM_RAMB_*` and later DCN316 register groups.
