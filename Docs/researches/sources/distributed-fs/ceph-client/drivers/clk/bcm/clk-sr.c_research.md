# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-sr.c

## Purpose
Provides Broadcom Stingray iProc PLL descriptor tables and platform-driver dispatch for multiple GENPLL and LCPLL blocks, plus an early OF declaration for GENPLL3.

## Important APIs, Types, And Functions
The file defines descriptor helper macros and static `iproc_pll_ctrl`/`iproc_clk_ctrl` arrays for `sr_genpll0`, `sr_genpll2`, `sr_genpll3`, `sr_genpll4`, `sr_genpll5`, `sr_lcpll0`, `sr_lcpll1`, and `sr_lcpll_pcie`. Per-block init functions call `iproc_pll_clk_setup`. `sr_clk_dt_ids`, `sr_clk_probe`, and `sr_clk_driver` dispatch platform probes using `of_device_get_match_data`.

## Control Flow
For most Stingray PLL nodes, the built-in platform driver probes, extracts the function pointer from the match table, and runs the matching init function. `sr_genpll3_clk_init` is instead registered through `CLK_OF_DECLARE`. The common iProc provider handles resource mapping, PLL programming, channel registration, and runtime callbacks.

## State And Persistence
This file is static SoC metadata. Runtime state is allocated by `iproc_pll_clk_setup`; hardware retains PLL and channel divider state. Many outputs are flagged `IPROC_CLK_AON`, and several PLLs require `IPROC_CLK_PLL_NEEDS_SW_CFG` before programming.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/bcm-sr.h`, `clk-iproc.h`, OF match data, and built-in platform driver registration. It integrates with the shared iProc PLL engine and common clock consumers.

## Risks And Edge Cases
The mixed early-declare and platform-driver model means init ordering differs between GENPLL3 and other PLLs. Descriptor copy-paste errors in shifts or channel indexes directly affect hardware programming. Missing match data returns `-ENODEV`.

## Test Signals
Probe each compatible string, verify channel indexes match binding enums, confirm software override bits are written for flagged PLLs, ensure always-on channels ignore disable, and check rate recalc/set behavior for fractional and integer-only PLLs.
