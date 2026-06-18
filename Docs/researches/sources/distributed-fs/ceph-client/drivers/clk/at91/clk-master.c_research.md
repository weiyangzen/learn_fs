# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-master.c

Purpose: provider for AT91 master clocks, split into prescaler and divider stages for legacy PMC layouts plus an integrated SAMA7G5-style master clock. It enforces SoC-specific master output ranges and supports safe divider notifiers.

Important APIs and data: exported helpers include `at91_clk_register_master_pres()`, `at91_clk_register_master_div()`, `at91_clk_sama7g5_register_master()`, and layout constants `at91rm9200_master_layout` and `at91sam9x5_master_layout`. `struct clk_master` stores regmap, lock, layout, characteristics, cached parent/div, mux table, and PM state.

Control flow: prepare waits for `MCKRDY`/`MCKXRDY`. Legacy pres recalc decodes CSS and prescaler; legacy div recalc decodes MCKR divider. Changeable div mode can program hardware and registers a notifier to switch to a safe divider before parent changes and restore the highest safe rate afterward. SAMA7G5 ops search parent/div pairs, stage parent/div in memory, and program `MCR_V2` on enable.

State and persistence: save/restore records parent/rate expectations and warns if firmware did not preserve them, or reprograms changeable dividers. SAMA7G5 stores enable status and replays setup if enabled.

Dependencies and integration: called by all SoC setup files and shared with newer SAMA7 code. It depends on regmap, spinlocks, common-clock notifier API, layout masks, and characteristic divisor arrays.

Risks: `master_div` is a single global notifier target, so only one safe-div master is supported; unbounded ready waits can hang if hardware never signals; wrong divisors can overclock the CPU/matrix. Test signals include rate-change notifier behavior, MCKR/MCR register values, warnings about over/underclock, and suspend/resume messages about firmware clock preservation.
