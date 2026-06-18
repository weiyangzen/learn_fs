# sources/distributed-fs/ceph-client/drivers/clk/sophgo/Makefile

## Purpose
This Makefile maps Sophgo Kconfig symbols to clock-driver objects. It also composes the CV1800 multi-object module from top-level, common, IP, and PLL implementation files.

## Important APIs, Types, And Functions
`clk-sophgo-cv1800.o` is built from `clk-cv1800.o`, `clk-cv18xx-common.o`, `clk-cv18xx-ip.o`, and `clk-cv18xx-pll.o`. SG2042 and SG2044 drivers are separate objects: `clk-sg2042-clkgen.o`, `clk-sg2042-pll.o`, `clk-sg2042-rpgate.o`, `clk-sg2044.o`, and `clk-sg2044-pll.o`.

## Control Flow
The kernel build system includes object files when the corresponding config symbol is enabled. CV1800 helper objects are linked only as part of the aggregate module.

## State And Persistence
No runtime state exists. Build output shape affects module names, symbol linkage, and which platform drivers are available.

## Dependencies And Integration Points
This file integrates directly with `Kconfig`, module metadata in each `.c` file, and the kernel build system's `obj-$(CONFIG_...)` and `foo-y` conventions.

## Risks
Leaving a helper object out of `clk-sophgo-cv1800-y` causes unresolved symbols for exported `clk_ops` or common helpers. Splitting SG2042 into independent objects means dependency mistakes in Kconfig can become runtime parent-clock failures.

## Test Signals
Build CV1800 as built-in and module, build SG2042 symbols in chained combinations, and build SG2044 main and PLL controllers. `modinfo` should show expected module descriptions from the source files.
