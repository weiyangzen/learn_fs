# sources/distributed-fs/ceph-client/drivers/clk/spear/spear6xx_clock.c

## Purpose
Builds the SPEAr6xx clock tree for the ARM platform clock framework. It provides root oscillators, PLLs, bus clocks, synth-backed muxes, peripheral gates, and clkdev aliases for SPEAr600-class devices.

## Important APIs, Types, And Functions
The exported initializer is `spear6xx_clk_init(void __iomem *misc_base)`. It defines hardware register offsets and masks, parent arrays for CLCD/FIRDA/UART/GPT/DDR, and three rate tables: `pll_rtbl`, `aux_rtbl`, and `gpt_rtbl`. It uses CCF primitives plus `clk_register_vco_pll`, `clk_register_aux`, and `clk_register_gpt`.

## Control Flow
The function registers `osc_32k_clk` and `osc_30m_clk`, gates RTC, creates `pll3_clk`, registers PLL1/PLL2 from PLL control/frequency registers, derives CPU/AHB/APB and DDR clocks, then registers shared UART/FIRDA/CLCD synth and mux chains. GPT0/1 share one synth while GPT2 and GPT3 have dedicated synths. It then registers USB, DMA, FSMC, GMAC, I2C, JPEG, SMI, ADC, GPIO, and SSP clocks.

## State And Persistence
Clock state lives in the MISC register block and in global clkdev registrations. The static `_lock` protects mux/divider/gate register updates made by registered clock ops.

## Dependencies And Integration Points
Depends on Linux CCF, clkdev, SPEAr-specific clock helper code, and platform device names such as `d0000000.serial`, `fc200000.clcd`, `e1800000.ehci`, and `d0200000.i2c`. Downstream platform drivers acquire clocks by these aliases rather than by this file directly.

## Risks And Edge Cases
No registration failures are handled inline. `pll3_clk` is declared as derived from `osc_24m_clk` while the file registers `osc_30m_clk`; this is likely an old naming quirk but is a parent-name risk. Duplicate `GPT1_CLK_ENB` and `GPT2_CLK_ENB` definitions both use bit 11, so hardware documentation should be checked before modifying timer gates. Incorrect mux masks can break display, timer, or serial clocks.

## Test Signals
Boot should show all SPEAr6xx clocks registered and peripherals probing. Clock summary should show plausible PLL, AHB, APB, CLCD, UART, FIRDA, and GPT rates. Runtime tests should include serial console, display, timers, USB host/device, I2C, SPI, GPIO, and flash access.
