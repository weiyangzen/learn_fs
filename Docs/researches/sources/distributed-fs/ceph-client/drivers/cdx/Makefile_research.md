# sources/distributed-fs/ceph-client/drivers/cdx/Makefile

## Purpose
This Makefile builds the CDX bus core and the CDX controller subtree when `CONFIG_CDX_BUS` is enabled, and adds optional MSI support when generic MSI IRQ infrastructure is present.

## Important APIs, Types, and Functions
It sets `ccflags-y += -DDEFAULT_SYMBOL_NAMESPACE='"CDX_BUS"'`, so exported symbols default to the `CDX_BUS` namespace unless overridden. Build targets are `cdx.o`, `controller/`, and conditionally `cdx_msi.o`.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_CDX_BUS)` to include the bus core and descend into `drivers/cdx/controller/`. If `CONFIG_GENERIC_MSI_IRQ` is defined, it also compiles `cdx_msi.o` for bus-level MSI domain support.

## State and Persistence Behavior
No runtime state is present. The file affects object inclusion and exported symbol namespace metadata in the resulting kernel/module build.

## Dependencies and Integration Points
The Makefile ties `CONFIG_CDX_BUS` to `cdx.c`, `cdx_msi.c`, and the controller Makefile. The namespace aligns with controller modules importing `CDX_BUS_CONTROLLER` and bus/controller symbols exporting under namespace annotations.

## Risks
When `CONFIG_GENERIC_MSI_IRQ` is off, the bus core must tolerate absent MSI-domain code. Namespace changes can break module linking if import/export annotations drift. The `controller/` descent depends on the subdirectory Kconfig deciding whether a controller object is actually built.

## Test Signals
Build with `CDX_BUS=y/m` with and without `GENERIC_MSI_IRQ`; confirm expected objects appear and no namespace import warnings are emitted.
