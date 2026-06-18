# Research: subset-b-001455

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.h

## Purpose

`dcn20_resource.h` declares the public DCN 2.0 resource-pool interface and reusable helper APIs shared by later DCN resource implementations. It exposes the `dcn20_resource_pool` wrapper, DCN2.0 SoC/IP bounding-box globals, resource-pool construction, hardware block factories, stream/resource operations, bandwidth validation, pipe split/merge helpers, DSC management, writeback arbitration, and unknown-plane patching.

## Important APIs, Types, And Functions

- `TO_DCN20_RES_POOL()` casts a generic `resource_pool` pointer to the DCN20 pool container.
- `struct dcn20_resource_pool` embeds `struct resource_pool base`.
- Extern bounding boxes and IP params: `dcn2_0_ip`, `dcn2_0_nv14_ip`, `dcn2_0_soc`, `dcn2_0_nv14_soc`, and `dcn2_0_nv12_soc`.
- Construction/factory declarations cover resource pool, link/stream encoder, hwseq, DPP/IPP/OPP/HUBP/TG/MPC/HUBBUB/AUX/I2C/DSC/DWB/MCIF_WB, and clock-source destruction.
- Resource-management declarations cover acquiring/releasing pipes and DSCs, adding/removing streams, adding DSC resources, building mapped resources, building pixel-clock parameters, validating bandwidth and DSC, fast bandwidth validation, applying split flags, ODM/MPC split helpers, pipe merge, DCC cap query, writeback arbitration, and unknown-plane patching.

## Control Flow

The header has no runtime control flow. It lets the generic DC resource manager and sibling generation files call the DCN20 implementation. Typical use starts with `dcn20_create_resource_pool()`, then the returned pool's `resource_funcs` dispatches to the declared functions as streams and planes are validated, mapped, split, programmed, or removed.

## State And Persistence Behavior

The header stores no state. Its declarations are for functions that mutate caller-owned `dc`, `dc_state`, `resource_context`, `pipe_ctx`, stream, plane, and pool state. The extern DML bounding-box objects are process-global kernel data defined elsewhere and patched by implementation code during initialization or bandwidth updates.

## Dependencies And Integration Points

The header includes `core_types.h` and `dml/dcn20/dcn20_fpu.h`, so it exposes DC core types plus DML/FPU-related pipe parameter types. It is included by `dcn20_resource.c` and by later generation files such as DCN201, DCN21, and DCN30 that reuse DCN20 helpers for validation, stream mapping, DSC, writeback, and pipe topology operations.

## Risks And Edge Cases

- This is a broad internal API. Signature drift can break several generations, not just DCN20.
- Exposing FPU/DML declarations through the header couples non-FPU resource code to FPU wrapper discipline in implementations.
- The helper names do not all encode their mutation scope; callers must know which functions clear or rebuild pipe topology and which require acquired resources.
- Extern bounding boxes are mutable shared generation data; consumers must avoid assuming they are immutable constants.

## Test Signals

Kernel builds catch missing prototypes, include-order problems, and type drift. Cross-generation compile coverage is especially important because DCN201/DCN21/DCN30 call these APIs. Runtime validation should exercise all vtable paths declared here through resource-pool construction, stream add/remove, bandwidth validation, pipe split/merge, DSC allocation, DCC cap query, and writeback arbitration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c

## Purpose

`dcn201_resource.c` is the DCN 2.0.1 resource-pool implementation for Cyan Skillfish-style hardware. It is a smaller DCN2-family variant that defines local IP and SoC DML bounding boxes, DCN201-specific register lists and constructors, a reduced capability table, and a resource function table that reuses many DCN20 algorithms.

## Important APIs, Types, And Functions

- `dcn201_create_resource_pool()` allocates and constructs a `dcn201_resource_pool`.
- `dcn201_resource_construct()` initializes caps/debug/workarounds, creates clocks, DCCG, DML instance, IRQ service, per-pipe HUBP/IPP/DPP, OPP/TG/MPC/HUBBUB/DIO, AUX/I2C, common stream/audio resources, and the DCN201 hardware sequencer.
- `dcn201_resource_destruct()` and `dcn201_destroy_resource_pool()` tear down the pool.
- Local factories create DCN201 DPP, IPP, OPP, HUBP, timing generator, MPC, HUBBUB, DIO, link encoder, clock sources, AUX/I2C, audio, stream encoder, and hwseq objects.
- `dcn201_acquire_free_pipe_for_layer()` provides a generation-local secondary-pipe acquisition helper.
- `dcn201_get_dcc_compression_cap()` forwards DCC capability queries to HUBBUB.
- `dcn201_populate_dml_writeback_from_context()` wraps the DCN201 FPU writeback population function.
- `dcn201_link_init()` reads integrated BIOS info to disable DP spread spectrum when requested.

## Control Flow

Construction assigns BIOS registers and `dcn201_res_pool_funcs`, hard-codes the reduced resource cap (`2` TG/OPP/audio/stream encoders/DDC, `4` video planes, no DWB/DSC), sets DC caps, color capabilities, debug defaults, and A0-era workarounds, then creates two clock sources plus the DP DTO source. It creates DCCG, patches `dcn201_ip.max_num_otg` and `max_num_dpp`, initializes DML with `DML_PROJECT_DCN201`, creates the DCN201 IRQ service, and allocates four HUBP/IPP/DPP pipes. It then creates OPPs, AUX/I2C engines, timing generators, MPC, HUBBUB, DIO, common resources via `resource_construct()`, and the hw sequencer.

The resource function table delegates major behavior to DCN20: bandwidth validation, DML pipe population, stream add/remove, pipe release, unknown-plane patching, MCIF arbitration, stream encoder matching, vstartup, and default tiling. DCN201 replaces construction/destruction, link init, pipe acquisition, DCC cap query, and writeback DML population.

## State And Persistence Behavior

The file has no disk persistence. It mutates the DC resource pool, DC caps/debug/check-config/workaround state, DML bounding-box instance, link spread-spectrum flag, and pipe/resource ownership state. The local `dcn201_ip` and `dcn201_soc` static objects provide DML state for this generation and are adjusted for actual OTG/DPP counts during construction.

## Dependencies And Integration Points

It depends on DCN201 register offset/mask headers, Cyan Skillfish offsets, DCN201 hardware constructors, DCN20 common resource helpers, DCN20 DML FPU helpers, generic DC resource code, IRQ service, DCE AUX/I2C/audio/clock helpers, and DIO/link/stream encoder constructors. Its `resource_funcs` table integrates with generic DC through the same callbacks as DCN20, but with no DSC allocation callback and no panel control constructor.

## Risks And Edge Cases

- The capability table advertises no DSC and no DWB; delegated DCN20 stream paths must tolerate `add_dsc_to_stream_resource = NULL` and zero DSC resources.
- The pool has four video planes but only two OPPs/TGs/stream encoders, so validation must prevent unsupported active stream combinations.
- Static DML SoC/IP values are hard-coded and can become stale relative to firmware/SMU reality.
- `dcn201_resource_destruct()` destroys IRQ service inside the per-pipe loop if non-NULL; pointer clearing by `dal_irq_service_destroy()` must prevent repeated destruction.
- Link init depends on optional integrated BIOS info.
- The debug defaults disable PP-lib clock requests and watermark ranges, which changes validation/runtime behavior compared with other DCN2 variants.

## Test Signals

Build tests should cover DCN201 register-list and constructor compatibility. Runtime tests should cover pool construction/destruction, failure cleanup, two-stream limits, four-plane/two-OTG validation behavior, DCN20 delegated bandwidth validation, no-DSC stream handling, DCC cap forwarding, DP spread-spectrum BIOS handling, DML bounding-box initialization, AUX/I2C creation, and FPU writeback population wrappers. Watch for `DC_FAIL_BANDWIDTH_VALIDATE`, allocation error logs, pipe acquisition failures, and unexpected calls to NULL DSC/panel callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.h

## Purpose

`dcn201_resource.h` declares the narrow public interface for the DCN 2.0.1 resource pool. It also defines DP PHY power-state constants used by DCN201 code paths.

## Important APIs, Types, And Functions

- `RRDPCS_PHY_DP_TX_PSTATE_POWER_UP`, `HOLD`, `HOLD_OFF`, and `POWER_DOWN` define DP transmitter PHY power-state values.
- `TO_DCN201_RES_POOL()` casts a generic resource pool to `struct dcn201_resource_pool`.
- `struct dcn201_resource_pool` embeds `struct resource_pool base`.
- `dcn201_create_resource_pool()` is the only exported constructor declared here.

## Control Flow

The header has no executable control flow. DC initialization code includes it to construct a DCN201 pool. After construction, behavior is dispatched through the pool's `resource_funcs` table rather than through additional public DCN201-specific declarations.

## State And Persistence Behavior

The header stores no state. The power-state constants are compile-time values. Runtime state is owned by the implementation's pool object, generic DC resource state, and DML state.

## Dependencies And Integration Points

The header includes `core_types.h` and forward-declares `dc`, `resource_pool`, and DML display pipe parameter types. It is intentionally smaller than the DCN20 header because DCN201 reuses most public helpers from `dcn20_resource.h`.

## Risks And Edge Cases

- Callers needing DCN20 helper behavior must include the DCN20 header, not this one.
- The PHY constants must match hardware register encodings; incorrect values can affect DP power transitions.
- The cast macro assumes the embedded `resource_pool base` remains the first/contained member in `struct dcn201_resource_pool`.

## Test Signals

Compile tests catch constructor declaration and type drift. Runtime DCN201 initialization should confirm the constructor is selected for the right ASIC and that DP PHY power handling still uses valid encoded constants where referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.h

## Purpose

`dcn21_resource.h` declares the public DCN 2.1 resource-pool entry points and DML bounding-box globals for Renoir-class display hardware.

## Important APIs, Types, And Functions

- `TO_DCN21_RES_POOL()` casts a generic `resource_pool` to `struct dcn21_resource_pool`.
- Extern globals `dcn2_1_ip` and `dcn2_1_soc` expose the DCN21 DML IP parameters and SoC bounding box.
- `struct dcn21_resource_pool` embeds `struct resource_pool base`.
- `dcn21_create_resource_pool()` constructs the DCN21 pool.
- `dcn21_fast_validate_bw()` exposes DCN21's fast validation path, adding the `allow_self_refresh_only` parameter on top of the DCN20-style bandwidth API.

## Control Flow

The header has no runtime control flow. DC initialization uses the constructor, and bandwidth code can call the declared fast validator with already populated DML pipe storage and output pointers for pipe count, split provenance, and selected voltage level.

## State And Persistence Behavior

The header stores no state. The extern DML globals are mutable implementation data, and the declared functions mutate `dc`, `dc_state`, DML validation state, pipe topology, and resource acquisition state.

## Dependencies And Integration Points

The header includes `core_types.h` and forward-declares DC/resource/DML pipe types. It sits beside `dcn21_resource.c` and also depends conceptually on `dcn20_resource.h` because DCN21 reuses many DCN20 helper APIs internally.

## Risks And Edge Cases

- `dcn21_fast_validate_bw()` has more parameters than the DCN20 fast validator; callers must pass valid storage for all output pointers.
- The mutable extern DML data can be patched based on fused pipe count and clock tables, so tests should not assume static defaults after initialization.
- Header declarations must stay consistent with resource function callbacks and FPU wrapper functions in the implementation.

## Test Signals

Compile coverage catches prototype drift. Runtime coverage should verify that DCN21 construction installs the expected validator and that direct fast-validator callers handle both full mclk-switch and self-refresh-only validation modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c

## Purpose

`dcn30_resource.c` is the DCN 3.0 resource-pool implementation for Navi2x/Sienna Cichlid-class display hardware. It extends the DCN20 resource model with DCN3 register lists, DML 3.0 validation, up to six pipes, HPO-adjacent stream encoder support through common resource construction, VPG/AFMT ownership on stream encoders, MALL/cache-related caps, MPC 3D LUT resources, DMUB PSR/ABM, firmware-assisted mclk switching logic, and DCN3 writeback arbitration.

## Important APIs, Types, And Functions

- `dcn30_create_resource_pool()` and `dcn30_resource_construct()` allocate and initialize the DCN30 resource pool.
- `dcn30_resource_destruct()` and `dcn30_destroy_resource_pool()` free DCN30-owned stream encoder VPG/AFMT, DPPs, HUBPs, OPPs, TGs, DSCs, DWB/MCIF_WB, ABMs, MPC LUT/shaper resources, PSR, DCCG, DIO, clocks, DDC, audio, and OEM DDC service.
- Factories create DCN30 DPP/HUBP/OPP/TG/MPC/HUBBUB/DIO/link encoder/stream encoder/VPG/AFMT/DSC/DWB/MCIF_WB/AUX/I2C/clock resources.
- `dcn30_internal_validate_bw()` is the core validation and topology mutation routine.
- `dcn30_validate_bandwidth()` allocates DML pipes, calls internal validation, and calculates watermarks/DLG when in programming mode.
- `dcn30_populate_dml_pipes_from_context()` reuses DCN20 population then forces 16-line-buffer depth.
- `dcn30_populate_dml_writeback_from_context()`, `dcn30_calculate_wm_and_dlg()`, and `dcn30_update_soc_for_wm_a()` wrap DCN30 FPU helpers.
- `dcn30_set_mcif_arb_params()` and `dcn30_calc_max_scaled_time()` handle DCN3 writeback arbitration.
- `dcn30_acquire_post_bldn_3dlut()` and `dcn30_release_post_bldn_3dlut()` manage MPC post-blending LUT/shaper resources and RMU mux state.
- `dcn30_update_bw_bounding_box()` derives DCFCLK/UCLK voltage states from clock tables and updates the DCN3 bounding box.
- Firmware-assisted mclk-switch helpers include `dcn30_can_support_mclk_switch_using_fw_based_vblank_stretch()`, `dcn30_setup_mclk_switch_using_fw_based_vblank_stretch()`, and refresh-rate helpers.

## Control Flow

Construction validates pipe-fuse recipes, enters an FPU section, sets BIOS registers and `dcn30_res_pool_funcs`, initializes DC caps for up to six pipes, MALL size, cursor cache, color pipeline, LTTPR VBIOS caps, debug/check defaults, VM helper, six PLL clock sources plus DP DTO, DCCG, SoC bounding box, fused DPP/OTG counts, DML 3.0 instance, IRQ service, HUBBUB, DIO, HUBPs, DPPs, OPPs, TGs, DMUB PSR, per-pipe DMUB ABMs, MPC with 3D LUT support, DSCs, DWB/MCIF_WB, AUX/I2C engines, common resources through `resource_construct()`, hardware sequencer, plane caps, ODM factor, cap functions, and optional OEM DDC service. Failure exits the FPU section, destructs partially initialized state, and returns false.

`dcn30_internal_validate_bw()` resets selected DML state, updates watermark-A SoC data, populates pipes, logs DML input, tries p-state-friendly validation for programming mode, optionally falls back to self-refresh-only validation, applies DCN20 split flags, rejects unsupported windowed MPO ODM when disabled, merges pipes flagged for merge, creates two-way or four-way MPC/ODM splits using `dcn30_split_stream_for_mpc_or_odm()`, preserves preferred previous pipe indices through `dcn30_find_split_pipe()`, rebuilds mapped stream resources for ODM, rebuilds scaling for all plane pipes, validates DSC, optionally repopulates DML pipes, and returns selected voltage and pipe count.

`dcn30_validate_bandwidth()` wraps internal validation, logs failure using DML status, skips watermark/DLG calculation for non-programming validation, and calls `calculate_wm_and_dlg` for programming commits. Firmware-assisted mclk switching checks single-display, panel/debug/capability flags, shutdown state, refresh rate at current and max-stretched vblank, FreeSync/VRR policy, stream status, and marks `fpo_in_use`.

## State And Persistence Behavior

The file has no disk persistence. It mutates DC caps/debug/check state, DML SoC/IP and selected validation state, watermark and DLG outputs, `bw_ctx` clocks/watermarks, resource pool arrays, pipe topology, DSC acquisition, MPC 3D LUT acquisition and RMU mux state, stream status `fpo_in_use`, writeback MCIF arbitration slots, MALL/cache-related caps, and optional OEM DDC service ownership.

The global `dcn3_0_soc` and `dcn3_0_ip` objects are patched from VBIOS VRAM info, clock tables, and fuse count. `dcn30_update_bw_bounding_box()` builds a dynamic voltage-state table from DCFCLK targets and UCLK states, so validation results depend on runtime clock data.

## Dependencies And Integration Points

The file depends on DCN30 register headers, Sienna Cichlid offsets, DCN30 DML/FPU helpers, `display_mode_vba_30`, DCN20 common helpers, generic DC resource code, DCE AUX/I2C/audio/clock helpers, DMUB PSR/ABM service, IRQ service, link service, VBIOS LTTPR queries, VM helper, amdgpu SoC bounding-box data, and kernel allocation/logging. The resource function table exports DCN30 validation, watermark/DLG calculation, SoC update, DML population, stream add/remove, pipe acquisition/release, writeback population, MCIF arbitration, 3D LUT acquire/release, bounding-box update, panel defaults, and tiling defaults.

## Risks And Edge Cases

- Pipe-fuse validation only expects all pipes or a single-pipe recipe; unexpected fuses are forced to single pipe after a debug break.
- The constructor wraps a long allocation sequence in an FPU section; every failure path must call `DC_FP_END()`.
- Four-way MPC/ODM splitting has complex old-index preservation and new split tracking; pointer mistakes can corrupt chains or cause transient underflow.
- Dynamic bounding-box construction depends on clock-table ordering, nonzero memclk, VRAM channel data, and array bounds for `DC__VOLTAGE_STATES`.
- Firmware-assisted mclk switching depends on single-stream, FreeSync, VRR policy, DMUB capability, refresh-rate math, and panel patches; false positives can harm timing stability.
- MPC LUT acquisition mutates LUT state bits and resource-context bitmaps; release must clear both LUT and shaper consistently.
- DCN3 writeback arbitration assumes packed 444/FP16 output and computes `time_per_pixel` from stream `phy_pix_clk`; invalid or zero clocks are hazardous.
- Destruction covers more nested resources than DCN20, including VPG/AFMT and multiple ABMs, making ownership drift easy.

## Test Signals

Tests should cover full and single-pipe fuse recipes, constructor failure cleanup, DML3 validation, p-state fallback, two-way and four-way MPC/ODM, DSC validation, watermark/DLG calculation only in programming mode, dynamic bounding-box updates from clock tables, firmware-assisted mclk-switch eligibility and setup, MPC 3D LUT acquire/release exhaustion, DWB/MCIF arbitration, LTTPR VBIOS cap reads, MALL/cursor caps, DMUB PSR/ABM creation, and stream encoder VPG/AFMT teardown. Runtime signals include `DC_FAIL_BANDWIDTH_VALIDATE`, DML validation messages, bandwidth trace markers, assertions in split allocation, underflow during topology updates, and FAMS/FPO flags in stream status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.h

## Purpose

`dcn30_resource.h` declares the public DCN 3.0 resource-pool interface and generation-specific helper APIs for validation, DML population, writeback, bandwidth bounding boxes, MPC 3D LUT resources, stream addition, and firmware-assisted mclk switching.

## Important APIs, Types, And Functions

- `TO_DCN30_RES_POOL()` casts a generic pool to `struct dcn30_resource_pool`.
- Extern `dcn3_0_ip` and `dcn3_0_soc` expose DCN3 DML IP and SoC bounding-box data.
- `dcn30_create_resource_pool()` constructs the resource pool.
- Validation and DML APIs include `dcn30_validate_bandwidth()`, `dcn30_internal_validate_bw()`, `dcn30_calculate_wm_and_dlg()`, `dcn30_update_soc_for_wm_a()`, `dcn30_populate_dml_pipes_from_context()`, and `dcn30_populate_dml_writeback_from_context()`.
- Writeback APIs include `dcn30_set_mcif_arb_params()` and `dcn30_calc_max_scaled_time()`.
- Resource APIs include `dcn30_add_stream_to_ctx()`, `dcn30_acquire_post_bldn_3dlut()`, and `dcn30_release_post_bldn_3dlut()`.
- Clock/bounding-box and mclk-switch APIs include `dcn30_update_bw_bounding_box()`, `dcn30_can_support_mclk_switch_using_fw_based_vblank_stretch()`, `dcn30_setup_mclk_switch_using_fw_based_vblank_stretch()`, and `dcn30_find_dummy_latency_index_for_fw_based_mclk_switch()`.

## Control Flow

The header has no executable control flow. DC initialization uses the constructor, the resource function table dispatches to validation/watermark/DML helpers, and feature code can call the mclk-switch and 3D LUT helpers around mode validation or commit preparation.

## State And Persistence Behavior

The header stores no state. Declared functions mutate DC resource pools, DML state, bandwidth/watermark state, pipe topology, writeback arbitration structures, MPC LUT/shaper acquisition state, and stream status. The extern DML globals are mutable generation-wide data patched by runtime clock and platform information.

## Dependencies And Integration Points

The header includes `core_types.h` and forward-declares resource and DML pipe types. It is included by DCN30 implementation and by common DC paths that need generation-specific validation, DML population, or mclk-switch support.

## Risks And Edge Cases

- Several declarations require FPU discipline in their implementations; callers should use the resource vtable unless they know the wrapper behavior.
- `dcn30_internal_validate_bw()` mutates topology and expects valid output pointers and a populated pipe array.
- The 3D LUT acquire/release API couples LUT and shaper pointers; callers must release both as a pair.
- Firmware-assisted mclk-switch helpers depend on current context assumptions such as single stream and valid timing.
- Extern bounding boxes should not be treated as immutable hardware constants after clock-table updates.

## Test Signals

Compile coverage catches prototype drift. Runtime tests should exercise the declared functions through resource-pool callbacks and direct feature paths: validation, watermark calculation, DML population, writeback arbitration, 3D LUT acquisition/release, bounding-box updates, stream addition, and mclk-switch eligibility/setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.h -->
