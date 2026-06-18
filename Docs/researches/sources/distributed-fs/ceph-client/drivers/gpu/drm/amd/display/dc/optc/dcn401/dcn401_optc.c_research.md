# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.c

## Purpose
Implements DCN 4.01 OPTC behavior. Compared with DCN3.x, it adds a more general ODM memory allocator, 3:1 ODM combine support with last-segment width, FAMS2-aware DRR programming through DMUB, P-state keepout programming, vupdate keepout helpers, and update-lock status waiting.

## Important APIs, Types, and Functions
Public functions include `dcn401_timing_generator_init()`, `optc401_set_drr()`, `optc401_set_vtotal_min_max()`, `optc401_setup_manual_trigger()`, `optc401_program_global_sync()`, enable/disable/phantom helpers, ODM bypass/combine, horizontal timing manual mode, out-mux selection, vupdate keepout, and update-lock wait. `decide_odm_mem_bit_map()` is a static allocator for shared ODM memory bits.

## Control Flow and State
`decide_odm_mem_bit_map()` computes required memory in even pairs from active width, allocates first preferred memory per OPP, then second preferred memory for active OPPs, then second preferred memory from inactive OPPs, and asserts allocation completeness. ODM combine supports 2, 3, and 4 input segments; 3:1 programs `OPTC_WIDTH_CONTROL2.OPTC_SEGMENT_WIDTH_LAST` and uses horizontal timing divide by 4 because the hardware packs four pixels per transfer. Disable clears ODM selection/memory, disables OTG/VTG, waits for `OTG_CURRENT_MASTER_EN_STATE == 0`, then waits for `OTG_BUSY == 0`. DRR either calls `dc_dmub_srv_fams2_drr_update()` when FAMS2 is enabled, uses FAMS1 DMUB commands for vtotal updates, or writes registers locally. Global sync stores offsets in `optc1` and programs startup/update/ready and P-state keepout registers.

## Dependencies and Integration Points
Depends on DCN31/DCN32 helpers, `dc_dmub_srv.h`, and shared `reg_helper` MMIO macros. DCN42 reuses many DCN401 functions directly. The vtable supplies Display Core with timing, ODM, DRR, sync, pending, and update-lock behavior for DCN401 resources.

## Risks and Test Signals
Risks include ODM memory double allocation across OPTCs, incorrect 3:1 active width or last-segment handling, FAMS/FAMS2 gating mismatches, and P-state keepout off-by-one values. Tests should cover 2:1/3:1/4:1 ODM, wide modes such as 11520x2160, FAMS1/FAMS2/disabled VRR paths, global sync with nonzero `vstartup_start`, HPO/DIO output mux, and update-lock wait timeout behavior.
