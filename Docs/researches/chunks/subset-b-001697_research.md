# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 24839-27351

## Scope

This chunk is a generated AMD DCN 3.0.0 register field header slice. It exports preprocessor constants only: `__SHIFT` bit positions and `_MASK` bit masks for fields in DPP4 and DPP5 display-pipe registers. There are no C functions, structs, enums, or local algorithms in this range.

The covered hardware domains are:

- Tail of DPP4 color-management (`CM4`) blend gamma RAM A/B, HDR multiplier, color-management memory power, dealpha, coefficient format, shaper LUT, shaper RAM A/B, and 3D LUT fields.
- DPP4 perfmon instance 16 (`DC_PERFMON16`) counter control, counter state, perfmon control, and value registers.
- DPP5 top (`DPP_TOP5`) control, soft reset, CRC, and host-read fields.
- DPP5 CNVC config/cursor (`CNVC_CFG5`, `CNVC_CUR5`) format conversion, FP bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC, pre-degamma, pre-realpha, and cursor fields.
- DPP5 DSCL (`DSCL5`) scaler coefficient RAM, scaling mode/taps/ratios/init, overscan, output geometry, line-buffer format/memory, memory power, and output-buffer power fields.
- Start and middle of DPP5 color-management (`CM5`) control, post-CSC, gamut remap, bias, gamma correction RAM A/B, blend gamma RAM A/B, HDR multiplier, memory power, dealpha, coefficient format, and shaper fields.

The line range starts mid-register at `CM4_CM_BLNDGAM_RAMA_REGION_30_31` and ends mid-register group at `CM5_CM_SHAPER_RAMA_START_CNTL_R`; whole-file reconciliation must join this with adjacent chunks for the complete `CM4` and `CM5` register maps.

## Purpose

The purpose of this chunk is to bind DCN 3.0 display driver code to exact field encodings for DPP color, scaler, converter, perfmon, CRC, and memory-power hardware. The companion offset header gives register addresses; this header gives the bit layout inside those registers. Functional code avoids hard-coded bit arithmetic by expanding these macros into typed shift/mask tables, then using register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT`.

For DCN30 DPP programming, these constants are consumed primarily through `display/dc/dpp/dcn30/dcn30_dpp.h`. `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` initialize `struct dcn3_dpp_shift` and `struct dcn3_dpp_mask` in DCN30-family resource files. Runtime DPP methods then read and write fields by symbolic names such as `CM_BLNDGAM_MODE`, `CM_BLNDGAM_SELECT_CURRENT`, `HDR3DLUT_MEM_PWR_STATE`, `SHAPER_MEM_PWR_FORCE`, `LUT_MEM_PWR_STATE`, `FORMAT_CONTROL__ALPHA_EN`, and `CM_GAMCOR_MODE_CURRENT`.

## Important API Surface

The exported API surface is the macro namespace. Important groups include:

- Blend gamma fields for `CM4` and `CM5`: `CM_BLNDGAM_CONTROL`, `CM_BLNDGAM_LUT_INDEX`, `CM_BLNDGAM_LUT_DATA`, `CM_BLNDGAM_LUT_CONTROL`, RAM A/B start/end/base/slope/offset fields, and region descriptors `REGION_0_1` through `REGION_32_33`. Region registers pack two PWL regions per register with LUT offset fields at bits 0/16 and segment-count fields at bits 12/28.
- Gamma correction fields for `CM5`: `CM_GAMCOR_CONTROL`, LUT index/data/control, RAM A/B start/end/base/slope/offset fields, and 34 region descriptors.
- Shaper and 3D LUT fields: `CM_SHAPER_CONTROL`, offsets/scales, LUT index/data/write-enable, RAM A/B region descriptors, and `CM_3DLUT_*` mode, index, data, read/write, normalization, and output-offset fields in the `CM4` part of this slice.
- Color matrix and format fields: `CM_POST_CSC_*`, `CM_GAMUT_REMAP_*`, `CM_BIAS_*`, `CM_COEF_FORMAT`, `CNVC_CFG5_PRE_CSC_*`, `PRE_DEGAM`, `PRE_DEALPHA`, `PRE_REALPHA`, `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, and FP conversion bias/scale fields.
- Scaler fields: coefficient RAM tap select/data, mode, tap control, manual replicate, horizontal/vertical scale ratios and init values for luma/chroma, black color, update/autocal, overscan, OTG blanking, recout size/start, MPC size, line-buffer data format/memory control, DSCL memory power, and OBUF memory power.
- Diagnostics and monitoring fields: DPP5 CRC control/value fields, host-read rate control, and DPP4 `DC_PERFMON16` counter/perfmon control and value fields.
- Memory-power controls and status: `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_MEM_PWR_CTRL2`, `CM_MEM_PWR_STATUS2`, `DSCL_MEM_PWR_CTRL`, `DSCL_MEM_PWR_STATUS`, `OBUF_MEM_PWR_CTRL`, and their force/disable/state fields.

The repeated `CM4_` and `CM5_` prefixes are instance-specific generated names. Consumer macros usually refer to instance 0 field names, for example `CM0_CM_BLNDGAM_CONTROL__CM_BLNDGAM_MODE_MASK`, then token-paste the desired instance through register-address tables. The bit layouts are expected to be identical across DPP instances.

## Control Flow

There is no local control flow in this header. Runtime control flow is external:

1. DCN30 resource construction includes `dcn_3_0_0_offset.h` and this mask header.
2. Macros such as `DPP_REG_LIST_DCN30(id)` populate per-DPP register-address tables for six DPP instances.
3. `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` populate the corresponding field shift/mask tables.
4. DPP methods in `dcn30_dpp.c`, DPP scaler code, and shared color-management helpers use the tables through `REG_*` helpers.
5. Hardware latches selected fields on modeset, vupdate, or block-specific update boundaries; the header only defines the bit positions used by those writes.

Representative runtime paths tied to this chunk include:

- `dpp30_read_state()` reads current gamma correction, shaper, 3D LUT, and blend gamma modes through `CM_GAMCOR_CONTROL`, `CM_SHAPER_CONTROL`, `CM_3DLUT_MODE`, and `CM_BLNDGAM_CONTROL`.
- `dpp3_cnv_setup()` programs CNVC format, alpha, pre-dealpha/realpha, pre-CSC/post-CSC selection, pixel format, and cursor disable behavior for input surfaces.
- Blend gamma programming chooses the inactive RAM A/B bank, writes LUT entries through `CM_BLNDGAM_LUT_INDEX` and `CM_BLNDGAM_LUT_DATA`, programs PWL region start/end/segment metadata through `CM_BLNDGAM_RAMA_*` or `CM_BLNDGAM_RAMB_*`, and flips `CM_BLNDGAM_CONTROL` select/mode fields.
- Memory low-power paths clear force fields and wait for state fields when powering on, while deferred disable paths set force fields after bypass is latched. This applies to DSCL LUT memory, gamma correction, blend gamma, 3D LUT, and shaper memory.
- Scaler control paths program DSCL coefficient RAM, ratios, taps, init phases, output geometry, line-buffer partitioning, and memory-power state using the DSCL5-equivalent field layouts.

## State and Persistence

The header itself has no mutable software state or persistence. It defines compile-time constants that address hardware state in MMIO registers.

The hardware state represented by this chunk persists until reprogrammed, power-gated, reset, or overwritten by a later display update. Important state includes:

- Double-buffered transfer-function state in gamma correction, blend gamma, and shaper RAM A/B banks.
- LUT index/data cursors and write-color masks used while host-loading LUT payloads.
- Current versus requested mode/select fields for gamma, blend gamma, shaper, 3D LUT, post-CSC, pre-CSC, and gamut remap.
- PWL region metadata: start value, start segment, start slope/base, end value/base/slope, offset, LUT offsets, and segment counts.
- CNVC pixel format, alpha handling, color keying, pre-degamma, pre/post CSC, and cursor configuration.
- DSCL filter coefficients, scaling ratios, taps, init phase, output rectangles, line-buffer memory configuration, and autocal state.
- Sticky or latched diagnostic state in CRC and perfmon registers.
- Memory power force/disable/state fields for color-management and scaler memories.

Because many fields are double-buffered or update-boundary latched, a wrong field definition can create delayed symptoms: the write may appear to succeed but the active `*_CURRENT` field, selected LUT bank, or memory-power state changes on a later vupdate.

## Dependencies and Integration Points

This chunk is tightly coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the matching register offsets.
- DCN30-family resource files such as `display/dc/resource/dcn30/dcn30_resource.c`, `dcn301_resource.c`, `dcn302_resource.c`, `dcn303_resource.c`, `dcn31_resource.c`, `dcn314_resource.c`, and `dcn315_resource.c`, which initialize DPP register, shift, and mask tables.
- `display/dc/dpp/dcn30/dcn30_dpp.h`, where `DPP_REG_LIST_SH_MASK_DCN30_COMMON` and `DPP_REG_LIST_SH_MASK_DCN30_UPDATED` name the fields consumed from this generated header.
- `display/dc/dpp/dcn30/dcn30_dpp.c`, which reads state, sets CNVC format, programs post-CSC, handles blend gamma/shaper/3D LUT power, and drives blend LUT bank switching.
- Shared color-management helpers under `display/dc/dcn30/dcn30_cm_common.c` and older DPP color code, which program transfer functions and color matrices using register/mask bundles assembled from these macros.
- DSCL code in `display/dc/dpp/dcn10/dcn10_dpp_dscl.c`, `dcn20_dpp.c`, and DCN30 DPP paths, which uses DSCL memory-power and scaler field layouts.
- Debug and validation paths in hardware sequencer/resource code that expose DPP CRC state and perfmon state.

The generated field layout also integrates with DC debug options. For example, `enable_mem_low_power.bits.cm` controls whether `CM_MEM_PWR_CTRL*` fields are manipulated, and deferred register writes rely on `*_MODE_CURRENT` fields to verify bypass before forcing memories off.

## Risks

- Field drift is high impact. A wrong mask or shift still compiles but writes the wrong bits, causing corrupted color output, invalid scaling, broken cursor/alpha handling, stuck memory-power state, or broken diagnostics.
- The chunk contains many nearly identical RAM A/RAM B and R/G/B field groups. Copy/paste errors can affect only one color channel, one LUT bank, or one DPP instance, making failures mode- and pipe-specific.
- Double-buffered LUT selection is sensitive. Incorrect `CM_BLNDGAM_SELECT`, `CM_BLNDGAM_SELECT_CURRENT`, or region metadata fields can cause updates to program the active bank or fail to switch banks cleanly.
- Memory-power force/status fields are timing-sensitive. Bad masks for `GAMCOR_MEM_PWR_FORCE`, `BLNDGAM_MEM_PWR_FORCE`, `HDR3DLUT_MEM_PWR_FORCE`, `SHAPER_MEM_PWR_FORCE`, `LUT_MEM_PWR_FORCE`, or matching state fields can lead to waits timing out or blocks being powered down while active.
- Region descriptor widths are contract-critical. LUT offsets use 9-bit masks and segment counts use 3-bit masks in packed two-region registers; wrong limits can make generated PWL curves index outside expected hardware regions.
- CNVC format fields affect surface interpretation. Wrong pixel-format, alpha-plane, crossbar, clamp, color-key, pre-dealpha, or pre-CSC masks can produce channel swaps, alpha artifacts, or incorrect YCbCr/RGB conversion.
- DSCL coefficient and tap fields directly affect image quality and bounds. Bad masks can corrupt filter coefficients, scale ratios, recout/MPC geometry, or line-buffer partitioning.
- Perfmon and CRC fields are debug-facing but still important. Incorrect fields can make validation counters, CRC captures, or host-read diagnostics misleading.

## Test Signals

Good validation signals for this chunk combine build coverage, generated-header comparison, and display behavior:

- Build all DCN30-family AMDGPU display configurations so `DPP_REG_LIST_SH_MASK_DCN30`, resource initializers, and `REG_*` call sites catch missing or renamed macros.
- Diff this generated header against AMD register database output and adjacent DCN 3.x mask headers to catch unexpected field-width, shift, or instance-layout changes.
- Exercise modesets across all DPP instances with RGB and YCbCr formats, alpha formats, 10-bit/FP formats, cursor formats, color keying, and pre/post CSC enabled.
- Validate color-management paths: pre-degamma, gamma correction, blend gamma, shaper LUT, 3D LUT, gamut remap, HDR multiplier, and RAM A/B bank switching.
- Run suspend/resume and display idle/active transitions with color-management memory low power enabled, watching for `REG_WAIT` failures on CM and DSCL memory-power state fields.
- Test scaling paths with identity, upscaling, downscaling, chroma scaling, non-default taps, coefficient RAM programming, overscan, and line-buffer partition changes.
- Use CRC/perfmon debug reads to confirm DPP CRC values and perfmon counters remain plausible after modesets and pipe reconfiguration.
- Check visual output for channel swaps, banding, incorrect gamma, alpha/dealpha artifacts, scaler ringing, and pipe-specific failures on DPP4/DPP5.

## Chunk Notes

This is a constants-only generated slice, so its research value is the hardware contract rather than local logic. It is especially important because it bridges color-management LUT programming, scaler setup, format conversion, memory power, and diagnostics for late DPP4 and DPP5 blocks in DCN 3.0. Changes here should be treated as hardware-spec changes and validated against both generated register sources and real display/color/scaler behavior.
