<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c

## Purpose

`dcn42_resource.c` builds the AMD Display Core DCN 4.2 resource pool. It binds DCN42 register maps, capability tables, debug defaults, hardware block factories, bandwidth validation hooks, and DML2 setup into the generic `resource_pool` interface used by Display Core commits.

## Important APIs, Types, And Functions

- `dcn42_create_resource_pool(init_data, dc)`: exported allocator and constructor entry point.
- `dcn42_resource_construct(num_virtual_links, dc, pool)`: initializes caps, debug/config defaults, register tables, hardware objects, link/DDC/AUX resources, DML2 callbacks, and SPL/sharpness defaults.
- `dcn42_resource_destruct(pool)` and `dcn42_destroy_resource_pool(pool)`: release every object allocated into the pool.
- Object factories: `dcn42_hubbub_create`, `dcn42_hubp_create`, `dcn42_dpp_create`, `dcn42_mpc_create`, `dcn42_opp_create`, `dcn42_timing_generator_create`, `dcn42_link_encoder_create`, `dcn42_stream_encoder_create`, HPO DP encoder factories, DSC/DWB/MMHUBBUB/AUX/I2C/clock-source creators.
- Bandwidth and programming hooks: `dcn42_validate_bandwidth`, `dcn42_update_bw_bounding_box`, `dcn42_prepare_mcache_programming`, and `dcn42_build_pipe_pix_clk_params`.
- Static contracts: `res_cap_dcn42`, `plane_cap`, `debug_defaults_drv`, `config_defaults`, `dcn42_res_pool_funcs`, and `res_create_funcs`.

## Control Flow

Construction initializes BIOS and block register structures, reads pipe fuses from `CC_DC_PIPE_DIS`, reduces the usable pipe count for harvested pipes, asserts impossible pipe-0/full-DCN harvest cases, and installs `dcn42_res_pool_funcs`. It then fills `dc->caps`, color pipeline capabilities, debug defaults, SPL/sharpness ranges, panel/LTTPR options, and DML2 configuration.

Hardware allocation proceeds in a fixed order: clock sources and DP DTO source, DCCG, power-gate control, IRQ service, HUBBUB/VMIDs, per-pipe HUBP/DPP/OPP/TG/ABM, PSR and Replay DMUB objects, MPC, DSCs, DWB/MMHUBBUB, AUX/I2C engines, DPIA counts, and generic `resource_construct` for audio, HWSEQ, stream encoders, HPO encoders, virtual links, and LUT resources. Any allocation failure jumps to `create_fail`, calls the destructor, and returns false.

Bandwidth validation enters the floating-point section, calls `dml2_validate`, and, for validate-and-programming mode, calls `dcn42_decide_zstate_support`. MCACHE programming is prepared only when DML 2.1 is enabled and chooses DC-power-source DML state when appropriate.

## State And Persistence Behavior

There is no on-disk persistence. The file mutates in-memory `dc`, `dc->caps`, `dc->config`, `dc->debug`, `dc->dml2_options`, `dc->dcn_ip`, and every resource pointer under `pool->base`. Durable effects occur later through the block objects' register programming callbacks. Register-table globals are process/static data initialized from per-ASIC offset arrays.

## Dependencies And Integration Points

The file integrates many AMD DC block implementations: DCE/DCE110 clock, AUX, I2C, audio, HWSEQ; DCN20/30/31/32/35/401/42 HUBBUB, HUBP, DPP, MPC, OPP, OPTC, DSC, DCCG, PG control, DWB, MMHUBBUB, stream/link encoders, HPO encoders, ABM/PSR/Replay, link encoder assignment, VM helper, DML2, and SPL. It is the ASIC-specific provider behind generic resource and commit code.

## Risks And Edge Cases

- `dcn42_create_resource_pool` allocates `sizeof(struct dcn401_resource_pool)` for a `struct dcn42_resource_pool *`; this relies on compatible layout/size and is easy to break if the structs diverge.
- Many arrays are sized for fixed block counts; invalid instance numbers can index static register arrays.
- The destructor must stay in lockstep with construction order to prevent leaks after partial construction.
- `dcn42_link_enc_create_minimal` uses an off-by-one-looking bounds check with `>` rather than `>=`.
- Pipe fuse handling asserts but still must avoid mapping logical pipe indices to disabled physical instances.
- DML2, FPU wrappers, MCACHE, SPL, SubVP, and z-state decisions depend on `dc->debug` and BIOS/SMU-provided runtime values.

## Test Signals

Build tests catch missing register fields, changed constructor signatures, and function-table mismatches. Runtime signals include `dm_error` allocation messages, `BREAK_TO_DEBUGGER`, pipe-fuse asserts, failed `dml2_validate`, incorrect display caps, link/AUX/I2C failures, and regressions in DSC, SubVP, MCACHE, SPL sharpness, and z-state behavior on DCN42 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c -->
