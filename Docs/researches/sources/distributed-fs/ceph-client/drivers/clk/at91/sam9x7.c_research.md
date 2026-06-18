# sources/distributed-fs/ceph-client/drivers/clk/at91/sam9x7.c

Purpose: SAM9X7 PMC setup for a richer clock tree with PLLA, UPLL, audio PLL, LVDS PLL, PLLA DIV2, master clock, generated clocks with non-linear mux IDs, peripherals, and system gates.

Important APIs and data: `sam9x7_pmc_setup()` is selected by `"microchip,sam9x7-pmc"`. It defines PLL ID/type enums, multiple PLL characteristic/range sets, fractional/divider layouts including DIVPMC and DIVIO, descriptor table `sam9x7_plls`, system/peripheral tables, and a large GCK descriptor table with per-clock PLL parents and mux hardware values.

Control flow: setup resolves three parent clocks, maps the PMC, allocates `pmc_data`, allocates a mux-table tracking buffer, registers RC/main oscillators and `mainck`, iterates PLL descriptors to register frac/div clocks and export selected outputs, registers master pres/div, USB, two programmable clocks, system clocks, PCR peripherals, then builds per-GCK mux tables and registers generated clocks.

State and persistence: allocated mux tables are intentionally retained after success because generated clocks keep pointers to them; the tracking buffer itself is freed. Critical PLLA/DIV2 and DDR/MPDDR clocks protect CPU/timer/memory domains. Provider-level PM callbacks handle active PLL/peripheral/generated state.

Dependencies and integration: uses SAM9X60 PLL provider, PCR generated/peripheral providers, and `PMC_INIT_TABLE`/`PMC_FILL_TABLE`. It sometimes obtains parent hardware with `of_clk_get_by_name()` for descriptor parents outside local handles.

Risks: `char pp_mux_table[8]` feeds `u32` mux tables; values must remain positive and small. Error paths free only mux tables tracked so far and `pmc_data`, not registered clocks. Test signals include all exported PLL indices (`PMC_PLLACK`, `PMC_AUDIOPMCPLL`, `PMC_AUDIOIOPLL`, `PMC_LVDSPLL`, `PMC_PLLADIV2`), GCK parent hardware IDs, USB parent selection, and LVDS/audio consumers.
