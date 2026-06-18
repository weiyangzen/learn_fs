# sources/distributed-fs/ceph-client/drivers/gpu/host1x/Kconfig

## Purpose

This Kconfig file defines NVIDIA Tegra host1x support, the host1x context bus, and an optional command-stream firewall.

## Important APIs, Types, And Functions

It defines hidden `TEGRA_HOST1X_CONTEXT_BUS`, tristate `TEGRA_HOST1X`, and boolean `TEGRA_HOST1X_FIREWALL`.

## Control Flow

No runtime control flow. Kconfig selects host1x support for Tegra or compile-test builds and selects required infrastructure.

## State And Persistence Behavior

No runtime state. Build-time symbols decide whether core host1x and context bus objects are compiled and whether firewall checks are enabled.

## Dependencies And Integration Points

`TEGRA_HOST1X` depends on `ARCH_TEGRA || COMPILE_TEST` and selects `DMA_SHARED_BUFFER`, `TEGRA_HOST1X_CONTEXT_BUS`, and `IOMMU_IOVA`. The firewall option defaults to enabled.

## Risks And Test Signals

Risks include compile-test exposure without runtime Tegra hardware and firewall configuration changing command-stream validation behavior. Test with Tegra defconfig, allmodconfig, and firewall on/off builds.
