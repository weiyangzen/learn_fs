# sources/distributed-fs/ceph-client/drivers/clk/rockchip/Makefile

## Purpose
Defines how Rockchip clock controller objects are linked. It builds a common `clk-rockchip.o` aggregate from shared helper files and adds SoC-specific CRU/reset objects according to Kconfig symbols.

## Important APIs, Types, and Functions
The aggregate includes `clk.o`, `clk-pll.o`, `clk-cpu.o`, `clk-gate-grf.o`, `clk-half-divider.o`, `clk-inverter.o`, `clk-mmc-phase.o`, `clk-muxgrf.o`, `clk-ddr.o`, `gate-link.o`, and optional `softrst.o` under `CONFIG_RESET_CONTROLLER`.

## Control Flow, State, and Persistence
No runtime control flow exists. Build selection controls helper availability and which platform driver objects are linked.

## Dependencies, Integration Points, Risks, and Test Signals
The Makefile depends on same-directory Kconfig symbols. Newer SoCs also build reset companion files. Risks are missing helpers or symbol/object mismatches. Test incremental builds for each `CONFIG_CLK_*` symbol and link checks for helper references.
