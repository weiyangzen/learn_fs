# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c

## Purpose

`dcn21_resource.c` implements the DCN 2.1 resource pool for Renoir-class APU display hardware. It specializes DCN20 resource behavior for DCN21 register layouts, fused pipe counts, RN PP/SMU integration, DMUB/DMCU ABM/PSR selection, DCN21 DML pipe population, and p-state-aware bandwidth validation.

## Important APIs, Types, And Functions

- `dcn21_create_resource_pool()` and `dcn21_resource_construct()` allocate and initialize the DCN21 pool.
- `dcn21_resource_destruct()` and `dcn21_destroy_resource_pool()` free all pool-owned objects.
- `dcn21_fast_validate_bw()` is the generation-specific fast bandwidth path. It tries self-refresh plus mclk switch first, may fall back to self-refresh-only behavior, applies DCN20 split flags, rejects unsupported MPO+ODM cases, mutates pipe topology, and validates DSC.
- `dcn21_validate_bandwidth()` wraps the FPU validation function and maps failure to `DC_NOT_SUPPORTED`.
- Factories create DCN21 clock sources, DIO, IPP/DPP/HUBP/HUBBUB/OPP/TG/MPC/DSC, PP/SMU funcs, stream/link encoders, panel control, audio, AUX/I2C, and hwseq.
- `read_pipe_fuses()` reads `CC_DC_PIPE_DIS` and constrains active pipe instances.
- `dcn21_patch_unknown_plane_state()` enables DCC by default when `disable_dcc == DCC_ENABLE`, aligns metadata pitch, and delegates swizzle selection to DCN20.
- `dcn21_update_bw_bounding_box()` wraps the DCN21 FPU bounding-box update.
- `dcn21_get_panel_config_defaults()` returns PSR/ILR defaults.

## Control Flow

Construction sets BIOS registers, installs `dcn21_res_pool_funcs`, starts from the RN resource cap, reads pipe fuses, and initializes DC caps for an APU with up to four active pipes and five DDC/stream encoder slots. It configures debug defaults, panel defaults, color capabilities, VM helper state, five clock sources, DP DTO source, DCCG, DMCU or DMUB PSR/ABM depending on `dc->config.disable_dmcu`, RN PP/SMU functions, fused DPP/OTG counts in `dcn2_1_ip`, DML instance, IRQ service, and active HUBP/IPP/DPP/OPP/TG objects while skipping fused-off hardware instances. It then creates DDC AUX/I2C engines, MPC, HUBBUB with VMIDs, DIO, DSCs, DWB/MCIF_WB via DCN20 helpers, common resources, and the DCN21 hw sequencer.

Bandwidth validation canonicalizes previous splits with `dcn20_merge_pipes_for_validate()`, populates DML pipes through `dcn21_populate_dml_pipes_from_context()`, prefers p-state support by trying `dm_allow_self_refresh_and_mclk_switch`, optionally falls back to `dm_allow_self_refresh`, applies split/merge policy through DCN20 logic, rejects windowed MPO with ODM, creates ODM or MPC secondary pipes as needed, rebuilds mapped stream resources for ODM, rebuilds scaling for MPC, validates DSC, and returns selected voltage level plus split provenance.

## State And Persistence Behavior

The file stores no persistent data outside normal kernel memory. It mutates DC caps/debug/check config, panel config defaults, DML state, PP/SMU function tables, fused active pipe count, resource pool arrays, `resource_context` pipe graph, DSC acquisition state, DCC defaults on unknown planes, and bandwidth bounding-box values.

Pipe-fuse handling is a key state transformation: physical register instances may be skipped while logical pool arrays are densely packed, and `pipe_count`, `mpcc_count`, and timing-generator count are reduced to active pipes.

## Dependencies And Integration Points

The file depends on Renoir/DCN2.1 register headers, DCN20 common helpers, DCN21 DML FPU functions, DCN21 hardware constructors, DMUB PSR/ABM, DCE DMCU/ABM/AUX/I2C/audio helpers, IRQ service, PP/SMU RN callbacks, VM helper, and generic resource management. Its resource function table is consumed by common DC and supplies validation, DML population, stream add/remove, pipe acquisition/release, writeback population, MCIF arbitration, panel defaults, tiling defaults, and bounding-box update hooks.

## Risks And Edge Cases

- Fused pipe remapping can desynchronize logical pipe indices from hardware instances if any constructor or register array assumes dense physical ids.
- The DMCU vs DMUB path changes ABM/PSR object types and destructor choice; mismatched config can free through the wrong helper.
- `dcn21_fast_validate_bw()` inherits DCN20 split complexity and adds p-state policy. Borderline modes can pass only after fallback to self-refresh-only.
- MPO plus ODM is limited to full-screen MPO unless newer config explicitly enables windowed MPO ODM.
- Default DCC enablement in `dcn21_patch_unknown_plane_state()` depends on meta pitch alignment and may expose unsupported surface cases if callers did not initialize plane state fully.
- PP/SMU version mismatch zeroes the function table; callers must tolerate non-NULL but inert SMU callbacks.

## Test Signals

Validation should cover all pipe-fuse recipes, pool construction/destruction, DMCU enabled/disabled modes, DMUB PSR/ABM creation, RN SMU present/missing, DML bounding-box updates, self-refresh plus mclk-switch validation, fallback validation, ODM/MPC splits, DSC validation/exhaustion, DCC-default unknown planes, panel defaults, DWB/MCIF_WB creation, and multi-plane/full-screen MPO restrictions. Runtime signals include `DC_NOT_SUPPORTED`, DML validation status, pipe fuse logs/assertions, DSC validation failure, allocation errors, and underflow during split transitions.
