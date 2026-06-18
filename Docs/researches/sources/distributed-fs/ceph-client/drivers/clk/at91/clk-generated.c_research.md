# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-generated.c

Purpose: provider for AT91 generated clocks (`GCK`) controlled through the PMC PCR register. These are per-peripheral mux/divider clocks with optional rate-changing parent support for audio-capable generated clocks.

Important APIs and data: `at91_clk_register_generated()` creates a `struct clk_generated` with PCR layout, mux table, range, parent id, divider, and optional `chg_pid`. Ops cover enable/disable, is_enabled, recalc, determine, set_parent, set_rate, save/restore.

Control flow: registration initializes local `parent_id` and `gckdiv` from hardware via `clk_generated_startup()`. Enable writes PCR PID, parent selector, divider, command, and `GCKEN` under `pmc_pcr_lock`; disable clears `GCKEN`. Determine-rate first searches fixed parents and divider 1-256, then optionally forwards parent-rate requests to a changeable parent such as audio PLL.

State and persistence: parent and divider changes are staged in memory because `CLK_SET_RATE_GATE` and `CLK_SET_PARENT_GATE` ensure hardware is modified at enable time. Save/restore stores whether the clock was enabled and replays PCR setup only when previously active.

Dependencies and integration: used by SAMA5D2, SAM9X60, SAM9X7, and DT compat. It relies on `clk_pcr_layout`, `field_prep/get`, regmap, and caller-provided parent arrays/mux tables.

Risks: debug logging dereferences `req->best_parent_hw` after searches, so logic must ensure a valid best parent; mux-table correctness is critical for SAM9X7 non-linear parent values; range max/min silently clamps requests. Test signals include GCK rates under clk_summary, PCR register parent/div fields, audio PLL parent-rate changes for I2S/ClassD, and suspend/resume restore of enabled GCKs.
