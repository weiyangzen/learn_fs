# sources/distributed-fs/ceph-client/drivers/virt/coco/efi_secret/Kconfig

## Purpose
Adds build configuration for the EFI confidential-computing secret-area securityfs driver.

## APIs, Types, and Functions
`EFI_SECRET` is a tristate depending on EFI and x86_64 or arm64, selecting `EFI_COCO_SECRET` and `SECURITYFS`.

## Control Flow and State
Build-time selection only. Runtime state is created by `efi_secret.c` when the platform exposes the EFI secret area.

## Dependencies and Integration
Integrates with EFI config-table discovery, encrypted memory mapping, and securityfs.

## Risks and Test Signals
Build and boot tests should cover EFI absent, EFI secret area absent, empty secret table, and module build. Security-sensitive tests should verify deleted secrets are wiped.
