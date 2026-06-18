<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.h

## Purpose

`dcn20_clk_mgr.h` exposes the DCN2 shared clock-manager helpers used by DCN20 and later derived managers.

## Important APIs, Types, And Functions

It declares `dcn2_update_clocks()`, `dcn2_update_clocks_fpga()`, `dcn20_update_clocks_update_dpp_dto()`, `dcn2_init_clocks()`, `dcn20_clk_mgr_construct()`, `dentist_get_did_from_divider()`, `dcn2_get_clock()`, `dcn20_update_clocks_update_dentist()`, and `dcn2_read_clocks_from_hw_dentist()`.

## Control Flow

There is no runtime flow in the header. It enables derived clock managers such as DCN201, Renoir, DCN30, Van Gogh, and DCN31 to reuse DCN20 DPP DTO and DENTIST helpers.

## State And Persistence Behavior

No state is owned. The declared functions operate on `clk_mgr`, `clk_mgr_internal`, `dc_state`, DCCG, and hardware registers.

## Dependencies And Integration Points

It sits at the boundary between generic DCN clock code and ASIC-specific managers. It must be included where derived managers need shared DENTIST/DTO behavior.

## Risks

Because many later files call these helpers, signature or semantic changes have broad impact. `dcn2_update_clocks()` is declared with parameter name `dccg` despite taking `struct clk_mgr *`, a readability issue but not functional.

## Test Signals

Build coverage across all DCN2/DCN3 managers and runtime tests in any derived manager that exercises DENTIST and DPP DTO sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.h -->
