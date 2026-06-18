# sources/distributed-fs/ceph-client/drivers/counter/counter-sysfs.h

Purpose: internal header for adding sysfs attributes to a Generic Counter device.

Important APIs/types/functions: declares `counter_sysfs_add(struct counter_device *counter)` and includes `linux/counter.h`.

Control flow: called from `counter_add()` after the hardware driver has filled `counter->ops`, signals, counts, and extensions, but before `cdev_device_add()` publishes the device.

State and persistence: the header has no state; the implementation allocates devm-managed attribute groups on the counter device.

Dependencies and integration: private glue between `counter-core.c` and `counter-sysfs.c`.

Risks: minimal; adding new sysfs lifecycle operations would require keeping this header private or moving declarations to a public counter header if hardware drivers ever need them.

Test signals: any successful `counter_add()` path with visible `/sys/bus/counter/devices/counterN` attributes verifies this interface.
