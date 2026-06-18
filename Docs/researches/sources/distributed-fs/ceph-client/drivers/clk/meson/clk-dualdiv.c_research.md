# sources/distributed-fs/ceph-client/drivers/clk/meson/clk-dualdiv.c

## Purpose
`clk-dualdiv.c` implements the Meson dual-divider clock type, originally used in always-on domains to derive precise low-frequency clocks such as 32.768 kHz for suspend, RTC, and CEC. The hardware can run either a single divider or alternate between two divider/counter pairs.

## Important APIs, Types, And Functions
The exported APIs are `meson_clk_dualdiv_ops` and `meson_clk_dualdiv_ro_ops`. `__dualdiv_param_to_rate()` computes the effective rate from table parameters. `meson_clk_dualdiv_recalc_rate()` reads the `dual`, `n1`, `m1`, `n2`, and `m2` fields from hardware. `__dualdiv_get_setting()` searches the static table for exact or closest settings. `determine_rate` reports the achievable rate, and `set_rate` writes the chosen table values minus one into the hardware fields.

## Control Flow
Rate selection is table-driven. Determine-rate and set-rate both call `__dualdiv_get_setting()`. Exact matches return immediately; otherwise the table entry with the smallest absolute rate error is selected. Set-rate rejects controllers without a table, then writes all five parameter fields. The read-only ops omit `set_rate` and only expose initialization and recalculation.

## State, Persistence, And Dependencies
State persists in the dual-divider register fields described by `struct meson_clk_dualdiv_data`. The implementation depends on `clk-regmap.h`, `clk-dualdiv.h`, `parm.h`, regmap-backed field helpers, Linux common clock registration, and rate rounding helpers. Table entries are expected to end with a sentinel where `n1 == 0`.

## Integration Points
C3 peripheral RTC clocks and G12A AO RTC/CEC clocks instantiate this helper. Consumers see it as a normal common-clock divider-like node whose exact behavior is constrained by the provided hardware-valid table.

## Risks And Edge Cases
If no table is provided, `determine_rate()` falls back to the current hardware rate but `set_rate()` fails with `-EINVAL`. The closest-rate calculation initializes `best` to zero; for very low target rates the absolute-difference comparison still converges, but table quality determines the result. All written values subtract one, so table entries must use human divider/count values, not raw bit encodings.

## Test Signals
Tests should verify exact and closest matches for the 32 kHz tables, recalc from programmed raw fields, set-rate writes for single and dual modes, missing-table behavior, and sentinel handling.
