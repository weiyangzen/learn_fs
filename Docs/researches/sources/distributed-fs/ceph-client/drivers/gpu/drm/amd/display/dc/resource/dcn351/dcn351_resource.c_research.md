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
