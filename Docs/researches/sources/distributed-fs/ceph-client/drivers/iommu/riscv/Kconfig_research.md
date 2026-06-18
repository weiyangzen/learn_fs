# sources/distributed-fs/ceph-client/drivers/iommu/riscv/Kconfig

## Purpose
This Kconfig fragment enables the RISC-V IOMMU driver family and its PCI transport support.

## Important APIs, Types, And Functions
`RISCV_IOMMU` is a boolean option defaulting to `RISCV`, constrained to `64BIT` and either native RISC-V or `COMPILE_TEST`, and dependent on `GENERIC_MSI_IRQ`. It selects `IOMMU_API`, `GENERIC_PT`, `IOMMU_PT`, and `IOMMU_PT_RISCV64`, which are required by `iommu.c` for generic page-table backed domains. `RISCV_IOMMU_PCI` defaults to yes when `RISCV_IOMMU` and `PCI_MSI` are enabled.

## Control Flow
There is no runtime flow. Build configuration determines whether `iommu.o` and platform support are built, and whether PCI support is included.

## State And Persistence
The file contributes persistent kernel build configuration only.

## Dependencies And Integration Points
It integrates the RISC-V IOMMU driver with the generic IOMMU API, generic page-table framework, RISC-V 64-bit page-table backend, generic MSI IRQ handling, and optional PCI MSI support.

## Risks
The driver assumes 64-bit RISC-V IOMMU page-table modes in the implementation, so relaxing `64BIT` or missing generic page-table selections would break compilation or runtime attach. PCI support is gated on `PCI_MSI`; systems with only platform IOMMU devices use the always-built platform object from the Makefile.

## Test Signals
Kconfig tests should cover native RISC-V builds, `COMPILE_TEST` builds, builds without `PCI_MSI`, and build dependency resolution for `GENERIC_PT` and `IOMMU_PT_RISCV64`.
