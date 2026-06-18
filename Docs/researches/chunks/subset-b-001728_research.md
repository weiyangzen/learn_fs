# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 14893-17407

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask header segment. It contains 2,115 preprocessor definitions: 1,052 `__SHIFT` constants and 1,063 `_MASK` constants for display pipe processor (`DPP`) register fields. There are no executable functions, types, global variables, runtime branches, or filesystem behavior in this source range.

The purpose of the chunk is to provide compile-time bitfield metadata for AMDGPU Display Core register helpers. The matching offset header, `dcn_3_0_1_offset.h`, supplies register addresses such as `mmDPP_TOP1_DPP_CONTROL`; this header supplies field layout constants such as `DPP_TOP1_DPP_CONTROL__DPP_CLOCK_ENABLE__SHIFT` and `DPP_TOP1_DPP_CONTROL__DPP_CLOCK_ENABLE_MASK`.

The slice starts in the tail of `DC_PERFMON10`, covers the complete DPP1 top, converter, cursor-converter, scaler, color-management, and `DC_PERFMON11` blocks, then enters DPP2 top and converter configuration before ending at the `CNVC_CFG2_PRE_DEGAM` marker. The final per-file report should merge adjacent chunks before treating `DC_PERFMON10` or DPP2 converter coverage as complete.

Although this file is under a `ceph-client` source mirror, this chunk is AMD GPU display register metadata. It does not implement Ceph, distributed filesystem logic, storage persistence, or network protocol behavior.

## Register Blocks Covered

The preamble finishes `DC_PERFMON10` with performance monitor control, run-enable start/stop selection, current-value interrupt status/ack bits, high/low counter readback, and read-select fields. The earlier counter-control and counter-state definitions for instance 10 begin before this chunk.

`dce_dc_dpp1_dispdec_dpp_top_dispdec` covers `DPP_TOP1_*` control, soft reset, CRC readback/control, and host read-rate control. These fields gate DPP clocks, request soft resets for CNVC/DSCL/CM/OBUF sub-blocks, configure CRC capture format/source/mask/stereo/interlace behavior, and expose CRC R/G/B/A result halves.

`dce_dc_dpp1_dispdec_cnvc_cfg_dispdec` covers `CNVC_CFG1_*` pixel converter configuration. It includes surface pixel format and alpha-plane enable, format expansion and channel crossbar controls, floating-point conversion bias/scale values, color keyer thresholds, alpha LUT, pre-dealpha, pre-CSC mode and coefficient matrices for banks A/B, coefficient format, pre-degamma mode/select, and pre-realpha.

`dce_dc_dpp1_dispdec_cnvc_cur_dispdec` covers `CNVC_CUR1_CURSOR0_*` cursor converter fields: cursor enable/mode/expansion, FP16 enable, color registers, and cursor floating-point scale/bias.

`dce_dc_dpp1_dispdec_dscl_dispdec` covers `DSCL1_*` scaler and line-buffer fields. It includes scaler coefficient RAM selection/data, scaler mode, tap counts, two-tap sharpness controls, manual replication, horizontal/vertical luma/chroma scale ratios and initial phases, black color, update/autocal controls, overscan, OTG blank windows, recout and MPC dimensions, line-buffer data format and memory layout, live vertical counter, DSCL memory power status/control, OBUF control, and OBUF memory power control.

`dce_dc_dpp1_dispdec_cm_dispdec` is the largest block in this chunk. It covers `CM1_*` color-management control, post-CSC matrices, gamut remap matrices, bias registers, GAMCOR and BLNDGAM programmable transfer functions with RAM A/B region metadata, HDR multiplier, dealpha, coefficient format, shaper LUT/RAM region programming, memory power controls and status, 3D LUT index/data/read-write controls and output normalization/offset, plus test debug index/data registers.

`dce_dc_dpp1_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` covers full `DC_PERFMON11` counter control, selection, state, global perfmon control, interrupt, and readback registers for DPP1 diagnostics.

`dce_dc_dpp2_dispdec_dpp_top_dispdec` mirrors the DPP top fields for instance 2. `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec` begins the DPP2 converter configuration block and is covered through `CNVC_CFG2_CNVC_COEF_FORMAT`; the final line is only the comment for `CNVC_CFG2_PRE_DEGAM`, with its field definitions continuing after this chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned 32-bit mask for that field.
- Instance prefixes in this chunk include `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, `CM1`, `DC_PERFMON10`, `DC_PERFMON11`, `DPP_TOP2`, and `CNVC_CFG2`.
- Address-block and register comments are documentation delimiters only; C code consumes the `#define` symbols.
- Names such as `CM1_CM_SHAPER_LUT_WRITE_EN_MASK__CM_SHAPER_LUT_WRITE_EN_MASK_MASK` are expected generated names where the hardware field itself includes `MASK`.

The main local consumer pattern is in the DCN 3.0 DPP register lists. `display/dc/resource/dcn301/dcn301_resource.c` builds `dpp_regs[]`, `tf_shift`, and `tf_mask` through `DPP_REG_LIST_DCN30(id)` and `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT/_MASK)`. `display/dc/dpp/dcn30/dcn30_dpp.h` maps logical DPP registers to instance-prefixed symbols with `SRI(...)` and field metadata with `TF_SF(...)`/`TF2_SF(...)`; those lists include the converter, cursor converter, scaler, color management, memory-power, and DPP control fields represented in this chunk.

Runtime code reaches these constants through register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WAIT`, plus transfer-function helpers that copy field shifts and masks into color-management programming structures.

## Functional Areas

Pixel conversion fields in `CNVC_CFG1` and the start of `CNVC_CFG2` describe how scanout surface data is interpreted before scaling and color management. Important field groups include pixel format, alpha-plane enable, 16-bit conversion, alpha enable, converter bypass and MSB alignment, positive clamping, RGB crossbar selection, FP bias/scale, color-key thresholds, 2-bit alpha LUT, pre-dealpha/pre-realpha, pre-CSC bank selection/current-state readback, pre-CSC coefficient matrices, and pre-degamma mode/select.

Cursor converter fields provide the DPP-local cursor conversion layer. They control cursor mode, expansion, enable, floating-point conversion enable, two cursor colors, and FP scale/bias. These fields integrate with cursor attribute programming in DPP code, while broader cursor fetch/address controls live in other cursor blocks and chunks.

Scaler fields in `DSCL1` drive the digital scaler and line buffer. Coefficient RAM fields select tap pairs, filter phase, filter type, and even/odd tap coefficients. Mode/tap/2-tap fields select scaler mode, luma/chroma coefficient RAM behavior, tap counts, boundary behavior, and 2-tap sharpening. Ratio/init fields program luma/chroma horizontal and vertical scale ratios and initial phases, including bottom-field values for interlaced paths. Output geometry fields define recout start/size, MPC size, overscan, and OTG blank reference windows.

Color-management fields in `CM1` describe the DPP color pipeline around post-CSC, gamut remap, programmable gamma correction (`GAMCOR`), blend gamma (`BLNDGAM`), shaper LUT, 3D LUT, HDR multiply, coefficient format, and dealpha. GAMCOR, BLNDGAM, and SHAPER use RAM A/B banks with LUT index/data windows plus many region start/end/base/slope/offset fields. The driver can program an inactive bank, switch selection, and read current mode/select state through adjacent control fields.

Power and clock fields include DPP top clock-enable/gating-disables, per-sub-block soft reset, DSCL/OBUF memory power force/disable/status fields, and CM memory power controls/status for GAMCOR, BLNDGAM, SHAPER, and 3D LUT memory. These are used by DPP initialization, power optimization, and suspend/resume paths.

Diagnostic fields include DPP CRC control/readback, host read-rate control, CM test debug index/data, and DC performance monitors. The perfmon registers expose event and increment selection, counted value selection, run-enable state, per-counter state selection, overflow/threshold interrupt controls, current-value interrupt status/ack bits, and high/low counter readback.

## Control Flow

This header has no local control flow. The effective flow is compile-time symbol expansion:

1. DCN 3.0.1 sources include `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h`.
2. Register-list macros select a DPP instance and paste names such as `CM1_CM_GAMCOR_CONTROL` or `DSCL1_SCL_MODE` into address tables.
3. Field-list macros paste instance-0 field names into shared shift/mask tables because replicated DPP instances have the same field layout.
4. Runtime DPP, color-management, cursor, scaler, and power code writes or reads fields through common MMIO helpers.

The runtime sequencing is external to this header. Typical flows set surface pixel format, converter/pre-CSC state, scaler geometry and coefficients, color-management LUTs/matrices, cursor conversion state, and memory-power controls during modeset, plane update, color update, cursor update, or power transition.

## State And Persistence Behavior

The file itself stores no state. Its macros describe memory-mapped DCN hardware state that persists while the display controller block remains powered and until driver, firmware, reset, or hardware logic changes it.

Persistent configuration state represented here includes converter format and alpha settings, color keyer bounds, pre-CSC/post-CSC/gamut matrices, scale ratios and coefficients, recout/MPC geometry, LUT region metadata, 3D LUT normalization and offsets, clock gating overrides, soft reset controls, and memory power force/disable settings.

Live or latched status state includes `*_CURRENT` mode/select fields, DSCL line-buffer and memory-power status, vertical counter readback, CRC result registers, perfmon counter values, perfmon interrupt status bits, and per-counter state fields. Fields named `*_ACK`, `*_STATUS`, `*_PENDING`, `*_CURRENT`, `*_STATE`, or `*_READ_*` should not be treated as ordinary writable configuration just because this header exposes their bit layout.

Several field groups have implicit double-buffering or bank-selection behavior. GAMCOR, BLNDGAM, SHAPER, pre-CSC, post-CSC, and gamut-remap bank A/B fields must be coordinated with mode/select/current fields so a partially programmed LUT or matrix is not made active. Memory power fields must be sequenced with use of the corresponding LUT RAMs; forcing memory off while a block is active can produce visible color errors or hangs waiting for status.

## Dependencies And Integration Points

This chunk depends on the DCN 3.0.1 register contract and must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`. Offset and mask headers must evolve together; a correct mask paired with a wrong address is still an incorrect MMIO operation.

Observed include and integration points include:

- `display/dmub/src/dmub_dcn301.c`, which includes both DCN 3.0.1 offset and shift/mask headers for DMUB register access.
- `display/dc/resource/dcn301/dcn301_resource.c`, which instantiates DPP register, shift, and mask tables using DCN30 DPP macros.
- `display/dc/dpp/dcn30/dcn30_dpp.h`, which names the DPP registers and fields covered here in `DPP_REG_LIST_DCN30_COMMON`, `DPP_REG_LIST_DCN30`, and `DPP_REG_LIST_SH_MASK_DCN30_COMMON`.
- `display/dc/dpp/dcn30/dcn30_dpp.c`, which programs pre-degamma, format control, surface pixel format, cursor conversion, DSCL memory power, and snapshots DPP/DSCL state.
- `display/dc/dpp/dcn30/dcn30_dpp_cm.c`, which programs GAMCOR LUT RAMs, gamut-remap matrices, transfer-function region descriptors, memory power, and related current-state fields.

The hardware integration points are the DPP pipeline stages: CNVC input conversion, CNVC cursor conversion, DSCL scaling/line buffering, CM color processing, DPP top-level clock/reset/CRC, and per-DPP performance monitoring.

## Risks And Edge Cases

Wrong shifts or masks compile cleanly but can silently corrupt display programming. High-risk fields include color matrices and LUT region descriptors, bank-select/current fields, memory-power force/disable bits, scaler ratios/initial phases, coefficient RAM selection/data, soft reset bits, CRC controls, and perfmon interrupt acknowledge fields.

Chunk boundaries split logical blocks. `DC_PERFMON10` is only a tail in this range, and `CNVC_CFG2_PRE_DEGAM` begins at the last line with no field definitions in the chunk. A final report should not claim complete DPP2 converter coverage from this file range alone.

Replicated instance names are easy to mix. DPP1 is complete here, DPP2 is partial, and shared field-mask tables often use instance-0 field names because field layouts are replicated. Manually substituting prefixes can break either address selection or field-table initialization.

Status and acknowledge bits are adjacent in perfmon and CRC-related registers. Confusing `*_STATUS`, `*_ACK`, `*_INT_EN`, `*_INT_TYPE`, or readback fields can leave interrupts stuck, clear diagnostic state unexpectedly, or report stale counter values.

Color pipeline fields require bank and memory sequencing. Programming `GAMCOR`, `BLNDGAM`, `SHAPER`, or 3D LUT data while the wrong bank is selected, while memory is powered down, or while current-mode readbacks are ignored can cause partial transfer functions to become visible.

Scaler fields are mode-sensitive and packed into limited-width fixed-point fields. Overwide or unvalidated mode-derived values for ratios, initial phases, blank windows, recout sizes, MPC sizes, or tap counts will be masked and can produce unintended scaling, clipping, underflow, or display corruption that only appears for particular formats or resolutions.

Generated names with full-width masks such as `0xFFFFFFFFL` should stay within existing 32-bit register helper paths. Ad hoc signed arithmetic or width changes around these constants can introduce subtle packing bugs.

## Test Signals

Build-time signals include successful compilation of DCN301 Display Core and DMUB sources that include `dcn_3_0_1_sh_mask.h`. Missing, renamed, or mismatched symbols should surface around `DPP_REG_LIST_DCN30`, `DPP_REG_LIST_SH_MASK_DCN30`, `TF_SF`, `TF2_SF`, `REG_SET`, `REG_UPDATE`, or `REG_GET` expansions.

Static generated-header validation should check that each intended field has both shift and mask constants, masks align with shifts and widths, replicated DPP instance layouts are consistent where the hardware spec says they should be, and all registers in this chunk have matching addresses in `dcn_3_0_1_offset.h`.

Runtime validation should exercise modesets and plane updates on DCN 3.0.1-class hardware across DPP instances, including different pixel formats, alpha-plane enablement, cursor conversion, color keying, scaling up/down, chroma formats, overscan/recout changes, and MPC sizing.

Color-management tests should cover pre-CSC/post-CSC/gamut-remap programming, GAMCOR and BLNDGAM RAM A/B updates, shaper LUT updates, 3D LUT programming, HDR multiplier behavior, bank switching, current-mode readbacks, and suspend/resume with LUT memory power transitions.

Diagnostic tests should cover DPP CRC capture and readback, CM debug index/data reads, perfmon counter setup/readback/interrupt acknowledgement, DSCL vertical counter readback, memory power status convergence, and absence of underflow, blanking, or visible color/scaling artifacts after repeated modesets and color updates.

## Chunk Notes

This is generated register metadata rather than algorithmic code. The main research value for the merge lane is the hardware coverage map: DPP1 converter, cursor conversion, scaler, color-management/LUT, memory-power, CRC, and perfmon field definitions, plus the beginning of DPP2 top/CNVC metadata. The merge lane should combine this with neighboring chunks before describing complete file-level coverage for `dcn_3_0_1_sh_mask.h`.
