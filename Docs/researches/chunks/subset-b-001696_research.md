# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 22334-24838

## Scope

This chunk is chunk 10 of the oversized generated DCN 3.0.0 register mask header. It covers lines 22334-24838 of `dcn_3_0_0_sh_mask.h`, beginning inside the `CM3_CM_GAMCOR_RAMB_REGION_*` table, finishing most of the DPP3 color-management register masks, then switching into DPP4 top, format conversion, cursor, scaler, and color-management masks. The final visible line starts `CM4_CM_BLNDGAM_RAMA_REGION_30_31`, so the DPP4 blend-gamma RAMA table continues into the next chunk.

The file is a generated C preprocessor header. It contains no functions, storage definitions, structs, or runtime control flow. Its API is the set of `#define` constants named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`, consumed by AMD DC register helper macros to pack, unpack, update, and poll MMIO bitfields.

## Purpose

This chunk supplies bit positions and bit masks for display pipe processor register fields in DCN 3.0.0 hardware. The definitions let the AMD display driver use symbolic field names instead of literal bit operations when programming:

- DPP3 color-management gamma correction, blend gamma, shaper LUT, 3D LUT, memory power, and test/debug registers.
- DC performance monitor instance 15 counter, control, interrupt, and value registers.
- DPP4 top-level DPP control, soft reset, CRC, and host read controls.
- DPP4 CNVC format-conversion and cursor controls, including surface format, alpha/color keying, pre-CSC matrices, pre-degamma, pre-dealpha, and pre-realpha fields.
- DPP4 DSCL scaler coefficient RAM, scaler mode, taps, ratios, initial phases, overscan, recout/MPC size, line-buffer settings, memory power controls, OBUF control, and blanking/viewport fields.
- DPP4 CM post-CSC, gamut remap, bias, gamma-correction RAM/LUT, and the beginning of blend-gamma RAMA definitions.

The constants are part of the hardware ABI for the DCN 3.0 register layout. A wrong mask or shift would compile successfully but steer later register writes into the wrong hardware bits.

## Important Macro Surfaces

### DPP3 Color Management Tail

The first part of the chunk is still in the DPP3 color-management block and starts mid-table:

- `CM3_CM_GAMCOR_RAMB_REGION_20_21` through `CM3_CM_GAMCOR_RAMB_REGION_32_33` define gamma-correction RAMB region LUT offsets and segment counts. Each pair uses a stable packing pattern: even region offset at shift `0x0`, even region segment count at `0xc`, odd region offset at `0x10`, and odd region segment count at `0x1c`; masks are `0x000001FFL`, `0x00007000L`, `0x01FF0000L`, and `0x70000000L`.
- `CM3_CM_BLNDGAM_CONTROL`, `CM3_CM_BLNDGAM_LUT_INDEX`, `CM3_CM_BLNDGAM_LUT_DATA`, and `CM3_CM_BLNDGAM_LUT_CONTROL` expose blend-gamma mode/select/current-state fields plus host LUT index/data/read/write controls.
- `CM3_CM_BLNDGAM_RAMA_*` and `CM3_CM_BLNDGAM_RAMB_*` define piecewise linear blend-gamma RAM programming for both RAM banks. Per color channel, start controls include start value and start segment, start slope/base use 18-bit masks, end controls split end base and end/slope words, offsets use 19-bit masks, and region tables cover regions 0 through 33 in pairs.
- `CM3_CM_HDR_MULT_COEF`, `CM3_CM_DEALPHA`, and `CM3_CM_COEF_FORMAT` provide color pipeline coefficient/de-alpha formatting controls.
- `CM3_CM_MEM_PWR_CTRL`, `CM3_CM_MEM_PWR_STATUS`, `CM3_CM_MEM_PWR_CTRL2`, and `CM3_CM_MEM_PWR_STATUS2` expose memory power force/disable/mode/state fields for CM LUT memories, 3D LUTs, and related RAMs.
- `CM3_CM_SHAPER_*` covers shaper offset/scale, LUT index/data/write masks, and RAMA/RAMB piecewise region programming.
- `CM3_CM_3DLUT_*` covers 3D LUT mode/size/current mode, LUT index/data words, 30-bit data mode, read/write enable, RAM select, read select, output normalization, and per-channel output scale/offset.
- `CM3_CM_TEST_DEBUG_INDEX` and `CM3_CM_TEST_DEBUG_DATA` expose CM test/debug selector and data fields.

These DPP3 names align with color-management programming paths in the DPP helpers. For example, the DPP code reads 3D LUT and blend-gamma status through `CM_3DLUT_*` and `CM_BLNDGAM_*` field names after the DPP register-list macros map the instance-specific register names.

### DC Performance Monitor 15

The `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` block defines `DC_PERFMON15_*` fields:

- `DC_PERFMON15_PERFCOUNTER_CNTL` selects event, counted value, increment mode, hardware control, run-enable mode, counter offset behavior, restart, interrupt enable, active status, and counter-control selector. It has dense high-bit control fields up to `PERFCOUNTER_CNTL_SEL` at mask `0xE0000000L`.
- `DC_PERFMON15_PERFCOUNTER_CNTL2` selects counted value type, hardware stop sources, counter-offset source, and secondary control selector.
- `DC_PERFMON15_PERFCOUNTER_STATE` packs state and state-select fields for eight counters, alternating 2-bit state and 2-bit selector nibbles.
- `DC_PERFMON15_PERFMON_CNTL` and `DC_PERFMON15_PERFMON_CNTL2` define performance monitor run, report count, counter-offset boolean behavior, interrupt type/status/ack, clock enable, and run-start/stop selectors.
- `DC_PERFMON15_PERFMON_CVALUE_INT_MISC`, `DC_PERFMON15_PERFMON_CVALUE_LOW`, `DC_PERFMON15_PERFMON_HI`, and `DC_PERFMON15_PERFMON_LOW` expose counter interrupt status/ack bits and sampled counter value words.

These macros are diagnostic and instrumentation infrastructure rather than display-mode policy. The high risk is stale field layout against the matching `dcn_3_0_0_offset.h` `mmDC_PERFMON15_*` addresses or later DCN family variants.

### DPP4 Top-Level Controls

The `dce_dc_dpp4_dispdec_dpp_top_dispdec` block starts DPP instance 4:

- `DPP_TOP4_DPP_CONTROL` contains clock gating/enable fields such as `DPP_CLOCK_ENABLE`, DPPCLK/DISPCLK gate-disable fields, and `DPP_TEST_CLK_SEL`.
- `DPP_TOP4_DPP_SOFT_RESET` supplies soft reset bits for CNVC, DSCL, CM, and OBUF sub-blocks.
- `DPP_TOP4_DPP_CRC_VAL_R_G`, `DPP_TOP4_DPP_CRC_VAL_B_A`, and `DPP_TOP4_DPP_CRC_CTRL` define DPP CRC value and control fields, including CRC enable, continuous mode, one-shot pending, 4:2:0 component select, source select, stereo/interlace/pixel/cursor format selects, and CRC mask.
- `DPP_TOP4_HOST_READ_CONTROL` exposes host-read rate control.

These fields integrate with resource and debug code that builds DPP register tables via `DPP_REG_LIST_DCN30(id)` and field tables via `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` / `_MASK` in `dcn30_resource.c`.

### DPP4 CNVC Format Conversion And Cursor

The `dce_dc_dpp4_dispdec_cnvc_cfg_dispdec` block defines format-converter fields:

- `CNVC_CFG4_CNVC_SURFACE_PIXEL_FORMAT` selects surface pixel format and alpha-plane enable.
- `CNVC_CFG4_FORMAT_CONTROL` includes format expansion, 16-bit conversion, alpha enable, CNVC bypass, MSB alignment, positive clamps, update-pending status, and R/G/B crossbar selectors.
- `CNVC_CFG4_FCNV_FP_BIAS_*` and `CNVC_CFG4_FCNV_FP_SCALE_*` define floating-point conversion bias and scale values for RGB channels.
- `CNVC_CFG4_COLOR_KEYER_*` provides enable/mode plus low/high threshold fields for alpha, red, green, and blue.
- `CNVC_CFG4_ALPHA_2BIT_LUT` packs four 2-bit alpha LUT entries.
- `CNVC_CFG4_PRE_DEALPHA`, `CNVC_CFG4_PRE_DEGAM`, and `CNVC_CFG4_PRE_REALPHA` expose pre-processing enables and degamma mode/select fields.
- `CNVC_CFG4_PRE_CSC_MODE`, `CNVC_CFG4_PRE_CSC_C*`, and `CNVC_CFG4_PRE_CSC_B_C*` define current-mode status and A/B coefficient matrix fields for pre-CSC.
- `CNVC_CFG4_CNVC_COEF_FORMAT` selects pre-CSC coefficient format.

The `dce_dc_dpp4_dispdec_cnvc_cur_dispdec` block defines cursor controls:

- `CNVC_CUR4_CURSOR0_CONTROL` includes cursor enable, expansion mode, pixel inversion mode, ROM enable, cursor mode, pixel alpha modulation, and update pending status.
- `CNVC_CUR4_CURSOR0_COLOR0` and `CNVC_CUR4_CURSOR0_COLOR1` define palette colors.
- `CNVC_CUR4_CURSOR0_FP_SCALE_BIAS` packs cursor floating-point scale and bias.

These fields feed plane format, cursor, color key, and input color conversion paths. Because many fields are state bits such as `*_UPDATE_PENDING` or `*_MODE_CURRENT`, callers may read them to confirm hardware state after programming double-buffered controls.

### DPP4 DSCL Scaler

The `dce_dc_dpp4_dispdec_dscl_dispdec` block is broad and latency-sensitive:

- Coefficient RAM access: `DSCL4_SCL_COEF_RAM_TAP_SELECT` and `DSCL4_SCL_COEF_RAM_TAP_DATA` select tap pair, phase, filter type, even/odd coefficients, and coefficient enables.
- Mode and taps: `DSCL4_SCL_MODE`, `DSCL4_SCL_TAP_CONTROL`, `DSCL4_DSCL_CONTROL`, and `DSCL4_DSCL_2TAP_CONTROL` select DSCL mode, coefficient RAM source/current/readback, chroma/alpha coefficient modes, vertical/horizontal luma and chroma tap counts, boundary mode, and 2-tap hardcode/sharpness fields.
- Ratios and phases: `DSCL4_SCL_HORZ_FILTER_SCALE_RATIO`, `DSCL4_SCL_HORZ_FILTER_INIT`, chroma `*_C` equivalents, `DSCL4_SCL_VERT_FILTER_SCALE_RATIO`, `DSCL4_SCL_VERT_FILTER_INIT`, bottom-field variants, and chroma/bottom-field variants provide horizontal/vertical scale ratios and fixed-point integer/fractional initialization.
- Viewport and output geometry: `DSCL4_DSCL_EXT_OVERSCAN_LEFT_RIGHT`, `DSCL4_DSCL_EXT_OVERSCAN_TOP_BOTTOM`, `DSCL4_OTG_H_BLANK`, `DSCL4_OTG_V_BLANK`, `DSCL4_RECOUT_START`, `DSCL4_RECOUT_SIZE`, and `DSCL4_MPC_SIZE` pack overscan, blanking, recout start/size, and MPC dimensions.
- Line buffer and memory: `DSCL4_LB_DATA_FORMAT`, `DSCL4_LB_MEMORY_CTRL`, `DSCL4_LB_V_COUNTER`, `DSCL4_DSCL_MEM_PWR_CTRL`, `DSCL4_DSCL_MEM_PWR_STATUS`, `DSCL4_OBUF_CONTROL`, and `DSCL4_OBUF_MEM_PWR_CTRL` define alpha/interleave, memory partitioning, counters, LUT/LB memory power force/disable/mode/state, OBUF bypass/full-buffer/half-width/hold count, and OBUF memory power.
- Update/autocal: `DSCL4_DSCL_UPDATE` exposes scaler update pending, and `DSCL4_DSCL_AUTOCAL` selects autocal mode, pipe count, and pipe ID.

Runtime DPP scaler code uses corresponding generic names such as `DSCL_MEM_PWR_CTRL`, `DSCL_MEM_PWR_STATUS`, `SCL_MODE`, `SCL_TAP_CONTROL`, and `DSCL_AUTOCAL` through per-instance register arrays. Incorrect DSCL shifts can lead to visible scaler artifacts, invalid viewport programming, hangs while polling memory power state, or silent corruption of line-buffer partitioning.

### DPP4 Color Management Start

The `dce_dc_dpp4_dispdec_cm_dispdec` block defines the start of DPP4 CM:

- `CM4_CM_CONTROL` and `CM4_CM_POST_CSC_CONTROL` define CM enable/mode and post-CSC mode/current status.
- `CM4_CM_POST_CSC_C*` and `CM4_CM_POST_CSC_B_C*` define A/B matrix coefficient pairs for post-CSC. Most coefficient-pair registers pack two signed/fixed-width coefficients with low/high halfword masks.
- `CM4_CM_GAMUT_REMAP_CONTROL`, `CM4_CM_GAMUT_REMAP_C*`, and `CM4_CM_GAMUT_REMAP_B_C*` mirror that pattern for gamut remap.
- `CM4_CM_BIAS_CR_R` and `CM4_CM_BIAS_Y_G_CB_B` define bias fields for chroma/red and Y/green/CB/blue paths.
- `CM4_CM_GAMCOR_CONTROL`, `CM4_CM_GAMCOR_LUT_INDEX`, `CM4_CM_GAMCOR_LUT_DATA`, and `CM4_CM_GAMCOR_LUT_CONTROL` define gamma-correction mode/select/current state plus LUT host access.
- `CM4_CM_GAMCOR_RAMA_*` and `CM4_CM_GAMCOR_RAMB_*` provide gamma-correction PWL RAM programming for both banks, including start/end/base/slope/offset and paired region tables 0 through 33.
- `CM4_CM_BLNDGAM_CONTROL`, `CM4_CM_BLNDGAM_LUT_INDEX`, `CM4_CM_BLNDGAM_LUT_DATA`, and `CM4_CM_BLNDGAM_LUT_CONTROL` begin DPP4 blend-gamma control and LUT access.
- `CM4_CM_BLNDGAM_RAMA_*` starts the DPP4 blend-gamma RAMA table and reaches `CM4_CM_BLNDGAM_RAMA_REGION_30_31` at the chunk boundary. The matching `REGION_32_33` and RAMB definitions continue in chunk `subset-b-001697`.

The DPP4 CM region mirrors the DPP3 CM pattern earlier in this chunk. That symmetry is an important validation signal: mismatches between `CM3_` and `CM4_` field layouts in otherwise repeated blocks should be intentional hardware differences, not manual edits.

## Control Flow And State Behavior

There is no executable control flow in this header. The relevant flow is compile-time expansion:

1. DCN resource files include `dcn/dcn_3_0_0_offset.h` and `dcn/dcn_3_0_0_sh_mask.h`.
2. Register-list macros, for example the DPP register list in DCN30 resource code, expand address constants from the offset header into per-block register structures.
3. Field-list macros expand this header's `__SHIFT` and `_MASK` constants into mask/shift structures.
4. Runtime helper macros such as `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT` use those structures to read-modify-write or poll MMIO fields.

The state represented here is hardware register state, not software persistence:

- `*_MODE`, `*_SELECT`, `*_WRITE_*`, `*_FORCE`, and `*_DIS` fields are writable controls.
- `*_CURRENT`, `*_UPDATE_PENDING`, `*_STATE`, `*_STATUS`, `*_ACTIVE`, and counter value fields are readback/status signals.
- RAM/LUT index/data/control fields expose host-programmed tables whose persistence is in display hardware until reprogrammed, reset, power-gated, or reinitialized by the display stack.
- Memory power fields (`CM3_CM_MEM_PWR_*`, `DSCL4_DSCL_MEM_PWR_*`, `DSCL4_OBUF_MEM_PWR_*`) are especially stateful because write-side force/disable fields and read-side state fields are paired and often polled.

## Dependencies And Integration Points

This chunk depends on the matching register-address header for DCN 3.0.0. Field macros alone do not identify MMIO addresses; they are paired with `dcn_3_0_0_offset.h` entries such as `mmDPP_TOP4_*`, `mmCNVC_CFG4_*`, `mmDSCL4_*`, `mmCM4_*`, and `mmDC_PERFMON15_*`.

Local include sites for `dcn_3_0_0_sh_mask.h` include:

- `display/dc/resource/dcn30/dcn30_resource.c`, where the DPP register and mask/shift tables are built.
- `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, `display/dmub/src/dmub_dcn30.c`, and `display/dmub/src/dmub_dcn302.c`.
- DCN30/302 IRQ service files and DCN30 GPIO factory/translation files.

The most direct consumer family for this chunk is the DPP code under `display/dc/dpp/`, particularly common DCN10/DCN20/DCN30 DPP and DSCL helpers. Those helpers use generic field names after the register-list macros resolve instance-specific prefixes. Examples visible in the local tree include reads of `CM_3DLUT_*` and `CM_BLNDGAM_*` status in DPP code and writes/polls of `DSCL_MEM_PWR_CTRL` and `DSCL_MEM_PWR_STATUS` in DSCL memory-power handling.

## Risks

- Generated-header drift: if this file is regenerated from a different hardware description than `dcn_3_0_0_offset.h`, the compiler will not catch semantic mismatches between register addresses and bitfields.
- Instance skew: this chunk switches from DPP3 to DPP4. Copy/paste or generation errors can silently put a DPP3 field layout under a DPP4 name, or miss a DPP4-specific field. The repeated CM RAMA/RAMB tables make this hard to review manually.
- Boundary incompleteness: the chunk starts in the middle of `CM3_CM_GAMCOR_RAMB_REGION_*` and ends in the middle of `CM4_CM_BLNDGAM_RAMA_REGION_*`. Whole-file synthesis must merge adjacent chunks before drawing conclusions about complete table coverage.
- Status/control confusion: fields ending in `CURRENT`, `UPDATE_PENDING`, `STATE`, `STATUS`, or `ACTIVE` are readback/status fields in many call paths. Treating them as ordinary writable configuration bits can produce ineffective writes or incorrect waits.
- Memory power polling risk: wrong `*_MEM_PWR_STATE` masks or shifts can make `REG_WAIT` loops wait on the wrong bits, leading to timeouts or using RAM blocks before they are powered.
- DSCL visual correctness risk: wrong scaler tap, ratio, phase, overscan, or line-buffer fields can produce visible corruption, underflow, or mode-set failures without a clean compile-time error.
- Perfmon diagnostic risk: `DC_PERFMON15_*` mistakes may only show under debug/performance tooling, making regressions easy to miss in normal display validation.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display behavior:

- Build coverage for DCN30 and DCN302 display code that includes `dcn_3_0_0_sh_mask.h`, especially `dcn30_resource.c`, DPP, DSCL, DMUB, IRQ, and clock manager objects.
- Register table initialization should compile without missing field symbols from `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `_MASK`.
- Display mode-set tests covering DPP4 planes should exercise CNVC format conversion, cursor enable/color modes, DSCL scaling ratios/taps, recout sizing, and CM post-CSC/gamut/gamma programming.
- Plane scaling tests should cover luma/chroma paths, bottom-field vertical init fields, bypass/scaling mode changes, and line-buffer partition programming.
- Color pipeline tests should cover post-CSC, gamut remap, gamma correction, blend gamma, shaper, and 3D LUT programming with readback of current/pending/status fields where available.
- Power-management tests should exercise DSCL/OBUF/CM memory power force/disable/state fields and verify waits do not time out.
- CRC and perfmon debug tests should verify DPP4 CRC controls/value registers and `DC_PERFMON15_*` counter setup/readback.
- Header consistency checks should diff repeated CM3/CM4 and RAMA/RAMB region layouts, and compare this header against adjacent DCN family generated headers where hardware compatibility is expected.

## Cross-Chunk Notes

- Previous chunk `subset-b-001695` is needed for the beginning of `CM3_CM_GAMCOR_RAMB_REGION_*` and earlier DPP3 CM state.
- Next chunk `subset-b-001697` is needed to complete `CM4_CM_BLNDGAM_RAMA_REGION_30_31`, `REGION_32_33`, and the remaining DPP4 blend-gamma RAMB or later register definitions.
- The final per-file report should synthesize all 29 chunks and avoid treating this chunk as an independently complete DPP3 or DPP4 register map.
