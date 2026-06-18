# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.c

## Purpose
Implements the DCN 3.1 OPTC timing-generator operations used by AMD Display Core for enabling/disabling OTG, ODM combine setup, DRR programming, ODM reset, and register-state readback. The file installs a `timing_generator_funcs` vtable in `dcn31_timing_generator_init()` and mostly reuses DCN1/DCN2/DCN3 helpers while overriding DCN31-specific ODM, DRR, disable, and diagnostics behavior.

## Important APIs, Types, and Functions
Key exported functions are `dcn31_timing_generator_init()`, `optc31_immediate_disable_crtc()`, `optc31_set_drr()`, `optc3_init_odm()`, `optc31_read_otg_state()`, and `optc31_read_reg_state()`. Static vtable functions include `optc31_set_odm_combine()`, `optc31_enable_crtc()`, and `optc31_disable_crtc()`. The code operates on `struct timing_generator`, downcasts through `DCN10TG_FROM_TG()` to `struct optc`, and uses register helper macros (`REG_UPDATE`, `REG_SET`, `REG_GET`, `REG_WAIT`, sequenced register writes).

## Control Flow and State
Enable flow selects the local OPP source, enables VTG, then enables `OTG_MASTER_EN` through a register sequence. Disable flow clears all ODM segment sources to `0xf`, clears `OPTC_MEM_SEL`, disables `OTG_MASTER_EN` and VTG, waits for `OTG_BUSY == 0`, and clears underflow. Immediate disable differs by forcing disable point 0 and skipping the wait in diagnostic environment. ODM combine computes `OPTC_MEM_SEL` from segment width and OPP count, programs two- or four-segment source selection, sets segment width, and records `optc1->opp_count`. DRR programming sets mid/min/max vertical totals, configures TRIGA manual trigger masking, and clears min/max selection when disabled. Readback functions snapshot live OTG status/timing fields and a broad `dcn_optc_reg_state` register dump for diagnostics.

## Dependencies and Integration Points
Includes `dcn30_optc.h`, `reg_helper.h`, `dc.h`, and `dcn_calc_math.h`; the vtable references helpers from DCN10/DCN20/DCN30 (`optc1_*`, `optc2_*`, `optc3_*`). Resource files create OPTC instances, assign generated register/shift/mask tables from the matching header, and call this init function to bind behavior.

## Risks and Test Signals
Risks center on incorrect ODM memory-mask allocation, disable waits timing out, DRR off-by-one programming, and stale register-state mappings. Useful tests are display mode enable/disable, ODM 2:1 and 4:1 modes, VRR/DRR transitions with manual trigger, CRC and underflow debug checks, suspend/resume, and register-readback validation against hardware traces.
