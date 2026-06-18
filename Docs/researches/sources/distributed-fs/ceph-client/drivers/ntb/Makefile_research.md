# sources/distributed-fs/ceph-client/drivers/ntb/Makefile

## Purpose

This Makefile builds the NTB framework, hardware/test subdirectories, and optional transport client according to Kconfig symbols.

## Important APIs, types, and functions

`obj-$(CONFIG_NTB) += ntb.o hw/ test/` builds the core object and descends into hardware/test directories when NTB is enabled. `obj-$(CONFIG_NTB_TRANSPORT) += ntb_transport.o` builds the transport client. `ntb-y := core.o` sets the core object contents, and `ntb-$(CONFIG_NTB_MSI) += msi.o` conditionally adds MSI support.

## Control flow and state behavior

There is no runtime behavior; the file controls link composition and subdirectory traversal.

## Dependencies and integration points

It pairs with the top-level NTB Kconfig and depends on `core.c`, optional `msi.c`, `ntb_transport.c`, and child Makefiles under `hw/` and `test/`.

## Risks and edge cases

If `CONFIG_NTB` is disabled but a transport or hardware object is selected incorrectly elsewhere, build rules may not descend as expected. Optional MSI code must be guarded by `CONFIG_NTB_MSI` in both Makefile and code.

## Test signals

Build matrix checks for `CONFIG_NTB=y/m`, `CONFIG_NTB_MSI=y`, and `CONFIG_NTB_TRANSPORT=y/m` are sufficient signals for this file.
