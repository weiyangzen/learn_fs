<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_device.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_device.c

## Purpose
Implements VFIO PCI device setup/teardown, BAR mapping, config access, IRQ management, group/container setup, and iommufd cdev setup.

## Important APIs, Types, and Functions
vfio_pci_device_init/cleanup, vfio_pci_irq_enable/disable/trigger, vfio_pci_config_access, vfio_pci_device_reset, vfio_pci_get_cdev_path, vfio_pci_bar_map/unmap.

## Control Flow
Finds IOMMU group or vfio cdev path, opens device via legacy group/container or iommufd bind/attach, queries device/config/BAR/IRQ info, mmaps mappable BARs with alignment, sets up eventfd IRQ vectors, probes driver backends, and cleans mappings/fds on teardown.

## State and Persistence
Device object owns VFIO fd/group fd, BAR mappings, eventfds, and embedded driver; hardware state is reset/configured by callers/backends.

## Dependencies and Integration Points
Depends on sysfs /sys/bus/pci/devices, /dev/vfio, VFIO ioctls, iommufd ioctls, mmap, eventfd, PCI config ABI.

## Risks and Edge Cases
Assumes IOMMU group is viable and vfio-pci bound; cdev path discovery expects /vfio-dev entries; BAR mapping requires power-of-two sizes and MMAP flags.

## Test Signals
VFIO tests validate config access, DMA mapping of BARs, iommufd setup, and init performance through this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/vfio_pci_device.c -->
