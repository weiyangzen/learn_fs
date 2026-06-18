# sources/distributed-fs/ceph-client/drivers/pci/msi/Makefile

## Purpose
Defines which PCI MSI implementation objects are built for each kernel configuration.

## Important APIs, Types, and Functions
The Makefile adds `pcidev_msi.o` whenever `CONFIG_PCI` is enabled, adds `api.o`, `msi.o`, and `irqdomain.o` for `CONFIG_PCI_MSI`, and adds `legacy.o` for `CONFIG_PCI_MSI_ARCH_FALLBACKS`.

## Control Flow
There is no runtime control flow. Kbuild uses these object lists to decide which MSI core and exported APIs are linked.

## State and Persistence Behavior
No runtime state exists. Build configuration determines which symbols are available in the resulting kernel.

## Dependencies and Integration Points
Integrates with Kbuild and the PCI/MSI source files in the same directory. `api.o` contains the driver-facing exported APIs, while `msi.o`, `irqdomain.o`, and `legacy.o` provide implementation backends.

## Risks
Incorrect object gating can expose APIs without backends or omit required fallback support. `pcidev_msi.o` being tied to `CONFIG_PCI` rather than `CONFIG_PCI_MSI` indicates some per-device MSI scaffolding is needed even when full MSI support is disabled.

## Test Signals
Build kernels with `CONFIG_PCI`, with and without `CONFIG_PCI_MSI`, and with/without architecture fallback support; check link symbols for MSI APIs and fallback paths.
