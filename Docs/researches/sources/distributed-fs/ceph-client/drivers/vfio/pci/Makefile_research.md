# sources/distributed-fs/ceph-client/drivers/vfio/pci/Makefile

## Purpose

This Makefile builds the VFIO PCI core, the generic vfio-pci driver, and vendor/device-specific VFIO PCI variant subdirectories.

## Important APIs, Types, and Functions

`vfio-pci-core-y` includes `vfio_pci_core.o`, `vfio_pci_intrs.o`, `vfio_pci_rdwr.o`, and `vfio_pci_config.o`, with optional `vfio_pci_zdev.o` and `vfio_pci_dmabuf.o`. `vfio-pci-y` includes `vfio_pci.o` and optional `vfio_pci_igd.o`. Subdirectories are selected for mlx5, ism, hisilicon, pds, virtio, nvgrace-gpu, qat, and xe.

## Control Flow

Kbuild links the common PCI core object when `CONFIG_VFIO_PCI_CORE` is set, the generic driver when `CONFIG_VFIO_PCI` is set, and each variant directory according to its symbol.

## State and Persistence Behavior

There is no runtime state; it controls build linkage.

## Dependencies and Integration Points

The object composition must match Kconfig symbols and exported functions used by variant drivers such as ISM and HiSilicon.

## Risks and Edge Cases

Variant drivers depend on the core object exports. Missing optional objects can break architecture-specific paths, for example zPCI or dmabuf support.

## Test Signals

Build with each PCI VFIO symbol on/off and as modules to verify object composition and subdirectory traversal.
