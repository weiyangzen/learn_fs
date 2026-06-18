# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7366.c

## Purpose
`clock-sh7366.c` defines the SH7366 clock tree and module-stop gates.

## Important APIs, Types, And Functions
Important objects are `r_clk`, `extal_clk`, `dll_clk`, `pll_clk`, `div4_clks`, `div6_clks`, `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
Init registers main clocks and clkdev aliases, then div4/div6 clocks and MSTP gates. DLL/PLL callbacks read `DLLFRQ` and `PLLCR`; dividers read FRQCR/SCLK/VCLK control registers through SH clock helpers.

## State And Persistence
Runtime clock enable/disable state is represented by MSTPCR hardware and `struct clk` data. No filesystem persistence exists.

## Dependencies And Integration Points
It supplies clocks to SCI, CMT, I2C, SDHI, USBF, display/video blocks, and other SH7366 platform devices via clkdev names.

## Risks
The SH7366 MSTP set differs subtly from SH7343 despite similar layout. Wrong parent selection for memory/video clocks can break display or DMA-heavy peripherals.

## Test Signals
Clock tree dumps, successful driver probes for SCI/CMT/I2C/SDHI/video blocks, and measured peripheral rates are the main validation signals.
