<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa.c

Purpose: Implements the generic Linux vDPA bus, device/driver registration, management device registry, generic netlink API, device config dumping, stats retrieval, and core locking.

Important APIs/functions: Exports `vdpa_set_status()`, `__vdpa_alloc_device()`, `vdpa_register_device()`, `_vdpa_register_device()`, `vdpa_unregister_device()`, `_vdpa_unregister_device()`, `__vdpa_register_driver()`, `vdpa_unregister_driver()`, `vdpa_mgmtdev_register()`, `vdpa_mgmtdev_unregister()`, `vdpa_get_config()`, and `vdpa_set_config()`. Netlink handlers implement management-device get, device new/delete/get, config get, vendor stats get, and device attr set.

Control flow: Module init registers the `vdpa` bus and generic netlink family. Device allocation validates config ops, IOMMU/use-VA constraints, allocates an IDA index, initializes a device, and sets `cf_lock`. Registration holds global `vdpa_dev_lock`, checks duplicate names, and calls `device_add()`. Management registration adds the management device to `mdev_head`; unregister removes it and deletes child devices through each mdev's `dev_del`. Netlink `DEV_NEW` parses attributes, validates management-device capabilities and feature implications, then calls `mdev->ops->dev_add()` under the global lock.

State and persistence: Global state includes `mdev_head`, `vdpa_dev_lock`, `vdpa_index_ida`, the bus, and netlink family. Per-device state includes `vdev->config`, feature-valid status, map ops, number of VQs, groups/address spaces, and `cf_lock`. No disk persistence.

Dependencies and integration points: Depends on Linux device model, DMA API, generic netlink, virtio IDs/config structures, vDPA/vhost IOTLB headers, and individual hardware/simulator management devices. Hardware drivers call `_vdpa_register_device()` from management callbacks and `vdpa_mgmtdev_register()` during probe.

Risks: Lock ordering matters: global `vdpa_dev_lock` protects mdev and device lists, while `cf_lock` protects device config/status. Managed devices created outside mdev are rejected by user delete/config operations. Config reads before feature negotiation force legacy feature setup with zero. Netlink feature validation for multi-class management devices rejects ambiguous device-feature masks.

Test signals: Exercise netlink `vdpa mgmtdev show`, `vdpa dev add/del/show/config show`, MAC attr set, stats get, duplicate name rejection, unsupported attrs/features, unmanaged device rejection, bus driver probe/remove, and module init netlink registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa.c -->
