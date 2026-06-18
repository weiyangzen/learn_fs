<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sckc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sckc.c

Purpose: This file implements AT91 slow clock controller support for multiple SoC generations. It registers internal slow RC oscillators, external 32 kHz oscillators, and slow-clock muxes used by timer and low-power domains.

Important APIs, types, and functions: Custom clock types include `clk_slow_osc`, `clk_sama5d4_slow_osc`, `clk_slow_rc_osc`, and `clk_sam9x5_slow`, all wrapping `struct clk_hw`. The major operations are `clk_slow_osc_prepare/unprepare/is_prepared`, `clk_slow_rc_osc_prepare/unprepare/is_prepared/recalc_rate/recalc_accuracy`, and `clk_sam9x5_slow_set_parent/get_parent`. Registration helpers include `at91_clk_register_slow_osc()`, `at91_clk_register_slow_rc_osc()`, `at91_clk_register_sam9x5_slow()`, plus matching unregister helpers. DT entry points are `of_at91sam9x5_sckc_setup()`, `of_sama5d3_sckc_setup()`, `of_sam9x60_sckc_setup()`, and `of_sama5d4_sckc_setup()`.

Control flow: The SAM9x5/SAMA5D3 path maps the SCKC register, registers slow RC, resolves the crystal and bypass mode from either modern DT or backward-compatible child nodes, registers slow oscillator, creates `slowck` mux, and publishes a simple provider. The SAM9X60 path exposes onecell outputs for `md_slck` and `td_slck`. The SAMA5D4 path uses fixed-rate RC plus a special slow oscillator that tracks preparation in software rather than controlling enable bits directly.

State and persistence behavior: Hardware state is in SCKC control bits (`cr_rcen`, `cr_osc32en`, `cr_osc32byp`, `cr_oscsel`). Preparation delays use `udelay()` before `SYSTEM_RUNNING` and `usleep_range()` afterward. SAMA5D4 maintains a `prepared` boolean because its oscillator handling differs. Registered providers are early boot state and are not devm-managed.

Dependencies and integration points: This integrates with DT clock providers, `of_iomap()`, common clock framework ops, and clock IDs from `dt-bindings/clock/at91.h`. It feeds later AT91 PMC drivers that require `slowck`, `md_slck`, or `td_slck`.

Risks and test signals: Risks include incorrect startup delays, backward-compatible DT parsing regressions, slow-clock parent switch timing, and leaks on partial registration failure. Tests should check early timer boot, low-power clock parent selection, clock accuracy/rate reporting, old and new DT layouts, and absence of missing slow-clock parent errors in SAMA5/SAM9/SAMA7 PMC setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sckc.c -->
