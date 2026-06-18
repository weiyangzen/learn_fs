# sources/distributed-fs/ceph-client/drivers/dma/idxd/Makefile

## Purpose
The IDXD Makefile composes the Intel DSA/IAA bus module, main driver, optional perfmon support, and compatibility module.

## Important APIs, Types, And Functions
It sets `DEFAULT_SYMBOL_NAMESPACE` to `IDXD`, builds `idxd_bus.o` from `bus.o`, builds the main `idxd.o` from `init.o irq.o device.o sysfs.o submit.o dma.o cdev.o debugfs.o defaults.o`, optionally adds `perfmon.o`, and builds `idxd_compat.o` from `compat.o`.

## Control Flow
Kbuild, not runtime code, controls object selection from `CONFIG_INTEL_IDXD_BUS`, `CONFIG_INTEL_IDXD`, `CONFIG_INTEL_IDXD_PERFMON`, and `CONFIG_INTEL_IDXD_COMPAT`.

## State And Persistence Behavior
The namespace affects exported symbol checks; object aggregation defines module boundaries and load behavior.

## Dependencies And Integration Points
The main module uses bus, dmaengine, cdev, debugfs, sysfs, submit, IRQ, defaults, and optional perfmon pieces.

## Risks And Test Signals
Omitting an object silently removes functionality. Validate build combinations and `modpost` namespace checks.
