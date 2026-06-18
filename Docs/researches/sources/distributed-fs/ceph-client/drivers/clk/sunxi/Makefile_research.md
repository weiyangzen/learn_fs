# sources/distributed-fs/ceph-client/drivers/clk/sunxi/Makefile

## Purpose
This Makefile maps legacy sunxi clock Kconfig symbols to object files.

## Important APIs, Types, And Functions
It always builds `clk-factors.o` for `CONFIG_CLK_SUNXI`; builds many legacy providers under `CONFIG_CLK_SUNXI_CLOCKS`; and builds PRCM-specific APB/AR100/CPUS providers for SUN6I/SUN8I/SUN9I options.

## Control Flow
There is no runtime flow. Kbuild evaluates object lists during compilation.

## State And Persistence
No runtime state exists. The build graph is determined by `.config`.

## Dependencies And Integration Points
It depends on Kbuild and the source files in this directory. Integration is with early `CLK_OF_DECLARE` providers and platform drivers.

## Risks
Omitting an object can make DT compatible strings unresolved at boot. Adding an object under the wrong config can introduce unused code or link failures.

## Test Signals
Build tests across all sunxi Kconfig combinations and boot logs for clock-provider registration are the main signals.
