# sources/distributed-fs/ceph-client/include/linux/vdpa.h

## Purpose
This header defines the vDPA bus/device contract for exposing virtio data-path accelerators to vhost, virtio, and management users.

## Important APIs, types, and functions
Key types are `vdpa_callback`, `vdpa_notification_area`, split/packed `vdpa_vq_state`, `vdpa_device`, `vdpa_iova_range`, `vdpa_dev_set_config`, `vdpa_map_file`, `vdpa_config_ops`, `vdpa_driver`, `vdpa_mgmtdev_ops`, and `vdpa_mgmt_dev`. APIs allocate/register/unregister devices and drivers, reset devices, set features/status/config, manage drvdata, and register management devices.

## Control flow, state, and persistence
Parent drivers allocate a `vdpa_device` with config/map ops, register it with a virtqueue count, and expose callbacks for queue addresses, readiness, state, notifications, features, status, config space, DMA/IOTLB maps, ASIDs, reset/suspend/resume, and optional VA binding. The framework serializes config access with `cf_lock`, tracks `features_valid`, queue/address-space counts, and management-device ownership. Persistence is not defined; configuration is runtime and driven by userspace/vhost/virtio negotiation.

## Dependencies and integration points
It depends on device core, interrupts, virtio, virtio-net/blk IDs, vhost IOTLB, Ethernet constants, eventfd, cpumasks, and mm structs. It integrates with vhost-vDPA, vdpa netlink management, virtio feature negotiation, IOMMU/IOTLB mapping, and hardware/software accelerator drivers.

## Risks and test signals
Risks include reset/map ordering mistakes, feature negotiation before status transitions, queue state mismatch for packed versus split rings, ASID/group errors, and failure to lock config changes. Tests should cover device/driver registration, management add/del/set_attr, feature set/reset, queue ready/state/callback paths, IOTLB map/unmap/reset, suspend/resume, and concurrent config access.
