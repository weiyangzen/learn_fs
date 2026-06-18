# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-utmi.c

Purpose: UTMI clock provider generating a fixed 480 MHz USB PHY clock, with classic UCKR/SFR trim handling and a SAMA7G5-style XTAL frequency programming variant.

Important APIs and data: `at91_clk_register_utmi()` registers classic UTMI; `at91_clk_sama7g5_register_utmi()` registers the XTALF variant. `struct clk_utmi` stores PMC regmap, optional SFR regmap, and PM status.

Control flow: classic prepare reads parent `mainck` rate, maps 12/16/24/48 MHz to trim values, writes SFR trim when needed, enables UPLL/BIAS/count in `CKGR_UCKR`, and waits for `LOCKU`. unprepare clears `UPLLEN`. SAMA7G5 prepare maps 16/20/24/32 MHz to `PMC_XTALF` values and does not perform a lock wait.

State and persistence: UTMI rate is fixed. Save/restore records prepared state and re-runs prepare for active clocks; SAMA7G5 save checks whether `XTALF` matches current parent rate.

Dependencies and integration: used by legacy SAM9/SAMA5 setup, DT compat, and newer SAMA7 code. It depends on optional SFR syscon for non-12 MHz trims and `soc/at91/atmel-sfr.h`.

Risks: unsupported parent rates return `-EINVAL`; missing SFR regmap is fatal for nonzero classic trim; lock wait is unbounded. Test signals include `utmick` at 480 MHz, successful USB PHY lock, correct SFR trim or XTALF value, and restore after backup suspend.
