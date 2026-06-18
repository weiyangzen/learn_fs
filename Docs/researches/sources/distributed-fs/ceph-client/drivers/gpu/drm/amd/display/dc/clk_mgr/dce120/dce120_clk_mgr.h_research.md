# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce120/dce120_clk_mgr.h

## Purpose
This header declares DCE12 and DCE12.1 clock-manager constructors.

## Important APIs, Types, And Functions
- `dce120_clk_mgr_construct()` constructs the base DCE12 manager.
- `dce121_clk_mgr_construct()` constructs the Vega20/DCE12.1 variant with adjusted DPREFCLK and XGMI handling.

## Control Flow
No runtime flow is implemented in the header.

## State And Persistence
No state is declared. Constructors initialize `struct clk_mgr_internal` instances.

## Dependencies And Integration Points
It is included by `clk_mgr.c` for FAMILY_AI clock-manager selection.

## Risks
Constructor declaration drift would break AI-family factory wiring. The header intentionally exposes only constructors, so DCE12 internals remain private.

## Test Signals
Build/link coverage plus AI/Vega20 runtime constructor selection validate this header.
