# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-pll-out.c

Implements Tegra PLL output gate/reset clocks. These are child outputs of PLLs controlled by enable and reset bits in a shared register.

`tegra_clk_pll_out_ops` implements is_enabled, enable, disable, and restore_context. Enable sets both output enable and reset bits under an optional spinlock and delays briefly. Disable clears both bits. Restore context uses the CCF enable count to decide whether to re-enable or disable after context loss. `tegra_clk_register_pll_out()` allocates and registers the output clock.

Output enable/reset state persists in the PLL output register. Software stores the bit indices, flags, and optional lock. The code depends on CCF registration, MMIO, and Tegra PLL setup code that creates named PLL outputs for consumers.

The meaning of reset bit polarity is encoded in `is_enabled()` and enable/disable; wrong bit indices break child outputs. Test signals include output enable counts after suspend/resume, register bit readback, and downstream consumers receiving expected PLL-derived rates.
