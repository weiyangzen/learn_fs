<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_device.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_device.h

## Purpose
Public VFIO PCI device abstraction with BAR, config, IRQ, reset, cdev, and IOVA conversion helpers.

## Important APIs, Types, and Functions
struct vfio_pci_bar/device, vfio_pci_device_init/cleanup/reset/config_access, config read/write macros, IRQ/MSI/MSI-X helpers, vfio_pci_get_cdev_path.

## Control Flow
Declares device lifecycle, config-space access via pread/pwrite, eventfd-backed MSI/MSI-X enabling/disabling, and BDF device matching helpers.

## State and Persistence
Device object owns fds, mapped BARs, IRQ eventfds, IOMMU pointer, VFIO info structs, and embedded driver state.

## Dependencies and Integration Points
Depends on linux/vfio.h, linux/pci_regs.h, libvfio iommu/driver/assert headers.

## Risks and Edge Cases
Eventfd array uses PCI_MSIX_FLAGS_QSIZE + 1 and assumes vector indexes fit; cleanup must close all owned fds/mappings.

## Test Signals
VFIO tests use the abstraction for setup, DMA, MMIO, and perf measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_device.h -->
