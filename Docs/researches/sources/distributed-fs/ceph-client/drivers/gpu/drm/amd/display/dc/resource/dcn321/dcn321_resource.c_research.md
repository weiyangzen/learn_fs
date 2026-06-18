# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c

## Purpose
This file constructs, configures, and destroys the DCN 3.2.1 Display Core resource pool. It maps generated DCN321 register offsets into block-specific register tables, creates all hardware abstraction objects, fills ASIC capability/default policy fields, initializes DML and DML2 options, and exposes a `resource_funcs` table that lets generic Display Core code drive this ASIC generation.

## Important APIs, Types, And Functions
- `dcn321_create_resource_pool` allocates `struct dcn321_resource_pool` and delegates construction.
- `dcn321_resource_construct` is the main bring-up path. It initializes BIOS/clock/ABM/DCCG registers, handles pipe fuses, fills `dc->caps`, `dc->config`, `dc->debug`, creates hardware blocks, calls `resource_construct`, installs sequencer functions, and configures DML2.
- Factory helpers create AUX/I2C engines, clock sources, DIO, HUBBUB/VMID, HUBP, DPP, MPC, OPP, timing generators, link encoders, audio, VPG/AFMT/APG, stream encoders, HPO DP stream/link encoders, HW sequencer, DWB, MMHUBBUB, and DSC.
- `dcn321_resource_destruct` releases all objects allocated by construction, including nested VPG/AFMT/APG objects and shared services.
- `dcn321_update_bw_bounding_box` calls the FPU bounding-box update and reinitializes active DML2 contexts when enabled.
- `read_pipe_fuses` reads `CC_DC_PIPE_DIS` and reduces usable pipe count.
- `dcn321_res_pool_funcs` wires generic resource operations to DCN32/DCN30/DCN20 implementations plus DCN321-specific link creation and bounding-box update.

## Control Flow
Construction starts by populating static register tables through macros from `dcn32_resource.h`, then assigns `ctx->dc_bios->regs`. It reads pipe fuses, asserts if pipe 0 or full DCN is disabled, adjusts `dcn3_21_ip.max_num_dpp/max_num_otg`, and sets pool counts based on remaining pipes. It fills capability fields for cursor, MALL/CAB, SubVP timing margins, DP/HPO, DSC, color, LTTPR, VM, and ODM behavior. It creates five PLL clock sources plus a DP DTO source, DCCG, DML instance, IRQ service, HUBBUB, DIO, then loops over non-fused pipe instances to create HUBP/DPP/OPP/TG/ABM entries compacted into pool arrays. It then creates PSR, MPC, DSCs, DWB/MMHUBBUB, AUX/I2C engines, and delegates audio/stream/HPO/virtual encoder creation to `resource_construct`. Failure at any step jumps to `create_fail`, destructs partial state, and returns false.

## State And Persistence
Persistent driver state includes `pool->base` object arrays, counts, function pointers, `dc->caps`, `dc->config`, `dc->debug`, DML state, DML2 options, optional OEM DDC service, and BIOS register pointers. Static register tables are rewritten during construction and then referenced by hardware objects. Pipe fuses persist in the chosen pipe count and compacted hardware-object arrays.

## Dependencies And Integration Points
The file depends on generated DCN321/NBIO register headers, shared DCN32 register-list macros, DML DCN321 FPU code, IRQ service DCN32, DMUB ABM/PSR, DC link service, DCE clock/audio/AUX/I2C, DWB/MMHUBBUB, and many DCN20/30/31/32 block constructors. It integrates with Display Core through `resource_pool`, `resource_create_funcs`, `resource_funcs`, DML/DML2, HW sequencer initialization, BIOS LTTPR queries, and link encoder assignment.

## Risks And Edge Cases
Partial-construction cleanup must match allocation order; an object missed by `dcn321_resource_destruct` leaks on failure. The IRQ destructor is inside the pipe loop and guarded by a null pointer, which is unusual and should be checked for repeated destroy safety. Pipe-fuse compaction means logical pool indexes differ from physical pipe instances, so any code assuming equal indexes can misprogram registers. Register-table macros depend on generated names and correct `REG_STRUCT`. Hard-coded caps, cursor limits, MALL sizing, and SubVP margins must stay synchronized with firmware, DML, and ASIC characterization.

## Test Signals
Key signals include successful probe on all fuse configurations, failure-injection for each factory allocation, modeset with four and fewer pipes, HPO DP and HDMI link bring-up, DSC allocation/release, AUX/I2C/DDC transactions, ABM/PSR operation, MALL/SubVP validation, DML/DML2 reinitialization after clock table updates, writeback operation, and teardown without leaks or double frees.
