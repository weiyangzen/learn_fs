# sources/distributed-fs/ceph-client/drivers/clk/davinci/da8xx-cfgchip.c

Purpose: exposes DA8xx/AM17xx/AM18xx CFGCHIP syscon bits as common-clock gates, muxes, special dividers, and USB PHY clocks.

Important APIs/types/functions: gate support uses `da8xx_cfgchip_gate_clk_info`, `da8xx_cfgchip_gate_clk`, and ops for enable/disable/is_enabled plus a `div4.5` recalc. Mux support uses `da8xx_cfgchip_mux_clk_info` and parent switching through `regmap_write_bits()`. USB-specific clocks are `da8xx_usb0_clk48` and `da8xx_usb1_clk48`, with USB0 prepare/enable sequencing, 48 MHz rate reporting, and PHY parent muxing. Platform dispatch uses `da8xx_cfgchip_of_match`, `da8xx_cfgchip_id_table`, and `da8xx_cfgchip_probe()`.

Control flow: probe obtains a CFGCHIP regmap from the parent syscon for DT or platform data for legacy devices, then calls a per-clock initializer. Initializers register tbclk, div4.5, async1, async3, or USB PHY clock providers. Legacy paths also install clkdev aliases and set default async3/USB parents to match existing boards.

State and persistence: hardware state is CFGCHIP register bits. Driver state is devm-managed `clk_hw` wrappers. USB0 enable temporarily enables its PSC functional clock while programming and waiting for PHY PLL lock.

Dependencies and integration points: depends on `mfd/da8xx-cfgchip.h`, syscon/regmap, `clkdev`, DT clock providers, platform data, and the DaVinci PSC/PLL clock names (`pll0_auxclk`, `pll1_sysclk2`, `async3`).

Risks: `da8xx_usb0_clk48_recalc_rate()` writes reference-frequency bits while recalculating rate, so a read-like clock operation mutates hardware. USB0 enable waits up to 500 ms for `PHYCLKGD`; failures propagate to consumers. Legacy default parent selection can fight board-specific assumptions if DT should have been used. Probe fails hard without regmap.

Test signals: validate probe on legacy and DT boards, async1/async3 parent selection, USB0 48 MHz lock behavior for all supported reference rates, USB1 parent muxing, and tbclk clkdev lookup for EHRPWM consumers.
