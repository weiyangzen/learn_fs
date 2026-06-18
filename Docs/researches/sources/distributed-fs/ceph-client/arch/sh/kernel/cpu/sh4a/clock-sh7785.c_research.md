# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7785.c

## Purpose
`clock-sh7785.c` registers SH7785 clocks: EXTAL/PLL roots, div4 clocks for peripheral/display/DDR/bus/SHYWAY/UMEM/CPU domains, and MSTP gates.

## Important APIs, Types, And Functions
It defines `extal_clk`, `pll_recalc()`, `pll_clk`, `clks`, `div4_clks`, `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
Initialization registers root clocks, lookup aliases, div4 clocks, and MSTP gates. Lookups bind clocks to SCI, SSI/HAC, MMCIF, FLCTL, TMU, SIOF, HSPI, HUDI, UBC, DMAC, and GDTA-related consumers.

## State And Persistence
Clock rates come from PLL and FRQMR1 divider state. Enable state lives in MSTPCR0/1. Some MSTP clocks have `NULL` parents, indicating gate-only or externally parented usage.

## Dependencies And Integration Points
It uses SH div4/MSTP helpers and clkdev names consumed by SH7785 setup/board devices.

## Risks
`NULL`-parent MSTP gates require consumers not to assume a meaningful parent rate. Divider masks for display/graphics/bus domains are subtype-specific and easy to misconfigure.

## Test Signals
Serial, timer, MMCIF, SPI, DMA, audio/HAC/SSI, and display-related probe/rate tests validate this file.
