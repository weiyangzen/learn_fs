<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/atm/Kconfig

## Purpose

This Kconfig file defines the ATM driver submenu and the Solos ADSL2+ PCI multiport card option. It gates ATM hardware drivers behind networking and ATM core support.

## Important APIs, types, and functions

The build-facing symbols are `ATM_DRIVERS` and `ATM_SOLOS`. `ATM_DRIVERS` is a bool menu option depending on `NETDEVICES && ATM`. `ATM_SOLOS` is a tristate depending on `PCI` and selecting `FW_LOADER`.

## Control flow

Kconfig evaluates `ATM_DRIVERS` first. If disabled, the guarded submenu is skipped. If enabled with networking and ATM core support, `ATM_SOLOS` becomes available and can be built in or as a module.

## State and persistence behavior

There is no runtime state. Persistent effects are build configuration choices in `.config`, which determine object inclusion and firmware loader availability.

## Dependencies and integration points

This file integrates the Solos PCI driver with the kernel ATM stack, PCI subsystem, and firmware loading infrastructure.

## Risks

Missing `FW_LOADER` selection would break the driver's flash-upgrade firmware requests. Incorrect dependencies could expose a build without ATM core or PCI support. Since the submenu itself adds no code, tests must verify selected child symbols, not just `ATM_DRIVERS=y`.

## Test signals

Run Kconfig builds for `ATM_DRIVERS=n`, `ATM_DRIVERS=y` with `ATM_SOLOS=m/y`, and dependency-negative configs without PCI/ATM. Confirm `solos-pci.o` is linked only when `CONFIG_ATM_SOLOS` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/Kconfig -->
