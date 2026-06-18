# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 22387-24908

## Scope

This chunk covers 2,522 lines from the generated DCN 2.0 register shift/mask header. It begins inside the `CM3_CM_BLNDGAM_RAMA` region table at `REGION_30_31`, completes the `CM3_CM_BLNDGAM_RAMA_REGION_32_33` and full `CM3_CM_BLNDGAM_RAMB` region/programming definitions, then covers the remaining DPP3 color-management blocks, `DC_PERFMON16`, MPCC0 through MPCC7 compositor masks, MPC global/update/output masks, and the start of the `MPCC_OGAM0` output-gamma block through `MPCC_OGAM_RAMB_REGION_30_31`.

The source is not executable C. It exports preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for bitfield packing and extraction. These macros pair with address definitions in `dcn_2_0_0_offset.h` and are consumed by AMD display register helper layers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `TF_SF`, `SF`, `SRI`, and `SRII`.

## Purpose

The chunk describes register bit layouts for DCN 2.0 display color processing, composition, monitoring, and output-gamma control:

- `CM3_CM_BLNDGAM_*` fields define the DPP3 blend-gamma PWL LUT RAM A/B programming surface: per-channel start points, start segments, linear slopes, end points, end slopes/bases, and 34 exponential regions encoded two regions per register.
- `CM3_CM_HDR_MULT_COEF`, `CM3_CM_MEM_PWR_*`, `CM3_CM_DEALPHA`, and `CM3_CM_COEF_FORMAT` describe DPP color-management multiplier, memory power, alpha handling, and coefficient format controls.
- `CM3_CM_SHAPER_*` provides another double-buffered PWL LUT surface around the 3D LUT path, including offsets/scales, LUT index/data/write enables, RAM A/B start/end/region maps, and mode/configuration status.
- `CM3_CM_3DLUT_*` defines 3D LUT mode, index, data, 30-bit data, read/write controls, output normalization, and per-channel output offsets.
- `DC_PERFMON16_*` defines a perfmon counter/control/value block for DPP3-related performance observation.
- `MPCC0_*` through `MPCC7_*` define repeated MPC compositor channel controls: top/bottom selectors, OPP routing, blending/alpha/gain/background fields, memory power controls, stall status, and status readback.
- `MPC_*`, `ADR_*`, `CFG_*`, and `CUR_*` fields define global MPC control, CRC, perfmon event selection, pending/taken update bookkeeping, vertical-update locks, output muxes, and output denormalization clamps.
- `MPCC_OGAM0_MPCC_OGAM_*` starts the first MPCC output-gamma block: output gamma mode, LUT address/data/RAM selection, and PWL RAM A/B region descriptors.

## Important Macro Families

`CM3_CM_BLNDGAM_RAMA/RAMB` is the DPP blend-gamma transfer-function surface for instance 3. Each RAM has B/G/R start controls with 18-bit start values and 7-bit start-segment fields, per-channel 18-bit linear-slope controls, end controls with 16-bit end values plus slope/base fields, and `REGION_0_1` through `REGION_32_33` pairs. Each region pair encodes two 9-bit LUT offsets and two 3-bit segment counts at shifts `0`, `0xc`, `0x10`, and `0x1c`.

`CM3_CM_SHAPER_RAMA/RAMB` mirrors the double-buffered PWL pattern for the shaper LUT, but its start/end controls are slightly different from blend gamma: shaper end controls pack the end coordinate and end base, while shaper LUT data is programmed through `CM_SHAPER_LUT_INDEX`, `CM_SHAPER_LUT_DATA`, and `CM_SHAPER_LUT_WRITE_EN_MASK`.

`CM3_CM_3DLUT_*` exposes three-dimensional LUT controls. `CM_3DLUT_MODE` contains enable/mode and size selection, `CM_3DLUT_INDEX` chooses entries, `CM_3DLUT_DATA` and `CM_3DLUT_DATA_30BIT` carry 12-bit-pair and 30-bit packed data paths, and `CM_3DLUT_READ_WRITE_CONTROL` carries RAM selection, write mask, config status, and 30-bit enable state.

`DC_PERFMON16_*` is a self-contained performance counter block with enable/start/stop/clear style controls, counter event selection, mode/state, current value, high/low result registers, and interrupt/status bits. It is generated in the same header because DC perfmon registers are address-block-specific hardware registers rather than standalone driver logic.

`MPCC[0-7]_*` masks are replicated per MPCC instance. They cover layer routing (`TOP_SEL`, `BOT_SEL`, `OPP_ID`), blend mode and alpha controls (`MPCC_CONTROL`), state-machine control/status, update-lock selection, gain/background values, memory power, stall detection, and compositor status. The repeated field layouts let generic MPC code index by `mpcc_id`.

`MPC_*` global masks cover clock/reset, CRC setup/results, event selection, bypass background colors, stall timing, host read controls, pending/taken status registers, vupdate lock sets, and six output mux/denorm blocks. The update status registers are wide bit collections, so a single incorrect mask can misreport many pipe or OPP update states.

`MPCC_OGAM0_MPCC_OGAM_*` is the MPCC-side output-gamma LUT for compositor output. In this DCN 2.0 chunk it uses `MPCC_OGAM_MODE`, `MPCC_OGAM_LUT_INDEX`, 19-bit `MPCC_OGAM_LUT_DATA`, `MPCC_OGAM_LUT_RAM_CONTROL`, and RAM A/B PWL region descriptors. The next chunk continues the tail of `MPCC_OGAM0` and subsequent OGAM instances.

## APIs, Types, and Functions

There are no functions, structs, or enums defined in this header chunk. The macros are the generated hardware-description API used by typed register tables in the DC driver:

- `*_SHIFT` constants hold field bit offsets.
- `*_MASK` constants hold already-positioned field masks.
- Address-block comments such as `dce_dc_mpc_mpcc0_dispdec`, `dce_dc_mpc_mpc_cfg_dispdec`, and `dce_dc_mpc_mpcc_ogam0_dispdec` group registers by hardware block.

Representative consumers include `display/dc/dpp/dcn20/dcn20_dpp.h`, `display/dc/dpp/dcn20/dcn20_dpp_cm.c`, `display/dc/mpc/dcn20/dcn20_mpc.h`, and `display/dc/mpc/dcn20/dcn20_mpc.c`. The DPP side maps `CM0_*`/`CM3_*` generated masks into `dcn20_dpp` transfer-function fields with `TF_SF(...)`; the MPC side maps `MPCC0_*`, `MPC_OUT0_*`, and `MPCC_OGAM0_*` fields into `dcn20_mpc_shift` and `dcn20_mpc_mask` structures with `SF(...)`.

At runtime, DPP functions such as `dpp20_program_blnd_lut`, `dpp20_program_shaper`, and `dpp20_program_3dlut` use these masks through `REG_SET`, `REG_SET_2`, `REG_SET_4`, `REG_UPDATE`, and `REG_GET`. MPC functions such as `mpc2_program_luta`, `mpc2_program_lutb`, `mpc20_configure_ogam_lut`, `mpc20_get_ogam_current`, and `mpc20_power_on_ogam_lut` use the MPCC OGAM masks to select RAM A/B, write PWL entries, program region descriptors, and read active configuration state.

## Control Flow

This header has no branches or callable control flow. The operational flow appears in the DCN20 DPP and MPC code that consumes the fields:

1. DCN resource construction includes the generated offset and shift/mask headers, then initializes per-instance register address arrays and per-field shift/mask tables.
2. DPP blend gamma programming selects a RAM through `CM_BLNDGAM_LUT_WRITE_EN_MASK`, resets `CM_BLNDGAM_LUT_INDEX`, streams packed RGB and delta entries through `CM_BLNDGAM_LUT_DATA`, writes RAM A/B PWL start/end/region descriptors, and switches `CM_BLNDGAM_CONTROL` to the newly programmed mode.
3. DPP shaper programming follows the same double-buffer pattern with `CM_SHAPER_LUT_WRITE_EN_MASK`, `CM_SHAPER_LUT_INDEX`, `CM_SHAPER_LUT_DATA`, RAM A/B start/end/region registers, and `CM_SHAPER_CONTROL`.
4. DPP 3D LUT programming reads current mode/status, selects the target RAM and bit depth through `CM_3DLUT_READ_WRITE_CONTROL`, writes LUT entries through either `CM_3DLUT_DATA` or `CM_3DLUT_DATA_30BIT`, then updates `CM_3DLUT_MODE` and output normalization/offset fields.
5. MPC/MPCC composition code programs MPCC selector/control/gain/background fields per plane composition tree, routes MPCCs to OPPs, and uses update lock/vupdate fields to coordinate hardware-visible changes.
6. MPCC OGAM programming selects the inactive output-gamma RAM, resets the LUT index, streams RGB/delta data through `MPCC_OGAM_LUT_DATA`, writes RAM A/B PWL descriptors, then changes `MPCC_OGAM_MODE`/RAM control state.
7. Diagnostic or debug paths read perfmon counters, CRC results, stall/status registers, MPCC status, and update-pending/taken registers to validate hardware state.

## State and Persistence

The header stores no software state, but the fields describe persistent MMIO state in display hardware. Color LUTs and region descriptors persist until overwritten, reset, power-gated, or reinitialized by a modeset. RAM A/B selection fields are persistent and are used to avoid changing the active LUT while programming a new one.

DPP state includes blend-gamma mode/config status, LUT index auto-advance state, LUT RAM contents, memory power state, dealpha enable/mode, shaper offsets/scales, shaper LUT state, 3D LUT size/mode/RAM selection/bit depth, output normalization, and test-debug selector/data registers.

MPC state includes MPCC routing and blend configuration, OPP assignment, MPCC state-machine controls, background colors, gain values, memory power controls, stall and disabled status, global clock/reset, CRC controls and results, output mux choices, denormalization clamp values, update pending/taken state, and vupdate locks.

Perfmon state includes selected events, counter enable/state, interrupt/mask state, current count, high/low latched result words, and misc current-value fields. These fields can be read-only, write-one-to-clear, or mode-dependent in hardware, but the generated masks do not encode that semantic distinction beyond field names.

## Dependencies and Integration Points

This chunk depends on the companion offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` for concrete register addresses. The offset names and these shift/mask names must match exactly for the register helper tables to be correct.

Key integration points are:

- `display/dc/dpp/dcn20/dcn20_dpp.h`, which lists DPP transfer-function registers and maps generated color-management field masks into DPP shift/mask structs.
- `display/dc/dpp/dcn20/dcn20_dpp_cm.c`, which programs blend gamma, shaper, and 3D LUT hardware through these fields and the shared `cm_helper_program_xfer_func` PWL helper.
- `display/dc/dpp/dcn20/dcn20_dpp.c`, which reads shaper, 3D LUT, and blend-gamma status fields into DPP state snapshots.
- `display/dc/mpc/dcn20/dcn20_mpc.h`, which builds MPC register and mask lists for MPCC, output denorm, vupdate lock, and MPCC OGAM fields.
- `display/dc/mpc/dcn20/dcn20_mpc.c`, which programs MPCC blending and output-gamma LUT RAMs using the generated masks.
- `display/dc/hwss/dce/dce_hwseq.h` and DCN hardware sequence code, which reference MPC CRC registers for diagnostics.

Later DCN generations keep similar conceptual blocks but sometimes rename, split, or remove fields. For example, later MPC OGAM control fields add more status/select bits, while DCN3.2 comments indicate DPP blend gamma was removed from that DPP path. That makes the DCN 2.0 generated field layout generation-specific rather than a universal schema.

## Risks

The primary risk is silent MMIO misprogramming. A wrong shift or mask can compile cleanly while writing a neighboring bitfield in a live color, blend, routing, or diagnostic register.

Chunk-boundary risk is present at both ends. The chunk starts after the earlier `CM3_CM_BLNDGAM_RAMA` controls and most `RAMA_REGION_*` definitions, so this document only covers the tail of RAM A. It ends at `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_30_31`; `REGION_32_33` and following OGAM blocks continue in the next chunk.

Repeated-block risk is high. `MPCC0` through `MPCC7` and `MPC_OUT0` through `MPC_OUT5` are structurally similar, as are RAM A/B LUT descriptors. Pairing an instance's offset array with another instance's masks can produce valid-looking register writes against the wrong compositor/output block.

Double-buffer sequencing is order-sensitive. Blend gamma, shaper, and MPCC OGAM programming must choose the inactive RAM, enable the correct write mask, reset the LUT index, write the full table, program region descriptors, then switch mode. Incorrect masks for RAM selection, config status, LUT index, or mode fields can cause visible color corruption or flip to partially programmed LUT contents.

Color precision fields are sensitive. LUT data masks, 3D LUT 30-bit enable/data masks, normalization factors, offsets, slopes, bases, and region segment counts directly affect transfer-function accuracy. Small field-width errors can produce banding, clipping, color shifts, or failed HDR/color-management validation.

Update and status fields can hide synchronization bugs. `MPC_PENDING_TAKEN_STATUS_REG*`, `MPC_UPDATE_ACK_REG*`, `CUR_VUPDATE_LOCK_SET*`, MPCC stall/status, and CRC/perfmon fields are often used to prove that hardware accepted a change. Incorrect masks may make the driver believe a transition completed when it did not, or may force unnecessary waits.

Power-management masks can be disruptive. `CM3_CM_MEM_PWR_CTRL`, `MPCC*_MPCC_MEM_PWR_CTRL`, and MPCC OGAM memory power bits can gate memories that hold LUT or compositor state. A bad mask can drop state, keep memories powered unnecessarily, or make subsequent color programming fail.

## Test Signals

Useful validation signals include:

- Build coverage for DCN20 DPP and MPC code that includes `dcn_2_0_0_sh_mask.h`, especially `dcn20_dpp_cm.c`, `dcn20_dpp.c`, `dcn20_mpc.c`, and their generated register-list headers.
- Generated-header checks that every `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, masks align with shifts, and repeated MPCC/output/color RAM blocks remain structurally equivalent where hardware intends equivalence.
- Diff checks against AMD's authoritative DCN 2.0 register database or known-good upstream generated headers.
- Color pipeline tests for blend gamma, shaper LUT, and 3D LUT programming, including RAM A/B flips, bypass mode, 17x17x17 versus 9x9x9 3D LUT size, 10-bit versus 12-bit/30-bit paths, HDR curves, and gamut/color-management validation patterns.
- Plane composition tests covering MPCC top/bottom selection, alpha blend modes, premultiplied alpha, global alpha/gain, background color, bottom gain modes, OPP routing, and multi-plane update locks.
- Output-gamma tests that program MPCC OGAM RAM A/B and verify that `MPCC_OGAM_CONFIG_STATUS`, LUT data, slopes, bases, region offsets, and segment counts produce expected ramp output.
- CRC and perfmon smoke tests that enable MPC CRC, read `MPC_CRC_RESULT_*`, select perfmon events, and verify counter transitions and interrupt/status bits.
- Power-management tests that toggle DPP CM and MPCC/OGAM memory power states, then reprogram or read back LUT/configuration state after power transitions.
- Modeset and cursor/plane-update tests that exercise `MPC_PENDING_TAKEN_STATUS_REG*`, `MPC_UPDATE_ACK_REG*`, and `CUR_VUPDATE_LOCK_SET*` fields under concurrent updates and vblank synchronization.

## Cross-Chunk Notes

This is a middle slice of `dcn_2_0_0_sh_mask.h`, not a standalone module boundary. The preceding chunk owns the beginning of `CM3_CM_BLNDGAM` and earlier DPP3 color-management definitions. The following chunk continues the `MPCC_OGAM0` region table and subsequent output-gamma instances. The final per-file report should reconcile those boundaries so `CM3_CM_BLNDGAM_RAMA` and `MPCC_OGAM0` are not described as incomplete hardware blocks.
