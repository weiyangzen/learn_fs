# sources/distributed-fs/ceph-client/drivers/mcb/Kconfig

## Purpose
This Kconfig file defines build-time configuration for MEN Chameleon Bus support and its PCI and LPC carriers.

## Important APIs, Types, and Functions
It declares `MCB` as the parent tristate, `MCB_PCI` as the PCI carrier option, and `MCB_LPC` as the LPC/non-PCI carrier option. `MCB` depends on `HAS_IOMEM`; `MCB_PCI` additionally depends on `PCI`.

## Control Flow, State, and Persistence
The file has no runtime control flow. Its state is the kernel configuration graph: enabling `MCB` permits the carrier submenu, and carrier selections determine which modules are built.

## Dependencies and Integration Points
It integrates with Kbuild and the matching `drivers/mcb/Makefile`. The help text documents module names `mcb.ko`, `mcb-pci.ko`, and `mcb-lpc.ko`.

## Risks and Test Signals
Risks are dependency drift between carrier code and Kconfig, missing `HAS_IOMEM`, or help text/module-name mismatch. Test signals are `allyesconfig`, `allmodconfig`, `randconfig`, and builds with `MCB=y/m`, `MCB_PCI=y/m`, and `MCB_LPC=y/m`.
