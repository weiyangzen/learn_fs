# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 7596-10129

## Scope

This chunk is part of AMDGPU's generated DCN 2.0.1 register field shift/mask header. It covers lines 7596-10129 of `dcn_2_0_1_sh_mask.h` and contains preprocessor constants only: 2,111 `#define` entries, including 1,056 `__SHIFT` constants and 1,079 `_MASK` constants. There are no C functions, structs, enums, variables, loops, or branches in this source range.

The chunk starts in the middle of the DPP2 display scaler (`DSCL2`) field definitions, covers the complete DPP2 color-management (`CM2`) field block, then covers DPP3 top/CNVC/cursor/scaler blocks and the beginning of the DPP3 color-management (`CM3`) block. The final per-file reconciliation should merge this artificial slice with adjacent chunks because both the opening `DSCL2` area and the closing `CM3_CM_BLNDGAM_RAMB_REGION_0_1` area are partial logical regions.

## Purpose

The purpose of this range is to publish exact bit positions and masks for DCN 2.0.1 display pipe registers. Functional display code uses these constants with the matching register address header, `dcn_2_0_1_offset.h`, and DC register helper macros to encode and decode packed memory-mapped hardware register fields.

The represented hardware domains are:

- Tail `DSCL2` fields for horizontal/vertical luma and chroma scale ratios, filter init phases, bottom-field phases, black offsets, scaler update pending state, scaler autocalibration, external overscan, OTG blanking, recout/MPC geometry, line-buffer data format, line-buffer memory partitions and counters, DSCL memory power, OBUF control, and OBUF memory power.
- Full `CM2` color-management fields for bypass/update state, input CSC matrices, gamut remap matrices, bias, degamma control and LUT access, degamma RAM A/B piecewise-linear region metadata, blend-gamma control and LUT access, blend-gamma RAM A/B region metadata, HDR multiplier coefficient, CM memory power/status, dealpha, coefficient format, shaper controls/LUTs/RAM A/B region metadata, additional memory power controls, and 3D LUT mode/index/data/read-write normalization/offset fields.
- `DPP_TOP3` fields for DPP3 control, soft reset, CRC readout/control, and host read control.
- `CNVC_CFG3` fields for surface pixel format, format conversion/expansion/clamping, floating-point bias/scale, color keyer control and color values, and alpha 2-bit LUT.
- `CNVC_CUR3` cursor fields for cursor0 enable/mode/format/address-related control, cursor colors, and cursor FP scale/bias.
- Full `DSCL3` fields mirroring the scaler, line-buffer, memory-power, OBUF, overscan, blanking, recout, and MPC geometry controls for DPP instance 3.
- Beginning `CM3` fields for color-management bypass/update state, input CSC and gamut remap matrices, bias, degamma control/LUT/RAM region metadata, and blend-gamma control/LUT/RAM A plus the start of RAM B region metadata.

Although this repository path is under `ceph-client`, this header range is AMD display hardware metadata. It has no Ceph filesystem protocol behavior and no distributed filesystem persistence semantics.

## Important API Surface

The exported API surface is the macro namespace. Each hardware field is represented by paired constants:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned bit mask for read-modify-write and extraction helpers.

Representative field families include:

- `DSCL2_SCL_VERT_FILTER_INIT__SCL_V_INIT_FRAC__SHIFT` / `_MASK` and the related chroma/bottom-field forms for scaler phase programming.
- `DSCL2_DSCL_MEM_PWR_CTRL__LB_G*_MEM_PWR_FORCE__SHIFT` / `_MASK` and `DSCL2_DSCL_MEM_PWR_STATUS__LB_G*_MEM_PWR_STATE__SHIFT` / `_MASK` for scaler LUT and line-buffer memory power control/status.
- `CM2_CM_ICSC_C11_C12__CM_ICSC_C11__SHIFT` / `_MASK` and the other matrix coefficient fields for input color-space conversion.
- `CM2_CM_GAMUT_REMAP_CONTROL__CM_GAMUT_REMAP_MODE__SHIFT` / `_MASK` plus RAM A/B matrix coefficients for gamut remapping.
- `CM2_CM_DGAM_LUT_INDEX`, `CM2_CM_DGAM_LUT_DATA`, and `CM2_CM_DGAM_LUT_WRITE_EN_MASK` fields for degamma LUT programming.
- `CM2_CM_BLNDGAM_*` and `CM3_CM_BLNDGAM_*` region fields for piecewise-linear blend-gamma RAM layout, with LUT offsets, segment counts, region starts, slopes, end bases, and end slopes.
- `CM2_CM_SHAPER_*` and `CM2_CM_3DLUT_*` fields for HDR shaper and 3D LUT programming, normalization, offsets, and read/write control.
- `DPP_TOP3_DPP_CRC_CTRL` and `DPP_TOP3_DPP_CRC_VAL_*` fields for DPP-level CRC diagnostics.
- `CNVC_CFG3_CNVC_SURFACE_PIXEL_FORMAT__CNVC_SURFACE_PIXEL_FORMAT__SHIFT` / `_MASK` and `CNVC_CFG3_FORMAT_CONTROL` fields for pixel format conversion, expansion mode, alpha enablement, clamping, and bypass behavior.
- `DSCL3_DSCL_AUTOCAL`, `DSCL3_LB_MEMORY_CTRL`, `DSCL3_OBUF_CONTROL`, and `DSCL3_OBUF_MEM_PWR_CTRL` fields for DPP3 scaler setup and buffering.

Consumers do not normally spell the long instance-specific identifiers directly. DCN code builds register, shift, and mask tables with macros such as `TF_REG_LIST_DCN201(id)`, `TF_REG_LIST_SH_MASK_DCN201(__SHIFT)`, `TF_REG_LIST_SH_MASK_DCN201(_MASK)`, `SF(...)`, and per-block `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `REG_READ` helpers.

## Control Flow

This header chunk has no local runtime control flow. Runtime behavior is created by the display core that includes this generated metadata:

1. DCN 2.0.1 resource construction includes `dcn_2_0_1_offset.h` and this mask header, then expands block-specific list macros into `dcn201_dpp_registers`, `dcn201_dpp_shift`, and `dcn201_dpp_mask` tables.
2. DPP setup code selects pixel formats, alpha handling, input color space, cursor behavior, scaler mode, scaler ratios, taps, color transforms, degamma/blend/shaper/3D LUT programming, and memory-power policy.
3. Register helper macros combine the register address with the corresponding `__SHIFT` and `_MASK` values from this header to write packed fields or decode hardware state.
4. Hardware applies those programmed fields during modeset, plane enable, scaling, color-management update, cursor update, page flip, power-gating, diagnostic CRC capture, or display readback.

Ordering constraints are external to this file. For example, callers must sequence LUT index/data/write-enable programming correctly, avoid reading status before hardware has latched updates, and respect DSCL/OBUF/CM memory-power transition timing. This header only supplies bit layouts; it does not encode access type, reset values, self-clearing behavior, or safe programming order.

## State And Persistence Behavior

The file stores no software state. Its constants map to hardware register state that persists according to DCN 2.0.1 hardware rules while the display block is powered.

The represented hardware state includes:

- Scaler geometry and filtering state: scale ratios, initial phases, taps/coefficient RAM access, black offsets, overscan, blanking, recout size/start, MPC output size, line-buffer format, line-buffer partitioning, and OBUF behavior.
- Color pipeline state: CM bypass and update-pending bits, input CSC and gamut remap coefficients, bias values, degamma and blend-gamma LUT modes, LUT indices/data/write masks, HDR multiplier, dealpha, coefficient format, shaper LUTs, shaper scale/offset, and 3D LUT controls/data/output normalization.
- Power state: DSCL LUT/line-buffer memory force/disable/status bits, OBUF memory power force/disable/mode/state bits, and CM memory power/status fields.
- Diagnostic state: DPP3 CRC values/control and host read control.
- Converter and cursor state: surface pixel format, format expansion/conversion/clamping, FP bias/scale, color-key alpha/R/G/B values, alpha 2-bit LUT entries, cursor enable/mode/color fields, and cursor FP scale/bias.

Some fields are programmed configuration, some are readback/status, some are write-enable or index/data ports, and some are update-pending or power-state indicators. The header does not distinguish those classes beyond field names. Incorrect constants can therefore create persistent hardware misconfiguration until the driver reprograms the block, resets the pipe, power-cycles the block, or the GPU resets.

## Dependencies And Integration Points

This chunk is tightly coupled to the generated DCN 2.0.1 register address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h`

Direct include points found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`

For this specific chunk, the most direct integration is DPP resource setup in `dcn201_resource.c`, where `TF_REG_LIST_DCN201(id)` and `TF_REG_LIST_SH_MASK_DCN201(...)` bind DPP register addresses, shifts, and masks into `tf_regs`, `tf_shift`, and `tf_mask`. Those tables are passed to `dpp201_construct()` in `display/dc/dpp/dcn201/dcn201_dpp.c`.

Functional users include shared DPP and color-management code:

- `display/dc/dpp/dcn201/dcn201_dpp.c` programs `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `ALPHA_2BIT_LUT`, cursor disable paths, and DPP functions for degamma, blend LUT, shaper LUT, 3D LUT, scaler, HDR multiplier, and gamut remap.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c` uses DSCL fields for scaler modes, autocalibration, line-buffer configuration, recout/MPC dimensions, OBUF behavior, and DSCL memory power polling.
- `display/dc/dpp/dcn10/dcn10_dpp_cm.c` uses CM fields for gamut remap matrices, degamma/blend/shaper piecewise-linear LUT programming, CM memory power, LUT write masks, and color-management readback.
- `display/dc/core/dc_hw_sequencer.c` reaches these DPP operations through high-level plane/color update sequencing, so errors here can surface during normal modeset, atomic commit, and color-management flows.

The instance suffixes are part of the contract. `CM2`/`DSCL2` and `CM3`/`DSCL3` describe different DPP instances with nearly mirrored layouts. Generic code relies on instance-indexed register lists rather than treating the names as interchangeable.

## Risks And Edge Cases

- Silent hardware misprogramming is the main risk. A wrong shift or mask can compile cleanly while writing adjacent fields or failing to update the intended hardware bits.
- Repeated instance blocks are vulnerable to generated copy/paste drift. `DSCL2`/`DSCL3` and `CM2`/`CM3` are similar but must match the exact DCN 2.0.1 register database for each instance.
- LUT programming fields are high risk because index, data, write-enable mask, RAM select, and region metadata must agree. Bad masks in `CM*_DGAM_*`, `CM*_BLNDGAM_*`, `CM*_SHAPER_*`, or `CM*_3DLUT_*` can produce wrong gamma, banding, HDR errors, or incorrect color-space output.
- Matrix coefficient fields are packed 16-bit halves. Incorrect masks for CSC or gamut remap coefficient pairs can corrupt one coefficient while preserving the other, making color errors subtle and format-dependent.
- Scaler ratio and phase fields use fixed-width fractional formats. Overflow or wrong masks in scale ratio/init fields can cause visual distortion, edge sampling errors, scaler underflow, or bad 4:2:0 chroma alignment.
- Geometry fields such as blanking, overscan, recout, MPC size, and line-buffer partition counts are packed into shared registers. Bad values can affect only specific modes, pipe splits, or scaling ratios.
- Power-control fields combine force, disable, mode, and status semantics. Confusing `*_MEM_PWR_CTRL` with `*_MEM_PWR_STATUS`, or using a bad mask in `REG_WAIT`, can leave DSCL/CM/OBUF memories unavailable or unnecessarily powered.
- Converter and cursor fields are format-sensitive. Incorrect `CNVC_SURFACE_PIXEL_FORMAT`, alpha, clamp, FP bias/scale, color key, or cursor fields can break only certain pixel formats such as FP16, 10bpc, packed RGB, or 4:2:0 video.
- The chunk boundaries are not semantic boundaries. The line range starts after earlier `DSCL2` definitions and ends before completing `CM3_CM_BLNDGAM_RAMB_REGION_*`; whole-file analysis should not infer missing hardware support from this slice alone.

## Test Signals

Useful validation for changes to this generated range is mostly build-time plus display hardware behavior:

- Build AMDGPU display code paths that include `dcn_2_0_1_sh_mask.h`, especially DCN201 resource, IRQ, clock manager, DPP, DSCL, and CM translation units.
- Static generated-register comparison should verify every `__SHIFT` and `_MASK` value against AMD's DCN 2.0.1 register database and the matching addresses in `dcn_2_0_1_offset.h`.
- Modeset and plane tests should exercise DPP instances 2 and 3 with no scaling, upscaling, downscaling, 4:2:0 luma/chroma scaling, multi-plane composition, pipe split, overscan, cursor enable/disable, and recout/MPC geometry changes.
- Color-management tests should cover input CSC, gamut remap, degamma PWL, blend LUT, shaper LUT, 3D LUT, HDR multiplier, coefficient format changes, and readback where supported.
- Pixel-format tests should cover ARGB/RGBA variants, RGB565/ARGB1555, 10bpc formats, FP16, RGB111110/BGR101111, and 4:2:0 video formats that drive CNVC and input CSC fields.
- Power-management stress should cover suspend/resume, runtime power gating, memory power transitions, clock changes, and repeated color/scaler updates while checking that `*_UPDATE_PENDING`, `*_MEM_PWR_STATUS`, and OBUF/DSCL status fields settle.
- Diagnostic signals include DPP CRC sanity, lack of DSCL/OBUF underflow symptoms, stable cursor behavior, absence of color banding or matrix errors, and no unexpected hangs during LUT programming.

## Cross-Chunk Notes

This is a generated constants-only slice. Its substantive behavior lives in the DCN201 display driver code and DCN 2.0.1 hardware. Adjacent chunks are needed to describe the full `dcn_2_0_1_sh_mask.h` file, including the earlier DPP2 scaler fields before line 7596 and the remaining CM3 fields after line 10129.
