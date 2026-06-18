# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7723.c

## Purpose
`clock-sh7723.c` defines the richer SH7723 clock tree with L2/FPU/internal gates, six SCIF clocks, media clocks, and div4 enable/reparent support.

## Important APIs, Types, And Functions
Key data includes root `r_clk`/`extal_clk`, DLL/PLL callbacks, `div4_clks`, `div4_enable_clks`, `div4_reparent_clks`, `div6_clks`, extensive `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
The init path registers main clocks, clkdev lookups, div4 clocks, optional enable/reparent dividers, div6 video clock, and MSTP gates. Device drivers later enable gates through names such as `sh-sci.0` through `.5`, I2C, SDHI, USB, camera, VPU, and LCDC.

## State And Persistence
Hardware clock state is in FRQCR, IRDACLKCR, SCLKACR/BCR, VCLKCR, DLL/PLL registers, and MSTPCR0-2. Software state is static `struct clk` arrays and lookup mappings.

## Dependencies And Integration Points
It ties SH7723 setup/board devices to the SH clock framework and clkdev. Internal gates marked on-init protect TLB/cache/FPU/SHYWAY paths.

## Risks
The large MSTP table has index/name mismatch risk. On-init gates for core blocks must not be disabled. Media clocks use mixed parents and reparenting, so audio/video regressions can be subtle.

## Test Signals
Boot with cache/FPU enabled, serial and timer clocks, I2C/SDHI/USB/display/camera probes, and clock enable/disable debug traces validate the file.
