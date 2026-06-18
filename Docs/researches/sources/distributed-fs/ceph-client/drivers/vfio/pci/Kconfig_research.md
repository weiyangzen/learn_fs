# sources/distributed-fs/ceph-client/drivers/vfio/pci/Kconfig

## Purpose

This Kconfig file defines VFIO support for PCI devices, including the common PCI core, generic vfio-pci driver, optional architecture/device extensions, dmabuf support, and vendor-specific variant drivers.

## Important APIs, Types, and Functions

Core symbols include `VFIO_PCI_CORE`, `VFIO_PCI_INTX`, and `VFIO_PCI`. Optional generic extensions include `VFIO_PCI_VGA`, `VFIO_PCI_IGD`, `VFIO_PCI_ZDEV_KVM`, and `VFIO_PCI_DMABUF`. It sources Kconfig files for mlx5, ISM, HiSilicon, pds, virtio, nvgrace-gpu, qat, and xe variant drivers.

## Control Flow

When `PCI` is available and top-level VFIO sources this menu, users can enable generic PCI VFIO or specific variant drivers. Variant drivers generally select `VFIO_PCI_CORE` and provide device-specific behavior while reusing common VFIO PCI helpers.

## State and Persistence Behavior

The file creates `.config` build state only.

## Dependencies and Integration Points

It integrates VFIO with PCI, IRQ bypass, virqfd, architecture features such as x86 VGA/IGD and s390 KVM, PCI P2PDMA/dmabuf, and vendor subdirectories.

## Risks and Edge Cases

The generic and variant driver split relies on correct selects. Enabling a variant without core support would fail, so each sub-Kconfig must select `VFIO_PCI_CORE`. Architecture-conditional extensions should remain hidden where unsupported.

## Test Signals

Build generic vfio-pci with and without VGA/IGD/zPCI/dmabuf and build each variant driver as module and built-in.
