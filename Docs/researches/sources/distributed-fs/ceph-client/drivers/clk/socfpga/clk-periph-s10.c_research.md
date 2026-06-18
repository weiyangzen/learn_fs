# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph-s10.c

Purpose: peripheral and counter clock constructors for Stratix10/Agilex/N5X/Agilex5.

Important APIs/types/functions: N5X/S10 counter recalc functions, `clk_peri_cnt_clk_recalc_rate()`, `clk_periclk_get_parent()`, constructors `s10_register_periph()`, `n5x_register_periph()`, `s10_register_cnt_periph()`, and `agilex5_register_cnt_periph()`.

Control flow: descriptor drivers allocate a peripheral clock, assign registers, divider/bypass/fixed-divider metadata, choose family ops, set parent names/data, and register with CCF.

State and persistence behavior: per-clock divider/bypass fields; parent is read from bypass first, then source field; hardware stores actual divider values.

Dependencies/integration points: `stratix10-clk.h`, shared `clk.h`, CCF, and SoC descriptor tables.

Risks: S10 recalc divides by raw low register bits and depends on hardware nonzero values; parent-name vs parent-data differences by family; N5X uses different field widths.

Test signals: recalc-rate comparisons for S10/Agilex/N5X/Agilex5, bypass parent reporting, and boot clock-summary checks.
