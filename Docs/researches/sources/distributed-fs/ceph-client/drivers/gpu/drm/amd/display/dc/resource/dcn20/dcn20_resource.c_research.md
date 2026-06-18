# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c

## Purpose

`dcn20_resource.c` is the DCN 2.0 resource-pool implementation for AMD Display Core. It binds Navi10/Navi12/Navi14 register lists, hardware block constructors, capability tables, Display Mode Library setup, bandwidth validation, pipe topology mutation, DSC allocation, writeback arbitration, and resource teardown behind `struct resource_funcs`.

The file is the generation-specific bridge between generic DC state management and concrete DCN2 hardware objects: HUBP, IPP, DPP, OPP, OPTC/TG, MPC, HUBBUB, DIO, link/stream encoders, DCCG, DMCU, ABM, DSC, DWB, MCIF_WB, VMID, AUX/I2C, audio, clock sources, IRQ service, and PP/SMU clock/watermark integration.

## Important APIs, Types, And Functions

- `dcn20_create_resource_pool()` allocates `struct dcn20_resource_pool`, calls `dcn20_resource_construct()`, and returns the embedded `resource_pool`.
- `dcn20_resource_construct()` is the main bring-up path. It selects Navi10 or Navi14 resource caps and DML bounding boxes, initializes DC caps/debug/workarounds, creates all hardware objects, initializes DML and watermark ranges, installs IRQ and hwseq support, and calls common `resource_construct()`.
- `dcn20_resource_destruct()` and `dcn20_destroy_resource_pool()` free all owned hardware objects and clear pool pointers.
- Hardware factory functions include `dcn20_dpp_create()`, `dcn20_ipp_create()`, `dcn20_opp_create()`, `dcn20_hubp_create()`, `dcn20_hubbub_create()`, `dcn20_mpc_create()`, `dcn20_timing_generator_create()`, `dcn20_dsc_create()`, `dcn20_dwbc_create()`, `dcn20_mmhubbub_create()`, `dcn20_link_encoder_create()`, `dcn20_stream_encoder_create()`, `dcn20_aux_engine_create()`, `dcn20_i2c_hw_create()`, and clock-source helpers.
- Stream/resource APIs include `dcn20_add_stream_to_ctx()`, `dcn20_remove_stream_from_ctx()`, `dcn20_build_mapped_resource()`, `dcn20_build_pipe_pix_clk_params()`, `dcn20_acquire_free_pipe_for_layer()`, and `dcn20_release_pipe()`.
- DSC APIs include `dcn20_acquire_dsc()`, `dcn20_release_dsc()`, `dcn20_add_dsc_to_stream_resource()`, and `dcn20_validate_dsc()`.
- Bandwidth/topology APIs include `dcn20_validate_bandwidth()`, `dcn20_fast_validate_bw()`, `dcn20_merge_pipes_for_validate()`, `dcn20_validate_apply_pipe_split_flags()`, `dcn20_split_stream_for_odm()`, `dcn20_split_stream_for_mpc()`, and `dcn20_find_secondary_pipe()`.
- Writeback support is handled by `dcn20_set_mcif_arb_params()` and `dcn20_calc_max_scaled_time()`.
- Capability hooks include `dcn20_get_dcc_compression_cap()` and `dcn20_patch_unknown_plane_state()`.

## Control Flow

Construction starts by assigning BIOS register access and `dcn20_res_pool_funcs`, selecting `res_cap_nv10`/`res_cap_nv14`, setting DC capability flags, initializing color capabilities, workarounds, VM helper state, and creating clock sources plus the DP DTO clock source. It then creates DCCG, DMCU, ABM, PP/SMU, initializes SoC/IP bounding boxes, calls `dml_init_instance()`, optionally publishes watermark ranges to SMU, creates IRQ service, per-pipe HUBP/IPP/DPP blocks, DDC AUX/I2C engines, OPPs, timing generators, MPC, HUBBUB, DIO, DSC blocks, DWB/MCIF_WB blocks, common resources through `resource_construct()`, and finally the DCN20 hardware sequencer. Any failed allocation jumps to `create_fail`, which destructs partially created state.

Stream addition maps pool resources, maps PHY clock resources, optionally acquires a DSC when stream timing requests DSC, and builds mapped hardware parameters. Pixel-clock parameter construction accounts for ODM pipe count, two-pixels-per-container timings, DP pixel-rate divisor policy, frame-packing 3D, color depth, pixel encoding, signal type, controller id, and link encoder assignment.

Bandwidth validation allocates per-pipe DML input arrays and enters an FPU-protected DML pass. `dcn20_fast_validate_bw()` first merges previous ODM/MPC splits back to canonical pipes, populates DML pipes, asks DML for a voltage level, applies split policy, mutates the `dc_state` pipe graph for ODM/MPC splits, rebuilds scaling, and validates DSC configuration. Split policy considers debug flags, multi-display avoidance, tiny plane dimensions, border timings, plane pressure, DML `NoOfDPP`, forced ODM, 4:2:0 very-wide timing, existing MPC/ODM slice count, and DPP clock adjustment.

`dcn20_merge_pipes_for_validate()` clears previous ODM chains and MPC bottom pipes, releases DSCs from removed ODM pipes, clears `plane_res` and `stream_res`, and rebuilds scaling on surviving primary pipes. `dcn20_split_stream_for_odm()` copies a primary pipe into a free pipe, wires `next_odm_pipe`/`prev_odm_pipe` and vertical layer relationships, assigns per-pipe resources and OPP/DSC, and rebuilds scaling. `dcn20_split_stream_for_mpc()` similarly copies the pipe and wires `top_pipe`/`bottom_pipe` for DPP/MPC split.

## State And Persistence Behavior

The file has no on-disk persistence. It owns in-memory DC resource state for the lifetime of the resource pool and mutates `dc`, `dc_state`, `resource_context`, `pipe_ctx`, `dc_stream_state`, `bw_ctx`, and pool-owned hardware object pointers.

Persistent runtime effects include DC caps/debug defaults, DML SoC/IP bounding-box state, SMU watermark ranges, resource acquisition bitmaps such as `is_dsc_acquired`, pipe graph pointers (`top_pipe`, `bottom_pipe`, `prev_odm_pipe`, `next_odm_pipe`), stream/plane resource assignments, DSC assignments, writeback MCIF arbitration parameters, and default tiling/DCC fields for unknown plane state. Teardown must mirror construction because partially initialized pools are destructed through the same path.

## Dependencies And Integration Points

The file depends on generic DC resource helpers, DML/FPU helpers, Navi register offset/mask headers, PP/SMU callbacks, BIOS tables, link service, IRQ services, VM helper, DCE/DCN hardware constructors, and kernel allocation/free primitives. `dcn20_res_pool_funcs` integrates with the common resource manager by supplying validation, stream add/remove, pipe acquisition/release, DML population, writeback population, MCIF arbitration, tiling defaults, and DCC capability callbacks.

It is reused by later generations: DCN201, DCN21, and DCN30 call several DCN20 helpers for stream management, pipe merging/splitting policy, DSC handling, bandwidth validation, writeback or common DML population, and unknown-plane patching.

## Risks And Edge Cases

- Construction has many dependent allocations; missing cleanup for one block can leak or leave stale pool pointers during `create_fail`.
- Pipe topology mutation is pointer-heavy. Incorrect ODM/MPC chain updates can corrupt stream ownership, cause underflow, or release the wrong DSC.
- `dcn20_validate_apply_pipe_split_flags()` mixes policy, DML outputs, debug overrides, workarounds, and clock adjustment; regressions often appear only for specific multi-plane, small-plane, border, 3D, or 4:2:0 modes.
- DSC allocation prefers one-to-one mapping when possible and previous-state DSC reuse otherwise. Count mismatches can fail late in validation or avoid needed reprogramming.
- FPU helpers must stay inside `DC_FP_START()`/`DC_FP_END()` regions in kernel context.
- `dcn20_pp_smu_create()` zeroes the allocated object when the PP/SMU version is not Navi; callers must tolerate a non-NULL but functionally empty SMU table.
- Global/static bounding boxes are patched using ASIC revision and SMU data; accidental reuse across revisions can change mode validation.
- Writeback arbitration assumes bounded `MAX_DWB_PIPES` and a shared watermark set; unsupported formats or zero pixel clocks can produce invalid timing.

## Test Signals

Build coverage should catch register-list, constructor, vtable, and prototype drift. Functional validation should cover Navi10, Navi12, and Navi14 pool construction, create-failure cleanup, stream add/remove with and without DSC, DSC exhaustion/reuse, ODM split, MPC split, split merge, MPO plus ODM rejection, forced split/debug policies, tiny-plane avoidance, 4:2:0 wide modes, border timing avoidance, DCC cap queries, unknown tiling defaults, writeback MCIF arbitration, and SMU watermark/bounding-box updates. Runtime signals include `DC_FAIL_BANDWIDTH_VALIDATE`, `DML_FAIL_DSC_VALIDATION_FAILURE`, DML validation status, allocation error logs, assertions around pipe availability/DSC, and display underflow or TDR during topology transitions.
