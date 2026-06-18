# sources/distributed-fs/ceph-client/drivers/iommu/riscv/Makefile

## Purpose
This Makefile declares the object composition for RISC-V IOMMU support.

## Important APIs, Types, And Functions
It always builds `iommu.o` and `iommu-platform.o` into the enclosing object when the directory is selected. It adds `iommu-pci.o` only under `CONFIG_RISCV_IOMMU_PCI`.

## Control Flow
There is no runtime flow. The file establishes build-time linkage: platform support is part of core RISC-V IOMMU support, while PCI support is optional.

## State And Persistence
No runtime state. Build products persist according to kernel build configuration.

## Dependencies And Integration Points
It depends on the parent IOMMU Kbuild selecting this directory and on Kconfig supplying `CONFIG_RISCV_IOMMU_PCI`.

## Risks
Because `iommu-platform.o` is unconditional once the directory is built, platform-driver dependencies must remain available under the same Kconfig constraints. Optional PCI code must not be referenced unconditionally by core code.

## Test Signals
Build with `RISCV_IOMMU=y, RISCV_IOMMU_PCI=y` and with `RISCV_IOMMU_PCI` absent to confirm object selection.
