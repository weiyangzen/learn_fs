# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-ns2.c

## Purpose
Provides Northstar 2 iProc PLL descriptor tables and DT initialization hooks for genpll SCR, genpll SW, LCPLL DDR, and LCPLL ports clock blocks.

## Important APIs, Types, And Functions
This file defines register helper macros (`REG_VAL`, `AON_VAL`, `RESET_VAL`, `DF_VAL`, `VCO_CTRL_VAL`, `ENABLE_VAL`), `iproc_pll_ctrl` instances `genpll_scr`, `genpll_sw`, `lcpll_ddr`, and `lcpll_ports`, plus matching `iproc_clk_ctrl` channel arrays. Init functions `ns2_genpll_scr_clk_init`, `ns2_genpll_sw_clk_init`, `ns2_lcpll_ddr_clk_init`, and `ns2_lcpll_ports_clk_init` call `iproc_pll_clk_setup`.

## Control Flow
Each `CLK_OF_DECLARE` compatible invokes a small init wrapper at boot. The wrapper passes the appropriate PLL descriptor and channel array to the generic iProc PLL setup code, which maps resources, registers output clocks, and handles runtime PLL/channel operations.

## State And Persistence
All state in this file is static descriptor data. Runtime state is created by `clk-iproc-pll.c` and hardware registers. Most clocks are marked `IPROC_CLK_AON`, so the generic disable path will leave them running.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/bcm-ns2.h` indexes, `clk-iproc.h`, OF `CLK_OF_DECLARE`, and the shared iProc PLL provider. Device-tree `clock-output-names` must align with the array indexes.

## Risks And Edge Cases
The NS2 comments note that `bypass_shift` is not defined and is set to 0 because the shared code does not use it. Split status/control flag requires the DT resource layout expected by `iproc_pll_clk_setup`. Index holes for unused channels still need stable binding alignment.

## Test Signals
Boot-time provider registration for all four compatible strings, correct onecell indexes for used and unused channels, recalc rates from MDIV fields, and no disable effect on always-on outputs are useful checks.
