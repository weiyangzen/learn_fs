<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/atm/Makefile

## Purpose

This Makefile is the Kbuild glue for ATM drivers in this directory. It conditionally builds the Solos PCI driver object when `CONFIG_ATM_SOLOS` is enabled.

## Important APIs, types, and functions

There are no runtime APIs. The only rule is `obj-$(CONFIG_ATM_SOLOS) += solos-pci.o`.

## Control flow

Kbuild expands the conditional object list during build evaluation. Disabled configs add no objects; `m` builds `solos-pci.ko`; `y` links the object into the kernel.

## State and persistence behavior

The file stores no runtime state. Its effect is the build artifact selected by `.config`.

## Dependencies and integration points

It depends on Kbuild syntax and the symbol defined in the sibling Kconfig. It integrates `solos-pci.c` into the kernel build.

## Risks

The risk surface is small: a symbol name mismatch silently omits the driver, while extra objects would alter module composition. It does not list `solos-attrlist.c` because that file is included by the C preprocessor, not compiled separately.

## Test signals

Build `CONFIG_ATM_SOLOS=m` and verify `solos-pci.ko`; build `CONFIG_ATM_SOLOS=n` and verify no Solos object is compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/Makefile -->
