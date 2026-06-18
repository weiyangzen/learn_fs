# sources/distributed-fs/ceph-client/drivers/virtio/virtio.c

## Purpose
`virtio.c` implements the Linux virtio bus core. It registers the bus, matches virtio devices to virtio drivers, negotiates features, manages status transitions, exposes sysfs attributes, handles config-change delivery, registers/unregisters devices and drivers, and supports power-management freeze/restore and device reset prepare/done flows.

## Important APIs, types, and functions
Exported APIs include `__register_virtio_driver`, `unregister_virtio_driver`, `register_virtio_device`, `unregister_virtio_device`, `is_virtio_device`, `virtio_add_status`, `virtio_reset_device`, `virtio_config_changed`, `virtio_config_driver_disable`, `virtio_config_driver_enable`, `virtio_check_driver_offered_feature`, `virtio_device_freeze`, `virtio_device_restore`, `virtio_device_reset_prepare`, and `virtio_device_reset_done`. Important internal functions are `virtio_dev_probe`, `virtio_dev_remove`, `virtio_features_ok`, `virtio_device_restore_priv`, and `virtio_device_of_init`.

## Control flow
Core init registers the `virtio` bus and debugfs root. Device registration initializes `struct device`, assigns an `ida` index/name, optionally attaches a devicetree child, resets the device, acknowledges it, initializes debugfs, and calls `device_add`. Probe sets DRIVER status, intersects device and driver feature sets, applies debugfs feature filtering, preserves transport features, finalizes features, runs optional validation, sets FEATURES_OK for modern devices, calls driver probe, marks DRIVER_OK if needed, runs scan, and enables config callbacks.

## State and persistence
Runtime state lives in each `struct virtio_device`: feature arrays, status bits in transport config space, config callback flags, virtqueue list, OF node reference, debugfs directory, and assigned index. The global `virtio_index_ida` persists while the bus module is loaded.

## Dependencies and integration points
It depends on the driver core, virtio config/ring helpers, OF, IDA, debugfs hooks, status/feature UAPI definitions, and `virtio_anchor` restricted-memory callback. It is the central integration point for all virtio transports and device drivers.

## Risks and test signals
Risks include feature negotiation regressions, transport feature preservation, config-change races while drivers disable callbacks, status ordering around FAILED/DRIVER_OK, OF child reference leaks, reset/shutdown ordering while virtqueues are active, and restricted-memory requirements for confidential-computing transports. Test signals include virtio-pci/mmio/vdpa probe/remove, feature validation failures, debugfs feature filtering before probe, PM freeze/restore, reset_prepare/reset_done, shutdown with active queues, OF child matching, and sysfs/modalias checks.
