<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn351_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn351_clk_mgr.c

## Purpose
Specializes DCN35 clock-manager construction for DCN351 register offsets and masks before delegating to the shared DCN35 implementation.

## Important APIs, Types, And Functions
- `clk_mgr_regs_dcn351`, `clk_mgr_shift_dcn351`, and `clk_mgr_mask_dcn351` define the DCN351-specific register access table using `CLK_REG_LIST_DCN35` and DCN32-style masks.
- `dcn351_clk_mgr_construct` installs those register tables into the embedded `clk_mgr_internal`, then calls `dcn35_clk_mgr_construct`.

## Control Flow
Construction is a two-step wrapper: preseed DCN351 register metadata, then reuse the generic DCN35 constructor. The shared constructor preserves these tables when `ctx->dce_version == DCN_VERSION_3_51`.

## State And Persistence
The only persistent state set here is the register/shift/mask pointer trio in `clk_mgr->base`, which all later `REG_*` helpers use for clock register access.

## Dependencies And Integration Points
Depends on `dcn35_clk_mgr.h`, DCN35 register-list macros, DCN32 common mask-list macros, and the shared `dcn35_clk_mgr_construct` path. It integrates DCN351 ASIC setup with the DCN35 clock-manager code.

## Risks And Edge Cases
Wrong register offsets would corrupt all subsequent clock reads/writes. The wrapper relies on the shared constructor not overwriting register tables for DCN_VERSION_3_51. Any new DCN351-only registers must be reflected here before construction.

## Test Signals
DCN351 boot should show correct boot snapshot/current clock reads, successful SMU DPM import using DCN351 translation, and no fallback to DCN35 register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn351_clk_mgr.c -->
