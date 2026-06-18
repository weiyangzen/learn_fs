# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-pll.h

## Purpose
`clk-pll.h` defines the shared Meson PLL data model used by PLL clock-controller declarations and exposes the PLL common-clock ops.

## Important APIs, Types, And Functions
`struct pll_params_table` stores one M/N pair and is usually populated through `PLL_PARAMS(_m, _n)`. `struct pll_mult_range` declares a legal multiplier range. `struct meson_clk_pll_data` describes all PLL bitfields, optional init sequences, parameter tables or ranges, fractional maximum, and flags. Flags are `CLK_MESON_PLL_ROUND_CLOSEST` and `CLK_MESON_PLL_NOINIT_ENABLED`. The header declares read-only, mutable, and PCIe PLL ops.

## Control Flow
The header contains no runtime logic. It establishes the structure consumed by `clk-pll.c`; SoC files choose either table-driven or range-driven settings and supply any required init sequence.

## State, Persistence, And Dependencies
The header is stateless and depends on `clk-provider.h`, `regmap.h`, and `parm.h`. Runtime persistence is in hardware registers pointed to by the `parm` descriptors and in static parameter/init tables.

## Integration Points
Included by Meson SoC PLL description files. The exported ops connect static SoC descriptors to Linux common clock framework behavior.

## Risks And Edge Cases
Descriptors must not provide inconsistent tables/ranges, invalid bit widths, or init counts. Missing optional `rst`, `frac`, `current_en`, or `l_detect` fields are supported only because the implementation checks applicability. Table arrays require a sentinel entry with `n == 0`.

## Test Signals
Build coverage of every PLL descriptor, review of table sentinels and bit widths, and runtime PLL rate/lock tests are the main signals.
