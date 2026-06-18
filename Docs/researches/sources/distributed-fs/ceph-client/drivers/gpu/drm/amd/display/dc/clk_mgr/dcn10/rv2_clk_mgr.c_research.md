<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.c

## Purpose

`rv2_clk_mgr.c` specializes the Raven2 DCN10 clock manager by reusing RV1 construction but replacing the internal clock setters with DCE112 register-based setters.

## Important APIs, Types, And Functions

The exported entry point is `rv2_clk_mgr_construct()`. The local `rv2_clk_internal_funcs` table maps `.set_dispclk` and `.set_dprefclk` to `dce112_set_dispclk()` and `dce112_set_dprefclk()`.

## Control Flow

Construction first calls `rv1_clk_mgr_construct()` to initialize all shared Raven clock-manager state, public callbacks, DPREF defaults, BIOS-derived VCO, spread-spectrum info, PP/SMU pointer, and DFS-bypass flags. It then overwrites `clk_mgr->funcs` with the RV2 internal table so later `update_clocks()` calls still use RV1 policy but program clocks through DCE112 helpers instead of the RV1 VBIOS-SMU DISPCLK mailbox.

## State And Persistence Behavior

The persistent state is inherited from RV1 construction. This file changes only the internal function table pointer, which changes future hardware programming behavior for the lifetime of the clock-manager instance.

## Dependencies And Integration Points

It depends on RV1 construction and DCE112 clock setter helpers. It is selected by ASIC/resource code for Raven2 hardware while preserving common RV1 update sequencing.

## Risks

The approach assumes RV2 differs only in the internal DISPCLK/DPREF programming mechanism. Any RV2-specific policy differences in voltage, DPP divider sequencing, or BIOS defaults would be hidden by the reused RV1 path. Because the static function table is file-local, tests need runtime coverage to confirm the correct constructor was selected.

## Test Signals

Raven2 display bring-up, DISPCLK/DPREFCLK register programming traces, suspend/resume, DPP divider transitions, and checks that VBIOS-SMU DISPCLK messages are not used on RV2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.c -->
