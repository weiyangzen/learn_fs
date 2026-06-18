<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll-tmpv770x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/pll-tmpv770x.c

## Purpose

`pll-tmpv770x.c` supplies TMPV770x PLL rate tables and early OF registration for the Visconti PLL controller.

## Important APIs, Types, And Functions

It defines rate tables for `pipll0`, `piddrcpll`, `pivoifpll`, and `piimgerpll`, each with divider and fractional parameters through `VISCONTI_PLL_RATE`. `pll_info[]` maps binding IDs, names, parent `osc2-clk`, base offsets, and rate tables. `tmpv770x_setup_plls()` maps registers, initializes the common PLL provider, registers fixed-rate `pipll1`, `pidnnpll`, and `pietherpll`, and registers programmable PLLs.

## Control Flow

`CLK_OF_DECLARE()` matches `toshiba,tmpv7708-pipllct` during early clock init. If mapping or provider allocation fails, setup returns without registering the provider.

## State And Persistence Behavior

PLL register state persists in the PIPLLCT block. Provider state is allocated permanently for early boot. Fixed-rate PLLs are modeled as software constants.

## Dependencies And Integration Points

It depends on TMPV770x clock binding IDs, `pll.h` common helpers, OF address mapping, and a shared PLL spinlock.

## Risks And Test Signals

Risks include incomplete provider registration if `visconti_register_plls()` does not add an OF provider, rate-table ordering assumptions, and hard-coded fixed PLL rates. Test PLL rate changes for each table entry, fixed PLL parent availability to PISMU, and boot with missing MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll-tmpv770x.c -->
