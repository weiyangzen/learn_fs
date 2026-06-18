# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/Kconfig

## Purpose
This Kconfig file defines `CONFIG_MLXFW`, the shared Mellanox firmware flash library used by mlxsw and other Mellanox drivers.

## Important APIs, Types, and Functions
The symbol is a tristate named `MLXFW`; it selects `XZ_DEC` for MFA2 component-block decompression and `NET_DEVLINK` for firmware flash status reporting.

## Control Flow and State
There is no runtime flow. Build-time selection controls whether `mlxfw.o` is built and whether callers can link against `mlxfw_firmware_flash()`. The selected dependencies ensure the parser and devlink notification paths are available.

## Dependencies and Integration Points
`MLXSW_CORE` selects `MLXFW`. The library integrates with firmware blobs, devlink flash update, XZ decompression, and per-device callback implementations supplied through `struct mlxfw_dev_ops`.

## Risks and Test Signals
Risks include missing selected dependencies or making the symbol unavailable to drivers that call the flash API. Test signals are build coverage with `MLXFW=y/m/n`, mlxsw builds, and devlink flash paths resolving `mlxfw_firmware_flash()`.
