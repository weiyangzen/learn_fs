# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c

## Purpose

`dcn401_resource.c` builds the resource pool for DCN 4.0.1/DCN 4.1-class AMD display hardware. Compared with the DCN35-derived files, it uses DCN401-native HUBBUB, HUBP, DPP, MPC, DSC, DCCG, timing generator, stream encoder, and link encoder constructors, supports pipe harvesting through fuses, exposes mcache/SubVP/MALL/DML2.1-specific hooks, and configures newer display capabilities such as FAMS2, sharpener support, MALL cache allocation, and DC-power DML2 options.

## Important APIs, Types, And Functions

- `enum dcn401_clk_src_array_id`: four combo-PHY PLL clock source indices.
- Static register tables for DCN401 blocks: `dcn401_dpp_registers`, `dcn401_mpc_registers`, `dcn401_dsc_registers`, DCN401 HUBP/HUBBUB/DCCG/OPTC macros, four HPO DP link encoders, and DCN4.1 offsets.
- `res_cap_dcn4_01`: four timing generators/OPPs/planes/DSCs, four audio/stream encoders/HPO stream encoders/HPO link encoders/DDC engines, one DWB, 16 VMIDs, and four MPC 3D LUTs.
- `debug_defaults_drv`: enables DML2 and DML2.1, FAMS 2.1 offload/stall recovery, cursor cache behavior, software cursor fallback policy, SubVP-related defaults, DCC meta propagation delay, and sharpness/cositing defaults.
- Factory helpers: `dcn401_aux_engine_create`, `dcn401_i2c_hw_create`, `dcn401_clock_source_create`, `dcn401_hubbub_create`, `dcn401_dio_create`, `dcn401_hubp_create`, `dcn401_dpp_create`, `dcn401_mpc_create`, `dcn401_opp_create`, `dcn401_timing_generator_create`, `dcn401_link_encoder_create`, audio/VPG/AFMT/APG and stream/HPO encoder creators, `dcn401_hwseq_create`, DWB/MMHUBBUB creators, and `dcn401_dsc_create`.
- Exported or function-table APIs: `dcn401_patch_unknown_plane_state`, `dcn401_validate_bandwidth`, `dcn401_prepare_mcache_programming`, `dcn401_get_default_tiling_info`, `dcn401_get_vstartup_for_pipe`, and `dcn401_get_power_profile`.
- `dcn401_calc_num_avail_chans_for_mall()`: rounds memory channels down to a power-of-two/even value and clamps per ASIC revision for MALL allocation.
- `dcn401_build_pipe_pix_clk_params()`: computes pixel clock params, encoder object ID, TMDS/DP pixel-per-cycle policy, DSC padding clock override, YCbCr420/3D clock transforms, and PLL dividers.
- `dcn401_res_pool_funcs`: DCN401 operation table, including SubVP phantom pipe and MALL/mcache hooks.
- `read_pipe_fuses()` and `dcn401_resource_construct()`: build the pool while skipping harvested pipe instances.

## Control Flow

`dcn401_create_resource_pool()` allocates the wrapper and calls `dcn401_resource_construct()`. Construction initializes register tables, sets `ctx->dc_bios->regs`, reads pipe fuses from `CC_DC_PIPE_DIS`, computes the active pipe count, asserts if pipe 0 or the full DCN block is disabled, and then sets resource counts to the number of usable pipes.

It programs broad `dc->caps` and `dc->config` state: I2C speeds, 64-pixel cursor limits/cache sizing, MALL sizing, SubVP timing margins, color pipeline caps, 8K DCC width limit for selected ASICs, SPL/EASF sharpener preferences, sharpness ranges, DC mode clock limiting, windowed MPO ODM, pipe unlock ordering, LTTPR awareness, and production debug defaults. It initializes the VM helper and then creates resources in dependency order: PLLs/DP DTO, DCCG, IRQ service, HUBBUB/VMIDs, DIO, per-live-pipe HUBP/DPP/OPP/TG/ABM using hardware instance `i` and compact resource index `j`, PSR, MPC, DSCs, DWB, MMHUBBUB, AUX/I2C, shared `resource_construct()`, HW sequencer init functions, plane caps, cap functions, optional OEM I2C DDC service, SDPIF request limit, DML2/DML2.1 options, SubVP pstate callbacks, MALL config, DET settings, sharpener capability, and DC-power DML options.

`dcn401_validate_bandwidth()` first clears stale stream cursor SubVP limits when legal. It runs DML2 validation when enabled. During programming validation, if SubVP is in use, it checks active non-phantom streams with enabled hardware cursors; if cursor attributes cannot be supported with SubVP, it marks a stream cursor SubVP limit and retries DML2 validation with SubVP disabled for that cursor case.

`dcn401_prepare_mcache_programming()` calls into DML2.1 mcache preparation for the correct AC/DC DML2 context. `dcn401_update_bw_bounding_box()` recomputes MALL/CAB size from memory channels and reinitializes current AC/DC DML2 contexts. `dcn401_resource_destruct()` frees all owned resources, including an optional OEM DDC service.

## State And Persistence Behavior

State is held in memory in `dc`, `dc_state`, and `resource_pool` objects. The file mutates caps/config/debug settings, active pipe counts based on fuse state, MALL sizing, DML2 and DC-power DML2 options, DML2 SubVP/MALL callback tables, optional OEM DDC state, and stream-level cursor SubVP limit flags during validation. It also writes `plane_state->tiling_info` defaults for unknown planes and reads `pipe_ctx->global_sync.dcn4x.vstartup_lines` for VStartup reporting.

No persistent storage is written. Hardware persistence comes later through the constructed objects' MMIO programming.

## Dependencies And Integration Points

This file depends on DCN401 block implementations, DCN4.1 offset/mask headers, NBIF offsets, shared resource code, `dml2_wrapper`, `dc_state_priv`, link encoder configuration, DMUB ABM/PSR, DCE AUX/I2C/audio/clock source helpers, and DCN32 helpers for SubVP, MALL way calculation, phantom pipes, panel control, and 3D LUT management.

Important integration points include `dcn401_hw_sequencer_init_functions(dc)`, `resource_construct()`, `dml2_validate()`, `dml2_prepare_mcache_programming()`, DML2 reinit for AC/DC contexts, `dc_state_*subvp*` helpers, `dc_stream_check_cursor_attributes()`, `link_enc_cfg_get_link_enc()`, and optional `dc->link_srv->create_ddc_service()` for OEM I2C devices.

## Risks And Edge Cases

- Pipe harvesting compacts resource-pool indices while preserving hardware instance IDs. Any code assuming resource index equals register instance can break on fused parts.
- `dcn401_link_encoder_create()` allocates before validating HPD source and does not check transmitter/channel bounds locally.
- `dcn401_stream_encoder_create()` accepts `eng_id <= ENGINE_ID_DIGF` but only four stream encoder register entries are initialized; the later `eng_id >= ARRAY_SIZE(stream_enc_regs)` guard prevents use but after allocation/subobject creation.
- `dcn401_calc_num_avail_chans_for_mall()` can return zero for `num_chans == 1` because it clears odd values; callers must tolerate no CAB/MALL allocation.
- DSC max image width is hard-coded to 5760 with a commented 6016 alternative.
- Bandwidth validation mutates cursor SubVP limit state and retries; callers must handle `DC_FAIL_HW_CURSOR_SUPPORT`/retry semantics correctly.
- `dcn401_get_power_profile()` assumes `context->clk_mgr` and memory-clock tables are valid and uses simple threshold counting.
- Optional OEM DDC service ownership differs from ordinary DDC arrays and must be destroyed through `link_srv`.

## Test Signals

- Compile tests should cover DCN401 register-list macros, struct-field drift, and exported header signatures.
- Resource-pool tests should run with no fuses and simulated fused pipes to verify compact pipe counts and hardware instance mapping.
- Failure-injection tests should cover every constructor branch and optional OEM DDC cleanup.
- Bandwidth tests should cover DML2 AC/DC contexts, SubVP active/non-active streams, phantom streams, hardware cursor rejection, retry with cursor SubVP limits, and DML2.1 mcache preparation.
- Runtime display tests should exercise HPO DP/HDMI, DSC at width limits, FAMS2/offload flip, MALL/SubVP, DWB, PSR, sharpener/SPL paths, four MPC 3D LUTs, pipe harvesting, and cursor cache sizing.
