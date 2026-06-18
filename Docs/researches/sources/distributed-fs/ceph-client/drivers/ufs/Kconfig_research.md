# sources/distributed-fs/ceph-client/drivers/ufs/Kconfig

## Purpose

This Kconfig file defines the top-level UFS host controller menu entry. It enables the generic `ufshcd` core and conditionally includes core and host-controller submenus.

## Important APIs, Types, and Functions

The key symbol is `SCSI_UFSHCD`, a tristate menuconfig named "Universal Flash Storage Controller". It depends on `SCSI`, `SCSI_DMA`, and a compatible `RPMB` setting, and selects `PM_DEVFREQ`, `DEVFREQ_GOV_SIMPLE_ONDEMAND`, and `NLS`.

## Control Flow

When `SCSI_UFSHCD` is enabled, the Kconfig parser sources `drivers/ufs/core/Kconfig` and `drivers/ufs/host/Kconfig`. Disabled top-level UFS support hides all subordinate UFS core and host options.

## State and Persistence Behavior

The file persists build-time configuration only through generated kernel config. It does not create runtime state, but choosing `m` or `y` affects whether UFS storage is available early enough for root filesystems.

## Dependencies and Integration Points

It integrates the UFS subsystem into the SCSI driver tree and ensures devfreq/simple-ondemand and NLS support are selected for the core driver.

## Risks and Test Signals

Risks are dependency mismatches, especially root-on-UFS systems built as modules, and unintended changes to selected dependencies. Test signals are `allyesconfig`, `allmodconfig`, rootfs boot configs, and visibility of core/host options only under enabled `SCSI_UFSHCD`.
