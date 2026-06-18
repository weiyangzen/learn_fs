# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 49291-51798

## Scope

This chunk is a generated register shift/mask slice for AMD DCN 3.0.2 display hardware. It covers 2,508 lines, with 2,106 `#define` constants split almost evenly between `__SHIFT` and `_MASK` definitions. The source file is included by `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` together with `dcn_3_0_2_offset.h`, and the field names are consumed by AMD Display Core register-table macros such as `SF(...)` in `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`.

The chunk is declarative rather than executable: it exports preprocessor constants that tell the DC register helper layer how to pack, update, and read bitfields in 32-bit display engine registers.

## Purpose

The constants in this range describe several MPC and MPCC color-pipeline register blocks:

- Tail of `MPCC_OGAM3` output gamma RAM A/B region metadata, offsets, endpoints, and gamut-remap coefficient fields.
- Full `MPCC_OGAM4` output gamma block, including LUT selection/control/data fields, RAM A/B piecewise-linear region descriptors, per-channel start/end/offset values, and gamut-remap matrix fields.
- `dce_dc_mpc_mpc_cfg_dispdec` MPC configuration fields for clock gating, soft reset, CRC control/results, background bypass color, host read throttling, DPP/OPP update-pending status, vupdate lock sets, and DWB muxing.
- `dce_dc_mpc_mpc_ocsc_dispdec` output mux, denormalization, and output CSC register fields for outputs 0 through 4.
- Start of `dce_dc_mpc_mpc_rmu_dispdec`, including RMU muxing, memory power control, RMU0 shaper LUT/RAM and 3DLUT fields, and RMU1 shaper LUT/RAM fields through `MPC_RMU1_SHAPER_RAMB_REGION_26_27`.

These definitions let shared DCN30-era MPC code use symbolic field names while the ASIC-specific header supplies the actual bit positions for DCN 3.0.2.

## Important APIs, Types, and Macro Families

There are no C functions or types in this chunk. The API surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the raw register value.
- Register comments such as `//MPC_CRC_CTRL` and address block comments group constants by hardware block.

Important families visible in this slice:

- `MPCC_OGAM3_*` and `MPCC_OGAM4_*`: per-MPCC output gamma and gamut remap. The RAM region pairs define `EXP_REGIONn_LUT_OFFSET` and `EXP_REGIONn_NUM_SEGMENTS` fields using the common pattern offsets at bits 0/12/16/28 and masks `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000`.
- `MPCC_OGAM4_MPCC_OGAM_CONTROL`, `LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL`: mode/select/current/status fields for OGAM LUT programming.
- `MPCC_OGAM*_MPC_GAMUT_REMAP_Cxx_Cyy_[AB]`: 16-bit coefficient pairs for gamut-remap matrices, with one coefficient in bits 0-15 and another in bits 16-31.
- `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_*`, `MPC_DPP_PENDING_STATUS`, and `MPC_PENDING_STATUS_MISC`: global MPC control, diagnostics, and update-state observation fields.
- `ADR_CFG_CUR_VUPDATE_LOCK_SETn`, `ADR_CFG_VUPDATE_LOCK_SETn`, `ADR_VUPDATE_LOCK_SETn`, `CFG_VUPDATE_LOCK_SETn`, and `CUR_VUPDATE_LOCK_SETn`: five sets of vupdate lock flags.
- `MPC_OUT[0-4]_MUX`, `MPC_OUT[0-4]_DENORM_*`, `MPC_OUT[0-4]_CSC_*`, and `MPC_OUT_CSC_COEF_FORMAT`: output path routing, clamping/denormalization, and color-space conversion.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`: RMU mux select/status and memory power/low-power state fields for RMU0-RMU2.
- `MPC_RMU0_*` and `MPC_RMU1_*`: shaper LUT offsets/scales, LUT index/data/write enables, RAM A/B region descriptors, and RMU0 3DLUT mode/data/read-write controls.

The companion consumer macros in `dcn30_mpc.h` declare register field lists and `MASK_SH` mappings, for example mapping `MPC_RMU0_SHAPER_RAMA_REGION_0_1` plus `MPC_RMU_SHAPER_RAMA_EXP_REGION0_LUT_OFFSET` through `SF(...)` into the runtime `mpc_shift` and `mpc_mask` tables. Runtime code then uses helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET`, `REG_GET`, and `REG_WAIT` against those tables.

## Control Flow and State Behavior

This header chunk has no direct control flow. Its behavior is compile-time substitution into the AMD display register access layer:

1. DCN302 resource setup includes the DCN 3.0.2 offset and shift/mask headers.
2. MPC/MPCC register structs are initialized with ASIC-specific register addresses, masks, and shifts.
3. Higher-level display code calls generic MPC operations, such as output mux setup, OGAM programming, CSC programming, CRC control, RMU shaper/3DLUT programming, or pending-status reads.
4. Register helper macros combine the runtime value with the field shift and mask from this header, preserving unrelated bits in the same register where appropriate.

Hardware state persists in MMIO registers, not in this file. Several fields expose latched or current hardware state:

- `*_CURRENT` fields report active OGAM/gamut/CSC/shaper modes after double-buffered programming takes effect.
- `*_STATUS` fields report mux or configuration status, including DWB mux, RMU mux, OGAM LUT status, shaper config status, and 3DLUT config status.
- `MPC_DPP_PENDING_STATUS` and `MPC_PENDING_STATUS_MISC` expose pending DPP, cursor, OPP, and DWB update bits.
- `MPC_CRC_RESULT_*` holds CRC output values when CRC capture is enabled.
- Memory power state fields in `MPC_RMU_MEM_PWR_CTRL` represent RMU shaper and 3DLUT memory state for RMU instances.

The many LUT and RAM fields are used by software sequencing that writes indices, data, region starts, region ends, offsets, and mode fields in a hardware-required order. The constants themselves do not enforce that order.

## Dependencies and Integration Points

Primary dependencies:

- `dcn_3_0_2_offset.h` supplies the matching register addresses. This file supplies only bit shifts and masks.
- `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` includes this header for DCN302 hardware resource construction.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h` and `dcn30_mpc.c` provide the shared MPC implementation that consumes these field names through generated register tables.
- The `reg_helper.h` macros consume field metadata to perform read-modify-write, field extraction, and wait loops.

Notable integration with display features:

- MPCC OGAM fields integrate with per-plane/per-MPCC output gamma LUT programming and gamut remap.
- MPC output CSC and denorm fields integrate with OPP/output color conversion and clamp control for each of five outputs.
- MPC CRC fields integrate with display CRC validation paths used for diagnostics and automated display tests.
- DPP/OPP/DWB pending-status fields integrate with update synchronization and flip/update sequencing.
- RMU shaper and 3DLUT fields integrate with advanced color management and RAM-backed LUT programming.
- RMU and OGAM memory-power fields integrate with display power-management sequencing; callers must usually power memories before LUT programming and wait for state changes.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask silently writes the wrong hardware bits, which can break color output, mux routing, CRC reads, power sequencing, or update synchronization.
- Register field names must stay aligned with the field-list macros in `dcn30_mpc.h`. If a consumer references a field not present in this ASIC header, compilation fails; if the name exists but the value is wrong, failure is runtime-only.
- Many registers pack two 16-bit values or two region descriptors into one register. Incorrect masks can corrupt the paired field during read-modify-write operations.
- Region descriptors use repeated bit layouts for RAM A/B and multiple instances. Copy-generation mistakes are hard to spot manually because the macro families are highly repetitive.
- Status/current fields should generally be treated as read-only or hardware-owned. Writing them accidentally through generic helpers can cause undefined display behavior if the register map does not ignore writes.
- The chunk boundary ends after `MPC_RMU1_SHAPER_RAMB_REGION_26_27`; subsequent RMU1 RAMB regions continue outside this chunk. Whole-file research must merge adjacent chunks before drawing complete conclusions about RMU1 coverage.

## Test Signals

Useful validation signals for code using this header include:

- Compile coverage for DCN302 resource construction and MPC register tables; missing or renamed macros are caught at build time.
- Display color-management tests that program OGAM, gamut remap, output CSC, shaper LUTs, and 3DLUTs, then verify visible output or hardware CRC values.
- CRC capture tests using `MPC_CRC_CTRL`, `MPC_CRC_SEL_CONTROL`, and `MPC_CRC_RESULT_*`.
- Flip/update sequencing tests that watch `MPC_DPP_PENDING_STATUS`, `MPC_PENDING_STATUS_MISC`, and vupdate lock bits for expected transitions.
- Power-management tests that exercise RMU memory power force/disable/state fields and confirm LUT access only occurs when memory is powered.
- Register trace or MMIO readback comparison against AMD register specifications for DCN 3.0.2, especially for packed coefficient and region descriptor fields.
