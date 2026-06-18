# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 12637-15195

## Chunk Scope

This chunk covers lines 12637-15195 of the generated AMD DCN 3.2.1 shift/mask header. It starts mid-register, with the final masks for `CM1_CM_GAMCOR_RAMB_REGION_26_27`, continues through DPP instance 1 top-level fields, full DPP instance 2 CNVC/DSCL/CM/DPP_TOP masks, full DPP instance 3 CNVC/DSCL/CM/DPP_TOP masks, and then enters MPC MPCC instance 0 plus most of MPCC instance 1. It ends mid-register at `MPCC1_MPCC_STATUS__MPCC_BUSY__SHIFT`; the remaining `MPCC1_MPCC_STATUS` masks are outside this chunk.

The file is a hardware register definition header, not executable logic. Every item in this range is a preprocessor macro that names either a bit shift (`__SHIFT`) or bit mask (`_MASK`) for a specific DCN 3.2.1 register field.

## Purpose

The chunk supplies the field-level layout used by the AMD display driver to program DCN 3.2.1 display pipeline blocks safely through generic register helper macros. It maps semantic field names such as `CM_GAMCOR_MODE`, `SCL_COEF_RAM_TAP_PAIR_IDX`, `DPP_CLOCK_ENABLE`, and `MPCC_GLOBAL_ALPHA` to their exact bit positions and masks inside MMIO registers.

The main hardware areas represented here are:

- DPP color management (`CM1`, `CM2`, `CM3`): post color space conversion, gamut remap, bias, gamma correction LUTs, RAMA/RAMB PWL region metadata, HDR multiplier, coefficient format, dealpha, and color-management memory power state.
- DPP top control (`DPP_TOP1`, `DPP_TOP2`, `DPP_TOP3`): DPP clock enable/gating, soft reset, CRC capture, and host read rate control.
- DPP conversion/configuration (`CNVC_CFG2`, `CNVC_CFG3`): surface pixel format, alpha plane enable, format expansion/conversion, bypass, clamping, color key ranges, 2-bit alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- Cursor conversion (`CNVC_CUR2`, `CNVC_CUR3`): cursor enable/mode/ROM/pixel-alpha controls plus cursor colors and FP scale/bias.
- DPP scaler (`DSCL2`, `DSCL3`): coefficient RAM selection/data, scaling mode, tap counts, 2-tap controls, manual replicate controls, scale ratios, initial phases, black color, update/autocal, overscan, blanking, recout/MPC dimensions, line-buffer format/memory, vertical counters, DSCL memory power, and OBUF controls.
- MPC compositor (`MPCC0`, `MPCC1`): top/bottom input selection, OPP routing, blend/control modes, stereo/SM controls, update lock selection, top/bottom gains, movable CM routing, background color, output gamma memory power, and status.

## Important APIs, Types, and Macro Families

There are no C functions or structs in this chunk. The exported API surface is the macro naming contract consumed by register-list and field-list code.

The core macro pattern is:

- `<REGISTER>__<FIELD>__SHIFT`: integer bit offset for packing/unpacking a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field in the 32-bit register value.

Representative field groups:

- `CM*_CM_POST_CSC_*` and `CM*_CM_GAMUT_REMAP_*` provide 16-bit matrix coefficient fields for active and "B" coefficient banks. `*_CONTROL` registers include requested mode and current mode fields, supporting double-buffered or latched color updates.
- `CM*_CM_GAMCOR_*` covers gamma-correction mode/select, LUT index/data/control, RAMA/RAMB start/end/offset controls, and region tables. Region-pair registers follow the repeated pattern `REGION_N_N+1` with low region fields at shifts `0x0`/`0xc` and high region fields at `0x10`/`0x1c`; masks are usually `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000`.
- `DPP_TOP*_DPP_CONTROL` exposes clock enable, gate-disable, dynamic gate-disable, DSCL gate, DISPCLK gates, fine-grain clock-gating repeat disable, and test clock select.
- `DPP_TOP*_DPP_CRC_*` exposes CRC value fields and controls for enable, continuous mode, one-shot pending, 4:2:0 component selection, source selection, stereo/interlace/pixel-format/cursor-format selection, and a 16-bit CRC mask.
- `CNVC_CFG*_FORMAT_CONTROL` defines format expansion/conversion, alpha enable, bypass alignment, positive clamp controls, update pending, and RGB crossbar selection fields.
- `CNVC_CFG*_PRE_CSC_*` and `*_PRE_CSC_B_*` provide paired 16-bit pre-CSC coefficient fields, with `PRE_CSC_MODE` exposing requested/current mode.
- `DSCL*_SCL_COEF_RAM_TAP_SELECT` and `DSCL*_SCL_COEF_RAM_TAP_DATA` define the coefficient RAM programming interface used by scaler code: tap pair index, phase, filter type, even/odd tap coefficients, and enable bits.
- `DSCL*_SCL_MODE`, `DSCL*_SCL_TAP_CONTROL`, and scale/init registers define scaler mode, coefficient RAM bank selection/current state, chroma/alpha coefficient modes, horizontal/vertical tap counts, integer/fractional scale ratios, and initial phases for luma/chroma/bottom fields.
- `DSCL*_DSCL_MEM_PWR_CTRL`, `DSCL*_DSCL_MEM_PWR_STATUS`, `DSCL*_OBUF_MEM_PWR_CTRL`, and `CM*_CM_MEM_PWR_*` define memory power force/disable/mode/state bits for DSCL LUT/LB/OBUF and CM GAMCOR memories.
- `MPCC*_MPCC_CONTROL` defines MPCC blend mode, alpha blend mode, premultiplied alpha mode, active-overlap-only blending, background bpc, bottom gain mode, global alpha, and global gain.
- `MPCC*_MPCC_SM_CONTROL`, `MPCC*_MPCC_UPDATE_LOCK_SEL`, `MPCC*_MPCC_MEM_PWR_CTRL`, and `MPCC*_MPCC_STATUS` define stereo/multi-plane control, update-lock routing/status, OGAM memory power, and idle/busy/disabled status bits.

## Control Flow

This header has no runtime control flow. Its macros become part of control flow indirectly when included by DCN 3.2.1 resource initialization and block implementations:

- `dcn321_resource.c` includes both `dcn_3_2_1_offset.h` and this `dcn_3_2_1_sh_mask.h`, then uses macros such as `SRI`, `SRI_ARR`, and field-list expansions to build per-block register address, shift, and mask tables.
- DPP and MPC block headers define register-field lists that map generic driver fields to generated macros. For example, DPP DSCL code uses `SCL_COEF_RAM_*`, `DSCL_MEM_PWR_*`, and color-management field names through `REG_SET_*`, `REG_UPDATE`, and `REG_WAIT` helpers. MPC code uses the MPCC field masks for compositor programming.
- At runtime, display programming functions pass semantic field names to register helpers; the helpers combine the register address from the offset header with the shift and mask values from this header to pack, update, poll, or decode MMIO values.

Because the values are compile-time constants, the important "control flow" risk is whether the symbolic field referenced by a block implementation resolves to the correct generated field for the target ASIC instance.

## State and Persistence Behavior

The header itself owns no state and persists nothing. The state described by these masks lives in DCN display hardware registers and internal memories:

- Color-management registers persist requested/current CSC, gamut remap, GAMCOR LUT, RAMA/RAMB, HDR multiplier, bias, and format state until reprogrammed, reset, or power-gated by hardware.
- DSCL registers persist scaler coefficient RAM contents, scale ratios, initial phases, recout geometry, line-buffer partitioning, memory power state, and OBUF settings.
- MPCC registers persist compositor routing, blend modes, gains, background color, update-lock state, memory power state, and idle/busy/disabled status.
- Several fields are explicitly status/current fields (`*_CURRENT`, `*_UPDATE_PENDING`, `*_MEM_PWR_STATE`, `MPCC_IDLE`, `MPCC_BUSY`, `MPCC_DISABLED`). Driver code generally writes requested fields and polls or reads current/status fields to synchronize with hardware latching.

## Dependencies and Integration Points

The chunk depends on the matching generated offset header for register addresses:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`

It is directly included from:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`

Important consumers and integration surfaces include:

- `display/dc/dpp/dcn30/dcn30_dpp.h` and `display/dc/dpp/dcn32/dcn32_dpp.h`, which define DPP register and field lists for CM, CNVC, DSCL, and DPP_TOP programming.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c`, `display/dc/dpp/dcn30/*`, and `display/dc/dpp/dcn32/*`, which use generic register helpers for scaler coefficients, memory power sequencing, color management, and DPP state.
- `display/dc/mpc/dcn30/dcn30_mpc.h`, `display/dc/mpc/dcn32/dcn32_mpc.h`, and related MPC C files, which use MPCC masks for compositor routing, blending, locks, and status.
- The common register helper layer (`reg_helper.h` and related macros) that expects each register field to have a matching shift and mask macro with stable spelling.

The generated naming is instance-specific (`CNVC_CFG2`, `DSCL2`, `CM2`, `DPP_TOP2`, etc.) while block implementation code often uses generic field names. Resource macros bridge those layers by selecting the correct instance-specific macro for each hardware instance.

## Risks and Edge Cases

- Chunk boundary risk: lines 12637-12638 are only the tail of `CM1_CM_GAMCOR_RAMB_REGION_26_27`, and lines 15194-15195 are only the shift definitions for the beginning of `MPCC1_MPCC_STATUS`. Merge logic must combine adjacent chunks before making whole-register claims for those two registers.
- Generated constant drift: any incorrect shift or mask silently corrupts MMIO field updates. A wrong mask can clear neighboring fields, and a wrong shift can write the intended value into an unrelated control/status bit.
- Instance symmetry can hide copy errors. DPP2 and DPP3 blocks are highly repetitive; a single mismatched instance prefix or field spelling may compile if another macro exists but program the wrong register table entry.
- Current/status fields should not be treated as ordinary writable configuration fields. Fields such as `*_CURRENT`, `*_UPDATE_PENDING`, memory power state, and MPCC status bits are used for synchronization or diagnostics.
- Memory power controls are sequencing-sensitive. DSCL LUT/LB/OBUF, CM GAMCOR, and MPCC OGAM memory power fields interact with register waits and hardware state transitions; incorrect masks can cause hangs, timeouts, or loss of display processing state.
- GAMCOR region packing is dense. Region-pair registers pack two regions into one 32-bit word with non-contiguous offset and segment fields. Region table programming must preserve the untouched region half during partial updates.
- CRC and debug fields can affect validation paths. DPP CRC masks and source/format controls are used for hardware CRC capture; wrong values can make display validation or automated CRC tests fail even when visual output appears correct.
- MPCC blending fields directly affect composition semantics. Errors in `MPCC_ALPHA_BLND_MODE`, `MPCC_ALPHA_MULTIPLIED_MODE`, `MPCC_GLOBAL_ALPHA`, or gain masks can produce subtle overlay, plane, and HDR blending regressions.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build test the AMD display driver for a DCN 3.2.1 target. Missing or misspelled shift/mask macros should fail compilation through resource field-list expansion.
- Exercise modeset and plane composition on DCN 3.2.1 hardware, especially multiple planes, cursor enable/format, alpha blending, global alpha/gain, and MPCC update-lock paths.
- Exercise color-management paths that program pre-CSC, post-CSC, gamut remap, bias, GAMCOR LUT/RAMA/RAMB region tables, HDR multiplier, dealpha, pre-dealpha, and pre-realpha.
- Exercise scaler paths with non-1:1 scaling, chroma scaling, alpha scaling, 2-tap modes, custom coefficient RAM programming, overscan, and recout/MPC sizing.
- Check memory power sequencing with display blank/unblank, suspend/resume, runtime power transitions, and repeated modesets; watch for `REG_WAIT` timeouts around DSCL/CM/MPCC memory power state fields.
- Use DPP CRC capture paths to verify `DPP_TOP*_DPP_CRC_*` field masks and source/format selections.
- Compare this header against the same register families in neighboring generated headers (`dcn_3_2_0_sh_mask.h`, `dcn_3_1_6_sh_mask.h`, or later DCN revisions) when diagnosing suspected generation drift. Repetition across revisions is a useful sanity signal but not a substitute for ASIC register spec validation.

## Summary for Merge Lane

This chunk is a dense generated macro segment for DCN 3.2.1 DPP color/conversion/scaler/top blocks and MPC MPCC blocks. It contributes no executable logic, but it is critical to all downstream register helper operations because it defines the exact bit layouts for color management, scaling, clock/reset/CRC, cursor conversion, memory power, and compositor blending/status registers. The merge lane should preserve the partial-register boundary notes for `CM1_CM_GAMCOR_RAMB_REGION_26_27` and `MPCC1_MPCC_STATUS` when synthesizing the full-file report.
