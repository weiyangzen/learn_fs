# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c

## Purpose
This file constructs the DCN 3.0.3 resource pool for Beige Goby-class hardware. It is a smaller DCN30-derived implementation with two display pipes and DCN303-specific register tables, IRQ service, FPU bounding-box update, and bandwidth defaults.

## Important APIs, Types, And Functions
`res_cap_dcn303` declares 2 timing generators, OPPs, video planes, audio blocks, stream encoders, DDC engines, and DSC blocks, plus 1 DWB, 16 VMIDs, and 1 MPC 3D LUT. The implementation provides factories for all pool hardware objects and installs `dcn303_res_pool_funcs`. Exported `dcn303_update_bw_bounding_box()` wraps `dcn303_fpu_update_bw_bounding_box()`, and `dcn303_create_resource_pool()` allocates the generic pool.

## Control Flow
`dcn303_resource_construct()` sets BIOS scratch registers, assigns caps/functions, fills display/color caps, enables `dc_mode_clk_limit_support`, reads LTTPR VBIOS state, applies debug/config defaults, initializes VM helpers, creates two PHY PLL sources and one DP DTO source, creates DCCG, initializes DCN303 SOC/IP data, initializes DML, creates DCN303 IRQ service, Hubbub, DIO, two HUBP/DPP pairs, two OPPs, two TGs, PSR, ABMs, MPC, DSCs, writeback resources, AUX/I2C, and common stream/audio/LUT resources. It constructs the HW sequencer, applies plane caps, sets max ODM combine factor, and optionally creates OEM DDC service.

## State And Persistence
The file mutates `dc->caps`, `dc->config`, `dc->debug`, `dc->check_config`, `dc->dml`, `dc->cap_funcs`, `pool` object arrays, `pool->psr`, `pool->oem_device`, and `dcn3_03_ip` / `dcn3_03_soc`. There is no durable disk persistence.

## Dependencies And Integration Points
Dependencies include Sienna Cichlid/Beige Goby register headers, DCN303 DCCG/IRQ/FPU code, DCN30 block constructors, DCE AUX/I2C/audio/panel-control implementations, DMUB PSR/ABM, DML, link service, and common resource helpers. The installed resource vtable mostly uses DCN30 algorithms, with DCN303-specific bounding-box update and panel defaults.

## Risks
The invalid bounding-box log string contains `/n` instead of `\n`, reducing log readability. As in DCN302, `init_soc_bounding_box()` failure is not fatal. Resource counts are small; any accidental reuse of DCN302 five-instance tables would overrun, while missing Beige Goby register coverage would fail construction. The destructor relies on common destroy functions and pointer nulling for repeated/partial cleanup safety.

## Test Signals
Expected signals are two working pipes, two DSC instances, successful Beige Goby probe, DCN303 IRQ creation, PSR/ABM allocation, correct OEM DDC behavior, successful DCN30 mode validation using DCN303 DML tables, and clean unload. Multi-display tests should emphasize two-pipe limits, DSC use, DWB, and clock-limit behavior.
