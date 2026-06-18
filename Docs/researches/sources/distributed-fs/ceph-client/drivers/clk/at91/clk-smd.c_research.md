# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-smd.c

Purpose: provider for the SAM9x5 SMD clock, a parent-selectable divided clock controlled by `AT91_PMC_SMD`.

Important APIs and data: `at91sam9x5_clk_register_smd()` registers the clock. `struct at91sam9x5_clk_smd` stores regmap and `clk_hw`; ops implement recalc, determine, get/set parent, and set_rate.

Control flow: recalc reads `SMD_DIV` and divides parent by `div + 1`. determine-rate clamps to parent or searches divisors 1-16 for the closest rate. set_parent toggles `AT91_PMC_SMDS` between two parents. set_rate requires exact integer division in range and writes `SMD_DIV`.

State and persistence: live state is entirely in `AT91_PMC_SMD`; no explicit PM save/restore exists.

Dependencies and integration: AT91SAM9x5 SoC setup registers `smdclk` and exposes system `smdck`; DT compat can register it when `CONFIG_HAVE_AT91_SMD` is enabled.

Risks: `get_parent` returns the raw `AT91_PMC_SMDS` bit value, which is suitable only if the bit encodes 0/1; no parent-count validation in set_parent beyond index > 1. Test signals include SMD rate and parent in clk_summary, SMD_DIV register values, and SMD consumers receiving exact supported rates.
