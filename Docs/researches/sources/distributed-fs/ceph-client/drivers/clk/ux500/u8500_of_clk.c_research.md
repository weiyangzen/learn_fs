<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/u8500_of_clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/u8500_of_clk.c

## Purpose

`u8500_of_clk.c` is the U8500 clock-tree definition and DT provider setup. It registers PRCMU clocks, PRCC peripheral and kernel gates, fixed clocks, external clkout providers, and the PRCC reset controller for `stericsson,u8500-clks`.

## Important APIs, Types, And Functions

`ux500_twocell_get()` resolves PRCC `<base bit>` clock specifiers. `ux500_clkout_get()` lazily creates `clkout1` or `clkout2` from `<id source divider>` specifiers. `u8500_clk_init()` is the large setup routine. It fills `u8500_prcmu_hw_clks`, registers PLL and firmware clocks such as `soc0_pll`, `uartclk`, `lcdclk`, `sdmmcclk`, `armss`, creates fixed `rtc32k` and `smp_twd`, registers dozens of PRCC pclk/kclk gates, and attaches child providers.

## Control Flow

`CLK_OF_DECLARE()` invokes setup during early OF clock init. The function allocates reset state, reads CLKRST resources, registers PRCMU sources based partly on PRCMU firmware project, builds PRCC clock arrays with helper macros, then scans child nodes by name to install the correct provider or reset controller.

## State And Persistence Behavior

Static arrays persist the PRCC pclk/kclk handles and `clkout` handles. PRCMU and PRCC hardware/firmware retain actual enable, rate, parent, and reset state. `clkout` registration is one-shot per output; later requests return the existing configuration.

## Dependencies And Integration Points

It integrates DT, PRCMU firmware, PRCC MMIO gates, fixed clocks, and Linux reset framework. Consumers use child nodes named `prcmu-clock`, `clkout-clock`, `prcc-periph-clock`, `prcc-kernel-clock`, `rtc32k-clock`, `smp-twd-clock`, and `prcc-reset-controller`.

## Risks And Test Signals

Risks include missing CLKRST resources leaving bad bases, firmware-project-specific `sgclk` parent selection, static arrays indexed by physical PRCC numbers, and clkout requests being non-reconfigurable. Test full boot, DT clock lookup for PRCMU and PRCC cells, clkout validation, reset-controller registration, and peripheral enablement for UART/I2C/SDI/MSP/GEM-like users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/u8500_of_clk.c -->
