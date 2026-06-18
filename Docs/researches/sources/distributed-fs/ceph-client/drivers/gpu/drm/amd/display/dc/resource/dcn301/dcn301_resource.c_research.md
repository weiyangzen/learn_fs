# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c

## Purpose
This file builds the AMD Display Core resource pool for DCN 3.0.1 / Vangogh. It binds generated register-offset tables to hardware object constructors, publishes `dcn301_create_resource_pool()`, and installs the DCN301 `resource_funcs` vtable used by mode validation, pipe allocation, DML population, link encoder creation, writeback, and destruction.

## Important APIs, Types, And Functions
`res_cap_dcn301` defines a 4 pipe/OTG/OPP/audio/stream-encoder pool, 1 DWB, 4 DDC engines, 16 VMIDs, 2 MPC 3D LUTs, and 3 DSC blocks. `plane_cap`, `debug_defaults_drv`, and `config_defaults` seed global DC capabilities. Factory helpers allocate and construct DPP, OPP, AUX, I2C, MPC, Hubbub, DIO, timing generator, link encoder, panel control, audio, VPG, AFMT, stream encoder, HWSEQ, HUBP, DWB, MMHUBBUB, DSC, and clock-source objects. `dcn301_resource_construct()` is the core initializer; `dcn301_destruct()` and `dcn301_destroy_resource_pool()` release every sub-object.

## Control Flow
Pool creation allocates `struct dcn301_resource_pool`, then calls `dcn301_resource_construct()`. Construction sets BIOS scratch registers, adjusts PLL count for a specific Vangogh device ID, assigns resource caps/functions, hardcodes display and color capabilities, reads LTTPR flags from VBIOS, initializes VM helpers, creates clock sources and DCCG, initializes the Vangogh DML/SOC bounding box, applies watermark ranges through PP/SMU when enabled, reads disabled pipe fuses, initializes DML, IRQ service, Hubbub, DIO, per-pipe HUBP/DPP/OPP/TG sets for unfused pipes, ABM, MPC, DSC, writeback, AUX/I2C, and common resources via `resource_construct()`. Failure jumps to `create_fail`, which destructs partial state.

## State And Persistence
The file mutates persistent in-memory DC state: `dc->caps`, `dc->debug`, `dc->check_config`, `dc->cap_funcs`, `dc->dml`, `dc->vm_helper`, `ctx->dc_bios->regs`, and `dcn3_01_ip` / `dcn3_01_soc`. Pipe fuse handling reduces `dcn3_01_ip.max_num_dpp` and `max_num_otg`, then updates `pool->base.pipe_count`, `timing_generator_count`, and `mpcc_count` to the live hardware count. The code does not persist to disk; persistence is kernel object lifetime plus hardware/firmware-visible registers and SMU watermark programming.

## Dependencies And Integration Points
The implementation depends on DC core resource helpers, DCE/DIO/DMUB objects, IRQ service `dal_irq_service_dcn30_create()`, generated Vangogh/DCN301/NBIO/DPCS register headers, DML/FPU wrappers, VBIOS callbacks, PP/SMU watermark callbacks, and generic VM helper initialization. `dcn301_res_pool_funcs` integrates DCN301 with common DC algorithms: DCN30 bandwidth validation, DCN301 watermark/DLG calculation, DML pipe population, pipe allocation/release, stream add/remove, DSC attachment, writeback DML population, MCIF arbitration, post-blend 3D LUT management, unknown-plane patching, tiling defaults, and startup selection.

## Risks
Key risks are register-table drift, mismatched resource counts, and partial-construction leaks. The destructor destroys IRQ service inside the per-pipe loop after checking `pool->base.irqs`, so the pointer must be nulled by `dal_irq_service_destroy()` to avoid repeated destruction. `init_soc_bounding_box()` logs invalid ASIC revisions but its return value is not enforced by construction. `dcn3_01_ip` is global and is patched for fuses, so repeated initialization paths must not accidentally compound reductions. Watermark programming depends on non-null PP/SMU hooks.

## Test Signals
Useful signals include successful driver probe on Vangogh, no `DC: failed to create ...` logs, correct pipe count when fuses disable pipes, DCN30 validation passing for single/multi-display modes, no DML underflow warnings, working AUX/I2C/DDC, PSR/ABM behavior through DMUB ABM, DSC modes using up to 3 DSCs, DWB creation, and clean unload with KASAN/KMEMLEAK enabled.
