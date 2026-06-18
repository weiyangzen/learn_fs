<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_driver.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_driver.h

## Purpose
Public generic PCI-driver operation layer used by device-specific DSA and IOAT backends.

## Important APIs, Types, and Functions
struct vfio_pci_driver_ops, struct vfio_pci_driver, probe/init/remove/memcpy/send_msi wrappers.

## Control Flow
Defines backend hooks for probe, lifecycle, async memcpy, wait, and MSI generation, plus max operation limits and a DMA region for descriptors/state.

## State and Persistence
Driver state records selected ops, initialized flag, memcpy_in_progress flag, DMA region, max limits, and MSI vector.

## Dependencies and Integration Points
Depends on libvfio/iommu.h and vfio_pci_device forward declaration.

## Risks and Edge Cases
Operation wrappers assert strict state transitions; backends must set max limits and use the provided region.

## Test Signals
Driver tests exercise wrapper state checks and backend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/vfio_pci_driver.h -->
