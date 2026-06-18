# sources/distributed-fs/ceph-client/drivers/clk/clk-nomadik.c

Purpose: ST-Ericsson Nomadik SRC clock implementation. It initializes oscillator policy, exposes PLL and source-gated clocks, registers HCLK divider clocks, and provides debugfs visibility.

Important APIs, types, and functions: `nomadik_src_init()` maps the SRC block, configures timer clock source bits, handles DT oscillator-disable properties, and registers a reboot notifier. `clk_pll` and `pll_clk_ops` model PLL1/PLL2. `clk_src` and `src_clk_ops` model peripheral gates with separate enable/disable/status registers. OF setup functions register PLL, HCLK divider, and SRC clocks.

Control flow: each OF clock setup lazily calls `nomadik_src_init()` if the SRC base is not mapped. PLL enable/disable updates `SRC_PLLCR`, respecting PLL1 override semantics. SRC enable writes the enable register and spins until status is set; disable writes the disable register and spins until status clears. Reboot handler force-enables the main crystal so reset can complete.

State and persistence: global `src_base` and boot debugfs snapshots persist for the system lifetime. Hardware state includes oscillator control, PLL control, peripheral enable/status registers, and divider bits. A spinlock protects `SRC_CR`/PLL RMW operations.

Dependencies and integration points: depends on OF early clocks, MMIO, reboot notifier, common clock divider helper, debugfs/seq_file when enabled, and Nomadik DT properties.

Risks and test signals: enable/disable loops have no timeout. The reboot notifier depends on `src_base` being initialized. Debugfs captures boot state after SRC init only. Test signals are oscillator DT property effects, PLL rate recalc, peripheral gate status transitions, HCLK divider rate, reboot path, and debugfs output.
