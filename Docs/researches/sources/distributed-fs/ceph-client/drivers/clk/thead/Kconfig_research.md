# sources/distributed-fs/ceph-client/drivers/clk/thead/Kconfig

## Purpose

This Kconfig entry exposes the T-HEAD TH1520 AP clock controller driver as `CONFIG_CLK_THEAD_TH1520_AP`.

## Important APIs, Types, And Functions

The symbol is a boolean named "T-HEAD TH1520 AP clock support". It depends on `ARCH_THEAD || COMPILE_TEST` and `64BIT`, defaults to `ARCH_THEAD`, and selects `REGMAP_MMIO`.

## Control Flow

When enabled, the T-Head Makefile builds `clk-th1520-ap.o`, which registers AP and VO clock providers for matching TH1520 device-tree nodes.

## State And Persistence Behavior

No runtime state is stored here. It controls compile-time availability and whether the driver is linked into the kernel.

## Dependencies And Integration Points

The `64BIT` dependency matches TH1520 platform assumptions. `REGMAP_MMIO` is required by the driver's MMIO-backed PLL and divider code.

## Risks And Edge Cases

If the driver is needed on a configuration that does not select `ARCH_THEAD`, it is available only through compile-test paths. Future driver changes requiring other framework helpers must update the `select` list.

## Test Signals

Compile 64-bit T-Head and compile-test configurations with the symbol enabled. Ensure the object is built and DT compatibles `thead,th1520-clk-ap` and `thead,th1520-clk-vo` can bind at runtime.
