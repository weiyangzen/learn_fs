# sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/Kconfig

## Purpose
This Kconfig file introduces the Vertexcom Ethernet vendor menu and the `MSE102X` SPI-attached Ethernet driver option.

## Important APIs, types, and functions
There are no C APIs. `NET_VENDOR_VERTEXCOM` is a boolean vendor gate defaulting to `y`, and `MSE102X` is a tristate driver symbol named "Vertexcom MSE102x SPI". `MSE102X` depends on `SPI`, so the driver is only offered when SPI support is available.

## Control flow and integration
The build configuration flow is standard vendor gating: enabling the vendor symbol reveals the specific device option, and selecting `MSE102X` later drives `obj-$(CONFIG_MSE102X)` in the local Makefile. As a tristate, the driver can be built in or as a module.

## State and persistence behavior
Kconfig selections persist in the kernel `.config` and determine whether `mse102x.c` participates in compilation. No runtime state is created by this file.

## Dependencies and integration points
The primary dependency is `SPI`, matching the driver's `spi_driver` registration and SPI transfer protocol. The file is expected to be included from the broader Ethernet vendor Kconfig tree.

## Risks and edge cases
There is no dependency on `OF`, even though the driver supports Device Tree matching and uses `of_get_ethdev_address`; non-DT SPI IDs remain available, so that is likely intentional. Missing dependencies would show up as compile errors only when the symbol is enabled.

## Test signals
Run Kconfig coverage for `CONFIG_SPI=y/m` with `CONFIG_MSE102X=y/m`, confirm the prompt appears under Ethernet vendor drivers, and build `mse102x.o` both built-in and modular.
