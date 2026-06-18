# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c

## Purpose
This file constructs the DCN 3.0.2 resource pool for Dimgrey Cavefish-class hardware. It is similar to DCN30 but sets DCN302 register tables, five display pipes, DMUB PSR support, OEM DDC service support, panel defaults, and DCN302-specific bandwidth-bounding-box updates.

## Important APIs, Types, And Functions
`res_cap_dcn302` advertises 5 timing generators, OPPs, planes, audio blocks, stream encoders, DDC engines, and DSC blocks, plus 1 DWB and 16 VMIDs. Static factories create DIO, Hubbub, VPG, AFMT, audio, stream encoders, clock sources, HWSEQ, HUBP, DPP, OPP, TG, MPC, DSC, DWB, MMHUBBUB, AUX, I2C, link encoders, and panel controls. `dcn302_update_bw_bounding_box()` wraps `dcn302_fpu_update_bw_bounding_box()`. `dcn302_resource_construct()` and `dcn302_resource_destruct()` own lifecycle, and `dcn302_create_resource_pool()` is the external constructor.

## Control Flow
The constructor allocates a generic `struct resource_pool`, sets BIOS register pointers, assigns `res_cap_dcn302` and `dcn302_res_pool_funcs`, fills global DC caps and color capabilities, reads VBIOS LTTPR state, installs production debug defaults, initializes VM helpers, creates five PHY PLL clock sources plus a DP DTO source, creates DCCG, initializes the Dimgrey Cavefish SOC/IP bounding box, initializes DML, creates IRQ/Hubbub/DIO, then creates per-pipe HUBP/DPP and per-resource OPP/TG arrays. It also creates DMUB PSR, ABM per timing generator, MPC, all DSCs, writeback, AUX/I2C, common resources via `resource_construct()`, HW sequencer, plane caps, and optionally an OEM DDC service from VBIOS firmware info.

## State And Persistence
State is stored in `dc->caps`, `dc->debug`, `dc->check_config`, `dc->dml`, `dc->cap_funcs`, `pool` arrays, optional `pool->oem_device`, and global `dcn3_02_ip` / `dcn3_02_soc`. `init_soc_bounding_box()` patches DML state with VBIOS SOC BB info and `dc->config.clamp_min_dcfclk`. No disk state is written.

## Dependencies And Integration Points
The file integrates generated DCN302/NBIO/DPCS register headers, DML/FPU code, DCN30 base hardware blocks, DMUB PSR/ABM, link service OEM DDC creation, IRQ service `dal_irq_service_dcn302_create()`, and the common resource construction framework. `dcn302_res_pool_funcs` connects common DC code to DCN30 validation, DML pipe and writeback population, MCIF arbitration, DSC attachment, post-blend LUT management, panel defaults, bounding-box updates, tiling defaults, and pipe allocation.

## Risks
`init_soc_bounding_box()` can return false for unexpected ASIC revisions, but construction continues after calling it. Destruction calls IRQ destroy inside the pipe loop and relies on pointer nulling. The OEM DDC service is only destroyed if it was created and if link service callbacks remain valid. Resource counts must match register arrays exactly; mismatches would index beyond static arrays. The `num_mpc_3dlut` comment in capability setup says 3 while caps say 2, which is a documentation drift risk.

## Test Signals
Probe on Dimgrey Cavefish should create five pipes and five DSCs without error logs. Mode validation should use DCN30 validation and DCN302 FPU bounding-box updates. PSR default policy should be visible through panel defaults. OEM I2C firmware configurations should create and destroy `pool->oem_device`. Hotplug/AUX/I2C, DSC, DWB, and multi-display 8K limits are important runtime signals.
