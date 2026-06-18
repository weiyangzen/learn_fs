# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/Kconfig

## Purpose

`hisi_sas/Kconfig` declares configuration options for the HiSilicon SAS driver family, including the core/platform driver, PCI variant, and default debugfs enablement.

## Important APIs, types, and data

- `CONFIG_SCSI_HISI_SAS` builds the core/platform HiSilicon SAS driver. It depends on MMIO, ARM64 or compile testing, ATA, and selects libsas, block integrity, and SATA host support.
- `CONFIG_SCSI_HISI_SAS_PCI` builds PCI support and depends on the core option, PCI, and ACPI.
- `CONFIG_SCSI_HISI_SAS_DEBUGFS_DEFAULT_ENABLE` defaults debugfs on when the core driver is enabled.

## Control flow

Kconfig selection controls which objects from the local Makefile are built and whether debugfs defaults are enabled in `hisi_sas_main.c`.

## State and persistence behavior

Build-time configuration persists in the kernel config. Runtime debugfs default state is derived from the debugfs option.

## Dependencies and integration points

It integrates the driver with SCSI SAS libsas, ATA/SATA support, block integrity for DIF/DIX, platform devices, and PCI/ACPI variants.

## Risks and edge cases

- PCI support is ACPI-only by dependency, so non-ACPI PCI environments will not build that variant.
- The core option depends on ATA and selects SATA host support because SAS HBAs may attach SATA/STP devices.

## Test signals

Build matrix tests should cover core-only, PCI-enabled, debugfs-default-enabled, ARM64 native, and COMPILE_TEST configurations.
