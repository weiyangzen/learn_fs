# sources/distributed-fs/ceph-client/drivers/clk/sunxi/Kconfig

## Purpose
This Kconfig file controls build selection for the legacy Allwinner `drivers/clk/sunxi` clock providers.

## Important APIs, Types, And Functions
It defines `CLK_SUNXI`, `CLK_SUNXI_CLOCKS`, and PRCM options for SUN6I, SUN8I, and SUN9I. `CLK_SUNXI_CLOCKS` depends on `ARCH_SUNXI || COMPILE_TEST` and defaults for legacy ARM multi-v7 sunxi builds.

## Control Flow
Kconfig has no runtime flow. Menu selections determine which objects in the Makefile are compiled into the kernel.

## State And Persistence
No runtime state exists. Build configuration is the persistent artifact in `.config`.

## Dependencies And Integration Points
It depends on the kernel Kconfig system, architecture symbols, `MFD_SUN6I_PRCM`, and common clock support. It integrates with DT-driven early clock initialization and PRCM platform support.

## Risks
Wrong dependencies can either omit required early clocks or build providers on unsupported platforms. Default changes can affect legacy boards.

## Test Signals
Test by building sunxi defconfigs, COMPILE_TEST configurations, and PRCM-enabled configs, then booting legacy A10/A20/A31/A80-style DTs.
