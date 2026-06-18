# sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-ast2600.c

Purpose: this driver supports AST2600/G6 SCU clocks and resets. It follows the older Aspeed split between early clock provider setup and platform-probed gates, but adapts for two stop/reset registers, more gates, and silicon revision differences.

Important functions: `ast2600_calc_pll()` and `ast2600_calc_apll()` decode PLL registers, with APLL behavior depending on `soc_rev`. `get_bit()`, `get_reset_reg()`, and `get_clock_reg()` handle indices across two 32-bit registers. Gate ops use write-to-set and set-to-clear register semantics plus reset sequencing. Reset ops expose 64 reset IDs. `aspeed_g6_clk_probe()` registers UART/UARTX fixed rates, eMMC/SD/MAC/LHCLK/D1/BCLK/VCLK/ECLK clocks and all gate descriptors. `aspeed_g6_cc_init()` maps SCU, reads revision, initializes onecell data with `-EPROBE_DEFER`, registers early PLL/AHB/APB/USB/I3C/FSI clocks, and adds the provider.

Control flow/state: global `aspeed_g6_clk_data`, `scu_g6_base`, and `soc_rev` persist across early and platform phases. Hardware state is in strap, PLL, selection, stop, and reset registers.

Risks and tests: many clocks are deferred until platform probe, so consumers must tolerate `-EPROBE_DEFER`. The code writes clock selection registers for D1 and I3C, changing bootloader configuration. PLL math uses integer division in fixed-factor registration. Test signals include AST2600 revisions A0/A1/A2, I3C/FSI clocks, MAC1-4, eMMC/SD, reset sequencing, and `clk_summary` after probe.
