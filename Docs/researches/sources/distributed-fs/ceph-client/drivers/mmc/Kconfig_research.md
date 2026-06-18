# sources/distributed-fs/ceph-client/drivers/mmc/Kconfig

## Purpose
Top-level Kconfig menu for MMC/SD/SDIO card support.

## Important APIs, Types, And Functions
- `menuconfig MMC` is a tristate option depending on `HAS_IOMEM`.
- Includes `drivers/mmc/core/Kconfig` and `drivers/mmc/host/Kconfig` when enabled.

## Control Flow
Enabling `MMC` reveals core and host-controller configuration. Built-in versus module selection influences whether core support is linked into the kernel or built as modules.

## State And Persistence
Only compile-time `.config` state is affected. No runtime state exists.

## Dependencies And Integration Points
Depends on Kconfig and `HAS_IOMEM`; integrates the MMC core and host driver configuration trees.

## Risks And Edge Cases
Disabling `MMC` hides all child drivers even with DT nodes present. Modular core choices can affect early boot or rootfs availability.

## Test Signals
Config/build matrix for `CONFIG_MMC=y/m/n`, verifying core and host options appear and expected objects build or disappear.
