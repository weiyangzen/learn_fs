# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 24953-27463

## Purpose

This chunk is a generated DCN 3.1.6 AMD display ASIC register shift/mask slice. It contains preprocessor constants only: 2,097 `#define` entries, split into 1,048 `__SHIFT` macros and 1,049 `_MASK` macros. The constants describe bit positions and register-value masks for MPC/MPCC color pipeline blocks and the beginning of the ABM0 backlight/PWM block. They are paired with `dcn_3_1_6_offset.h` register-address macros and consumed by DCN 3.1.6 display resource construction and register helper code.

Although this repository path is under `sources/distributed-fs/ceph-client`, the file is AMDGPU display-driver hardware metadata, not Ceph filesystem logic. There are no functions, structs, enums, heap objects, locks, syscalls, or executable control-flow statements in this chunk.

The range has artificial boundaries. It starts after the first field of `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33`; adjacent previous lines define that register's `REGION32_LUT_OFFSET__SHIFT`. It ends at the comment for `ABM0_BL1_PWM_BL_UPDATE_SAMPLE_RATE`, before that register's fields are emitted.

## Covered Hardware Blocks

- Tail of `MPCC_OGAM1`: final RAMB region 32/33 fields plus output-gamma gamut-remap coefficient format, remap mode/current-mode, and A/B matrix coefficient fields.
- Complete `dce_dc_mpc_mpcc_ogam2_dispdec`: `MPCC_OGAM2` output-gamma control, LUT index/data/control, RAM A and RAM B PWL curve descriptors, and gamut-remap matrix banks.
- Complete `dce_dc_mpc_mpcc_ogam3_dispdec`: the same `MPCC_OGAM3` output-gamma, PWL RAM A/B, and gamut-remap field surface.
- `dce_dc_mpc_mpc_ocsc_dispdec`: MPC output mux, denormalization, output color-space conversion (OCSC) coefficient banks for outputs 0-3, and OCSC test/debug access.
- `dce_dc_mpc_mpc_rmu_dispdec`: RMU mux/memory-power control, RMU0 and RMU1 shaper LUT/PWL fields, and RMU0/RMU1 3D LUT fields. RMU0 starts at global control and RMU1 is complete through 3DLUT output offsets.
- Start of `dce_dc_opp_abm0_dispdec`: ABM0 BL1 PWM ambient/user/target/current levels, final/minimum duty-cycle fields, and ABM PWM policy control.

## Important APIs, Types, and Macros

The naming contract is generated and token-paste driven:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask after shifting into register-value position.
- Some names intentionally include repeated `MASK` tokens, such as `MPC_RMU1_SHAPER_LUT_WRITE_EN_MASK__MPC_RMU_SHAPER_LUT_WRITE_EN_MASK_MASK`, because the hardware field itself is named `*_MASK`.

Important field families in this chunk include:

- `MPCC_OGAM<n>_MPCC_OGAM_CONTROL`: active OGAM mode, RAM select, PWL disable, and current mode/select readback.
- `MPCC_OGAM<n>_MPCC_OGAM_LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL`: host programming cursor, 18-bit LUT data, per-color write mask, read color selection, debug-read enable, host RAM selection, and config mode.
- `MPCC_OGAM<n>_MPCC_OGAM_RAMA_*` and `RAMB_*`: two hardware RAM-bank descriptions for output-gamma PWL curves. Region registers pack two regions per register with `LUT_OFFSET` fields at bits 0/16 and `NUM_SEGMENTS` fields at bits 12/28.
- `MPCC_OGAM<n>_MPCC_GAMUT_REMAP_*` and `MPC_GAMUT_REMAP_Cxx_Cyy_[AB]`: gamut-remap coefficient format, active/current bank/mode, and packed 16-bit coefficient pairs for A/B matrix banks.
- `MPC_OUT<n>_MUX`, `DENORM_*`, and `CSC_*`: output routing/rate-control, denormalization clamp controls, output CSC mode/current mode, and A/B coefficient matrices.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`: RMU mux selection/status and force/disable/state fields for RMU0/RMU1 shaper and 3DLUT memories.
- `MPC_RMU<n>_SHAPER_*`: shaper LUT mode/current mode, RGB offset/scale, LUT index/data/write enables, RAM A/B PWL start/end/region descriptors.
- `MPC_RMU<n>_3DLUT_*`: 3DLUT mode/size/current mode, index, 16-bit paired data path, 30-bit data path, RAM select/write/read controls, output normalization factor, and RGB output offset/scale.
- `ABM0_BL1_PWM_*`: 17-bit ambient, user, target, current, final-duty, and minimum-duty values plus enable and auto-update policy bits.

The direct integration points are visible in this tree. `display/dc/resource/dcn316/dcn316_resource.c` includes `dcn_3_1_6_sh_mask.h`, then builds `mpc_regs`, `mpc_shift`, and `mpc_mask` with `MPC_REG_LIST_DCN3_0`, `MPC_RMU_GLOBAL_REG_LIST_DCN3AG`, `MPC_RMU_REG_LIST_DCN3AG(0/1)`, and `MPC_COMMON_MASK_SH_LIST_DCN30`. It also builds ABM register/shift/mask tables with `ABM_DCN302_REG_LIST` and `ABM_MASK_SH_LIST_DCN30`. `display/dmub/src/dmub_dcn316.c` includes the same generated header for DMUB register-table constants. `display/dc/mpc/dcn30/dcn30_mpc.h` provides the MPC list and mask/shift macros that consume the `MPCC_OGAM`, `MPC_OUT`, and `MPC_RMU` field names; `display/dc/dce/dce_abm.h` consumes the ABM0 BL1 PWM field names through `ABM_SF(...)`.

## Control Flow and State

This header has no local runtime control flow. Its constants are compiled into register descriptor structures. Runtime display code later passes those descriptors to helper macros such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_WAIT`, which perform MMIO reads, bit masking, shifts, writes, and polling.

The state represented by the chunk is hardware state:

- Output gamma state: active/bypass mode, selected RAM bank, PWL disable state, current-mode/current-bank readback, LUT cursor position, LUT payload contents, and PWL curve region geometry for `MPCC_OGAM1` tail plus full `MPCC_OGAM2` and `MPCC_OGAM3`.
- Gamut-remap state: coefficient format, active/current remap mode, and two coefficient banks. The A/B matrix registers allow software to stage one bank while another is active, depending on hardware sequencing.
- MPC output state: mux routing/source selection for outputs 0-3, rate/flow control, denormalization mode and clamp limits, and output CSC coefficient banks with current-mode readback.
- RMU state: mux selection/status, memory-power force/disable/status bits, shaper LUT mode/current state, 1D shaper LUT contents, shaper PWL RAM A/B regions, 3DLUT mode/size/current state, 3DLUT RAM selection, 16-bit or 30-bit data path selection, output normalization, and output offset/scale.
- ABM/PWM state: ambient-light, user, target, current ABM level, final/minimum duty cycle, and hardware auto-update policy bits for BL1 PWM.

Persistence is hardware-local. LUT RAM contents, matrix coefficients, mux selections, and PWM levels persist in the display engine until overwritten, reset, or lost through power/reset sequencing. Indexed registers such as LUT and 3DLUT index/data pairs form stateful write streams, so write order and cursor reset are part of the hardware programming contract even though they are not encoded by this header.

## Dependencies and Integration Points

This chunk depends on exact DCN 3.1.6 register database generation. It must remain aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies the matching register offsets and base-index values.
- `display/dc/resource/dcn316/dcn316_resource.c`, which instantiates DCN 3.1.6 resource objects and populates the MPC and ABM register tables from generated offset/shift/mask macros.
- `display/dc/mpc/dcn30/dcn30_mpc.h` and `dcn30_mpc.c`, where common DCN3 MPC code expects the field names and widths used for MPCC OGAM, MPC OCSC, and RMU programming.
- `display/dc/dce/dce_abm.h` and ABM implementation code, which use the ABM0 field names as common mask/shift templates for ABM instances.
- `display/dmub/src/dmub_dcn316.c`, which includes this header for DCN 3.1.6 DMUB register descriptors.
- Register helper infrastructure in `reg_helper.h`, where masks and shifts are interpreted as bitfield metadata for MMIO helper calls.

The repeated instance prefixes are part of the ABI between generated headers and handwritten display code. Resource construction uses instance-aware offset macros for `MPCC_OGAM2`, `MPCC_OGAM3`, `MPC_OUT0`-`MPC_OUT3`, and `MPC_RMU0`/`MPC_RMU1`, while common mask/shift lists often use instance-0 names as templates for shared field layouts.

## Risks and Edge Cases

- A wrong mask or shift can compile cleanly while programming the wrong bits. Visible failures include color corruption, wrong gamma curves, broken gamut remap, blank or misrouted outputs, incorrect CSC/clamp behavior, failed 3DLUT programming, or incorrect panel backlight behavior.
- The chunk boundaries split logical registers. `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33` is incomplete at the top boundary, and `ABM0_BL1_PWM_BL_UPDATE_SAMPLE_RATE` begins only as a comment at the bottom boundary. The merge lane must reconcile adjacent chunks before making whole-file completeness claims.
- Banked LUT programming is order-sensitive. Software must select the inactive RAM bank, reset the index, write all expected entries with the correct color write mask, and switch modes only after data and region descriptors are valid.
- Status/current fields use the same macro shape as writable fields. Code that treats all fields as ordinary read-write bits can corrupt control registers or misread synchronization state.
- Memory-power state matters for RMU shaper and 3DLUT memories. Writes while memories are disabled or still transitioning can be dropped or read back inconsistently; runtime code uses waits and status reads around those paths.
- Repeated instance blocks are copy/regeneration-sensitive. A prefix mix-up between `MPCC_OGAM2` and `MPCC_OGAM3`, `MPC_OUT2` and `MPC_OUT3`, or RMU0 and RMU1 can affect only one pipe/path, making bugs display-topology dependent.
- Packed coefficient fields and limited-width value fields can silently truncate data if callers pass values outside expected fixed-point ranges. Examples include 16-bit coefficient halves, 18-bit LUT/PWL values, 17-bit PWM levels, and 9-bit LUT indices.

## Test and Validation Signals

- Build coverage for DCN 3.1.6 display code should catch missing or misspelled field macros in `dcn316_resource.c`, `dmub_dcn316.c`, `dcn30_mpc.h`, and `dce_abm.h`.
- Generated-header checks should verify that complete in-range registers have paired `__SHIFT` and `_MASK` definitions, while allowing the two documented boundary exceptions.
- Register-table sanity checks should compare `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h` for the repeated `MPCC_OGAM2/3`, `MPC_OUT0-3`, `MPC_RMU0/1`, and ABM0 field families.
- Hardware or emulator validation should exercise mode set, multi-pipe composition, output mux routing, CSC/denorm programming, gamma LUT updates, gamut-remap updates, RMU shaper programming, RMU 3DLUT programming, suspend/resume, and memory-power transitions.
- Useful runtime readbacks include `MPCC_OGAM_MODE_CURRENT`, `MPCC_OGAM_SELECT_CURRENT`, `MPCC_GAMUT_REMAP_MODE_CURRENT`, `MPC_OCSC_MODE_CURRENT`, `MPC_RMU*_MUX_STATUS`, `MPC_RMU*_SHAPER_MEM_PWR_STATE`, `MPC_RMU*_3DLUT_MEM_PWR_STATE`, `MPC_RMU_3DLUT_MODE_CURRENT`, and ABM current/final PWM level registers.

## Chunk Boundary Notes

The previous chunk is required for the beginning of `MPCC_OGAM1_MPCC_OGAM_RAMB_REGION_32_33`, including the missing `REGION32_LUT_OFFSET__SHIFT` line. The next chunk is required for `ABM0_BL1_PWM_BL_UPDATE_SAMPLE_RATE` and the remaining ABM0 register family. This document should be merged with neighboring chunk notes before producing a final per-file report for `dcn_3_1_6_sh_mask.h`.
