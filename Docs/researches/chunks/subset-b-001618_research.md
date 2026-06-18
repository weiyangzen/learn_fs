# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 19867-22386

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0.0 register field header. It contains C preprocessor `__SHIFT` and `_MASK` constants for display pipe and plane (DPP) hardware fields, specifically the end of DPP2 scaler memory/output-buffer fields, most of the DPP2 color-management block, DPP2 perfmon fields, and the beginning of DPP3 top/config/cursor/scaler/color-management fields.

There are no functions, structs, enums, global variables, or executable statements in this range. The exported surface is a large macro namespace used by DCN display code to build typed register shift/mask tables. Runtime code combines these field constants with paired register-offset constants from `dcn_2_0_0_offset.h` and then performs MMIO through DC register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, and indexed debug helpers.

Although this repository path is under a `ceph-client` source mirror, the chunk is AMD DCN display-driver hardware metadata and has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

The important interface is the generated field macro set. Each hardware field normally has two constants:

- `REGISTER__FIELD__SHIFT`: bit position used to align a field value.
- `REGISTER__FIELD_MASK`: bit mask used to isolate or update that field.

The chunk starts mid-register at `DSCL2_DSCL_MEM_PWR_CTRL__LB_G1_MEM_PWR_FORCE__SHIFT`, so the first register family is completed from the previous chunk. The main covered families are:

- `DSCL2_DSCL_MEM_PWR_CTRL`, `DSCL2_DSCL_MEM_PWR_STATUS`, `DSCL2_OBUF_CONTROL`, and `DSCL2_OBUF_MEM_PWR_CTRL`: DPP2 scaler LUT/line-buffer memory power control and status, output-buffer bypass/full-buffer/half-width/hold-count control, and OBUF memory power force/disable/mode/state fields.
- `CM2_CM_CONTROL` and `CM2_CM_ICSC_*`: DPP2 color-management bypass/update status and input color-space conversion mode plus A/B coefficient banks. The coefficient registers pack two signed/fixed-point coefficients per register, for example `CM_ICSC_C11` and `CM_ICSC_C12` in the low/high 16-bit halves.
- `CM2_CM_GAMUT_REMAP_*`: DPP2 gamut-remap control and A/B coefficient banks with the same paired 16-bit coefficient layout as ICSC.
- `CM2_CM_BIAS_*`, `CM2_CM_DEALPHA`, `CM2_CM_COEF_FORMAT`, and `CM2_CM_HDR_MULT_COEF`: DPP2 color bias, coefficient-format selection, dealpha/additive-blending controls, and HDR multiplier coefficient fields.
- `CM2_CM_DGAM_*`: DPP2 degamma LUT control, LUT index/data ports, write-enable/mask/status fields, and RAM A/RAM B piecewise-linear region programming. RAM programming fields include per-channel start values and start segments, linear slopes, region end points, end slopes/bases, and region-pair LUT offset/segment-count descriptors.
- `CM2_CM_BLNDGAM_*`: DPP2 blend/output-gamma LUT control and RAM A/RAM B programming. It mirrors the DGAM shape but has a larger region set, running through `REGION_32_33` for both RAM banks.
- `CM2_CM_SHAPER_*`: DPP2 shaper LUT control, offset/scale, LUT index/data, write-enable/status, and RAM A/RAM B region descriptors through `REGION_32_33`.
- `CM2_CM_MEM_PWR_CTRL`, `CM2_CM_MEM_PWR_STATUS`, `CM2_CM_MEM_PWR_CTRL2`, and `CM2_CM_MEM_PWR_STATUS2`: DPP2 shared, degamma, blend-gamma, shaper, 3D LUT, and 3D LUT RAM-slice memory power force/disable/mode/status fields.
- `CM2_CM_3DLUT_*`: DPP2 3D LUT mode, index, data, 30-bit data access, read/write control, normalization factor, and per-channel output offsets.
- `CM2_CM_TEST_DEBUG_INDEX` and `CM2_CM_TEST_DEBUG_DATA`: indexed CM debug/status accessors. DCN color code uses this path to read live coefficient-bank selection and config status that may not be represented by ordinary direct reads.
- `DC_PERFMON15_*`: DPP2/DC perfmon 15 counter control, state, perfmon control, latched/current values, and interrupt/misc fields.
- `DPP_TOP3_*`: DPP3 top-level clock enable, clock-gate-disable, test clock select, soft reset, CRC values/control, and host-read control fields.
- `CNVC_CFG3_*` and `CNVC_CUR3_*`: DPP3 converter/config fields for surface pixel format, alpha-plane enable, format conversion/bypass/expansion/clamping, fixed-point bias/scale values, color-keyer controls/ranges, 2-bit alpha LUT, and cursor mode/color/expansion/enable fields.
- `DSCL3_*`: beginning of DPP3 scaler fields for coefficient RAM tap selection/data, scaler mode/taps, DSCL control, 2-tap control, manual replicate, horizontal/vertical luma and chroma ratios/initial phases, black offset, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format/memory/v-counter, DSCL memory power, and OBUF control/power.
- `CM3_CM_CONTROL` through `CM3_CM_BLNDGAM_RAMA_REGION_30_31`: beginning of DPP3 color-management fields. The covered range includes control, ICSC A/B matrices, gamut-remap A/B matrices, bias, degamma RAM A/B setup, and blend-gamma RAM A setup through `REGION_30_31`. The next chunk continues the DPP3 CM blend-gamma table.

The macros in this file are consumed indirectly by tables such as `tf_shift`, `tf_mask`, `ipp_shift`, and `ipp_mask`. In `dcn20_dpp.h`, macros like `TF_REG_LIST_SH_MASK_DCN20_COMMON`, `TF_REG_LIST_SH_MASK_DCN20_UPDATED`, and related register-list macros select many of the `CM*_CM_BLNDGAM_*`, `CM*_CM_3DLUT_*`, `CM*_CM_SHAPER_*`, `DSCL*_DSCL_MEM_PWR_CTRL`, `CNVC_CFG*_COLOR_KEYER_*`, and `CNVC_CFG*_ALPHA_2BIT_LUT` fields represented in this chunk. In `dcn10_ipp.h`, `IPP_MASK_SH_LIST_DCN` uses `CNVC_CFG0_*` and `CNVC_CUR0_*` fields with the same generated naming scheme for per-instance CNVC/IPP programming.

## Control Flow

This header has no runtime control flow. It changes driver behavior by determining which bit positions and masks generated register helpers use when updating hardware fields.

A typical DCN20 DPP path is:

1. `dcn20_resource.c` creates DPP/IPP instances with per-instance register tables and the generated shift/mask tables.
2. A high-level display operation calls a DPP or IPP function through `struct dpp_funcs` or `struct ipp_funcs`.
3. That function uses register macros such as `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_GET`, `REG_GET_2`, `REG_WAIT`, or `IX_REG_GET`.
4. The helper looks up the register offset and the field shift/mask, then performs the MMIO read/modify/write or indexed debug read.

Representative flows tied to this chunk include:

- `dpp20_read_state()` in `dcn20_dpp.c` reads `DPP_CONTROL.DPP_CLOCK_ENABLE`, `CM_DGAM_CONTROL.CM_DGAM_LUT_MODE`, `CM_SHAPER_CONTROL.CM_SHAPER_LUT_MODE`, `CM_3DLUT_READ_WRITE_CONTROL.CM_3DLUT_CONFIG_STATUS`/`CM_3DLUT_30BIT_EN`, `CM_3DLUT_MODE.CM_3DLUT_SIZE`, and `CM_BLNDGAM_LUT_WRITE_EN_MASK.CM_BLNDGAM_CONFIG_STATUS`.
- `dpp2_power_on_obuf()` updates `CM_MEM_PWR_CTRL.SHARED_MEM_PWR_DIS`, `OBUF_MEM_PWR_CTRL.OBUF_MEM_PWR_FORCE`, and `DSCL_MEM_PWR_CTRL.LUT_MEM_PWR_FORCE` to control DPP memory and OBUF/scaler memory power.
- `dpp1_power_on_dscl()` in the shared DSCL implementation uses `DSCL_MEM_PWR_CTRL.LUT_MEM_PWR_FORCE` and waits on `DSCL_MEM_PWR_STATUS.LUT_MEM_PWR_STATE`; the DPP2 and DPP3 field definitions in this chunk provide the instance-specific bit layout.
- `dpp2_cnv_setup()` programs `FORMAT_CONTROL` and `CNVC_SURFACE_PIXEL_FORMAT` fields to configure conversion bypass, expansion mode, clamp behavior, alpha enable, and pixel format.
- `dpp2_program_input_csc()` writes `CM_ICSC_CONTROL` and the `CM_ICSC_*` coefficient fields, alternating A/B coefficient banks after reading current selection via `CM_TEST_DEBUG_INDEX`/`CM_TEST_DEBUG_DATA`.
- `read_gamut_remap()` and `dpp2_cm_get_gamut_remap()` read gamut-remap mode through CM test/debug fields and then read either the A or B gamut-remap coefficient bank.
- The blend-gamma, degamma, shaper, and 3D LUT programming routines in `dcn20_dpp_cm.c` use the RAM start/slope/end/region/index/data/write-enable fields described by this chunk to build piecewise-linear transfer functions and 3D LUT state.

## State And Persistence Behavior

The header stores no software state. The state represented by its macros lives in DCN hardware registers inside DPP2, DPP3, DSCL, CNVC, CM, OBUF, and perfmon blocks.

The hardware state covered by this chunk includes:

- DPP clock enable, clock-gating disable, dynamic gating disable, soft reset, CRC, and host-read behavior.
- DSCL scaler mode, luma/chroma tap counts, ratios, initial phases, overscan, recout size, MPC size, line-buffer layout, vertical counters, coefficient RAM access, and scaler/line-buffer memory power.
- OBUF bypass/full-buffer/half-width/hold-count settings and OBUF memory power state.
- CNVC surface pixel format, alpha-plane enable, format conversion, expansion/clamp mode, fixed-point scale/bias, color-keying ranges, 2-bit alpha LUT values, and cursor mode/color/enable state.
- CM bypass/update status, input CSC coefficients, gamut-remap coefficients, color bias, degamma LUT state, blend/output-gamma LUT state, shaper LUT state, 3D LUT state, HDR multiplier, dealpha/additive blending, CM memory power state, and debug/status index-data reads.
- Perfmon counter configuration, counter state, current/latched values, high/low data, and interrupt/misc state for perfmon block 15.

Persistence is hardware-defined. Some fields are ordinary sticky configuration bits that remain until another modeset, color update, power-management operation, suspend/resume path, display core reset, or GPU reset changes them. LUT RAM contents and coefficient banks are programmed through index/data windows and can be double-buffered or selected by A/B bank mode fields. Status fields such as memory-power state, update-pending/config-status, v-counter, CRC, and perfmon values are readback/counter/status state rather than durable configuration. The header does not encode which fields are read-only, write-one-to-clear, self-clearing, double-buffered, or timing-sensitive; that sequencing is handled in the DCN DPP/IPP/CM/DSCL code and firmware/hardware specifications.

## Dependencies And Integration Points

The file's direct dependency is only the C preprocessor. Practical integration depends on the generated AMD register-header set:

- `dcn_2_0_0_offset.h` provides the matching register offsets and base-index information.
- `dcn_2_0_0_sh_mask.h` provides the field shifts and masks in this chunk.
- Other generated DCN headers provide enum values and neighboring ASIC-version definitions.
- DC register-access macros in the display driver combine offsets, masks, and shifts for typed MMIO access.

Important integration points in the local tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h`: declares DCN20 DPP register lists and field-list macros that consume many CM, CNVC, DSCL, OBUF, 3D LUT, shaper, and blend-gamma fields represented here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.c`: reads DPP state, controls DPP/DSCL/OBUF memory power, and programs CNVC setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp_cm.c`: programs input CSC, gamut remap, degamma, blend gamma, shaper, 3D LUT, CM bias, dealpha, and related color state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_dscl.c`: shared DSCL scaler code that uses DSCL memory power/status and line-buffer/scaler fields across DCN DPP versions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.h` and `dcn10_ipp.c`: converter/cursor field tables and IPP setup paths for CNVC/IPP state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`: constructs DPP and IPP instances with generated register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dpp.h`: documents the DPP pipeline as CNVC, DSCL, CM, OBUF, and DPB modules and defines the high-level DPP state and function interface that the generated fields support.

The chunk is source-tree-aligned with a large generated hardware register map. It should be reconciled with adjacent chunks rather than treated as a standalone module because it starts in the middle of `DSCL2_DSCL_MEM_PWR_CTRL` and ends in the middle of the `CM3_CM_BLNDGAM_RAMA_*` region table.

## Risks And Edge Cases

The main risk is silent bitfield corruption. A wrong shift or mask can compile cleanly while causing register helpers to update the wrong bits within the right register. For display hardware, that can manifest as blank planes, bad scaling, wrong colors, cursor artifacts, unstable clocks/power state, or intermittent failures on only one DPP instance.

High-impact areas in this chunk are:

- Memory power fields: incorrect `DSCL*_DSCL_MEM_PWR_CTRL`, `DSCL*_DSCL_MEM_PWR_STATUS`, `OBUF_MEM_PWR_CTRL`, or `CM*_CM_MEM_PWR_CTRL*` fields can make power-on/off waits time out, leave LUT/line-buffer/OBUF/CM memory powered down while in use, or block low-power optimizations.
- LUT RAM programming fields: degamma, blend-gamma, shaper, and 3D LUT programming depends on index/data windows, write-enable masks, A/B bank selection, region offsets, segment counts, start values, slopes, and end bases. A mask width error can corrupt transfer functions even when the selected register address is correct.
- Double-buffered coefficient banks: ICSC and gamut-remap A/B matrix fields are paired with debug/status selection reads. If A/B field masks or debug fields are wrong, updates may target the wrong bank or read back stale selection, causing frame-boundary color changes to fail.
- CNVC format fields: bad pixel-format, alpha enable, expansion, clamp, scale/bias, color-keyer, or 2-bit alpha LUT masks can break primary plane interpretation or blending without producing a build failure.
- DSCL scaler fields: wrong tap count, ratio, initial phase, viewport/recout, line-buffer, or coefficient RAM fields can produce scaling artifacts, underflow symptoms, or failures only for chroma/4:2:0 paths.
- DPP3 instance fields: this chunk switches from DPP2 to DPP3. Instance-numbered generated names must remain consistent with offset tables and DPP instance construction; copy/paste or generator drift could make one pipe differ from another.
- Cross-chunk boundaries: the start lacks the first `DSCL2_DSCL_MEM_PWR_CTRL` field lines, and the end stops at `CM3_CM_BLNDGAM_RAMA_REGION_30_31`. Merge/reconciliation should join this with chunks 8 and 10 before drawing final per-file conclusions.

Because generated mask headers are often included indirectly, removing or renaming an apparently unused field can still break macro expansion in versioned register-list code. Some debug, status, and perfmon fields may be used only by diagnostics, validation, or future code paths.

## Test Signals

Useful validation signals are a mix of build-time checks, register-map comparison, and display behavior:

- Build AMDGPU DCN20 paths with display enabled. This catches missing or renamed field macros in `dcn20_dpp.h`, `dcn20_dpp.c`, `dcn20_dpp_cm.c`, shared DSCL code, IPP code, and resource construction.
- Generate or compare the `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h` pair against AMD's source register database. Field masks should match their documented widths and should not overlap unexpectedly within the same register.
- Exercise modesets on all DPP instances that exist on the target ASIC. DPP2 and DPP3 coverage is important because this chunk spans both instance groups.
- Run plane format tests for ARGB/RGB/FP formats, alpha-plane enable, 2-bit alpha LUT, format expansion, clamp, color keying, and cursor color/enable behavior.
- Run scaler tests covering bypass, luma/chroma scaling, 4:2:0 paths, horizontal and vertical ratios, tap counts, overscan, line-buffer partitioning, and recout/MPC sizing.
- Run color-management tests for ICSC, gamut remap, degamma, blend/output gamma, shaper, 3D LUT, HDR multiplier, CM bias, and dealpha/additive blending. Visual CRC or hardware CRC comparisons should catch many bitfield errors.
- Run suspend/resume, display power-gating, and low-power-memory tests while verifying `REG_WAIT` paths for DSCL/CM/OBUF memory power status do not time out.
- Read DPP state through debugfs or driver instrumentation after programming color/scaler state and compare readback with expected `dcn_dpp_state` and `dcn_dpp_reg_state` values.
- Exercise perfmon block 15 counter programming and readback to verify counter control/state/value fields are mapped to the intended perfmon block.

Regression symptoms from bad constants include build failures in generated register-list expansion, `REG_WAIT` timeouts, black or corrupted planes, incorrect color transforms, banding or gamma errors, broken 3D LUT programming, cursor color/enable artifacts, scaling artifacts, underflow, CRC mismatch, a single DPP pipe failing, or power-management failures during modeset and resume.

## Cross-Chunk Notes

This is chunk 9 of 28 for `dcn_2_0_0_sh_mask.h`. It begins inside the DPP2 DSCL memory-power register family, completes DPP2 CM and related DPP2 perfmon fields, begins DPP3 top/CNVC/DSCL/CM fields, and ends inside the DPP3 blend-gamma RAM A region table. The final per-file research document should merge this with the adjacent chunks so the repeated DPP0-DPPn generated patterns and the split register families are described as one continuous DCN 2.0.0 mask/shift map.
