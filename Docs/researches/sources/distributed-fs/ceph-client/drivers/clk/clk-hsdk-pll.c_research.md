# sources/distributed-fs/ceph-client/drivers/clk/clk-hsdk-pll.c

Purpose: Synopsys HSDK PLL clock driver for ARC core, general-purpose, and HDMI PLLs. It maps requested rates to supported hardware PLL configurations and programs CGU registers.

Important APIs, types, and functions: `hsdk_pll_cfg` is a supported-rate table entry. `hsdk_pll_clk` stores MMIO register bases, optional core-specific register, device data, and clock hw. `hsdk_pll_devdata` selects a rate table and update callback. `hsdk_pll_ops` implements recalc, determine, and set-rate. `of_hsdk_pll_clk_setup()` registers the early core PLL; `hsdk_pll_clk_probe()` registers platform GP/HDMI PLLs.

Control flow: determine-rate chooses the nearest table rate. set-rate searches for an exact table entry and calls either common or core update. Common update writes PLL fields, delays 100 us, then checks lock and error bits. Core update also adjusts the core interface divider before or after the PLL transition depending on the 500 MHz threshold.

State and persistence: state is CGU PLL control/status registers and, for the core PLL, a special interface-divider register. No persistent software state exists beyond clock objects. The driver uses static tables rather than deriving arbitrary PLL parameters.

Dependencies and integration points: depends on platform resources, OF match data, early `CLK_OF_DECLARE` for CPU timer needs, common clock APIs, MMIO, and fixed parent count constraints.

Risks and test signals: common PLL probe does not map `spec_regs`, which is only needed by core data. Lock wait is a fixed delay followed by status checks, so slow hardware can fail with `-ETIMEDOUT`. Unsupported exact rates return `-EINVAL` even if determine-rate would round. Test signals include nearest-rate decisions, exact set-rate success, lock/error handling, and early core clock availability.
