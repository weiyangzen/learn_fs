# sources/distributed-fs/ceph-client/drivers/media/cec/platform/stm32/Makefile

## Purpose
This Makefile builds the STM32 CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_STM32` to `stm32-cec.o`.

## Control Flow
Kbuild includes the STM32 CEC object when configured.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The object depends on the implementation using platform MMIO, regmap, CEC core, clocks, and optional reset resources.

## Risks and Test Signals
Build tests should verify the module is included for `CONFIG_CEC_STM32`.
