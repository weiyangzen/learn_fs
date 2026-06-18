# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 14848-17356

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register shift/mask header segment. It contains preprocessor constants only: every hardware register field is represented by a `__SHIFT` macro and a matching `_MASK` macro. The slice spans 2,509 source lines and contains 2,113 `#define` entries across 379 register symbols. It starts inside the `CM0_CM_BLNDGAM_RAMA_REGION_6_7` field list and ends inside `CM1_CM_BLNDGAM_RAMB_REGION_24_25`, so both boundaries are partial register groups that must be reconciled with neighboring chunks for complete file-level coverage.

## Purpose

The purpose of this header segment is to expose symbolic bit locations for DCN 3.0.2 display pipe programming. Driver code does not hand-code these bit offsets directly; it includes generated `*_sh_mask.h` headers and feeds the `__SHIFT`/`_MASK` constants into AMDGPU display register helper tables. The covered hardware is mostly display pipe processor (DPP) color-management, converter, scaler, cursor, and diagnostics state for DPP instance 0 and DPP instance 1.

This chunk is data-like source rather than executable logic. Its correctness depends on exact agreement with the matching DCN 3.0.2 register specification and the companion `dcn_3_0_2_offset.h` address header. A wrong value here changes how runtime code masks or shifts MMIO fields.

## Address Blocks And Register Surface

The visible address blocks are:

- `dce_dc_dpp0_dispdec_cm_dispdec` tail: end of `CM0` blend-gamma RAM A, full blend-gamma RAM B region descriptors, CM0 shaper, CM0 3D LUT, memory-power, debug, and HDR multiplier controls.
- `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON11` counter control, state, counter values, and performance-monitor compare/value registers.
- `dce_dc_dpp1_dispdec_dpp_top_dispdec`: `DPP_TOP1` pipe-level enable/reset and DPP CRC controls/status.
- `dce_dc_dpp1_dispdec_cnvc_cfg_dispdec`: `CNVC_CFG1` input format, expansion, pre-CSC, pre-degamma, pre-dealpha/pre-realpha, color key, alpha LUT, and FP scale/bias fields.
- `dce_dc_dpp1_dispdec_cnvc_cur_dispdec`: `CNVC_CUR1` cursor enable/mode/color/floating-point scale-bias fields.
- `dce_dc_dpp1_dispdec_dscl_dispdec`: `DSCL1` scaler coefficient RAM, mode, taps, filter ratios/initial phases, recout/MPC dimensions, line-buffer, memory-power, OBUF, and OTG blanking fields.
- `dce_dc_dpp1_dispdec_cm_dispdec`: start of the `CM1` color-management block, including control, post-CSC, gamut-remap, bias, gamma-correction RAM A/B, and blend-gamma RAM A/B definitions through the partial `Ramb region 24/25` block.

By counted prefix, the chunk includes 718 `CM0_CM*` definitions, 126 `DC_PERFMON11*` definitions, 56 `DPP_TOP1*` definitions, 154 `CNVC_CFG1/CNVC_CUR1*` definitions, 200 `DSCL1*` definitions, and 859 `CM1_CM*` definitions.

## Important Macro Families

The `CM0_CM_BLNDGAM_*` and `CM1_CM_BLNDGAM_*` groups describe blend/output gamma LUT control and piecewise-linear RAM metadata. The visible fields cover mode/current-select bits, LUT index/data/control, RAM A and RAM B start/end/offset registers, per-channel B/G/R start values, start segments, start slopes, start bases, end bases, end slopes, and dense region descriptors. Region registers pack two regions per register, each with a 9-bit LUT offset and 3-bit segment count.

The `CM0_CM_SHAPER_*` group describes the shaper LUT path for DPP0. It includes shaper control and status/current mode, per-channel offsets and scales, LUT index/data/write mask, RAM A/B start/end registers, and shaper region descriptors. These fields are used with 3D LUT programming because the shaper prepares color values before 3D LUT lookup.

The `CM0_CM_3DLUT_*` group describes 3D LUT mode, host index/data access, 30-bit data path fields, read/write controls, output normalization factor, and RGB output offsets. The read/write control fields include configuration status, mode, read selection, width, and 30-bit enable state.

The `CM1_CM_GAMCOR_*` group describes the DPP1 gamma-correction RAM. It mirrors the blend-gamma PWL layout with RAM A/B start, base, slope, end, offset, and region registers, plus LUT index/data/control and mode/current-select fields.

The `CM1_CM_POST_CSC_*` and `CM1_CM_GAMUT_REMAP_*` groups describe color matrix programming. Each matrix register packs coefficient pairs such as `C11/C12` through `C33/C34`, and there are A/B or current/alternate coefficient banks so the driver can stage updates before switching modes.

The `CNVC_CFG1_*` groups describe DPP1 input conversion. They cover source pixel format, expansion, bypass, alpha enable, 16-bit conversion format, component crossbar, positive clamp, pre-CSC matrix banks, pre-degamma select, pre-dealpha and pre-realpha control, fixed-point conversion scale/bias, color-key ranges, and a packed 2-bit alpha LUT.

The `CNVC_CUR1_*` groups describe cursor format and color controls for DPP1. Fields include cursor enable, mode, expansion, ROM enable, pixel inversion, pixel alpha modulation, two cursor colors, and FP scale/bias.

The `DSCL1_*` groups describe scaler and line-buffer programming. They include coefficient RAM tap select/data, scaler mode and coefficient-bank select, horizontal/vertical/chroma tap counts, 2-tap hardcoded/sharp controls, manual replicate controls, scale ratios, initial phases, recout rectangle, MPC size, line-buffer data format and memory configuration, DSCL update/autocal controls, OTG blanking, memory-power, and OBUF state.

The `DPP_TOP1_*` and `DC_PERFMON11_*` groups describe diagnostics and status rather than color math. `DPP_TOP1` includes pipe clock enable, soft reset, host-read and CRC control/result fields. `DC_PERFMON11` includes counter enable/clear/selection, perfmon state, mode, windowing, high/low counter values, and compare/mask values.

## Integration Points

The main runtime integration path is through generated register tables in AMDGPU display code. For DCN 3.0-style DPPs, `display/dc/dpp/dcn30/dcn30_dpp.h` defines `DPP_REG_LIST_DCN30*` and `DPP_REG_LIST_SH_MASK_DCN30*` macros. Those macros name fields such as `CM0_CM_BLNDGAM_CONTROL__CM_BLNDGAM_MODE`, `CM0_CM_3DLUT_MODE__CM_3DLUT_MODE_CURRENT`, `CNVC_CFG0_FORMAT_CONTROL__FORMAT_EXPANSION_MODE`, and `DSCL0_SCL_MODE__DSCL_MODE`; instance-specific address macros then map the same field layout onto each DPP instance. The generated `__SHIFT` and `_MASK` constants in this chunk are the low-level values assigned into the `dcn3_dpp_shift` and `dcn3_dpp_mask` structures.

`display/dc/resource/dcn30/dcn30_resource.c` is the resource-construction side of that integration. It includes DCN offset and sh/mask headers, builds DPP register-address arrays with `DPP_REG_LIST_DCN30(id)`, and builds shift/mask tables with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`. DCN 3.0.2-specific resource code follows the same pattern with the DCN 3.0.2 generated headers.

`display/dc/dpp/dcn30/dcn30_dpp.c` is the direct consumer pattern. It reads and writes these fields through `REG_GET`, `REG_GET_2`, `REG_SET`, `REG_SET_2`, `REG_UPDATE`, and `REG_READ`. Examples include `dpp30_read_state()` reading DPP enable, pre-degamma, gamma-correction current mode, shaper mode, 3D LUT mode/bit depth/size, and blend-gamma current mode; `dpp3_program_post_csc()` selecting between CSC banks and programming coefficient registers; and DPP scaler/converter functions programming format, pre-degamma, cursor, recout, filter ratios, taps, and line-buffer state.

The helper layer comes from `reg_helper.h` and associated display core code. Those helpers combine an MMIO register address, a field mask, and a field shift to perform read-modify-write or extraction. The macros in this chunk therefore become part of the ABI between generated hardware descriptions and typed DC driver structures.

## Control Flow And Runtime Behavior

There is no C control flow in this header chunk. The represented runtime flows are indirect:

- DPP construction selects the DCN 3.0.2 register address and shift/mask tables for a specific pipe instance.
- DPP state readback extracts status/current fields from registers, such as DPP clock enable, shaper/3D LUT/gamma modes, memory-power state, scaler mode, recout size, and OBUF state.
- Color-management programming writes staged coefficient or LUT data into CM registers, then switches mode/select fields so hardware uses the intended RAM or matrix bank.
- Converter setup writes pixel format, alpha, expansion, crossbar, pre-CSC, pre-degamma, pre-dealpha/pre-realpha, color-key, cursor, and fixed-point conversion fields.
- Scaler setup writes tap counts, coefficient RAM entries, filter ratios, initial phases, recout/MPC dimensions, line-buffer partitioning, autocal, update, and memory-power controls.
- Diagnostics paths may enable DPP CRC or DC performance counters, read low/high counter values, and clear or reset state.

The double-buffering pattern is important even though it is not implemented here. Several mode/current, select/current, and A/B matrix/RAM field pairs imply that driver code writes an inactive bank, then flips a control selector so the new color transform takes effect on a safe hardware boundary.

## State And Persistence

The macros themselves hold no mutable software state. They describe persistent hardware state in memory-mapped registers. Once the driver writes fields described here, the device state persists until another write, a block reset, a full display reinitialization, suspend/resume restore, or GPU reset.

Important state categories exposed by this slice:

- LUT and PWL state: blend-gamma, gamma-correction, shaper, and 3D LUT fields define visible color output. Bad persistence or failed restore can cause wrong gamma, HDR tone mapping, or color-space conversion after mode changes and resume.
- Bank/current state: `*_MODE_CURRENT`, `*_SELECT_CURRENT`, and current coefficient-bank fields expose which staged bank hardware is actually using.
- Memory-power state: `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_MEM_PWR_CTRL2`, `CM_MEM_PWR_STATUS2`, `DSCL_MEM_PWR_CTRL`, `DSCL_MEM_PWR_STATUS`, `LB_MEMORY_CTRL`, and `OBUF_MEM_PWR_CTRL` affect whether LUT, shaper, 3D LUT, line-buffer, scaler, and output-buffer memories are powered or forced.
- Status and clear state: DPP CRC status, soft reset, performance counter state, autocal status, update pending/taken, and host-read controls represent transient hardware handshakes.
- Cursor/converter/scaler state: CNVC and DSCL fields define the active surface interpretation, cursor appearance, scaling geometry, and filtering.

## Dependencies

This chunk depends on companion generated DCN 3.0.2 headers for register addresses and base indices, especially the matching `dcn_3_0_2_offset.h`. It also depends on the AMD display register-helper convention where `REG_FIELD` tables contain masks and shifts in separate structures. Macro naming must match the typed field names in DPP headers; a mismatch is a compile-time failure when referenced, while a numerically wrong mask/shift can compile cleanly and break runtime hardware programming.

The hardware semantics are outside this file. The header gives bit positions only; it does not describe write-one-to-clear behavior, double-buffer timing, reset sequencing, memory-power timing, or legal enum values for mode fields. Runtime code must get those semantics from the DPP implementation and hardware spec.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A single wrong mask or shift can corrupt adjacent fields in a 32-bit MMIO register, causing color corruption, scaler misprogramming, cursor artifacts, CRC/test failures, memory-power issues, or display blanking.
- The chunk boundaries are partial. The first visible definitions are the tail of `CM0_CM_BLNDGAM_RAMA_REGION_6_7`; the final visible definition starts `CM1_CM_BLNDGAM_RAMB_REGION_24_25`. Merge/reconciliation must include adjacent chunks before making completeness claims.
- Instance parity is easy to assume incorrectly. `CM0` and `CM1`, `CNVC_CFG0/1`, and `DSCL0/1` are structurally similar, but the actual generated macros are instance-qualified and may differ across ASIC revisions or block revisions.
- Dense repeated PWL region definitions are off-by-one sensitive. Region registers encode pairs such as regions 0/1, 2/3, ..., 32/33. Consumers that calculate offsets or generate arrays must preserve the exact register/field pairing.
- Fields whose logical names contain `MASK` generate macro names ending in `_MASK_MASK`, such as LUT write-enable masks. Parsers or validators that strip `_MASK` naively can misidentify these names.
- Hardware-current fields are readback/status-oriented. Writing only the desired mode field and then immediately trusting the corresponding current field without respecting update boundaries can create races in diagnostics or tests.
- Memory-power controls are shared with LUT and scaler programming. Powering a memory block down while a LUT/scaler path still expects it can produce nondeterministic display output or stale readback.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header consistency, and hardware-display regression signals:

- Compile DCN 3.0.2 AMDGPU display paths so all referenced DPP, CM, CNVC, DSCL, DPP_TOP, and PERFMON field names resolve.
- Run a generated-header consistency check that every field has both `__SHIFT` and `_MASK`, masks fit within 32 bits, and paired region registers use the expected offset/segment bit positions.
- Compare DCN 3.0.2 masks against the matching offset header and against adjacent DCN 3.0.x revisions to catch accidental drift in repeated CM/CNVC/DSCL blocks.
- Exercise display mode changes with scaling enabled, bypass scaling, 4:4:4 and 4:2:0 formats, cursor enable/disable, color-keying, alpha formats, and FP formats.
- Exercise color-management paths: pre-degamma, post-CSC, gamut remap, gamma-correction RAM A/B, blend-gamma RAM A/B, shaper LUT, 3D LUT, HDR multiplier, and bank switching.
- Exercise suspend/resume, display off/on, and memory-power transitions while verifying LUT/scaler state restores and no underflow, blanking, or color shifts occur.
- Use diagnostics that read DPP CRC, DPP soft reset/clock enable, DC performance counters, DSCL update/autocal state, OBUF/LB memory state, and readback current-mode fields.

## Open Questions For Merge Lane

- Confirm adjacent chunks include the missing opening definitions for `CM0_CM_BLNDGAM_RAMA_REGION_6_7` and the remaining definitions for `CM1_CM_BLNDGAM_RAMB_REGION_24_25`.
- Check whether DCN 3.0.2 resource code includes this exact header directly or through ASIC-specific include indirection, and note the final per-file integration path accordingly.
- Compare CM0 and CM1 field coverage in the final merged file to determine whether any apparent asymmetry is a chunk-boundary artifact or an intentional hardware/layout difference.
