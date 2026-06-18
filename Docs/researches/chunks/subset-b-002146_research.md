# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 5118-7579

## Scope

This chunk is a middle slice of AMDGPU's generated DCN 4.1.0 register-offset header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or local executable control flow. Each exported pair follows the generated register contract: `reg<INSTANCE>_<REGISTER>` gives the register offset and `reg<INSTANCE>_<REGISTER>_BASE_IDX` gives the register-base table index used by AMD display register helpers.

The range starts inside the DPP3 color-management block, at the gamma-correction LUT and RAM A/B region descriptors for `CM3`. It then covers the DPP3 top block, four MPCC blend-tree instances, MPC global configuration, four MPCC output-gamma (`MPCC_OGAM`) instances, and most of four MPCC movable color-management (`MPCC_MCM`) instances. It ends inside `MPCC_MCM3`, after the first three registers of the second gamut-remap matrix, so the following chunk owns the tail of `MPCC_MCM3` and the later MPC output CSC blocks.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to bind DCN 4.1.0 display-driver logical register names to ASIC-specific MMIO offsets. Runtime DCN401 code constructs register tables from these constants, then uses common `REG_*` helpers to program display pipe color, blending, timing-independent MPC routing, and diagnostics.

The covered hardware areas are:

- Tail of `dcn_dcec_dpp3_dispdec_cm_dispdec`: DPP3 `CM_GAMCOR` indexed LUT access, RAM A/B PWL region configuration, HDR multiplier, CM memory-power status/control, dealpha, coefficient format, and CM test-debug ports.
- `dcn_dcec_dpp3_dispdec_dpp_top_dispdec`: DPP3 top-level control, soft reset, CRC readback/control, and host-read throttling.
- `dcn_dcec_mpc_mpcc0_dispdec` through `mpcc3`: four MPCC blender slices, each with top/bottom selection, OPP routing, MPCC control/state-machine control, update-lock selection, alpha/multiplier controls, background color, clamping, memory-power control, movable-CM location, and MPCC debug index/data registers.
- `dcn_dcec_mpc_mpc_cfg_dispdec`: global MPC and HUBP routing/configuration registers, including `MPC_CONTROL`, mux mapping, active-size and memory power controls, clock-gating controls, CRC controls, output mux diagnostics, OUT handshake/status, MPCC request/init state, and per-HUBP output mux selectors.
- `dcn_dcec_mpc_mpcc_ogam0_dispdec` through `mpcc_ogam3`: four MPCC output-gamma/color-remap blocks, each with OGAM control, LUT index/data/control, RAM A/B PWL region descriptors, gamut-remap coefficient format/mode, matrix coefficient banks A/B, memory power, and test-debug ports.
- `dcn_dcec_mpc_mpcc_mcm0_dispdec` through `mpcc_mcm3`: four movable color-management blocks, each with shaper LUT control, shaper offset/scale/index/data/write-enable controls, RAM A/B PWL descriptors, 3DLUT mode/read-write/LUT data/control, 1DLUT control/index/data/RAM A/B descriptors, first and second gamut-remap coefficient formats/modes, matrix banks A/B, memory power, and 3DLUT fast-load select/status registers. The `MPCC_MCM3` second-remap list is incomplete in this chunk.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro namespace:

- `regCM3_*` offsets use base index `2`, matching the DPP/CM register-base group for the fourth DPP instance.
- `regDPP_TOP3_*` offsets also use base index `2`, matching DPP3 top-level registers.
- `regMPCC0_*` through `regMPCC3_*`, `regMPC_*`, `regHUBP*_MPC_OUT_MUX`, `regMPCC_OGAM*_*`, and `regMPCC_MCM*_*` use base index `3`, matching the MPC/MPCC register-base group.

The visible macro families are table-driven. Resource headers paste logical names onto these instance names through macros such as `SRI_ARR`, `SRII`, and `SRI`, while field-table macros from the companion `dcn_4_1_0_sh_mask.h` provide masks and shifts for the same register names.

Important register groups in this slice include:

- `regCM3_CM_GAMCOR_LUT_INDEX`, `regCM3_CM_GAMCOR_LUT_DATA`, and `regCM3_CM_GAMCOR_LUT_CONTROL`: indexed DPP3 gamma LUT programming ports.
- `regCM3_CM_GAMCOR_RAMA_*` and `regCM3_CM_GAMCOR_RAMB_*`: DPP3 gamma PWL RAM A/B start, slope, base, end, offset, and region-pair registers.
- `regDPP_TOP3_DPP_CONTROL`, `regDPP_TOP3_DPP_SOFT_RESET`, `regDPP_TOP3_DPP_CRC_*`, and `regDPP_TOP3_HOST_READ_CONTROL`: top-level DPP3 enable/reset/CRC/read controls.
- `regMPCC{0..3}_MPCC_TOP_SEL`, `BOT_SEL`, `OPP_ID`, `CONTROL`, `SM_CONTROL`, `UPDATE_LOCK_SEL`, `ALPHA_*`, `BG_*`, `MEM_PWR_CTRL`, and `MOVABLE_CM_LOCATION_CONTROL`: MPCC blend graph, plane selection, alpha, background, update synchronization, power, and movable color-management placement.
- `regMPC_*`: global MPC mux, clock-gating, CRC, output, memory-power, MPCC request/init, and HUBP routing controls.
- `regMPCC_OGAM{0..3}_MPCC_OGAM_*` and `regMPCC_OGAM{0..3}_MPC_GAMUT_REMAP_*`: output-gamma LUT/PWL and MPCC OGAM gamut-remap controls.
- `regMPCC_MCM{0..3}_MPCC_MCM_SHAPER_*`, `3DLUT_*`, `1DLUT_*`, `FIRST_GAMUT_REMAP_*`, `SECOND_GAMUT_REMAP_*`, `MEM_PWR_CTRL`, and `3DLUT_FAST_LOAD_*`: movable color-management shaper, 3D LUT, post 1D LUT, dual gamut remap, memory power, and fast-load status controls.

## Control Flow

This header range has no local control flow. Runtime behavior is created by consumers that include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`, build register tables, then perform MMIO reads and writes through display register helpers.

A typical DCN401 path is:

1. DCN401 resource construction includes the DCN 4.1.0 generated offset and shift/mask headers.
2. Register-list macros expand logical names into instance-specific macros, for example `SRII(MPCC_MCM_FIRST_GAMUT_REMAP_MODE, MPCC_MCM, inst)` expands to `regMPCC_MCM0_MPCC_MCM_FIRST_GAMUT_REMAP_MODE` for instance 0.
3. The generated offsets are stored in DCN401 register structures such as `dcn401_mpc_registers`, while field shifts/masks are stored in matching shift/mask structures.
4. Runtime code calls helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_GET_3`; those helpers combine the register offset from this header with field masks/shifts from the companion header.
5. Higher-level display code sequences the actual hardware programming around modeset, plane composition, color-management updates, LUT loading, update locks, blanking, memory power, and hardware initialization.

Concrete visible consumers include `display/dc/resource/dcn401/dcn401_resource.h`, which lists DPP `CM_GAMCOR_*` registers and MPC/MPCC register arrays; `display/dc/mpc/dcn401/dcn401_mpc.h`, which defines DCN401 MPC register arrays and field lists for `MPCC_MCM_*` features; `display/dc/mpc/dcn401/dcn401_mpc.c`, which programs 3DLUT fast-load select/status, shaper/3DLUT/1DLUT modes, and MPCC MCM gamut-remap matrices; and `display/dc/hwss/dcn401/dcn401_hwseq.c`, which programs first/second MCM gamut remap and OGAM gamut remap during pipe color setup.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware register state whose lifetime is controlled by display hardware programming, pipe enable/disable, modesets, power transitions, suspend/resume, and GPU reset.

State represented by this chunk includes:

- DPP3 CM gamma state: indexed LUT position/data/control, RAM A/B PWL region descriptors, HDR multiplier, coefficient format, dealpha, and CM memory-power state.
- DPP3 top state: DPP enable/control, soft-reset state, CRC capture/readback state, and host-read control.
- MPCC composition state: top/bottom source selection, OPP assignment, alpha and multiplier controls, blend state-machine control, update-lock binding, background colors, clamp limits, memory-power control, debug index/data, and movable color-management placement.
- MPC global state: mux mappings, active dimensions, stereo mux, global/3D LUT memory power, CRC selection and readback, clock-gating controls, output mux and handshake status, MPCC request/init controls, and HUBP-to-MPC-output routing.
- MPCC OGAM state: per-MPCC output gamma LUTs, RAM A/B PWL descriptors, color-remap matrix banks, mode/current-mode selection, memory power, and debug ports.
- MPCC MCM state: shaper LUTs, 3DLUT contents/mode/read-write selection, 1DLUT contents and bank selection, dual gamut remap matrices, memory-power controls, and 3DLUT fast-load select/status.

Indexed and banked LUT registers are particularly stateful. The `*_LUT_INDEX`, `*_LUT_DATA`, read/write control, bank-select, and RAM A/B descriptor registers together determine which table entries are modified and which table bank is active. Bad ordering or wrong offsets can leave a valid-looking but visually incorrect LUT bank programmed.

Many state bits are live hardware controls rather than passive descriptors. MPCC muxing, OPP IDs, movable-CM placement, memory-power controls, and gamut-remap mode selections directly affect scanout composition or block availability until reprogrammed or reset.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`, which supplies the field masks and shifts for these offsets. The offset and shift/mask headers must be paired for DCN 4.1.0/DCN401; nearby DCN 3.x, DCN 4.2, or other generated headers may share names but are not interchangeable.

Important integration points are:

- `display/dc/resource/dcn401/dcn401_resource.h`: declares the runtime register lists that pull in `CM_GAMCOR_*`, MPCC, MPC, OGAM, and MCM register offsets from this generated header.
- `display/dc/resource/dcn401/dcn401_resource.c`: constructs the DCN401 resource pool and binds register tables used by display pipes and MPC.
- `display/dc/dpp/dcn401/dcn401_dpp.h`: maps DPP color-management fields such as `CM_GAMCOR_LUT_*` onto generated DCN 4.1.0 names.
- `display/dc/dpp/dcn30/dcn30_dpp_cm.c`: common DPP color-management code programs `CM_GAMCOR_LUT_INDEX`, `CM_GAMCOR_LUT_DATA`, and `CM_GAMCOR_LUT_CONTROL`; for DCN401, the register table resolves those logical operations to offsets like the DPP3 `CM3` macros in this chunk.
- `display/dc/mpc/dcn401/dcn401_mpc.h` and `display/dc/mpc/dcn401/dcn401_mpc.c`: define and use the DCN401 MPC register arrays for MPCC MCM gamut remap, LUT modes, 3DLUT fast-load select/status, and banked LUT controls.
- `display/dc/hwss/dcn401/dcn401_hwseq.c`: sequences pipe-level gamut-remap setup by calling MPC functions for `MPCC_MCM_FIRST_GAMUT_REMAP`, `MPCC_MCM_SECOND_GAMUT_REMAP`, and `MPCC_OGAM_GAMUT_REMAP`.
- `display/dmub/src/dmub_dcn401.c` and `display/dmub/src/dmub_dcn401.h`: include the same generated DCN 4.1.0 headers for DMUB register programming, though this particular chunk is mostly display-pipe/MPC color and routing rather than mailbox registers.

The chunk also depends on AMD display common infrastructure: `reg_helper.h` for MMIO helper macros, `dcn10_cm_common.h`/`dcn30_cm_common.h` color-matrix and LUT helpers, DC plane/stream color state, and hardware sequencing code that decides when it is safe to update color or composition registers.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong offset or base index compiles cleanly but can target the wrong register, wrong instance, or wrong base aperture. Symptoms may look like sequencing, color, or power bugs rather than a generated-header issue.

Chunk-boundary risk is high here. The chunk starts after the beginning of the `CM3` block, so whole-DPP3 CM conclusions require the previous chunk. It also ends in the middle of `MPCC_MCM3` second gamut-remap registers, so whole-MCM3 and MPC-output conclusions require the following chunk.

Instance alignment is critical. `CM3`/`DPP_TOP3` offsets use base index `2`, while MPC/MPCC/OGAM/MCM offsets use base index `3`. Mixing the base index or copying offsets across instances can direct a register helper to a different block even when the logical register name looks correct.

Color-management registers are precision-sensitive. Gamma PWL regions, shaper LUTs, 1DLUTs, 3DLUTs, HDR multiplier, coefficient-format registers, and dual gamut-remap matrices directly affect output color. Errors can cause color shifts, banding, broken HDR/gamut transforms, or LUT updates that appear to succeed but select the wrong bank.

Composition and routing fields can blank or corrupt scanout. MPCC top/bottom selection, OPP ID, alpha/multiplier controls, MPC mux controls, HUBP output mux controls, and movable-CM location must match the pipe topology chosen by resource and hardware-sequencing code.

Power controls are hazardous. `CM_MEM_PWR_CTRL`, `MPCC_MEM_PWR_CTRL`, `MPC_*MEM_PWR*`, `MPCC_OGAM_MEM_PWR_CTRL`, and `MPCC_MCM_MEM_PWR_CTRL` interact with low-power modes and active display blocks. Incorrect offsets can power down memories while active, prevent blocks from idling, or produce stuck status bits.

Fast-load and status registers can hide data integrity problems. `MPCC_MCM_3DLUT_FAST_LOAD_SELECT` chooses a HUBP source for fast loading, while status reports done/underflow conditions. Wrong offsets or masks can report success while the intended 3DLUT bank was not populated correctly.

Debug and CRC registers are diagnostic-sensitive. Bad constants for CRC, OUT mux, handshake, init status, and test-debug registers may not break normal display output but can mislead validation, hardware bring-up, and failure triage.

## Test Signals

Useful validation is generated-header, build, and hardware-behavior oriented:

- Compile coverage for DCN401 resource construction, DPP color management, MPC/MPCC code, hardware sequencing, and DMUB users that include the DCN 4.1.0 generated headers.
- Generated-register consistency checks that every register referenced by `dcn401_resource.h` and `dcn401_mpc.h` exists in `dcn_4_1_0_offset.h`, has the expected `*_BASE_IDX`, and has matching fields in `dcn_4_1_0_sh_mask.h`.
- Cross-generation or database diffing against AMD's authoritative DCN 4.1.0 register database, with expected differences from DCN 3.2/3.5 and DCN 4.2 reviewed explicitly.
- DPP3 tests for gamma LUT programming/readback, PWL RAM A/B selection, HDR multiplier, dealpha, coefficient format, CM memory power, DPP soft reset, CRC capture, and host reads.
- MPCC composition tests for multi-plane blending, top/bottom tree selection, OPP routing, per-plane alpha, global alpha/multipliers, background color, update locks, clamp behavior, and movable-CM placement.
- MPC routing tests for HUBP-to-MPC output muxing, MPCC request/init state, active-size programming, output mux status, stereo mux, memory power, and CRC paths.
- OGAM tests for output gamma LUT loading, RAM A/B bank switching, gamut remap banks A/B, mode/current-mode readback, memory power, and debug-port accessibility across MPCC0-3.
- MCM tests for shaper LUT, 3DLUT 9x9x9/17x17x17 modes, 1DLUT, first and second gamut remap, fast-load select/status, memory low-power transitions, bank switching, and restore after suspend/resume or GPU reset.
- End-to-end visual tests for SDR/HDR, ICC/gamut remap, color temperature matrices, plane color transforms, scaled/rotated planes, multi-plane overlays, cursor interactions, and hotplug/modeset transitions on DCN401 hardware.

Regression symptoms from bad constants include blank output, wrong plane routing, blend errors, incorrect alpha, visible color shifts, banding, HDR or gamut failures, stuck update locks, failed memory-power transitions, incorrect CRC/readback/debug data, false 3DLUT fast-load success, or failures isolated to the fourth DPP/MPCC instances.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dcn_4_1_0_offset.h`. The previous chunk owns the start of DPP3 `CM3` and DSCL3 context before line 5118. The following chunk owns the rest of `MPCC_MCM3` and later MPC output CSC/register blocks after line 7579. The merge/reconciliation lane should treat this document as the DPP3 CM tail plus DPP3 top, MPCC0-3, MPC config, MPCC OGAM0-3, and most of MPCC MCM0-3 for the full DCN 4.1.0 offset contract.
