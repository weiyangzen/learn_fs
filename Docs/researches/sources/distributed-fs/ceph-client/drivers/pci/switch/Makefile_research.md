# sources/distributed-fs/ceph-client/drivers/pci/switch/Makefile

## Purpose
This Makefile wires the Switchtec PCIe switch management driver object into the kernel build.

## Important APIs, types, and functions
The only build rule is `obj-$(CONFIG_PCI_SW_SWITCHTEC) += switchtec.o`.

## Control flow and behavior
Kbuild includes `switchtec.o` only when `CONFIG_PCI_SW_SWITCHTEC` is `y` or `m`. The SPDX line declares GPL-2.0 licensing for the build file.

## State and persistence
There is no runtime state. The persistent effect is build output selection, either linking the object into the kernel or producing a module depending on Kconfig.

## Dependencies and integration points
It depends on the Kconfig symbol from the same directory and the source file `switchtec.c`.

## Risks
The file is simple. The main risk is drift between Kconfig symbols and object names, which would silently omit the driver from builds.

## Test signals
Build with `CONFIG_PCI_SW_SWITCHTEC=n`, `m`, and `y`, and confirm object/module presence or absence.
