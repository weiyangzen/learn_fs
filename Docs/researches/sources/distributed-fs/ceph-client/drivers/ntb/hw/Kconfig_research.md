# sources/distributed-fs/ceph-client/drivers/ntb/hw/Kconfig

## Purpose

This Kconfig file is the NTB hardware-driver submenu aggregator. It does not define symbols itself; it includes Kconfig files for supported hardware families.

## Important APIs, types, and functions

It sources `drivers/ntb/hw/amd/Kconfig`, `idt/Kconfig`, `intel/Kconfig`, `epf/Kconfig`, and `mscc/Kconfig`.

## Control flow and state behavior

There is no runtime behavior. Build-time visibility comes from the sourced hardware Kconfig files and the parent `if NTB` in the top-level NTB Kconfig.

## Dependencies and integration points

This file connects the NTB core configuration menu to AMD, IDT, Intel, generic EPF, and Switchtec/MSCC hardware drivers. It is paired with `drivers/ntb/hw/Makefile`.

## Risks and edge cases

Adding a new hardware driver requires updating both this aggregator and the hardware Makefile; otherwise a symbol may be visible but not built, or built without a visible option.

## Test signals

Kconfig tests should confirm all sourced hardware symbols appear under the NTB menu and remain hidden when `CONFIG_NTB` is disabled.
