<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.h

## Purpose

`rn_clk_mgr.h` exposes Renoir clock-manager construction and watermark table symbols.

## Important APIs, Types, And Functions

It declares external watermark tables for DDR4, LPDDR4, Green Sardine, disabled periodic retraining, and single-rank variants. It defines a small `rn_clk_registers` snapshot struct and declares `rn_clk_mgr_construct()`.

## Control Flow

The header has no runtime control flow. It lets the Renoir resource constructor instantiate the DCN2.1 clock manager and lets other compilation units provide watermark tables.

## State And Persistence Behavior

The header owns no state. The declared constructor initializes persistent manager state, selected watermark tables, SMU version fields, and DCCG clock data.

## Dependencies And Integration Points

It includes `clk_mgr.h`, `dm_pp_smu.h`, and `clk_mgr_internal.h`, tying it to the DC clock-manager and PP/SMU interfaces.

## Risks

External watermark table declarations must match exactly one definition elsewhere. The `rn_clk_registers` struct contains only one register and is not the full internal dump shape used in the C file, so it should not be treated as a complete ABI.

## Test Signals

Build/link coverage for watermark table definitions and Renoir resource construction. Runtime signals are in `rn_clk_mgr.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.h -->
