# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa3xx.c

## Purpose
`clk-pxa3xx.c` registers the Marvell PXA3xx clock tree for legacy, mostly non-devicetree PXA platforms, with a small DT entry point for `marvell,pxa300-clocks`. It models the 13 MHz oscillator, 32.768 kHz oscillator, ring oscillator, system PLL, core PLL, run/core/system-bus muxes, AC97 and static-memory clocks, plus CKEN-gated peripheral clocks.

## Important APIs, Types, And Functions
Important exported or external entry points are `pxa3xx_get_clk_frequency_khz()`, `pxa3xx_clk_update_accr()`, `pxa3xx_clocks_init()`, and the `CLK_OF_DECLARE()` init hook. The file builds `desc_clk_cken` tables for common PXA3xx devices and PXA300/PXA310, PXA320, and PXA93x variants. Rate helpers include `clk_pxa3xx_ac97_get_rate()`, `clk_pxa3xx_smemc_get_rate()`, `clk_pxa3xx_system_bus_get_rate()`, `clk_pxa3xx_core_get_parent()`, `clk_pxa3xx_run_get_rate()`, and `clk_pxa3xx_cpll_get_rate()`.

## Control Flow, State, And Persistence
Global state is the mapped `clk_regs` pointer. Init records the register base, registers fixed/factor PLL roots, derived core and bus clocks, dummy compatibility clocks, and CKEN gates. CPU identification chooses the variant-specific CKEN table. Runtime state is entirely hardware register backed: ACCR/ACSR select PLL ratios, turbo mode is read through CP14 XCLKCFG, CKENA/CKENB gate peripherals, and `pxa3xx_clk_update_accr()` writes ACCR then busy-waits until ACSR reflects masked bits.

## Dependencies, Integration Points, Risks, And Test Signals
The file depends on PXA common clock helpers, clkdev names used by legacy platform devices, `cpu_is_pxa*()` SoC detection, SMEMC memory-divider helpers, MMIO, CP14 instructions, and DT clock binding IDs. Risks include indefinite waits if ACCR changes never settle, division by zero from malformed hardware state, fragile legacy device-name lookup, and a stray `pr_info()` in CPLL rate calculation that can spam logs. Test signals include boot on PXA300/310/320/93x, expected `/sys/kernel/debug/clk` rates, peripheral probe success for UART/I2C/MMC/USB/AC97/LCD, DT clock provider registration, and frequency-change paths reaching matching ACSR values.
