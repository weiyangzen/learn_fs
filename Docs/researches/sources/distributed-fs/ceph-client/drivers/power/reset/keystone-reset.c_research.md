# sources/distributed-fs/ceph-client/drivers/power/reset/keystone-reset.c

## Purpose
TI Keystone reset controller/restart driver.

## Important APIs, Types, and Functions
global PLL control regmap and `rspll_offset`, `rsctrl_enable_rspll_write()`, `rsctrl_restart_handler()`, and probe.

## Control Flow
probe maps reset control resource, resolves PLL syscon and offset, optionally checks device properties, and registers restart; restart enables reset-isolation/PLL writes then triggers reset.

## State and Persistence Behavior
global regmap/offset plus handler persist; hardware reset-control writes persist until reset.

## Dependencies and Integration Points
ARCH_KEYSTONE, syscon/regmap, MMIO, OF, sys-off restart.

## Risks and Edge Cases
global state is not multi-instance safe; PLL write-enable sequence must match SoC; restart failure only logs.

## Test Signals
Keystone DT, syscon phandle/offset errors, restart path, and compile-test.
