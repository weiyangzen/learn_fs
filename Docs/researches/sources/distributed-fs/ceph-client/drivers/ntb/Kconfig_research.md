# sources/distributed-fs/ceph-client/drivers/ntb/Kconfig

## Purpose

This Kconfig file defines the top-level Non-Transparent Bridge configuration menu. It gates the NTB framework on PCI support, exposes optional MSI interrupt forwarding support, includes hardware and test submenus, and defines the NTB transport client option.

## Important APIs, types, and functions

The key symbols are `NTB`, `NTB_MSI`, and `NTB_TRANSPORT`. `NTB` is a tristate menuconfig depending on `PCI`. `NTB_MSI` is a bool depending on `PCI_MSI` and documents MSI forwarding support. `NTB_TRANSPORT` is a tristate client that exposes queue-pair APIs to other drivers.

## Control flow and state behavior

There is no runtime flow. Build-time inclusion is controlled by the symbols and by `source` lines for `drivers/ntb/hw/Kconfig` and `drivers/ntb/test/Kconfig`, both active only inside `if NTB`.

## Dependencies and integration points

The file integrates the NTB subsystem with kernel configuration and the recursive Kconfig tree for hardware drivers, tests, and transport. It is paired with `drivers/ntb/Makefile`.

## Risks and edge cases

Misconfigured dependencies can expose hardware drivers without PCI support or hide client drivers. Enabling `NTB_MSI` requires hardware driver support for MSI interrupt creation and may consume an extra memory window.

## Test signals

Configuration tests should verify `menuconfig NTB` visibility only with PCI, `NTB_MSI` visibility only with PCI_MSI, hardware submenu availability under NTB, and build coverage for `NTB=m/y` plus `NTB_TRANSPORT=m/y`.
