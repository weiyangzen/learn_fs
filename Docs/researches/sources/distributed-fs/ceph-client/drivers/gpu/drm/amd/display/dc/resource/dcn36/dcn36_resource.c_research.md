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
