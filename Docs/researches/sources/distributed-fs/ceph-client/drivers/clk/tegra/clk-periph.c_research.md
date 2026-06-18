# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph.c

Composes Tegra peripheral clocks from mux, divider, and gate subcomponents while presenting them as one CCF clock.

Wrapper ops delegate parent operations to embedded mux ops, rate operations to embedded fractional divider ops, and enable operations to embedded peripheral gate ops after binding each sub-hw to the top-level clock. Three operation tables cover full mux/div/gate clocks, no-divider clocks, and no-gate clocks. `_tegra_clk_register_periph()` selects the right ops from flags, initializes register pointers, gate bank metadata, and shared refcount storage, registers the top-level clock, then backfills subcomponent `hw.clk` pointers. Public helpers register normal, no-divider, or data-table-driven periph clocks.

State is distributed across a mux/divider register, CAR gate registers, and the shared gate refcount array. Restore context reprograms divider and parent after suspend when applicable. Dependencies include `tegra_clk_frac_div_ops`, Tegra mux ops, `tegra_clk_periph_gate_ops`, global `periph_clk_enb_refcnt`, and SoC initialization tables.

Subcomponent `__clk_hw_set_clk()`/`hw.clk` binding is essential for CCF parent/rate helpers. Flag combinations such as no-div/no-gate change operation exposure. Test signals include parent switching, fractional rate programming, gate reference counting, and context restore after suspend.
