# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-cpus.c

Implements the Allwinner A80 CPUS composite clock. It combines a parent mux with a custom divider block that has an additional PLL4 predivider when PLL4 is selected.

`struct sun9i_a80_cpus_clk` stores `clk_hw` and the mapped register. `sun9i_a80_cpus_clk_recalc_rate()` reads the mux, applies the PLL4 predivider if parent index 3 is selected, and then applies the main divider. `sun9i_a80_cpus_clk_round()` chooses main divider and optional PLL4 predivider. `determine_rate` evaluates each parent, optionally asking parents to round if `CLK_SET_RATE_PARENT` is present, and picks the fastest child rate not exceeding the request. `set_rate` writes divider fields under a static spinlock. Setup creates a composite clock with standard mux ops and custom rate ops.

Mux and divider fields persist in the CPUS register. The global spinlock serializes mux/divider updates because the mux and divider share a register. It uses OF early registration, `clk_register_composite()`, `clk_mux_ops`, and the CCF rate-request API. It is exposed for compatible `allwinner,sun9i-a80-cpus-clk`.

The PLL4 predivider path is sensitive to parent index ordering in DT. `sun9i_a80_cpus_clk_round()` initializes `pre_div` as 1 but returns `pre_div - 1` for programming, so tests should cover non-PLL4 and PLL4 parents. Test signals include parent switching, requested rates across divider thresholds, and CPUS consumers retaining stable operation after set-rate.
