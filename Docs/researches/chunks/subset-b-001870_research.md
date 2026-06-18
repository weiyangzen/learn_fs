# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 12577-15089

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata for the display pipe color and scaler blocks. It contains no executable C; it publishes preprocessor constants mapping hardware register fields to bit shifts and masks. The display driver consumes these constants with the matching DCN 3.1.5 offset header to build register tables for DPP color processing, scaling, cursor, performance counter, and per-pipe state.

The range covers 2,513 physical lines and 2,112 `#define` entries: 1,057 `__SHIFT` macros and 1,064 `_MASK` macros. It starts inside the `CM0_CM_GAMCOR_RAMB` register family, continues through the rest of the DPP0 color-management and scaler-related fields, then enters DPP1 converter/scaler/color-management fields. It ends inside `CM1_CM_BLNDGAM_RAMA_REGION_6_7`, so the next chunk must complete that register and the remaining DPP1 blend-gamma RAMA/RAMB region definitions.

Although the repository path is under a `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct MMIO operations in this slice. Its public interface is the generated register-field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Important field families in this chunk:

- `CM0_CM_GAMCOR_RAMB_*`: final green/red end-control fields, RGB offsets, and 34 piecewise-linear region descriptors for gamma-correction RAM bank B on DPP0.
- `CM0_CM_BLNDGAM_*`: DPP0 blend-gamma control, LUT index/data/control, RAMA and RAMB start/end/base/offset fields, and region descriptors from `REGION_0_1` through `REGION_32_33`.
- `CM0_CM_HDR_MULT_COEF`, `CM0_CM_MEM_PWR_CTRL`, `CM0_CM_MEM_PWR_STATUS`, `CM0_CM_DEALPHA`, `CM0_CM_COEF_FORMAT`: DPP0 color multiplier, memory power force/status, alpha/dealpha, and coefficient format controls.
- `CM0_CM_SHAPER_*`: DPP0 shaper-LUT mode, RGB offsets/scales, LUT index/data/write-enable, RAMA/RAMB start/end controls, and region descriptors.
- `CM0_CM_MEM_PWR_CTRL2`, `CM0_CM_MEM_PWR_STATUS2`, `CM0_CM_3DLUT_*`, `CM0_CM_TEST_DEBUG_*`: DPP0 HDR 3D LUT and shaper memory-power controls, 3D LUT addressing/data/read-write controls, output normalization/offsets, and test/debug access.
- `DPP_TOP0_*`: DPP0 top-level clock enable, bypass, global alpha, soft reset, CRC values/control, and host read-control fields.
- `DC_PERFMON11_*`: performance counter and perfmon control/state/value fields for a DPP-related performance monitor instance.
- `CNVC_CFG1_*` and `CNVC_CUR1_*`: DPP1 surface pixel format, format expansion, fixed-point conversion bias/scale, color keying, alpha lookup, pre-dealpha/pre-realpha, pre-CSC matrices, coefficient format, pre-degamma selection, and cursor format/color/scale-bias fields.
- `DSCL1_*`: DPP1 scaler coefficient RAM access, scaler mode/taps, DSCL control, manual replication, horizontal/vertical/chroma ratios and initial phases, black color, update/autocal, overscan, OTG blank, recout/MPC size, line-buffer format/memory, LUT memory power, output buffer, and memory-power status/force fields.
- `CM1_CM_*`: DPP1 color-management control, post-CSC matrices, gamut remap matrices, bias controls, gamma-correction LUT/RAMA/RAMB fields, blend-gamma control/LUT, and the beginning of blend-gamma RAMA region descriptors.

The values are designed for token-pasting helpers in AMD display code. In `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, DCN315 includes `dcn/dcn_3_1_5_offset.h` and this shift/mask header, then initializes `dpp_regs[]`, `tf_shift`, and `tf_mask` from `DPP_REG_LIST_DCN30()` and `DPP_REG_LIST_SH_MASK_DCN30()`. Those macros are defined in `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, where `SRI()` builds register addresses and `TF_SF()` pastes generated names such as `CM0_CM_GAMCOR_RAMB_REGION_0_1__CM_GAMCOR_RAMB_EXP_REGION0_LUT_OFFSET_MASK` into typed field tables.

## Control Flow

This header has no runtime control flow. The runtime flow is provided by AMD display resource construction and DPP programming code:

1. DCN315 resource construction includes the generated offset and shift/mask headers.
2. `dcn315_resource.c` expands `DPP_REG_LIST_DCN30(id)` for DPP instances 0 through 3, creating per-instance register address tables from the offset macros.
3. The same file expands `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` once into `tf_shift` and `tf_mask`.
4. `dcn31_dpp_create()` passes those tables to `dpp3_construct()`, which gives each DPP object the addresses and field metadata needed by the shared DPP color/scaler implementation.
5. Runtime modeset, plane update, color-management, scaling, cursor, and power-management flows use register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and table-driven DPP operations to program the hardware.

The macros do not encode ordering. Consumers still need the hardware sequence for LUT access and bank switching: select host/config mode, write LUT indices/data, program start/end/region fields, handle current-vs-requested mode fields, avoid updating active banks incorrectly, and respect memory power state before touching shaper, blend-gamma, gamma-correction, or 3D LUT RAMs.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes fields whose state is held in DCN display hardware registers.

Hardware state represented here includes gamma-correction and blend-gamma PWL RAM selection, LUT index/data windows, RGB start/end/base/slope/offset values, region-to-LUT segmentation, shaper LUT configuration, HDR multiplier and 3D LUT output normalization/offsets, CSC and gamut-remap matrices, alpha/color-key/cursor/converter state, scaler taps/ratios/viewport sizing, DPP CRC/debug/perfmon state, and memory-power force/status for color and scaler RAMs.

Persistence is hardware-defined. Programmed color and scaler configuration normally survives until the next modeset/plane update, DPP reprogramming, display power gating, suspend/resume, or ASIC reset. Status fields such as `*_CURRENT`, `*_STATE`, `*_DONE`, `*_ERROR`, `*_CRC_*`, `*_READ_BUSY`, and memory-power status fields may be read-only, sticky, self-clearing, or write-sensitive depending on the underlying register specification. This generated header only provides bit layout; it does not describe access type or side effects.

## Dependencies And Integration Points

The constants in this range must match the generated DCN 3.1.5 register-offset file at `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. A shift/mask macro is only useful when the corresponding `reg...` offset macro exists for the same register instance.

Important in-tree integration points:

- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`: includes this header, creates DPP register tables for four DPP instances, and sets DCN315 color capabilities. The capabilities explicitly advertise gamma correction, hardware 3D LUT, output gamma RAM, post-CSC, and shaper/blend-gamma related color features that depend on these register definitions.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`: defines `DPP_REG_LIST_DCN30_COMMON()`, `DPP_REG_LIST_DCN30()`, `DPP_REG_LIST_SH_MASK_DCN30_COMMON()`, and `DPP_REG_LIST_SH_MASK_DCN30_UPDATED()`. These macros consume many fields in this chunk for gamma correction, blend gamma, shaper, 3D LUT, converter, cursor, scaler, and DPP top-level control.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h`: supplies shared transform-field lists used by the DCN30 DPP definitions, especially the exhaustive blend-gamma RAMA/RAMB region field list.
- `reg_helper.h` and the DPP implementation files: consume the generated `tf_shift` and `tf_mask` structures indirectly through register helper macros and DPP methods.
- DC color-management and DRM color pipeline entry points: user-visible gamma/CSC/gamut/shaper/3D-LUT changes ultimately rely on this register metadata when programmed on DCN315 hardware.

The chunk boundary is important. Lines before this chunk define the beginning of `CM0_CM_GAMCOR_RAMB_END_CNTL1_B` and `END_CNTL2_B`; this chunk begins at the green channel end-base field. Lines after this chunk complete `CM1_CM_BLNDGAM_RAMA_REGION_6_7` and continue the remaining DPP1 blend-gamma region definitions. The final per-file document should merge neighboring chunks before making complete claims about these two boundary families.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These macros are untyped constants, so incorrect generated values can compile cleanly while corrupting adjacent hardware fields.
- The generated names are consumed through token pasting. A missing, renamed, or instance-mismatched macro can fail builds in resource construction, while a wrong value can pass builds and fail only on hardware.
- `CM0` and `CM1` families are structurally similar but apply to different DPP instances. Copy/paste or generation errors can affect only one pipe, producing pipe-specific color, scaling, cursor, or CRC failures.
- PWL region fields are dense and repetitive. LUT offsets use 9-bit masks, segment counts use three-bit masks at bits 12 and 28, start/end/base fields commonly use 18-bit masks, end/slope pairs share one register, and RGB offsets use 19-bit masks. A one-bit mismatch can break only specific transfer-function segments.
- LUT access registers (`*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, `*_3DLUT_READ_WRITE_CONTROL`) are sequencing-sensitive. Incorrect host selection, read/write mode, or index handling can update the wrong color bank or read stale data.
- Memory power controls interact with color RAM availability. Forcing or disabling gamma, blend-gamma, shaper, 3D LUT, scaler LUT, line-buffer, or output-buffer RAM power at the wrong time can cause blanking, corruption, underflow-like symptoms, or lost LUT writes.
- Scaler and converter fields are highly mode-dependent. Incorrect ratios, initial phases, taps, recout/MPC sizing, pixel format, alpha handling, or CSC matrix fields can create visual corruption that only appears for scaled, chroma, cursor, FP16, alpha, or color-keyed planes.
- Perfmon and debug fields may have side effects or require precise select/clear ordering. The header does not identify which fields are counters, status, clear bits, or readback windows.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU display support with DCN315 enabled so `dcn315_resource.c`, `dcn30_dpp.h`, and `dcn20_dpp.h` expansions catch missing or renamed macros.
- Mechanically verify that complete registers in this range have expected `__SHIFT` and `_MASK` pairs, while accounting for intentional chunk-boundary partials at the start and end.
- Compare this DCN 3.1.5 chunk against AMD's authoritative register database and adjacent DCN generation headers where DPP color/scaler layouts are expected to remain compatible.
- Exercise color-management paths on DCN315 hardware: gamma correction, blend gamma, shaper LUT, 3D LUT, post-CSC, gamut remap, HDR multiplier, alpha/dealpha, color keying, and bypass/current-mode transitions.
- Test LUT programming across RAMA/RAMB bank switching and suspend/resume to catch stale bank select, host select, memory power, or current-mode issues.
- Validate DPP1-specific scaler/converter behavior with scaled planes, chroma formats, cursor planes, alpha planes, FP16 conversion, color-keyed planes, and multi-plane composition.
- Use CRC and perfmon/debug readback where available to confirm that DPP top-level and perfmon fields remain readable and that field masks do not overlap unexpectedly.

## Cross-Chunk Notes

This chunk is source-tree-aligned to `dcn_3_1_5_sh_mask.h` and intentionally writes only the chunk research file. The previous chunk should cover the first part of `CM0_CM_GAMCOR_RAMB_END_CNTL*`; the next chunk should complete `CM1_CM_BLNDGAM_RAMA_REGION_6_7` and continue DPP1 blend-gamma RAMA/RAMB definitions. The later merge/reconciliation lane should combine these boundaries before producing final per-file conclusions.
