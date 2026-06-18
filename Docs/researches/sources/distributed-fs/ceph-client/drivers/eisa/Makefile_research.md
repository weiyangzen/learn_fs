# sources/distributed-fs/ceph-client/drivers/eisa/Makefile

## Purpose
This Makefile wires EISA core, PCI bridge, virtual root, and generated name-table support into Kbuild.

## Important APIs, types, and functions
It builds `eisa-bus.o` for `CONFIG_EISA`, `pci_eisa.o` for `CONFIG_EISA_PCI_EISA`, and `virtual_root.o` for `CONFIG_EISA_VIRTUAL_ROOT`. It generates `devlist.h` from `eisa.ids` with a `sed` command that converts ID/name records to `EISA_DEVINFO()` initializers.

## Control flow
Kbuild first generates `devlist.h` when EISA is enabled, ensures `eisa-bus.o` depends on it, and cleans the generated file through `clean-files`. `virtual_root.o` is intentionally last so a real root bridge can register first.

## State and persistence behavior
There is no runtime state. The generated `devlist.h` is build output derived from `eisa.ids`.

## Dependencies and integration points
The file depends on Kbuild, the sibling `eisa.ids` database, and `include/linux/device.h` as a dependency trigger. It integrates directly with the Kconfig symbols defined in `Kconfig`.

## Risks and edge cases
The `sed` transform assumes a stable `eisa.ids` format. Object ordering matters for root registration: moving `virtual_root.o` earlier could let the virtual root consume the bus before a real bridge registers. Missing `devlist.h` generation breaks `CONFIG_EISA_NAMES` builds.

## Test signals
Build with `CONFIG_EISA=y` and `CONFIG_EISA_NAMES=y` to confirm `devlist.h` generation, with bridge and virtual-root toggles to confirm object inclusion and link coverage.
