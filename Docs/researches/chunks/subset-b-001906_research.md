# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 22448-24952

## Scope

This chunk is part of the generated AMDGPU DCN 3.1.6 register shift/mask header. It contains C preprocessor constants only; there are no executable functions, structs, enums, or runtime branches in the covered lines. The chunk begins in the middle of the `CM3_CM_BLNDGAM_RAMB_REGION_2_3` mask definitions, then covers the tail of DPP3 color-management registers, DPP3 top-level and performance-monitor registers, MPC/MPCC compositor registers, and the beginning of MPCC output-gamma instance 1. It ends mid-register at `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33__MPCC_OGAM_RAMB_EXP_REGION32_LUT_OFFSET_MASK`.

The public interface is the generated macro pair pattern:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: mask for the same field.

These values are hardware ABI for the DCN 3.1.6 display engine. Driver code uses them with generated register address headers and DC register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and `SF(...)`-built mask/shift tables.

## Purpose

The chunk exposes bitfield layouts for several display pipeline areas:

- `CM3` color-management controls for DPP pipe 3, including blend-gamma RAM B region descriptors, HDR multiplier, memory power control/status, dealpha, coefficient formats, shaper LUT programming, shaper RAM A/B region descriptors, 3D LUT access, 3D LUT output normalization/offset, and test debug access.
- `DPP_TOP3` top-level DPP pipe 3 controls, including DPP clock enable/gating, soft reset for CNVC/DSCL/CM/OBUF sub-blocks, DPP CRC result/control fields, and host read rate control.
- `DC_PERFMON14` for the DPP3 performance-monitor address block, covering performance counter event selection, count/run/interrupt controls, counter state multiplexing, high/low count value readback, and interrupt status/ack fields.
- `MPCC0` through `MPCC3` compositor slice controls, including top/bottom source selection, OPP routing, alpha/blending/overlap controls, stereo/side-by-side controls, update-lock selection, gains, background color, memory power control, and MPCC busy/idle/status bits.
- Global `MPC` controls, including clock control, soft reset, CRC source/result selection, perfmon event selection, bypass background colors, host read control, DPP pending status, vupdate lock set programming, and DWB0 mux selection.
- `DC_PERFMON15` for the MPC performance-monitor block, with the same counter/control/readback pattern as `DC_PERFMON14`.
- `MPCC_OGAM0` and partial `MPCC_OGAM1` output-gamma and gamut-remap controls, including LUT index/data/control, RAM A/B piecewise-linear region start/end/slope/base/offset fields, 34 exponential region descriptors, output gamut-remap mode/format, and A/B coefficient matrices for `MPCC_OGAM0`.

## Important APIs, Types, and Definitions

There are no C APIs or types defined in this chunk. The important definitions are the register-field constants grouped by prefix.

`CM3_CM_*` definitions describe DPP3 color blocks:

- `CM3_CM_BLNDGAM_RAMB_REGION_4_5` through `CM3_CM_BLNDGAM_RAMB_REGION_32_33` encode paired blend-gamma RAM B region descriptors. Each pair has LUT offset fields and number-of-segments fields for two adjacent regions.
- `CM3_CM_HDR_MULT_COEF`, `CM3_CM_COEF_FORMAT`, and `CM3_CM_DEALPHA` expose HDR multiplier, coefficient fixed-point format selection, and dealpha enable/alpha blend behavior.
- `CM3_CM_MEM_PWR_CTRL`, `CM3_CM_MEM_PWR_STATUS`, `CM3_CM_MEM_PWR_CTRL2`, and `CM3_CM_MEM_PWR_STATUS2` expose power force/disable/state controls for gamma correction, blend-gamma, shaper, and 3D LUT memories.
- `CM3_CM_SHAPER_*` exposes shaper mode, RGB offsets/scales, host LUT index/data/write color masks, and RAM A/B start/end/region layout.
- `CM3_CM_3DLUT_*` exposes 3D LUT mode, index/data access, 30-bit data access, read/write control flags, output normalization factor, and RGB output offsets.

`DPP_TOP3_*` definitions describe the top-level state of DPP pipe 3:

- `DPP_TOP3_DPP_CONTROL` controls clock enable and fine-grained clock gating disables.
- `DPP_TOP3_DPP_SOFT_RESET` controls reset bits for DPP sub-blocks.
- `DPP_TOP3_DPP_CRC_VAL_R_G`, `DPP_TOP3_DPP_CRC_VAL_B_A`, and `DPP_TOP3_DPP_CRC_CTRL` select and read CRC diagnostics.
- `DPP_TOP3_HOST_READ_CONTROL` controls host read pacing.

`DC_PERFMON14_*` and `DC_PERFMON15_*` definitions describe display performance-monitor programming:

- `*_PERFCOUNTER_CNTL` selects events, cvalue inputs, increment modes, run-enable modes, restart, interrupt enable, active status, and counter selector fields.
- `*_PERFCOUNTER_CNTL2` selects counted value type and hardware stop/count-off selectors.
- `*_PERFCOUNTER_STATE` exposes eight packed counter state/select pairs.
- `*_PERFMON_CNTL`, `*_PERFMON_CNTL2`, `*_PERFMON_CVALUE_INT_MISC`, `*_PERFMON_CVALUE_LOW`, `*_PERFMON_HI`, and `*_PERFMON_LOW` expose monitor run state, report count, count-off interrupt controls, interrupt status/ack bits, and 64-bit-style readback split across high/low fields.

`MPCC0_*` through `MPCC3_*` definitions describe four multi-plane compositor components:

- `MPCC*_MPCC_TOP_SEL`, `MPCC*_MPCC_BOT_SEL`, and `MPCC*_MPCC_OPP_ID` select compositor inputs and output processor routing.
- `MPCC*_MPCC_CONTROL` defines alpha blending, mode/current mode, pre/post-multiply controls, overlap-only mode, and stereo controls.
- `MPCC*_MPCC_SM_CONTROL` defines slice/segment metadata for side-by-side operation.
- `MPCC*_MPCC_UPDATE_LOCK_SEL` selects which update-lock source gates updates.
- `MPCC*_MPCC_TOP_GAIN`, `MPCC*_MPCC_BOT_GAIN_INSIDE`, `MPCC*_MPCC_BOT_GAIN_OUTSIDE`, and `MPCC*_MPCC_BG_*` define blend gains and background color values.
- `MPCC*_MPCC_MEM_PWR_CTRL` and `MPCC*_MPCC_STATUS` expose MPCC memory power forcing/disabling/state plus busy and idle flags.

`MPC_*`, `ADR_*_VUPDATE_LOCK_SET*`, `CFG_*_VUPDATE_LOCK_SET*`, and `CUR_*_VUPDATE_LOCK_SET*` definitions describe global compositor behavior:

- `MPC_CLOCK_CONTROL` and `MPC_SOFT_RESET` gate or reset MPC sub-blocks.
- `MPC_CRC_CTRL`, `MPC_CRC_SEL_CONTROL`, and `MPC_CRC_RESULT_*` configure and read MPC CRC output.
- `MPC_DPP_PENDING_STATUS` and `MPC_PENDING_STATUS_MISC` expose pending DPP, OPP, MPCC, update-lock, and idle status bits.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET*`, `ADR_CFG_VUPDATE_LOCK_SET*`, `ADR_VUPDATE_LOCK_SET*`, `CFG_VUPDATE_LOCK_SET*`, and `CUR_VUPDATE_LOCK_SET*` define per-lock-set address/config/current vupdate lock associations.
- `MPC_DWB0_MUX` chooses the DWB0 source.

`MPCC_OGAM0_*` and `MPCC_OGAM1_*` definitions describe per-MPCC output gamma:

- `MPCC_OGAM*_MPCC_OGAM_CONTROL` selects OGAM mode, LUT selection, PWL disable state, and current mode/select readback.
- `MPCC_OGAM*_MPCC_OGAM_LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL` expose host-indexed LUT programming and readback controls.
- `MPCC_OGAM*_MPCC_OGAM_RAMA_*` and `RAMB_*` define piecewise-linear RAM A/B start, start segment, start slope, start base, end base, end value, end slope, RGB offset, and paired region descriptors.
- `MPCC_OGAM0_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM0_MPC_GAMUT_REMAP_C**_*` define gamut remap mode/current mode, coefficient format, and two coefficient banks. The equivalent `MPCC_OGAM1` gamut-remap coefficients begin after this chunk.

## Control Flow

There is no control flow in the header itself. Runtime flow is created by code that includes this header:

1. The driver selects a DCN 3.1.6 register address from the matching address header or a generated register table.
2. It chooses the field constants from this header through macros such as `FN(reg, field)` or `SF(reg, field, mask_sh)`.
3. `REG_GET`, `REG_UPDATE`, `REG_SET`, or related helpers shift and mask values using the generated constants.
4. The helper reads or writes the memory-mapped register, and hardware updates or reports state asynchronously.

The covered fields support several hardware protocols:

- LUT programming: shaper, 3D LUT, blend-gamma, and OGAM RAM fields are written by selecting an index/control mode, writing data, and programming region descriptors for RAM A/B.
- Double-buffer/current-state observation: fields with `*_CURRENT`, `*_PENDING`, and vupdate-lock names distinguish requested state from state taken by hardware at an update boundary.
- Power management: memory power force/disable/status fields in `CM3` and `MPCC*` allow software or firmware to force blocks on/off and then observe power state.
- Diagnostics: CRC and perfmon fields configure counters or CRC sources, start/stop counting, acknowledge interrupts, and read result fields.
- Compositor routing: MPCC and MPC fields persistently define source routing, blending, update locking, and output mapping until reprogrammed.

## State and Persistence

The macros are compile-time constants and hold no state. State persistence is entirely in hardware registers after memory-mapped writes. Important persistent or observable state includes:

- Programmed DPP3 color pipeline state: HDR multiplier, coefficient formats, shaper/3D LUT mode, RAM region descriptors, LUT contents, and memory power settings.
- Programmed MPCC compositor state: top/bottom input selections, OPP routing, blending controls, gains, background colors, update-lock selection, and memory power controls.
- Programmed MPC global state: clock/reset settings, CRC source selection, DPP/OPP/MPCC pending state, update-lock set mappings, and DWB0 mux source.
- Perfmon state: active counters, selected events, run-enable sources, count-off thresholds, interrupt status/ack bits, and high/low readback values.
- OGAM state: mode/select/current mode, PWL disable, LUT index/data/control, RAM A/B region descriptors, offsets, and gamut-remap matrices.

Fields named `*_STATUS`, `*_CURRENT`, `*_ACTIVE`, `*_BUSY`, `*_IDLE`, `*_STATE`, `*_PENDING`, `*_INT_STATUS`, and `*_ACK` should be treated as hardware handshake or readback fields rather than ordinary storage.

## Dependencies and Integration Points

This header depends on the generated AMD ASIC register contract:

- The matching DCN 3.1.6 register address header supplies the register offsets with the same register names.
- AMD display code includes `dcn/dcn_3_1_6_sh_mask.h`; for example the DMUB DCN 3.1.6 source includes it so firmware-facing register helpers can use the DCN 3.1.6 field layout.
- DC register-helper layers use the field constants through `REG_*` helper macros and generated `mask_sh` tables.
- MPC code for nearby DCN generations demonstrates the direct integration pattern with `SF(MPCC_OGAM0_..., field, mask_sh)` entries for OGAM LUT, RAM, and gamut-remap fields. The same generated field names in this chunk are intended for that style of per-generation register table.
- Display color, plane/compositor, diagnostics, performance-monitor, and DMUB paths are the primary consumers because this chunk covers DPP3 color management, DPP top, MPCC/MPC, OGAM, CRC, and perfmon fields.

The replicated instance prefixes are significant. `CM3` and `DPP_TOP3` identify DPP pipe 3, `MPCC0` through `MPCC3` identify compositor components, `DC_PERFMON14` and `DC_PERFMON15` identify separate perfmon address blocks, and `MPCC_OGAM0`/`MPCC_OGAM1` identify per-MPCC output gamma blocks.

## Risks and Edge Cases

- Generated-header drift is the main risk. Any incorrect shift or mask can silently write the wrong bits in display hardware, causing color corruption, bad blending, failed updates, broken CRC/perfmon diagnostics, missed interrupts, or display pipeline hangs.
- The chunk boundaries are not semantic boundaries. It starts after the first two masks for `CM3_CM_BLNDGAM_RAMB_REGION_2_3` and ends before the remaining masks for `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33`. The later merge lane must combine neighboring chunks before making whole-register claims for those boundary registers.
- Names such as `*_MASK_MASK` are generated intentionally when the field itself is named `*_MASK`; they should not be manually simplified because users expect the generated `REGISTER__FIELD_MASK` contract.
- The header does not encode access semantics. Fields named `*_ACK`, `*_CLR`, `*_STATUS`, `*_CURRENT`, `*_ACTIVE`, and `*_PENDING` may have write-one-to-clear, read-only, latched, or update-boundary behavior that must be enforced by caller code and hardware documentation.
- Many LUT and region descriptors pack two region definitions into one register with small fields, for example 9-bit LUT offsets and 3-bit segment counts. Raw writes with out-of-range values can truncate or spill unless the register helper masks and caller validation are correct.
- Power-control bits can affect memories backing color or compositor blocks. Incorrect sequencing around memory power force/disable and LUT programming can lead to stale or invalid readback even if the bitfield constants are syntactically correct.
- MPCC update-lock fields and current-mode fields indicate hardware synchronization. Assuming writes take effect immediately can race vupdate or update-lock gating.
- `MPCC_OGAM0` is complete through gamut-remap bank B in this chunk, while `MPCC_OGAM1` is only complete through most RAM B region descriptors. Absence of `MPCC_OGAM1` gamut-remap definitions in this chunk does not imply absence from the source file.

## Test Signals

This chunk has no directly unit-testable function behavior. Useful validation signals are structural and integration-oriented:

- Compile AMDGPU display code for DCN 3.1.6 with this header included; undefined macro errors catch missing or renamed generated fields.
- Compare generated `__SHIFT`/`_MASK` pairs against the authoritative ASIC register database for DCN 3.1.6.
- Run static checks that every field used in DCN 3.1.6 `mask_sh` tables has both a shift and mask definition.
- Validate mask/shift consistency mechanically: masks should align with their shifts, paired low/high fields should not overlap, and full-register fields such as low counter values should use `0xFFFFFFFFL`.
- Exercise display modes that program DPP3 color management, shaper/3D LUT, MPCC blending, OGAM, and gamut remap, then verify visual output or CRC stability.
- Exercise perfmon and CRC debug paths: counters should start/stop, interrupt status/ack bits should behave, and high/low result fields should produce plausible values.
- Exercise update-lock and vupdate paths by changing MPCC/MPC state during active scanout and confirming no stuck `*_PENDING`, `*_BUSY`, or update-lock status remains.
- Exercise power-management transitions around CM and MPCC memories, checking that status fields match programmed force/disable values and that LUT programming survives required power states.
