<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.h

## Purpose

`dcn30_clk_mgr.h` declares DCN3 clock-manager construction/destruction and carries temporary DCN30 CLK register field definitions missing from generated headers.

## Important APIs, Types, And Functions

It declares `dcn3_init_clocks()`, `dcn3_clk_mgr_construct()`, and `dcn3_clk_mgr_destroy()`. It also defines several CLK PLL/DFS masks, shifts, and MMIO offsets for CLK0/CLK1/CLK2/CLK3 instances and AMCLK-related registers when the generated mask is absent.

## Control Flow

There is no runtime flow. The macros are consumed at compile time by DCN30 clock-manager code that reads VCO/DFS state.

## State And Persistence Behavior

The header owns no mutable state. The declared constructor allocates runtime `bw_params` and watermark GPU memory; destroy frees them.

## Dependencies And Integration Points

It integrates DCN30 resource construction with clock-manager internals and provides stopgap register definitions needed by implementation code.

## Risks

Temporary duplicated register definitions can drift from generated hardware headers. If the include guard around the fallback macros is wrong, stale masks or offsets could be used silently. Constructor/destroy declarations must remain synchronized with `dcn30_clk_mgr.c`.

## Test Signals

Build coverage, VCO readback sanity, clock-manager construction/destruction tests, and comparing fallback register constants against generated headers when they become available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.h -->
