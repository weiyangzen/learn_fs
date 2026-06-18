# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-periph.c

Purpose: Armada 37xx peripheral clock driver for northbridge/southbridge composite clocks, including mux/divider/gate combinations and a DVFS-aware CPU clock.

Important APIs/functions: `armada_3700_periph_clock_probe` registers all clocks described by match data. `armada_3700_add_composite_clk` adapts static mux/rate/gate templates to the mapped register base and calls `clk_hw_register_composite`. Custom ops include `clk_double_div_ops` and `clk_pm_cpu_ops`.

Control flow: match data selects NB or SB clock tables. Probe maps registers, initializes a lock, converts template register offsets to real MMIO addresses, handles special PM CPU mux/rate setup via the NB PM syscon, registers composites, and publishes a onecell provider. Suspend stores selector/divider/gate registers; resume writes them back in ATF-compatible order.

State and persistence: driver data stores hardware register snapshots for sleep. Runtime clock state is hardware-backed. `clk_pm_cpu` keeps an `l1_expiration` jiffies value for the high-frequency DVFS workaround.

Dependencies and integration: CCF composite clocks, syscon/regmap for NB PM, platform compatibles for NB/SB periph clocks, TBG parent clocks, and noirq system sleep PM.

Risks: `get_div` can return zero for invalid encodings, leading to division by zero in rate recalculation. Static template objects are mutated at probe, so multiple instances of the same data set would conflict. CPU DVFS set-rate returns `rate` instead of zero on success.

Test signals: NB and SB provider registration, all composite indexes, suspend/resume register restore, CPU DVFS level transitions including 20 ms L1 workaround, and invalid divider handling.
