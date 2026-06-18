# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-plldiv.c

Purpose: small provider for the PLLA divide-by-two selector controlled by `AT91_PMC_PLLADIV2` in `MCKR`.

Important APIs and data: `at91_clk_register_plldiv()` registers a single-parent clock with `plldiv_ops`. The private struct stores `clk_hw` and PMC regmap.

Control flow: recalc reads `MCKR` and returns parent or parent/2. Determine-rate chooses whichever of parent and parent/2 is closer to the request. set-rate validates exact parent or half-parent and updates `PLLADIV2`.

State and persistence: hardware bit is the only persistent divider state; the clock object keeps the regmap pointer. No save/restore hooks are implemented.

Dependencies and integration: used by AT91SAM9G45, SAM9N12, SAM9x5, SAMA5D2, and DT compat setup before master/USB/programmable clocks consume `plladivck`.

Risks: exact-rate validation means callers must use determine/round before set; no explicit ready wait after MCKR update. Test signals include `plladivck` rate in clk_summary, MCKR bit changes, and downstream master/USB clocks selecting correct parent rates.
