# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll-s10.c

Purpose: shared PLL constructors and rate operations for Stratix10, Agilex, N5X, and Agilex5.

Important APIs/types/functions: family-specific PLL recalc functions, boot clock recalc/parent ops, prepare callbacks, ops tables, and constructors `s10_register_pll()`, `agilex_register_pll()`, `n5x_register_pll()`, `agilex5_register_pll()`.

Control flow: SoC descriptor drivers call a constructor for each PLL. The constructor allocates `socfpga_pll`, maps register offset, chooses boot/family ops, initializes parents, registers a `clk_hw`, and returns it for onecell insertion.

State and persistence behavior: per-PLL register pointer and power bit; hardware source/divider/feedback/reset state.

Dependencies/integration points: `stratix10-clk.h`, shared `clk.h`, CCF, and SoC platform drivers.

Risks: family/constructor mismatch yields wrong rates; boot parent mask handling deserves hardware validation; some formulas assume nonzero divisors from hardware.

Test signals: compare CCF rates with hardware/firmware on all families, test prepare reset deassertion, and inspect boot clock parent/divider behavior.
