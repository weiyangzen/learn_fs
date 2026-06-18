# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/Makefile

## Purpose

`hisi_sas/Makefile` maps Kconfig options to HiSilicon SAS driver objects.

## Important APIs, types, and data

- `hisi_sas_main.o` is built for `CONFIG_SCSI_HISI_SAS`.
- Hardware v1 and v2 platform implementations are also built for the core option.
- Hardware v3 PCI implementation is built for `CONFIG_SCSI_HISI_SAS_PCI`.

## Control flow

Kbuild includes the common core and platform hardware versions when the core driver is selected, and adds PCI v3 support when the PCI option is enabled.

## State and persistence behavior

No runtime state exists. The file controls build artifacts.

## Dependencies and integration points

It ties `Kconfig` selections to `hisi_sas_main.c`, `hisi_sas_v1_hw.c`, `hisi_sas_v2_hw.c`, and `hisi_sas_v3_hw.c`.

## Risks and edge cases

- The core option always builds v1 and v2 hardware files, so those files must compile for all core-supported environments.
- v3 support is isolated behind the PCI option.

## Test signals

Kbuild tests should verify object inclusion for each config combination and link success when PCI support is disabled.
