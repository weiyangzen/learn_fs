# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c

## Purpose
This file constructs the DCN 1.0/1.01 resource pool for Raven-family hardware. Unlike the DCE files, it builds DCN objects such as HUBP, DPP, MPC, HUBBUB, OPTC, DIO, and DML/SOC/IP bandwidth state while still reusing several DCE components for AUX, I2C, audio, DMCU/ABM, and clock sources.

## Important APIs, Types, And Functions
- `dcn10_create_resource_pool()` allocates `struct dcn10_resource_pool` and invokes `dcn10_resource_construct()`.
- `dcn10_res_pool_funcs` installs DCN-specific destroy, link encoder, validation, secondary-pipe acquisition, add-stream, unknown-plane patching, stream encoder selection, vstartup, and tiling callbacks.
- `dcn10_validate_bandwidth()` wraps `dcn_validate_bandwidth()` in `DC_FP_START/END`.
- `dcn10_validate_global()` enforces DCN 1.0 MPO limits and a single-channel-memory underflow workaround for 4K desktop plus downscaled 4K video.
- `dcn10_acquire_free_pipe_for_layer()` allocates secondary DPP pipes for layer composition and maps HUBP/IPP/DPP/MPCC state.
- `dcn10_get_default_tiling_info()` publishes GFX9 linear default tiling.

## Control Flow
Construction binds NBIO BIOS scratch registers, selects four-pipe DCN 1.0 caps or three-pipe DCN 1.01 caps, publishes extensive DC caps and color-pipeline capabilities, creates combo PHY PLLs plus a DP DTO, DMCU, ABM, initializes DML with `dcn1_0_soc`/`dcn1_0_ip`, copies DCN IP/SOC defaults, and applies floating-point bandwidth construction. It creates PP/SMU function hooks, optionally updates bandwidth from PPLIB FCLK/DCFCLK voltage tables, synchronizes DML/bandwidth state, notifies PPLIB watermark ranges, creates IRQ service, skips disabled pipe fuses, then creates HUBP, IPP, DPP, OPP, and OPTC objects for valid pipes. It creates AUX/I2C engines, sets the final pipe and MPCC counts, updates DML max DPP counts, creates MPC, HUBBUB, and DIO, calls `resource_construct()` for shared resources, constructs the DCN HW sequencer, fills plane caps, and exposes DCC compression caps.

The add-stream path maps pool resources, calls DCE 11.2 PHY clock mapping, and builds DCN pipe clock/clamping/bit-depth parameters. Stream encoder selection prefers matching PHY or USB4 DPIA engines while avoiding virtual encoders as the generic fallback.

## State And Persistence
Persistent state includes `pool->base` object arrays, `dc->caps`, `dc->debug`, `dc->check_config`, `dc->dml`, `dc->dcn_ip`, `dc->dcn_soc`, `pool->base.pp_smu`, `pipe_count`, `timing_generator_count`, `mpcc_count`, and `dc->cap_funcs`. Pipe fuses can reduce usable pipe count and update DML maximum DPPs. Unknown plane states are patched to GFX9 64KB swizzle modes based on bits per pixel.

## Dependencies And Integration Points
The file depends on DCN 1.0 register offsets, SOC15/NBIO/MMHUB offsets, DML/FPU helpers, DCN component constructors, DCE clock/audio/AUX/I2C helpers, IRQ service DCN10, PPLIB/SMU clock APIs, DCE 11.2 clock-resource mapping, and generic resource construction. It is the DCN 1.x entry point for Display Core resource ownership.

## Risks
Destructors destroy IRQ service inside the per-pipe loop, which is sensitive to repeated calls if multiple pipes were allocated. Link encoder creation returns NULL without freeing `enc10` if HPD source is out of range after allocation. PPLIB clock verification breaks to debugger when clock tables are missing or zero, so platform firmware quality matters. Global validation intentionally rejects MPO on multi-display and specific 4K underflow-prone cases. Pipe fuse compaction requires all per-pipe arrays and DML counts to stay aligned.

## Test Signals
Signals include Raven/Raven2 pool construction, pipe-fuse-reduced systems, DCN 1.01 three-pipe systems, DP/HDMI/USB4 DPIA stream encoder selection, DML bandwidth validation, PPLIB FCLK/DCFCLK update and watermark notification, DCC capability queries through HUBBUB, MPO validation failures, unknown tiling patch behavior, and allocation-failure teardown.
