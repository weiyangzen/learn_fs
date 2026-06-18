# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 19828-22333

## Scope

This chunk is part of the generated AMD DCN 3.0.0 ASIC register shift/mask header. It covers lines 19828-22333 and exports 2,113 preprocessor constants: 1,056 `__SHIFT` constants and 1,057 `_MASK` constants. There are no C functions, structs, enums, or executable statements; the API is the generated macro namespace used by AMDGPU display register helper code.

The slice starts in the tail of DPP2 color-management gamma-correction RAM A region metadata and ends mid-way through DPP3 gamma-correction RAM B region metadata at `CM3_CM_GAMCOR_RAMB_REGION_18_19`. Whole-file reconciliation should merge this with neighboring chunks to describe the complete DCN 3.0.0 register map.

## Purpose

The purpose of this chunk is to bind symbolic DCN 3.0.0 display register fields to exact bit positions and masks. Runtime driver code uses these macros through `REG_SET`, `REG_UPDATE`, `REG_GET`, `TF_SF`, `SF`, and instance register-list macros rather than hard-coding packed bitfield values.

Major hardware domains represented here are:

- `CM2` color-management registers for DPP instance 2, including the tail of `CM_GAMCOR_RAMA`, full `CM_GAMCOR_RAMB`, blending gamma RAM A/B, HDR multiplier, memory power control/status, dealpha, coefficient format, shaper LUT RAM A/B, and HDR 3D LUT control/data/output normalization.
- `DC_PERFMON14` performance-counter registers in the DPP2 performance-monitor address block, including counter control, counter state, monitor control, current-value interrupt status/clear/mask fields, and high/low counter value readback.
- `DPP_TOP3` top-level DPP instance 3 control, soft reset, CRC value/control, and host-read control fields.
- `CNVC_CFG3` and `CNVC_CUR3` converter and cursor-color fields for DPP instance 3, including surface pixel format, alpha/dealpha/re-alpha handling, expansion/rounding/clamp controls, pre-CSC matrices, pre-degamma, color keying, cursor mode/color, and cursor FP scale/bias.
- `DSCL3` scaler and line-buffer fields for DPP instance 3, including coefficient RAM, scaler mode/taps/ratios/init values, manual replication, black color, update/autocal, overscan, OTG blank timing, RECOUT/MPC sizing, line-buffer format/counters, DSCL memory power, and output-buffer power/control.
- `CM3` color-management registers for DPP instance 3, including post-CSC matrices, gamut remap matrices, channel bias, gamma-correction LUT control/data, and gamma-correction RAM A plus the beginning of RAM B region descriptors.

## Important API Surface

The exported API shape is the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important groups in this chunk include:

- `CM2_CM_GAMCOR_RAMB_*` and `CM3_CM_GAMCOR_RAMA/RAMB_*` fields for gamma-correction piecewise LUT start, slope, base, end, offset, and per-region segment descriptors. These are consumed by DCN30 DPP color-management code when programming `dpp3_program_gamcor_lut`.
- `CM2_CM_BLNDGAM_CONTROL`, `CM2_CM_BLNDGAM_LUT_INDEX`, `CM2_CM_BLNDGAM_LUT_DATA`, and RAM A/B descriptor fields for blend gamma LUT programming.
- `CM2_CM_SHAPER_*` fields for shaper LUT mode, channel offset/scale, LUT write selection, RAM A/B region setup, and LUT data writes.
- `CM2_CM_3DLUT_MODE`, `CM2_CM_3DLUT_INDEX`, `CM2_CM_3DLUT_DATA`, `CM2_CM_3DLUT_DATA_30BIT`, `CM2_CM_3DLUT_READ_WRITE_CONTROL`, and output normalization/offset fields for HDR 3D LUT programming.
- `CM2_CM_MEM_PWR_CTRL`, `CM2_CM_MEM_PWR_STATUS`, `CM2_CM_MEM_PWR_CTRL2`, and `CM2_CM_MEM_PWR_STATUS2` fields for LUT, shaper, 3D LUT, and gamma memory power force/disable/low-power/status controls.
- `DC_PERFMON14_PERFCOUNTER_*` and `DC_PERFMON14_PERFMON_*` fields for selecting performance sources, arming counters, defining window/start/stop events, and reporting or clearing current-value interrupt conditions.
- `DPP_TOP3_DPP_CONTROL`, `DPP_TOP3_DPP_SOFT_RESET`, and `DPP_TOP3_DPP_CRC_CTRL` fields for DPP3 enable, reset, alpha selection, CRC selection, CRC enable, continuous mode, region mode, and CRC mask/valid state.
- `CNVC_CFG3_FORMAT_CONTROL`, `CNVC_CFG3_PRE_CSC_*`, `CNVC_CFG3_PRE_DEGAM`, and `CNVC_CFG3_PRE_REALPHA` fields used by DPP setup and format conversion paths.
- `DSCL3_SCL_*`, `DSCL3_RECOUT_*`, `DSCL3_MPC_SIZE`, `DSCL3_LB_*`, `DSCL3_DSCL_MEM_PWR_*`, and `DSCL3_OBUF_*` fields used by scaler, line-buffer, and output-buffer programming.
- `CM3_CM_POST_CSC_*`, `CM3_CM_GAMUT_REMAP_*`, `CM3_CM_BIAS_*`, and `CM3_CM_GAMCOR_*` fields used by DPP3 color transforms and gamma correction.

## Control Flow

This header chunk has no local control flow. Runtime behavior is supplied by AMD display code that includes the DCN 3.0.0 mask header, binds the macros into per-block register tables, and then performs ordered register programming through display helper macros.

The typical external flow is:

- DCN30 resource construction builds DPP, scaler, color-management, IRQ, GPIO, clock, and DMUB register tables from matching offset and shift/mask headers.
- Plane setup programs `CNVC_CFG3` format, conversion, pre-CSC, pre-degamma, alpha, and cursor-color fields according to the selected framebuffer format and color pipeline.
- Scaling setup programs `DSCL3` coefficient RAM, taps, ratios, initial phases, RECOUT/MPC dimensions, line-buffer format, autocal/update state, and memory-power fields.
- Color-management setup powers LUT memories, selects RAM A or RAM B, writes region descriptors and LUT entries, then flips the active mode for gamma correction, blend gamma, shaper, and 3D LUT blocks.
- Status/readback paths query current shaper and 3D LUT mode fields, DPP CRC values, memory power status bits, line-buffer counters, and perf monitor counters.

Ordering is an implicit hardware contract enforced by callers such as `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c` and `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp_cm.c`. For example, LUT programming must select the intended RAM bank and write-enable mask before streaming LUT data, and memory power bits must be set before depending on LUT or scaler RAM contents.

## State and Persistence

The file stores no software state. The macros describe memory-mapped hardware state that persists inside DCN display blocks while those blocks remain powered:

- Color LUT data, RAM-bank selection, mode-current fields, region start/end/base/slope descriptors, and offsets persist as the active plane color pipeline until reprogrammed, bypassed, power-gated, or reset.
- `CM2` memory power controls affect whether LUT/shaper/3D-LUT/gamma memories retain valid contents and whether status bits report powered, low-power, or disabled states.
- Converter state persists the active surface interpretation: pixel format, alpha handling, color keying, clamping, component expansion, pre-CSC matrices, and pre-degamma mode.
- Scaler state persists coefficient RAM contents, taps, ratios, phase initialization, output rectangle, MPC size, line-buffer format, blanking reference fields, and output-buffer power state.
- CRC and performance-monitor registers hold live measurement state, sticky status, clear bits, selected counter sources, and captured counter values.

Incorrect constants can therefore corrupt persistent hardware programming until a modeset, DPP reprogramming, display block reset, GPU reset, or power transition restores valid register contents.

## Dependencies and Integration Points

This chunk depends on the matching DCN 3.0.0 register offset header and on AMD display register helper macros that paste register and field identifiers into generated `__SHIFT` and `_MASK` symbols. The constants are only meaningful when paired with the correct DCN 3.0.0 register addresses.

Direct include points for `dcn_3_0_0_sh_mask.h` include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which wires DCN30 display resources and register tables.
- `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`, which need the same generated field metadata for interrupt setup.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c` and `hw_translate_dcn30.c`, plus `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`, which share DCN30 register metadata with DMUB-side helpers.

Important functional consumers include `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, `dcn30_dpp.c`, and `dcn30_dpp_cm.c`. Those files define DPP3 field lists and use fields visible in this chunk for post-CSC/gamut remap, converter setup, cursor attributes, scaler setup, blend gamma programming, shaper LUT programming, HDR 3D LUT programming, gamma-correction LUT programming, state readback, and deferred update handling.

## Risks

- A wrong mask or shift silently writes unrelated hardware bits. The highest-risk fields here are LUT RAM bank selection, LUT write masks, memory power controls, scaler ratios/taps, surface format controls, color matrices, and CRC/perfmon clear or status fields.
- DPP instance drift is likely because `CM2` and `CM3` use near-identical register families. A bad generated instance prefix or copied field can affect only one pipe, making failures dependent on display topology or plane assignment.
- Region descriptor macros repeat 34 gamma/shaper regions with paired `LUT_OFFSET` and `NUM_SEGMENTS` fields. An off-by-one region, swapped RAM A/B selector, or channel mismatch can create color artifacts without compile-time failures.
- Some fields are write-one-to-clear or status/mask/control mixes, especially in CRC and performance-monitor interrupt registers. Incorrect read-modify-write usage can drop measurement events or leave sticky flags uncleared.
- Memory power bits gate LUT and scaler memories. Programming data while RAM is disabled or trusting stale status masks can produce intermittent color/scaler failures after suspend, clock gating, or power transitions.
- `DC_PERFMON14` values are diagnostic but still sensitive: incorrect counter source, state, or interrupt masks can invalidate performance data and mislead debug or validation work.
- The chunk boundary is mid-family: it begins after the first `CM2_CM_GAMCOR_RAMA` fields and ends before all `CM3_CM_GAMCOR_RAMB` fields. Isolated edits or review of this chunk can miss cross-boundary consistency problems.

## Test Signals

Useful validation signals for changes to this chunk are:

- Build AMDGPU display code for DCN30 and DCN302 configurations to catch renamed, missing, or mismatched shift/mask macros in DPP, IRQ, GPIO, clock, resource, and DMUB paths.
- Static comparison against the vendor register database and the adjacent generated DCN 3.0.0 offset/mask files, especially verifying every `__SHIFT` has the intended `_MASK` and matching register offset.
- Multi-plane display tests that force use of DPP2 and DPP3, including format conversion, cursor composition, scaling, RECOUT/MPC sizing, and line-buffer behavior.
- Color pipeline tests for post-CSC, pre-CSC, gamut remap, gamma correction, blend gamma, shaper LUT, HDR 3D LUT, HDR multiplier, dealpha, and bias programming; visual CRC, readback, or color ramp tests are good signals.
- Suspend/resume and display idle/power-gating tests that verify `CM2` and `DSCL3` memory power state fields converge and LUT/scaler contents are restored when required.
- CRC/performance-monitor smoke tests that arm counters, check high/low readback, clear current-value interrupt status, and verify DPP3 CRC valid/status fields under active scanout.

## Chunk Notes

This is generated register metadata, not logic. The main research value is mapping the hardware surfaces covered by the constants: DPP2 advanced color LUTs and perf monitoring, plus DPP3 top/converter/cursor/scaler/color-management fields. The final merged file report should connect this slice with neighboring chunks to cover complete DPP2 and DPP3 register families.
