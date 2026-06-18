# sources/distributed-fs/ceph-client/drivers/media/cec/platform/sti/Makefile

## Purpose
This Makefile builds the STiH4xx CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_STI` to `stih-cec.o`.

## Control Flow
Kbuild compiles the STi CEC driver as selected by Kconfig.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The implementation depends on platform MMIO, a CEC clock, IRQ, and CEC notifier.

## Risks and Test Signals
Build testing with `CONFIG_CEC_STI=m/y` verifies the object path and module composition.
