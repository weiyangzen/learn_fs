# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 46765-49290

## Scope

This chunk covers a generated AMD DCN 3.0.2 register shift/mask header region. It contains C preprocessor constants only: register grouping comments plus `__SHIFT` and `_MASK` `#define` entries. There are no C functions, structs, enums, storage objects, or direct MMIO operations in this slice.

The range starts in the middle of the display writeback output-gamma RAM A region table, continues through display writeback output-gamma RAM B fields, covers MPCC0 through MPCC4 compositor/blender field definitions, then covers MPCC output-gamma and gamut-remap blocks for MPCC OGAM0, OGAM1, OGAM2, and the beginning of OGAM3. It ends inside `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_12_13`, so the later merge lane must combine adjacent chunks before making whole-file completeness claims.

## Purpose

The purpose of this header region is to define bit positions and masks for DCN 3.0.2 display writeback, multi-plane composition, output-gamma, and gamut-remap registers. AMD display code uses these generated constants through register-helper macros so implementation files can update fields symbolically instead of hard-coding bit shifts and masks.

The covered hardware areas are:

- DWB OGAM RAMA/RAMB region descriptors and start/end/offset controls, used by the display writeback path's output transfer function programming.
- MPCC0-4 compositor controls, including top/bottom source selection, OPP assignment, alpha/blending controls, overlap behavior, global alpha/gain, per-layer gain, background color, memory power state, and disabled status.
- MPCC OGAM0-3 output-gamma LUT controls, including RAM A/B selection, mode/current-mode fields, LUT index/data access, per-color write masks, read selection, host RAM selection, and configuration mode.
- MPCC OGAM0-3 piecewise-linear region controls for RAM A and RAM B, including per-channel start/end/base/slope/offset fields and 34 region descriptors packed two regions per register.
- MPCC OGAM0-2 gamut-remap controls and matrix coefficient registers, with the beginning of MPCC OGAM3 following in the next chunk.

This is a hardware contract file. Its behavioral importance is that the numeric mask/shift values must match the DCN 3.0.2 register database and the matching offset header.

## Important APIs, Types, And Constants

There are no callable APIs or concrete types in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Address-block comments such as `// addressBlock: dce_dc_mpc_mpcc0_dispdec` and register comments such as `//MPCC0_MPCC_CONTROL` preserve the hardware grouping used by register-table macros.

Important register families in this chunk include:

- `DWB_OGAM_RAMA_REGION_6_7` through `DWB_OGAM_RAMA_REGION_32_33`, plus `DWB_OGAM_RAMB_*`, define DWB output gamma PWL RAM region layout. Region-pair registers pack one region's LUT offset at bits 0-8, segment count at bits 12-14, the next region's LUT offset at bits 16-24, and segment count at bits 28-30. Start controls carry an 18-bit start value and a start segment field; start/end base and slope fields are 18-bit or 16-bit depending on register; offsets are 19-bit.
- `MPCC<n>_MPCC_TOP_SEL`, `MPCC_BOT_SEL`, and `MPCC_OPP_ID` map compositor input and output routing fields for MPCC instances 0-4.
- `MPCC<n>_MPCC_CONTROL` maps composition mode and alpha/blend state: `MPCC_MODE`, `MPCC_ALPHA_BLND_MODE`, `MPCC_ALPHA_MULTIPLIED_MODE`, `MPCC_BLND_ACTIVE_OVERLAP_ONLY`, `MPCC_GLOBAL_ALPHA`, `MPCC_GLOBAL_GAIN`, `MPCC_BG_BPC`, and `MPCC_BOT_GAIN_MODE`.
- `MPCC<n>_MPCC_SM_CONTROL` maps state-machine controls and status such as `MPCC_SM_FORCE_NEXT_FRAME_POL`, `MPCC_SM_FIELD_ALT`, `MPCC_SM_FRAME_ALT`, `MPCC_SM_FORCE_NEXT_TOP_POL`, and current polarity fields.
- `MPCC<n>_MPCC_UPDATE_LOCK_SEL` maps the update lock source for each MPCC.
- `MPCC<n>_MPCC_TOP_GAIN`, `BOT_GAIN_INSIDE`, `BOT_GAIN_OUTSIDE`, and `BG_R_CR/G_Y/B_CB` map gain and background color data.
- `MPCC<n>_MPCC_MEM_PWR_CTRL` maps OGAM memory power controls and status: force, disable, and power-state fields.
- `MPCC<n>_MPCC_STATUS` maps the `MPCC_DISABLED` status bit.
- `MPCC_OGAM<n>_MPCC_OGAM_CONTROL`, `LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL` define output-gamma mode selection, active/current RAM selection, 9-bit LUT index, 18-bit LUT data, color write mask, read color selection, debug read, host RAM selection, and config mode.
- `MPCC_OGAM<n>_MPCC_OGAM_RAMA_*` and `RAMB_*` define the double-buffered output-gamma PWL RAM control surface for each MPCC OGAM block.
- `MPCC_OGAM<n>_MPCC_GAMUT_REMAP_COEF_FORMAT` and `MPCC_GAMUT_REMAP_MODE` define coefficient format and active/current gamut-remap mode fields.
- `MPCC_OGAM<n>_MPC_GAMUT_REMAP_C11_C12_A` through `C33_C34_B` pack signed matrix coefficients two 16-bit fields per register for two coefficient banks, A and B.

Related semantic values live outside this chunk. For example, generated enum headers define values such as `MPCC_GAMUT_REMAP_COEF_FORMAT_S2_13`, `MPCC_GAMUT_REMAP_COEF_FORMAT_S3_12`, gamut-remap mode selectors, DWB OGAM mode/select values, LUT host selection, and LUT read color selection.

## Control Flow

This chunk has no runtime control flow. Its effective control flow is compile-time macro expansion into register-helper operations:

1. DCN 3.0.2 display code includes this shift/mask header with the matching DCN 3.0.2 offset header.
2. Register table macros such as `SR`, `SRII`, `SF`, and DWB-specific `SF_DWB2` bind generated register names and field names into per-block register, shift, and mask structures.
3. Runtime code calls helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and multi-field variants.
4. The helper layer uses the generated shift and mask values from this header to produce the MMIO read/modify/write value for the selected register field.

The runtime consumers provide the actual flow. DWB code configures frame capture, programs gamut remap and output gamma, then enables or updates capture under DWB update-lock handling. MPC code configures composition trees by programming MPCC source routing, blend mode, OPP ID, gains, status, memory power controls, MPCC OGAM LUTs, and gamut-remap matrices. The header only supplies the field layout needed for those sequences.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes stateful hardware registers:

- DWB OGAM RAMA/RAMB fields persist the display writeback output transfer function's PWL segmentation, start/end values, slopes, base values, offsets, and selected LUT RAM until reprogrammed or reset.
- MPCC routing state persists which DPP/top source and bottom MPCC feed each compositor, and which OPP receives the composed output.
- MPCC control state persists blend mode, alpha semantics, global alpha/gain, background bit depth, and bottom gain handling.
- MPCC update-lock selection and state-machine fields coordinate when compositor changes take effect relative to display timing.
- MPCC OGAM mode/select/current fields expose double-buffered output-gamma state. Software programs one RAM bank while hardware can continue using another, then switches selected/current RAM under the block's update semantics.
- MPCC OGAM LUT index/data/control fields represent host access to LUT RAM; the index and host selection determine which RAM entry and color component subsequent data writes or reads touch.
- Gamut-remap mode/current-mode and coefficient bank fields persist matrix color conversion state in the MPC/MPCC OGAM path.
- Memory power control bits can force, disable, or report OGAM memory power state. Incorrect values can make later LUT or gamma programming ineffective even if the register writes appear to complete.

Persistence is hardware-defined. Writable control fields remain until a later driver update, block reset, display power-state transition, or full ASIC reset. Status/current fields are read by software but are represented with the same mask/shift style as writable fields, so legal read/write direction is not encoded in this header.

## Dependencies And Integration Points

This chunk depends on several generated and handwritten AMD display components staying synchronized:

- The matching `dcn_3_0_2_offset.h` register-offset header supplies MMIO addresses for the register names whose fields are described here.
- The register helper layer in AMD display code consumes the suffix convention through macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT`.
- DWB integration appears in `drivers/gpu/drm/amd/display/dc/dwb/dcn30/`, where `dcn30_dwb.h` lists the DWB OGAM registers and field masks and `dcn30_dwb.c` programs DWB enable/update, gamut remap, and output transfer function state.
- MPC integration appears in `drivers/gpu/drm/amd/display/dc/mpc/dcn10/` and `dcn30/`. `dcn10_mpc.c` uses MPCC top/bottom/OPP/control fields to build and tear down composition trees. `dcn30_mpc.h` adds the DCN 3.x MPCC OGAM and gamut-remap register/field table entries.
- Higher-level display color management and plane composition code supplies transfer functions, blend parameters, gamut-remap matrices, and stream/plane topology that eventually become writes through these fields.
- Generated enum headers such as `soc21_enum.h` and `soc24_enum.h` document semantic values for DWB OGAM and MPCC gamut-remap fields, but this file only defines bit placement.

The main integration contract is preprocessor naming. If a field macro is missing or renamed, register-table construction usually fails at compile time. If a mask or shift is numerically wrong, the code can compile and then program the wrong hardware bits.

## Risks And Edge Cases

- The line range starts mid-DWB `RAMA` region table and ends mid-MPCC OGAM3 `RAMA` region table. Adjacent chunk reconciliation is required for complete DWB/OGAM3 coverage.
- The repeated region-pair pattern is easy to generate incorrectly. A wrong offset or segment-count mask in one pair can corrupt only one part of the gamma curve while most neighboring registers continue to look correct.
- Region descriptors have unused bit gaps between LUT offset and segment count fields. Code must rely on masks rather than assuming adjacent packed fields.
- RAM A and RAM B fields are nearly identical. Accidentally using a `RAMA` field with a `RAMB` register, or selecting the wrong host RAM, can write a valid-looking LUT into the inactive or unintended bank.
- Current-mode/current-select fields are status/readback fields adjacent to desired mode/select fields. Confusing desired and current fields can make polling or update sequencing unreliable.
- Gamut-remap matrices pack two 16-bit coefficients per 32-bit register. Bad masks can swap or overwrite adjacent coefficients and cause subtle color-space errors rather than obvious hardware faults.
- MPCC top/bottom/OPP routing fields use small instance identifiers. A bad field width or invalid sentinel value can miswire a composition tree, especially when planes are inserted or removed dynamically.
- MPCC memory power fields affect OGAM RAM availability. Power gating or forced memory state mismatches can make LUT programming fail or produce stale output after resume.
- The macros do not encode access direction. Status bits such as `MPCC_DISABLED`, `MPCC_OGAM_MODE_CURRENT`, or memory power state look like ordinary fields to the preprocessor.
- Cross-generation reuse is risky. DCN 3.0.0, 3.0.1, and 3.0.2 names are similar, but the offset and shift/mask headers must match the target ASIC.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Compile the DCN 3.0.2 AMD display driver paths that include this header to catch missing or renamed `__SHIFT`/`_MASK` macros in `SF`, `SR`, `SRII`, and DWB field-list expansion.
- Preprocess representative DWB and MPC objects to confirm that register-helper field names resolve to the expected generated constants.
- Compare this chunk against the matching DCN 3.0.2 register database and offset header to verify register/field coverage, especially the DWB OGAM RAMA/RAMB and MPCC OGAM0-3 repeated blocks.
- Exercise DWB capture with output transfer functions enabled and disabled; expected signals are correct capture color output, stable DWB update-lock behavior, and no stale LUT bank after switching RAM A/B.
- Exercise display color-management paths that program MPCC OGAM LUTs and gamut-remap matrices, then validate visible output or CRCs across identity, sRGB-like, HDR/PQ-like, and custom matrix cases.
- Exercise plane composition with multiple planes, alpha blending, global alpha/gain, background color, and plane insert/remove operations; watch for MPCC routing errors or incorrect disabled status.
- Test suspend/resume and display power transitions, because OGAM memory power control and LUT RAM persistence are common failure points for generated mask mistakes.
- Run register readback/debug traces around `MPCC_OGAM_MODE_CURRENT`, `MPCC_OGAM_SELECT_CURRENT`, gamut-remap current mode, and `MPCC_DISABLED` to ensure software observes state changes through the expected fields.

## Open Cross-Chunk Questions

- The later merge lane should combine this with the previous chunk to present the full DWB OGAM RAMA table and the start of the DWB OGAM block.
- The later merge lane should combine this with the next chunk to present complete MPCC OGAM3 RAMA/RAMB and gamut-remap coverage.
- Whole-file analysis should verify that all MPCC and MPCC OGAM instances expected for DCN 3.0.2 are represented consistently across the offset header, shift/mask header, and the DCN 3.x MPC register-list macros.
