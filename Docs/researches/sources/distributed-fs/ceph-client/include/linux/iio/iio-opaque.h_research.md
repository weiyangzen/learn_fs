<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio-opaque.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/iio-opaque.h

Purpose: Defines private IIO core storage that is embedded behind public `struct iio_dev` but not meant for direct driver access.

Important APIs/types/functions: `struct iio_dev_opaque` carries internal ids, character device, indio parent, event interface, buffer list/count, channel attribute group, scan-index mapping, clock id, flags for registration and sysfs enablement, mutexes, event interface, and optional debugfs dentry. `to_iio_dev_opaque()` maps a public IIO device to its private tail storage.

Control flow: IIO core allocation/register/unregister code initializes and consumes the opaque structure; drivers use public helpers instead.

State/persistence: Holds persistent per-device core state for registered IIO devices, including buffer/event/sysfs/debugfs internals.

Dependencies/integration: Integrates with device model, cdev, mutexes, events, buffers, and debugfs.

Risks: Direct use outside core can violate locking/lifetime assumptions; layout must stay synchronized with allocation code.

Test signals: IIO device allocation/free, register/unregister, debugfs builds, multiple buffers, and event interface creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio-opaque.h -->
