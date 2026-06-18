<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/i2s_pll_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/axs10x/i2s_pll_clock.c

Purpose: This platform driver exposes the Synopsys AXS10x I2S PLL as a common-clock provider. It supports a fixed table of audio-related output rates for two supported parent oscillator rates.

Important APIs, types, and functions: `i2s_pll_cfg` stores output rate and register programming values for IDIV, FBDIV, ODIV0, and ODIV1. `i2s_pll_clk` stores MMIO base, `clk_hw`, and device pointer. Clock ops are `i2s_pll_recalc_rate()`, `i2s_pll_determine_rate()`, and `i2s_pll_set_rate()`. Probe is `i2s_pll_clk_probe()`, remove is `i2s_pll_clk_remove()`, and matching uses `"snps,axs10x-i2s-pll-clock"`.

Control flow: Probe allocates state, maps the PLL register resource, initializes one-parent `clk_init_data` using the DT node name, registers the clock with `devm_clk_register()`, and adds a simple OF provider. Rate determination selects a configuration table based on `best_parent_rate` (`27000000` or `28224000`) and accepts only exact table rates. Setting a rate writes all four PLL divider registers from the matching table entry.

State and persistence behavior: Runtime state is minimal and devm-managed. Hardware state persists in the PLL divider registers. The driver does not poll for lock or validate hardware status after writes; it assumes table entries are safe.

Dependencies and integration points: It depends on MMIO resources, a single parent clock in DT, and the common clock framework. It is a module-capable platform driver and exports the PLL clock through a simple provider.

Risks and test signals: Risks include unsupported parent rates, exact-rate matching that rejects near rates, no lock/status check, and recalc division by malformed zero register values if hardware is uninitialized. Test signals include successful DT binding, accepted common audio sample rates, correct recalc rate after programming, and audible/stable I2S operation at all table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/i2s_pll_clock.c -->
