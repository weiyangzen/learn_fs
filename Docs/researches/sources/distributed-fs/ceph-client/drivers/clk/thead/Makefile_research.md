# sources/distributed-fs/ceph-client/drivers/clk/thead/Makefile

## Purpose

This Makefile connects the TH1520 AP clock-controller Kconfig symbol to its implementation object.

## Important APIs, Types, And Functions

The build rule is `obj-$(CONFIG_CLK_THEAD_TH1520_AP) += clk-th1520-ap.o`.

## Control Flow

Kbuild includes the TH1520 clock driver when `CONFIG_CLK_THEAD_TH1520_AP` is enabled.

## State And Persistence Behavior

There is no runtime state. The file only affects kernel build composition.

## Dependencies And Integration Points

It integrates with `drivers/clk/thead/Kconfig`. Any split of AP and VO clock support into separate files would need corresponding Makefile updates.

## Risks And Edge Cases

The rule is minimal. The main maintenance risk is adding new T-Head clock-controller files without adding objects here.

## Test Signals

Build a kernel with `CONFIG_CLK_THEAD_TH1520_AP=y` and verify `clk-th1520-ap.o` is linked.
