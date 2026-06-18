# Research: subset-b-001459

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c

## Purpose

`dcn351_resource.c` builds the AMD Display Core resource pool for the DCN 3.5.1 ASIC family. It binds DCN 3.5-era register offset tables, masks, shifts, capability defaults, debug defaults, resource factory functions, bandwidth-validation hooks, and teardown logic into one `struct resource_pool` returned by `dcn351_create_resource_pool()`.

The file is mostly generation glue: it uses DCN35 implementations for HUBBUB, HUBP, DPP, OPP, DSC, DCCG, DWB, MMHUBBUB, timing generation, stream encoding, and link encoding, but wires them to DCN 3.5.1 register definitions and to a DCN351 IRQ service and DML2/FPU helpers.

## Important APIs, Types, And Functions

- `enum dcn351_clk_src_array_id`: indexes five combo-PHY PLL clock source objects plus the DP DTO clock source.
- Static register tables and shift/mask tables such as `clk_src_regs`, `abm_regs`, `dpp_regs`, `hubp_regs`, `hubbub_reg`, `dccg_regs`, `hwseq_reg`, and `vmid_regs`: initialized at runtime from DCN 3.5.1 offset macros using the local `SR`, `SRI`, `SRII`, and NBIO helper macros.
- `res_cap_dcn351`: declares four pipes/TGs/OPPs/planes/DSCs, five DIG link/stream encoders, four HPO DP stream encoders, two HPO DP link encoders, one DWB, five DDC engines, 16 VMIDs, and two MPC 3D LUT resources.
- `plane_cap`, `debug_defaults_drv`, `config_defaults`, and `panel_config_defaults`: publish ASIC capabilities and default policy choices to `dc`.
- Factory helpers: `dcn35_dpp_create`, `dcn35_opp_create`, `dcn31_aux_engine_create`, `dcn31_i2c_hw_create`, `dcn35_mpc_create`, `dcn351_dio_create`, `dcn35_hubbub_create`, `dcn35_timing_generator_create`, `dcn35_link_encoder_create`, `dcn31_link_enc_create_minimal`, `dcn31_panel_cntl_create`, `dcn31_create_audio`, `dcn35_stream_encoder_create`, HPO stream/link encoder creators, `dcn351_hwseq_create`, `dcn35_hubp_create`, DWB/MMHUBBUB creators, `dcn35_dsc_create`, and `dcn35_clock_source_create`.
- `dcn351_validate_bandwidth()`: calls `dml2_validate()` through `DC_FP_START/END`, then runs `dcn35_decide_zstate_support()` for programming validation.
- `populate_dml_pipes_from_context_fpu()` and `dcn351_update_bw_bounding_box()`: FPU wrappers around DCN351-specific DML pipe population and bounding-box update.
- `dcn351_res_pool_funcs`: the resource operation table consumed by shared DC resource code.
- `dcn351_resource_construct()` and `dcn351_resource_destruct()`: central constructor and teardown paths.
- `dcn351_create_resource_pool()`: exported allocation entry point.

## Control Flow

`dcn351_create_resource_pool()` allocates `struct dcn351_resource_pool`, calls `dcn351_resource_construct()`, returns `&pool->base` on success, and frees on failure.

Construction first initializes BIOS, clock-source, ABM, and DCCG register tables and attaches `bios_regs` to `ctx->dc_bios`. It sets `pool->base.res_cap`, `pool->base.funcs`, pipe counts, MPCC counts, display caps, color caps, host-router/DPIA caps, DML2/debug defaults, ASSR/LTTPR behavior, fine-grain clock-gating defaults, and VM helper state.

It then creates resources in dependency order: PLL clock sources and DP DTO, legacy DML instance, DCCG, power-gate controller, IRQ service, HUBBUB/VMIDs, DIO, per-pipe HUBPs and DPPs, OPPs, TGs, DMUB PSR and Replay, ABMs, MPC, DSCs, DWB, MMHUBBUB, AUX engines, I2C engines, USB4 DPIA count, and finally shared `resource_construct()` for audio, stream encoders, HPO encoders, virtual links, and MPC 3D LUTs. After that it installs the DCN351 HW sequencer, plane caps, cap functions, and DML2 callback/options.

Every allocation failure jumps to `create_fail`, which calls `dcn351_resource_destruct()` and returns false. The destructor walks every pool array and destroys or frees nested resources, including VPG/AFMT/APG subobjects owned by stream encoders, HPO encoders, DSCs, MPC, HUBBUB, DPP/HUBP/IPP, IRQ service, AUX/I2C, OPP, TG, DWB/MMHUBBUB, audio, clock sources, MPC LUT/shaper objects, DP clock source, ABMs, PSR, Replay, PG controller, DCCG, and DIO.

## State And Persistence Behavior

There is no on-disk persistence. The file persists runtime state by mutating `struct dc` and `struct resource_pool`.

Important mutations include `dc->caps`, `dc->config`, `dc->debug`, `dc->check_config`, `dc->cap_funcs`, `dc->dcn_ip->max_num_dpp`, `dc->dml2_options`, `ctx->dc_bios->regs`, VM helper setup, `pool->base.*` resource arrays/counts, `pool->base.usb4_dpia_count`, and resource function pointers. Hardware state is later affected through the constructed block function tables, but this file itself mainly allocates/registers objects and initializes register descriptors.

## Dependencies And Integration Points

The file integrates with common DC resource management (`resource_construct`, `resource_pool`, `resource_funcs`), link encoder assignment (`link_enc_cfg_*`), DMUB features (`dmub_psr`, `dmub_replay`, `dmub_abm`), DML/DML2 validation and FPU helpers, DCN35 block constructors, IRQ service `dal_irq_service_dcn351_create`, and VBIOS queries for LTTPR caps. The preferred DPIA encoder table maps four DPIA endpoints across two host routers to DIGC/DIGD preferences.

Shared DC code calls the function table for bandwidth validation, DML pipe population, stream add/remove, pipe allocation/release, DSC assignment, writeback population, 3D LUT acquisition, panel defaults, VStartup, pipe pixel clock params, and default tiling.

## Risks And Edge Cases

- The file relies on large static register arrays being initialized before object construction. Wrong instance counts or offset macros can wire hardware objects to incorrect registers.
- `dcn351_get_preferred_eng_id_dpia()` indexes a four-entry table without a local bounds check; callers must pass a valid DPIA index.
- `dcn31_link_enc_create_minimal()` checks `(eng_id - ENGINE_ID_DIGA) > num_dig_link_enc`; equality would still index one past the valid DIG encoder range.
- `dcn35_link_encoder_create()` leaks `enc20` if `enc_init_data->hpd_source` is out of range because allocation happens before the guard returns NULL.
- Resource construction has many partial-allocation exits; destructor coverage is critical and must remain aligned with ownership in each factory.
- Debug defaults deliberately disable several power-gating paths or ignore PG, so power behavior depends heavily on later debug/config overrides.
- Commented TODOs show DML1 compatibility and DET/DML2 constants are still transitional.

## Test Signals

- Build coverage should catch missing register macro fields, constructor signature mismatches, and function-table type mismatches.
- Resource-pool smoke tests should instantiate and destroy the pool with mock BIOS/register offsets and verify every count matches `res_cap_dcn351`.
- Failure-injection tests around each allocation site should verify `dcn351_resource_destruct()` handles partially built pools.
- Runtime validation signals include `dm_error("DC: failed to create ...")`, `BREAK_TO_DEBUGGER()`, DML2 validation failures, and link/DPIA assignment errors.
- Display validation should cover HDMI/DP/eDP, HPO DP, DSC, PSR/Replay, DWB, four-pipe ODM/MPC cases, DML2 DC/AC power-source validation, and USB4 DPIA routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.h

## Purpose

`dcn351_resource.h` is the public declaration header for the DCN 3.5.1 resource pool implementation. It exposes the DCN351 DML IP/SOC bounding boxes, the typed resource-pool wrapper, and the factory used by DC initialization to create the generation-specific resource pool.

## Important APIs, Types, And Functions

- `extern struct _vcs_dpi_ip_params_st dcn3_51_ip` and `extern struct _vcs_dpi_soc_bounding_box_st dcn3_51_soc`: DCN351 DML tuning inputs supplied by the FPU/DML side.
- `TO_DCN351_RES_POOL(pool)`: container macro converting a generic `struct resource_pool *` to `struct dcn351_resource_pool *`.
- `struct dcn351_resource_pool`: thin wrapper containing only `struct resource_pool base`.
- `dcn351_create_resource_pool(init_data, dc)`: exported constructor implemented in `dcn351_resource.c`.

## Control Flow

The header has no runtime control flow. It is included by the DCN351 implementation and by DC initialization code that needs to call `dcn351_create_resource_pool()`. The container macro is used by teardown to recover the outer allocation from the embedded base pool.

## State And Persistence Behavior

The header defines no storage. It declares external DML data and a resource-pool type whose state is owned and populated by the C file.

## Dependencies And Integration Points

It depends on `core_types.h` for DC core structures and on Linux `container_of` semantics through the included headers. Its exported factory is the integration point between ASIC selection and the generic display-core resource model.

## Risks And Edge Cases

- The wrapper currently has no extra generation-specific fields. Any future per-ASIC state must be added here and initialized/destructed in the C file.
- The `TO_DCN351_RES_POOL` macro assumes the incoming pointer is a valid `base` member of a `struct dcn351_resource_pool`; misuse will produce invalid memory access.
- The external DML symbols must be linked whenever DCN351 support is built.

## Test Signals

- Compile/link tests catch missing DML symbols and signature drift for `dcn351_create_resource_pool()`.
- Resource-pool creation/destruction tests indirectly validate the container macro by exercising `dcn351_destroy_resource_pool()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c

## Purpose

`dcn36_resource.c` builds the resource pool for DCN 3.6. It is closely derived from the DCN35/DCN351 pool code but uses DCN 3.6 register offsets, DCN36 IRQ service creation, DCN36 resource typing, and DCN36-specific policy defaults. It still reuses many DCN35 block constructors and DML helpers.

## Important APIs, Types, And Functions

- `enum dcn36_clk_src_array_id`: indexes five combo-PHY PLL clock sources.
- Runtime register tables for clocks, ABM, audio, VPG/AFMT/APG, stream/link encoders, HPO encoders, DPP/OPP, AUX/I2C, DWB/MMHUBBUB, DSC, MPC, OPTC, HUBP, HUBBUB, DCCG, PG control, HWSEQ, VMID, and DIO.
- `res_cap_dcn36`: same headline resource counts as DCN351: four pipes and four DSCs, five DIG encoders/DDC engines, four HPO stream encoders, two HPO link encoders, one DWB, 16 VMIDs, two MPC 3D LUTs.
- `debug_defaults_drv`: DCN36 display defaults, notably DML2 enabled, symclk32 link-encoder root clock optimization enabled, `disable_timeout = true`, and pstate/IPS/power defaults comparable to DCN35 lineage.
- `dcn36_get_preferred_eng_id_dpia()`: maps the four DPIA indices to preferred DIGC/DIGD engines.
- Factory helpers: mostly `dcn35_*` or `dcn31_*` functions with DCN36 register lists, plus `dcn36_dio_create()` and `dcn36_hwseq_create()`.
- `dcn35_validate_bandwidth()`: DCN36 uses the DCN35 DML2 validation path and zstate decision.
- `dcn36_res_pool_funcs`: operation table for resource management.
- `dcn36_resource_construct()`, `dcn36_resource_destruct()`, and exported `dcn36_create_resource_pool()`.

## Control Flow

`dcn36_create_resource_pool()` allocates the wrapper pool, delegates to `dcn36_resource_construct()`, returns the generic base on success, and frees on failure.

Construction initializes register tables and installs `bios_regs`, then sets resource caps, function pointers, pool counts, display caps, color pipeline caps, host-router/DPIA caps, DML2 defaults, and VM helper state. It conditionally enables `dc->caps.sequential_ono` when `hw_internal_rev >= 0x40`, enables pipe-context sync logic, disables HBR audio for DP2 through `dc->config.disable_hbr_audio_dp2`, reads VBIOS LTTPR caps, and installs production debug defaults.

The resource creation sequence matches DCN351: clock sources, DP DTO, temporary DML instance, DCCG, PG controller, DCN36 IRQ service, HUBBUB, DIO, per-pipe HUBP/DPP, OPP, timing generators, PSR, Replay, ABMs, MPC, DSCs, DWB/MMHUBBUB, AUX/I2C, DPIA count, shared `resource_construct()`, DCN35 HW sequencer construction, plane caps, cap functions, and DML2 option callbacks. Failures jump to `create_fail` and run `dcn36_resource_destruct()`.

The destructor mirrors the constructor's ownership model: stream encoders and their VPG/AFMT sub-blocks, HPO stream/link encoders, DSCs, MPC, HUBBUB, per-pipe blocks, IRQ service, AUX/I2C engines, OPPs, TGs, DWB/MMHUBBUB, audio, clock sources, LUT/shaper objects, DP clock source, ABMs, PSR, Replay, PG control, DCCG, and DIO are freed or destroyed.

## State And Persistence Behavior

The file only creates runtime state. It mutates `dc->caps`, `dc->config`, `dc->debug`, `dc->check_config`, `dc->cap_funcs`, `dc->dcn_ip`, `dc->dml2_options`, VBIOS register pointers, and the `pool->base` resource arrays/counts/function table. It does not store anything to disk.

## Dependencies And Integration Points

DCN36 integrates with common resource code, DCN35 block constructors, DCN36 register headers, `dal_irq_service_dcn36_create()`, DMUB PSR/Replay/ABM, link encoder assignment, VBIOS LTTPR queries, DML2 validation, and DCN35 FPU helpers. The `dcn36_resource.h` register macro `HWSEQ_DCN36_REG_LIST()` supplies a generation-specific HWSEQ register list.

Shared DC callers use `dcn36_res_pool_funcs` for bandwidth validation, pipe allocation, stream add/remove, DSC resources, writeback modeling, encoder-switch state updates, default tiling, and panel defaults.

## Risks And Edge Cases

- Most behavior is inherited from DCN35, so DCN36-specific hardware differences must be represented correctly in register lists and caps; otherwise constructors succeed but program wrong registers.
- `dcn36_get_preferred_eng_id_dpia()` has no local bounds check.
- The comment says "DCN3.5 has 6 DPIA" but the value is `4`; stale comments can mislead future topology changes.
- The DML init still uses `dcn3_5_soc` and `dcn3_5_ip` as a temporary compatibility path while DML2 is the main validator.
- Partial-construction cleanup depends on destructor ownership staying aligned with factory allocation patterns.
- `disable_timeout = true` changes timeout behavior and should be validated against hang-detection expectations.

## Test Signals

- Compile tests catch DCN36 offset/mask macro drift and HWSEQ macro usage.
- Pool create/destroy tests should validate the four-pipe/five-DIG/two-HPO-link resource counts and cleanup on injected allocation failures.
- Runtime smoke tests should cover DP2/HPO, eDP DSC, PSR/Replay, DWB, USB4 DPIA routing, four-pipe ODM/MPC, sequential ONO ASIC revisions, and DML2 AC/DC validation.
- Logs and assertions include resource creation `dm_error()` messages, `BREAK_TO_DEBUGGER()`, DML2 bandwidth failures, and IRQ/link encoder assignment failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.h

## Purpose

`dcn36_resource.h` exposes the DCN 3.6 resource-pool constructor and generation wrapper, plus a DCN36-specific HWSEQ register-list macro used by the C file to initialize `struct dce_hwseq_registers`.

## Important APIs, Types, And Functions

- `extern struct _vcs_dpi_ip_params_st dcn3_6_ip` and `extern struct _vcs_dpi_soc_bounding_box_st dcn3_6_soc`: DCN36 DML IP/SOC inputs.
- `TO_DCN36_RES_POOL(pool)`: converts a generic `struct resource_pool *` to `struct dcn36_resource_pool *`.
- `struct dcn36_resource_pool`: wrapper around `struct resource_pool base`.
- `dcn36_create_resource_pool(init_data, dc)`: exported constructor implemented in `dcn36_resource.c`.
- `HWSEQ_DCN36_REG_LIST()`: enumerates HW sequencer register offsets for global timer, host VM, DIO/ODM/MMHUBBUB/DCCG power and clock controls, OTG pixel-rate controls, time-base divisors, DISPCLK change control, RBBMIF timeout controls, CRC controls, power-gating domains, AZALIA audio controls, HPO control, and DMU clock control.

## Control Flow

The header has no executable flow. `HWSEQ_DCN36_REG_LIST()` expands inside the implementation's `hwseq_reg_init()` path after `REG_STRUCT` and register accessor macros are configured.

## State And Persistence Behavior

The header defines no runtime storage. Its macros drive initialization of C-file static register tables and expose type declarations used by the resource pool.

## Dependencies And Integration Points

It depends on `core_types.h` and the register macro environment established by `dcn36_resource.c`. The HWSEQ macro integrates DCN36-specific register coverage with the shared DCE/DCN hardware sequencer object.

## Risks And Edge Cases

- `HWSEQ_DCN36_REG_LIST()` is macro-context dependent: it assumes `SR` and `SRII` are defined to write a `REG_STRUCT` of the correct type.
- Register coverage must stay in sync with `dce_hwseq_registers` fields and DCN36 power/clock gating requirements.
- The external DML declarations must match linked FPU/DML objects.

## Test Signals

- Build coverage catches missing registers or structure fields when HWSEQ definitions drift.
- Runtime power/clock-gating tests exercise whether the listed domains and gates are complete for DCN36.
- Resource-pool destruction tests indirectly validate `TO_DCN36_RES_POOL()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.h

## Purpose

`dcn401_resource.h` declares the DCN401 resource-pool API and exports the large register-list macros needed for runtime initialization of DCN401 hardware blocks. It is both a public constructor header and a generation-specific register binding contract shared by `dcn401_resource.c` and DCN401 block constructors.

## Important APIs, Types, And Functions

- `TO_DCN401_RES_POOL(pool)` and `struct dcn401_resource_pool`: typed wrapper around generic `struct resource_pool`.
- `dcn401_create_resource_pool()`: creates the DCN401 pool.
- Exported helpers: `dcn401_patch_unknown_plane_state()`, `dcn401_validate_bandwidth()`, `dcn401_prepare_mcache_programming()`, `dcn401_get_default_tiling_info()`, `dcn401_get_vstartup_for_pipe()`, and `dcn401_get_power_profile()`.
- Register-list macros: `HUBP_REG_LIST_DCN401_RI`, `ABM_DCN401_REG_LIST_RI`, `VPG_DCN401_REG_LIST_RI`, `SE_DCN4_01_REG_LIST_RI`, `LE_DCN401_REG_LIST_RI`, `DPP_REG_LIST_DCN401_COMMON_RI`, `OPP_REG_LIST_DCN401_RI`, `DSC_REG_LIST_DCN401_RI`, MPC mux macros, and `OPTC_COMMON_REG_LIST_DCN401_RI`.

## Control Flow

The header has no executable flow. Its macros expand inside C-file register initialization after `REG_STRUCT`, `SRI_ARR`, `SR_ARR`, NBIO accessors, and related macros are defined. The exported function declarations let other DC code call DCN401-specific validation, tiling, mcache, vstartup, and power-profile behavior through direct references or `resource_funcs`.

## State And Persistence Behavior

The header owns no state. Its register macros define which hardware register offsets are stored into static register-table structures at runtime. The declared functions mutate runtime `dc`, `dc_state`, `pipe_ctx`, or `dc_plane_state` objects in the C implementation.

## Dependencies And Integration Points

It depends on `core_types.h`, `dcn32/dcn32_resource.h`, and `dcn401/dcn401_hubp.h`. The register macros integrate DCN401 blocks with HUBP, ABM, VPG, stream encoder, link encoder, DPP/SPL/sharpener, OPP, DSC, MPC, and OPTC constructors. The exported helpers are used by generic DC resource management and validation paths.

## Risks And Edge Cases

- The register-list macros are highly sensitive to the macro environment in the including C file; missing or differently named helper macros break compilation or silently bind wrong fields if reused incorrectly.
- The macros contain very broad hardware coverage, including cursor, DMDATA, flip, mcache, 3D LUT, EASF, iSharp, DSC PPS/error counters, and timing-generator registers. Omissions can surface as feature-specific runtime failures rather than compile failures if structure fields still match.
- Header declarations must remain synchronized with `dcn401_res_pool_funcs`; otherwise generic callers can lose access to DCN401-specific behavior.

## Test Signals

- Build tests catch most macro/field drift.
- Feature tests should cover every macro-heavy block family: HUBP flip/mcache/cursor, ABM backlight, VPG/AFMT/APG packets, stream/link encoders, DPP color/SPL/sharpener, DSC PPS/status, MPC muxing, and OPTC timing/interrupts.
- API-level tests should call exported helpers through both direct symbols and the resource function table where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.h -->
