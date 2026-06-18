<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.h

## Purpose

`pll.h` declares the common Visconti PLL provider, rate-table, and registration APIs.

## Important APIs, Types, And Functions

`struct visconti_pll_provider` contains the register base, DT node, and flexible onecell clock data. `VISCONTI_PLL_RATE()` initializes `struct visconti_pll_rate_table` entries. `struct visconti_pll_info` maps clock ID, name, parent, base register, and rate table. The APIs are `visconti_init_pll()` and `visconti_register_plls()`.

## Control Flow

No executable flow exists. SoC files define rate tables and call the helper APIs during early OF setup.

## State And Persistence Behavior

The structs describe runtime state allocated by `pll.c`; hardware persistence remains in PLL registers.

## Dependencies And Integration Points

It depends on CCF, regmap type declarations, and spinlocks. TMPV770x PLL data is the direct user.

## Risks And Test Signals

Risks include sentinel-based rate tables missing a terminating zero and mismatched base offsets. Build tests catch API drift; runtime tests should verify provider size equals last binding ID plus one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.h -->
