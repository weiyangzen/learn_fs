# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_pci_driver_test.c

## Purpose

`vfio_pci_driver_test.c` exercises optional selftest driver operations exposed through a VFIO PCI test device. It validates driver init/remove idempotence, DMA memcpy through mapped IOVA ranges, behavior with unmapped IOVA addresses, MSI generation, and sustained DMA copy workloads across all configured IOMMU modes.

## Important APIs, Types, and Functions

The fixture uses `struct iommu`, `struct vfio_pci_device`, `struct vfio_pci_driver`, `struct iova_allocator`, and `struct dma_region` from `libvfio.h`. `region_setup()` mmaps anonymous memory, allocates IOVA space, and calls `iommu_map()`. `region_teardown()` unmaps from the IOMMU and munmaps host memory. Driver interactions include `vfio_pci_driver_init()`, `vfio_pci_driver_remove()`, `vfio_pci_driver_memcpy()`, `vfio_pci_driver_memcpy_start()`, `vfio_pci_driver_memcpy_wait()`, and `vfio_pci_driver_send_msi()`. `ASSERT_NO_MSI()` checks that an eventfd remains empty with `EAGAIN`.

## Control Flow

Fixture setup selects the requested IOMMU mode, opens the VFIO PCI device, initializes an IOVA allocator, maps a 1 GiB memcpy region plus the driver's own 2 MiB region, reserves one unmapped IOVA, initializes the driver, and records the driver's MSI eventfd. The memcpy size is bounded by both the device maximum and half the mapped region so source and destination do not overlap. Individual tests repeatedly remove/reinitialize the driver, perform successful DMA copies, try reads or writes using an unmapped IOVA without requiring a specific device error, generate an MSI and read eventfd value `1`, mix successful DMA, failed/unmapped DMA, and MSI generation, and run a 60-second-bounded storm of up to 250 GiB total copy work.

## State and Persistence Behavior

State is per test instance: VFIO device fd state, IOMMU mappings, anonymous memory buffers, allocated IOVA ranges, eventfds, and the selftest driver's device-visible region. No persistent files are written. The test mutates the selected PCI device through driver init/remove, DMA commands, and MSI generation.

## Dependencies and Integration Points

The test requires a BDF whose VFIO PCI selftest driver ops are present; `device_has_selftests_driver()` skips the suite if not. It depends on VFIO, the chosen IOMMU backend modes, eventfd, anonymous mmap, and the shared selftest `libvfio` helpers.

## Risks and Edge Cases

Mapping a 1 GiB anonymous region can fail under constrained memory or address-space limits. The unmapped-IOVA tests intentionally ignore the command return because not all devices surface IOMMU faults the same way; this means they mainly assert no spurious MSI. The storm test divides by `self->size`, so helper/device setup must never report zero `max_memcpy_size`. Hardware DMA and MSI behavior depend on a real VFIO test device.

## Test Signals

Pass signals include stable init/remove loops, byte-for-byte equality after DMA copy, empty MSI eventfd after memcpy and unmapped IOVA attempts, eventfd value `1` after explicit MSI send, repeated mix-and-match success, and `vfio_pci_driver_memcpy_wait()` returning zero after the large transfer batch.
