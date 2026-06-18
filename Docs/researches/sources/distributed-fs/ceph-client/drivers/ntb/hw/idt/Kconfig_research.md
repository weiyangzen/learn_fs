# sources/distributed-fs/ceph-client/drivers/ntb/hw/idt/Kconfig

## Purpose

This Kconfig file defines the IDT PCIe-switch NTB hardware driver option and documents required platform pre-initialization.

## Important APIs, types, and functions

The main symbol is `NTB_IDT`, a tristate option named "IDT PCIe-switch Non-Transparent Bridge support". It depends on `PCI` and selects `HWMON`.

## Control flow and state behavior

There is no runtime behavior. The help text describes that partitions, NT-function ports, and NT-function BAR apertures must be configured before Linux PCI enumeration, typically via EEPROM or BIOS/SMBus, because some driver behavior depends on peer BAR settings.

## Dependencies and integration points

It is sourced by `drivers/ntb/hw/Kconfig` and matched by `drivers/ntb/hw/idt/Makefile`. Selecting it implies hardware monitoring support through `HWMON`.

## Risks and edge cases

The driver depends on platform pre-initialization that cannot be done reliably through kernel PCI fixups. Systems without correct EEPROM/BIOS setup may expose incomplete or incorrect NT functions, leading to probe failures or unsafe BAR assumptions.

## Test signals

Configuration tests should verify the PCI dependency, `HWMON` selection, and build of the IDT driver. Platform tests should include correctly and incorrectly pre-initialized switches to validate failure diagnostics.
