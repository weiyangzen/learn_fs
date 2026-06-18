# sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-plat.c

## Purpose

`spi-loongson-plat.c` is the OF/platform glue for Loongson SPI controllers. It maps the MMIO resource from a platform device and delegates the implementation to the shared Loongson core.

## Important APIs, Types, And Functions

The central function is `loongson_spi_platform_probe()`. The OF match table contains `loongson,ls2k1000-spi`; the platform driver uses `loongson_spi_dev_pm_ops`.

## Control Flow, State, And Persistence

Probe maps resource 0 using `devm_platform_ioremap_resource()` and calls `loongson_spi_init_controller()`. Cleanup is devm-managed. There is no private persistent state.

## Dependencies And Integration Points

This file depends on platform device and OF matching infrastructure plus `spi-loongson.h`. It imports namespace `SPI_LOONGSON_CORE` and should be considered a frontend, not an independent controller implementation.

## Risks And Test Signals

Risks include device-tree compatible/resource mistakes and dependency on the shared core's optional clock handling. Test with DT probe, unbind/rebind, runtime transfers, and system suspend/resume.
