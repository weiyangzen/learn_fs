# sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-aspeed.c

Purpose: this driver supports AST2400/AST2500 SCU clocks and resets. It registers early core clocks through `CLK_OF_DECLARE_DRIVER` and later registers gates/resets through a built-in platform driver.

Important functions/types: PLL helpers `aspeed_ast2400_calc_pll()` and `aspeed_ast2500_calc_pll()` translate HPLL/MPLL register values to fixed-factor clocks. Gate callbacks implement reset-before-enable sequencing for IPs with reset bits. Reset callbacks map reset IDs to SCU04 or SCUD4 bits. `aspeed_clk_probe()` registers the reset controller, UART/MPLL/SD/MAC/LHCLK/BCLK/ECLK clocks, AST2500 RMII gates, and every `aspeed_gates` entry. `aspeed_cc_init()` maps the SCU, initializes `aspeed_clk_data` with `-EPROBE_DEFER`, registers early `clkin`, `hpll`, `ahb`, and `apb`, then exposes a onecell provider.

Control flow/state: global `aspeed_clk_data` and `scu_base` bridge early OF initialization to platform probe. Hardware state is in SCU reset, stop, strap, selection, and PLL registers.

Risks and tests: several registered clocks are not device-managed in early init. Integer PLL calculation for AST2500 uses `(m + 1) / (n + 1)` before applying `p`, losing fractional precision. Gate enable intentionally toggles reset with delays; incorrect reset index can disrupt devices. Test signals include AST2400/2500 boot, deferred consumers resolving after platform probe, reset sequencing for USB/MAC/video, and clock-rate validation from straps.
