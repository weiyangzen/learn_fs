<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Makefile

## Purpose

The Marvell PM-domain Makefile maps the PXA1908 PM-domain Kconfig symbol to its provider object.

## Important APIs, types, and functions

The single build rule is `obj-$(CONFIG_PXA1908_PM_DOMAINS) += pxa1908-power-controller.o`.

## Control flow

There is no runtime flow. Kbuild includes the object when the symbol is enabled.

## State and persistence behavior

The persistent effect is whether the PXA1908 provider exists in the kernel image or module set.

## Dependencies and integration points

It depends on `CONFIG_PXA1908_PM_DOMAINS` from the Marvell Kconfig and integrates with the provider source in the same directory.

## Risks and edge cases

Source renames must update this mapping. Module and built-in paths should both be covered because the symbol is tristate.

## Test signals

Check `PXA1908_PM_DOMAINS=y` and `m` builds, object/module lists, and module aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Makefile -->
