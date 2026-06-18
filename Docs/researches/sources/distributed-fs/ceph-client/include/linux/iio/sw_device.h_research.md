<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sw_device.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/sw_device.h

Purpose: Exposes configfs-backed software IIO device type registration and lifecycle helpers.

Important APIs/types/functions: `module_iio_sw_device_driver()` builds module init/exit for a software device type. `struct iio_sw_device_type` names a type and ops; `struct iio_sw_device` embeds an `iio_dev` pointer and configfs group; `struct iio_sw_device_ops` provides `probe()` and `remove()`. APIs register/unregister types and create/destroy instances.

Control flow: Type modules register ops; configfs creates named instances, invoking probe; destroy invokes remove and cleanup.

State/persistence: Per-instance state lives in `struct iio_sw_device` and configfs items until destroyed.

Dependencies/integration: Depends on module/device/IIO/configfs and conditional configfs group initialization.

Risks: Probe/remove imbalance or configfs naming conflicts can leak IIO devices.

Test signals: Module load/unload, configfs mkdir/rmdir instance lifecycle, failed probe cleanup, and IIO device registration visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sw_device.h -->
