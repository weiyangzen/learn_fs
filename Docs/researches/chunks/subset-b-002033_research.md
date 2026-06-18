# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 15196-17712

## Scope

This chunk is a generated AMD DCN 3.2.1 register field mask/shift header segment. It covers 2,517 source lines and 2,082 preprocessor definitions: 1,040 `__SHIFT` macros and 1,042 `_MASK` macros. There are no C functions, structs, enums, or software storage objects in this range.

The chunk begins inside the tail of the `MPCC1_MPCC_STATUS` field group, then covers the complete `MPCC2`, `MPCC3`, MPC configuration, and `MPCC_OGAM0` through most of `MPCC_OGAM3` field groups. It ends at `MPCC_OGAM3_MPC_GAMUT_REMAP_C31_C32_B__MPCC_GAMUT_REMAP_C32_B__SHIFT`, before the corresponding mask definitions and the remaining `C33_C34_B` group that continue in the next chunk.

## Purpose

The purpose of this header slice is to provide compile-time bitfield metadata for DCN 3.2.1 display Multi-Plane Compositor hardware. Each register field has the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position for inserting or extracting a value.
- `<REGISTER>__<FIELD>_MASK`, the positioned bit mask for the same field.

Driver code combines these constants with register addresses from `dcn_3_2_1_offset.h` and with the AMD display register helper macros. The macros are a hardware layout contract, not an algorithm. Correctness depends on the masks and shifts matching the silicon register database.

The hardware surfaces covered here are:

- MPCC blender instances `MPCC1` tail, `MPCC2`, and `MPCC3`: compositor plane selection, OPP binding, alpha/blend control, stereo or frame-alternate control, update locks, per-layer gain, background color, OGAM memory power control, and status bits.
- MPC global configuration: clock gating/test clock selection, soft resets for MPCC/SFR/SFT/MPC blocks, CRC control and readback, bypass background values, host read control, DPP pending status, vupdate lock sets, and DWB mux selection.
- MPCC OGAM instances `MPCC_OGAM0` through `MPCC_OGAM3`: output gamma/1D LUT mode, LUT host access, RAM A/RAM B piecewise-linear region programming, RGB offsets/start/end/slope/base fields, gamut remap coefficient format, gamut remap mode, and matrix coefficients for RAM A/B.

## Important APIs, Types, And Macros

The macro namespace is the only API in this chunk. Consumers do not call into this file; instead, DCN register tables expand these names into shift and mask structures used by register helper calls such as `REG_UPDATE`, `REG_SET`, `REG_GET`, and related field access macros.

Important register families in the chunk include:

- `MPCC2_MPCC_*` and `MPCC3_MPCC_*`: `TOP_SEL`, `BOT_SEL`, `OPP_ID`, `CONTROL`, `SM_CONTROL`, `UPDATE_LOCK_SEL`, `TOP_GAIN`, `BOT_GAIN_INSIDE`, `BOT_GAIN_OUTSIDE`, `MOVABLE_CM_LOCATION_CONTROL`, background RGB/YUV components, `MEM_PWR_CTRL`, and `STATUS`.
- `MPC_*`: `CLOCK_CONTROL`, `SOFT_RESET`, `CRC_CTRL`, `CRC_SEL_CONTROL`, CRC result registers, bypass background values, `HOST_READ_CONTROL`, `DPP_PENDING_STATUS`, `PENDING_STATUS_MISC`, four `*_VUPDATE_LOCK_SET*` groups, and `MPC_DWB0_MUX`.
- `MPCC_OGAM{0,1,2,3}_MPCC_OGAM_*`: OGAM mode/select/PWL-disable state, LUT index/data/control, RAM A and RAM B PWL region start/end/offset/region definitions, and RAM selection or current-state fields.
- `MPCC_OGAM{0,1,2,3}_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM{0,1,2,3}_MPC_GAMUT_REMAP_*`: gamut remap coefficient format/mode and packed 16-bit matrix coefficient fields for coefficients `C11` through `C34` in A and B banks.

The dominant data shape is a 32-bit hardware register containing one or more packed fields. Examples include:

- 4-bit MPCC selectors and OPP IDs.
- 8-bit `MPCC_GLOBAL_ALPHA` and `MPCC_GLOBAL_GAIN` fields inside `MPCC*_MPCC_CONTROL`.
- 12-bit background color fields for R/Cr, G/Y, and B/Cb.
- 19-bit gain, LUT offset, region base, end, and offset fields in OGAM PWL programming.
- 16-bit packed gamut remap coefficients, with two coefficients per register.
- Current/readback fields such as `MPCC_OGAM_MODE_CURRENT`, `MPCC_OGAM_SELECT_CURRENT`, `MPCC_GAMUT_REMAP_MODE_CURRENT`, `MPCC_UPDATE_LOCKED_STATUS`, `MPC_DWB0_MUX_STATUS`, and `MPCC_OGAM_MEM_PWR_STATE`.

## Control Flow And Behavior

This chunk has no executable control flow. Runtime behavior is created by other AMD display code that includes the generated header, selects a register address from the matching offset header, and then performs hardware reads or writes through DC register helpers.

The implied hardware flows represented by these fields are:

1. MPCC composition setup: software selects top and bottom inputs, assigns an OPP, chooses blend mode and alpha mode, programs global alpha/gain, selects background bit depth, and applies per-plane top or bottom gain.
2. Update synchronization: MPCC update lock selection and vupdate lock set fields coordinate register updates with display timing so composition changes do not tear or partially apply.
3. MPC reset and diagnostics: MPC soft reset fields can reset MPCC, SFR, SFT, or whole-MPC blocks; CRC controls select windows and components for display-pipeline verification; pending status fields report DPP and MPC outstanding work.
4. Memory power sequencing: `MPCC*_MPCC_MEM_PWR_CTRL` exposes OGAM memory force/disable/low-power/state bits. In the DCN32 MPC code, `mpc32_mpc_init()` programs `MPCC_OGAM_MEM_LOW_PWR_MODE` across MPCC instances when MPC memory low power is enabled.
5. OGAM LUT programming: callers select RAM A or RAM B, set LUT index/data and write-color masks, program PWL region starts/end slopes/base/offsets for RGB channels, then switch or verify the active/current OGAM mode and selected RAM.
6. Gamut remap programming: the gamut remap coefficient format/mode fields and packed coefficient registers describe the per-MPCC color matrix state used by MPC gamut remap paths.
7. DWB routing: `MPC_DWB0_MUX` and status fields select and observe the display writeback mux source.

The header does not encode safe sequencing, register volatility, read/write permissions, or timeouts. Those requirements live in the MPC implementation and hardware programming guide.

## State And Persistence Behavior

The file stores no software state and has no persistence behavior by itself. It describes hardware register state in the GPU display block.

State classes represented in this chunk include:

- Latched compositor configuration: MPCC input selection, OPP binding, blend/alpha/gain/background color, DWB mux, and OGAM/gamut-remap mode.
- Double-buffered or banked color state: OGAM RAM A/RAM B LUT entries, PWL region programming, and gamut remap A/B coefficient banks.
- Synchronization state: update lock selection, locked-status readback, vupdate lock set values, and current-mode/current-select readback fields.
- Power state: OGAM memory force/disable/low-power configuration and memory power-state readback.
- Reset and transient control state: soft-reset bits and CRC control fields can have immediate hardware side effects.
- Diagnostic/readback state: CRC result registers, DPP pending status, pending-status misc fields, MPCC idle/busy/disabled status, and DWB mux status.

Because the macros only expose bit locations, they cannot distinguish read-only status fields from writable control fields. Consumers must avoid writing status/current fields unless the programming sequence explicitly requires it.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.2.1 register map set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h` supplies the matching register addresses and base indices. For example, the offset header defines registers such as `regMPCC2_MPCC_CONTROL`, `regMPC_SOFT_RESET`, `regMPCC_OGAM0_MPCC_OGAM_CONTROL`, and `regMPCC_OGAM0_MPC_GAMUT_REMAP_C33_C34_B`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h` supplies the field masks and shifts studied here.

Direct include evidence in this tree shows DCN 3.2.1 resource construction includes both generated headers from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`. The broader MPC field tables and functions are shared with DCN32-era code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h` maps many of these mask/shift names through `MPC_COMMON_MASK_SH_LIST_DCN32`, including MPCC memory power fields, OGAM controls, PWL region fields, gamut remap fields, and DWB mux fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c` uses the populated mask/shift tables for memory low-power initialization, LUT power control, post-1D LUT programming, gamut remap hooks, and MPC function dispatch.
- Older and newer MPC headers (`dcn30`, `dcn42`) show the same generated-mask contract reused across DCN generations, so this chunk is part of an established register-table pattern rather than a standalone API.

Although the repository path is under a local `ceph-client` mirror, this source has AMDGPU display hardware semantics. It has no Ceph filesystem protocol behavior and no distributed-filesystem persistence model.

## Risks And Edge Cases

- Mask/shift drift can silently program wrong hardware bits. A bad constant may still compile but break blending, color correction, update locking, writeback routing, or memory power behavior.
- Chunk boundaries are artificial. This chunk starts after the beginning of `MPCC1_MPCC_STATUS` and ends before the final `MPCC_OGAM3_MPC_GAMUT_REMAP_C31_C32_B` masks and subsequent group. The final per-file merge must reconcile adjacent chunks.
- Repetitive instance blocks are easy to miscompare. `MPCC2` and `MPCC3`, and `MPCC_OGAM0` through `MPCC_OGAM3`, intentionally share field layouts. A generated prefix or instance-offset error would look plausible in review but affect only one compositor path.
- Bank selection and current readback must be kept straight. OGAM and gamut remap expose A/B banks and current-mode/current-select fields; using the wrong bank can make a LUT or matrix update appear to succeed while inactive.
- LUT programming has packed, width-sensitive fields. Region offsets, segment counts, start/end slopes, bases, and RGB offsets occupy different widths. Open-coded arithmetic instead of shared field helpers risks truncation or overlap.
- Update-lock and vupdate-lock mistakes can cause visible tearing, partial composition updates, or stale state if writes land outside the intended blanking/update window.
- Reset fields are broad. `MPC_SOFT_RESET` contains per-MPCC, SFR, SFT, and whole-MPC reset bits; accidental writes could disrupt unrelated pipes.
- Power-management fields interact with hardware readiness. Forcing OGAM memory low power or disable state at the wrong time can corrupt LUT access or color processing, especially around suspend/resume, modeset, and runtime power transitions.
- CRC and status fields are diagnostic-sensitive. Incorrect decode can mislead validation by reporting the wrong component, pending state, or CRC result.

## Test Signals

Useful validation signals for code using this chunk include:

- Kernel build coverage for DCN 3.2.1 resource and MPC paths that include `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`.
- Generated-register consistency checks comparing each `*_MASK`/`*__SHIFT` pair against the authoritative register database and against the matching offsets in `dcn_3_2_1_offset.h`.
- Static checks that repeated MPCC and OGAM instances have identical field widths where the hardware intends identical layouts, and that the MPCC/OGAM instance count matches the resource configuration.
- Modeset and plane-composition tests that exercise MPCC top/bottom selection, OPP routing, blend modes, global alpha/gain, background color, and update locks.
- Color-management tests that program OGAM PWL LUTs, switch RAM A/B banks, program gamut remap coefficients, and verify current-mode/current-select readbacks.
- Display CRC tests using MPC CRC control, selection, and result registers to confirm decoded results match expected frames.
- Display writeback tests that exercise `MPC_DWB0_MUX` selection and status readback.
- Runtime power-management, suspend/resume, and hotplug tests that check OGAM memory power fields and verify LUT state survives or is restored as expected.
- Debug traces or register dumps showing sane `MPCC_IDLE`, `MPCC_BUSY`, `MPCC_DISABLED`, pending-status, vupdate-lock, DWB mux status, and OGAM current-state values after programming.

## Research Notes

This is source-tree-aligned chunk research only. The final per-file document should merge this with neighboring chunks of `dcn_3_2_1_sh_mask.h` to describe the entire generated DCN 3.2.1 mask namespace, including the portion of `MPCC1_MPCC_STATUS` before line 15196 and the remainder of `MPCC_OGAM3` plus the following MPC MCM blocks after line 17712.
