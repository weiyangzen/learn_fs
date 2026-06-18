# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.h

## Purpose
This header declares the DCE112 clock-manager constructor and split clock-programming helpers.

## Important APIs, Types, And Functions
It declares `dce112_clk_mgr_construct()`, `dce112_set_clock()`, `dce112_set_dispclk()`, and `dce112_set_dprefclk()`.

## Control Flow
No executable flow is present.

## State And Persistence
No state is declared. Functions operate on `clk_mgr` and `clk_mgr_internal` objects.

## Dependencies And Integration Points
It is included by `clk_mgr.c` and DCE120 manager code, making DCE112 `SetDCEClock` helpers shared with later DCE12.

## Risks
Any change to these helper signatures affects DCE120 and factory construction. The split helper APIs expose partially programmed states if used incorrectly.

## Test Signals
Compile coverage plus runtime DCE112/DCE120 clock programming validate the shared API.
