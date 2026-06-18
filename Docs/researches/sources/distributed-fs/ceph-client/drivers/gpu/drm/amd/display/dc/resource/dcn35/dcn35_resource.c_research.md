# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c

## Purpose
This file builds the DCN 3.5 Display Core resource pool. It is the ASIC-specific factory for newer DCN35 blocks, adding DML2-first bandwidth validation, Replay support, power-gating control, fine-grain clock-gating defaults, DPIA preferences, DCN35 register maps, and updated block constructors while still reusing large pieces of DCN31/DCN32/DCN20 infrastructure.

## Important APIs, Types, And Functions
- `dcn35_create_resource_pool` allocates `struct dcn35_resource_pool` and returns the embedded generic pool after construction.
- `dcn35_resource_construct` initializes register tables, capabilities, debug defaults, hardware objects, DML/DML2 options, and sequencer state.
- Factory helpers create DPP/OPP/AUX/I2C/MPC/DIO/HUBBUB/HUBP/TG/link encoders/minimal link encoders/panel control/audio/VPG/AFMT/APG/stream encoders/HPO DP encoders/HWSEQ/DWB/MMHUBBUB/DSC/clock sources.
- `dcn35_validate_bandwidth` calls `dml2_validate`, then decides z-state support when validation includes programming.
- `dcn35_patch_unknown_plane_state` sets unknown plane tiling to `DcGfxVersion9` before delegating to DCN20 patching.
- `dcn35_update_bw_bounding_box` updates DCN35 bandwidth bounding boxes through FPU code.
- `dcn35_res_pool_funcs` exposes DCN35 behavior to generic Display Core, including link encoder assignment/unassignment, DML2 validation, panel defaults, DPIA preferred encoder selection, DET size callback, and encoder-switch state update.

## Control Flow
Construction populates BIOS/clock/ABM/DCCG register tables, enables 4:1 MPC by default, assigns DCN35 resource caps, and fills broad capability/config/debug defaults including APU, zstate, IPS, seamless ODM, host-router/DPIA counts, root clock optimization, power-gating policy, and fine-grain clock gating. It creates five clock-source entries plus DP DTO, initializes a temporary DML1 instance for compatibility, creates DCCG and PG control, IRQ service, HUBBUB, DIO, all HUBPs/DPPs/OPPs/TGs, PSR, Replay, ABMs, MPC, DSCs, DWB/MMHUBBUB, AUX/I2C, and then uses `resource_construct` for audio and encoder families. It sets USB4 DPIA count unless disabled by debug, constructs the DCN35 HW sequencer, publishes plane caps, and configures DML2 options. Any allocation or constructor failure jumps to cleanup via `dcn35_resource_destruct`.

## State And Persistence
Persistent state includes the `resource_pool` object arrays, PG control, PSR/Replay, DCCG, DIO, DML/DML2 option fields, `dc->caps`, `dc->config`, and `dc->debug`. Static register tables are initialized for the active context and referenced by constructed blocks. Debug defaults deliberately keep several power gates disabled or ignored while enabling fine-grain clock-gating masks.

## Dependencies And Integration Points
The file depends on DCN35 generated offset/mask headers, MMHUB/NBIO headers, DML2 wrapper, DCN35 FPU, DCN35 HUBBUB/HUBP/DPP/OPTC/OPP/DSC/DCCG/PG/DWB/MMHUBBUB/HWSEQ blocks, IRQ service DCN35, DMUB ABM/PSR/Replay, link encoder configuration, and shared DCN32 register macros. It integrates with Display Core resource initialization, link assignment, DML2 validation, HW sequencing, BIOS LTTPR queries, USB4 DPIA routing, PSR/Replay panel features, and writeback.

## Risks And Edge Cases
The constructor has many hard-coded caps and debug policies, so ASIC characterization changes can cause regressions without compiler signals. `res_cap_dcn35.num_pll` is four while the clock-source array creates five entries plus DP DTO; this may be intentional naming but is a review point. `dcn31_link_enc_create_minimal` uses an engine-id bounds check that should be validated around off-by-one behavior. Destruction must free newer Replay and PG control objects as well as inherited nested encoder sub-blocks. DML2 validation requires a valid `context->bw_ctx.dml2` or DC-power variant; callers must initialize those contexts before validation. Register table correctness is critical because DCN35 adds new clock-gating and power-domain registers.

## Test Signals
Run probe and teardown on DCN35 hardware or emulation, DML2 bandwidth validation for AC/DC power sources, zstate/IPS transitions, PSR and Replay enablement, USB4 DPIA routing with preferred DIGC/DIGD encoders, HPO DP and legacy link encoders, DSC and ODM modes, fine-grain clock gating toggles, DWB/MMHUBBUB writeback, AUX/I2C, panel default propagation, unknown-plane patching, and failure injection across all factory helpers.
