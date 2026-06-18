# sources/distributed-fs/ceph-client/include/linux/vfio.h

## Purpose
This header defines the VFIO kernel driver framework for safely exposing devices to userspace with IOMMU isolation, migration, dirty logging, IRQFD, and device cdev/group support.

## Important APIs, types, and functions
Key types are `vfio_device_set`, `vfio_device`, `vfio_device_ops`, `vfio_migration_ops`, `vfio_log_ops`, `vfio_info_cap`, and `virqfd`. APIs cover device allocation/registration/unregistration, iommufd binding/attach/detach, feature validation, precopy ioctl validation, device-set management, migration FSM transitions, IOVA range combination, file validation/KVM association, page pin/unpin, DMA read/write, capability construction, IRQ set validation, and virqfd enable/disable/flush.

## Control flow, state, and persistence
Bus drivers embed `vfio_device`, set static ops/migration/logging properties, register with the VFIO core, and serve file operations through callbacks. Open/close are serialized by device sets; iommufd/group state controls DMA address spaces; migration/log callbacks implement userspace-requested state transitions. State is runtime references, open counts, cdev/group/iommufd attachments, KVM pointer, PASIDs, IRQFD work, and debug roots; persistent state belongs to hardware or userspace migration streams.

## Dependencies and integration points
It depends on IOMMU, iommufd, mm, poll, cdev, IOVA bitmaps, uaccess, workqueues, eventfd, and VFIO UAPI. It integrates PCI/platform/mdev VFIO drivers, KVM, userspace VMMs, IOMMUFD, dirty logging, and migration.

## Risks and test signals
Risks include lifetime/refcount races, incorrect iommufd detach, unsafe page pinning, bad user ioctl validation, migration stream state leaks, and IRQFD shutdown races. Tests should cover open/close sets, cdev/group paths, iommufd physical/emulated ops, feature/probe ioctls, migration FSM, dirty logging, DMA map/unmap callbacks, and IRQFD teardown.
