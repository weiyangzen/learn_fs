# File Research: sources/cow-pools/bcachefs-tools/include/linux/device.h

This header provides skeletal `struct class` and `struct device` implementations. `class_create()` and `device_create()` allocate zeroed placeholder objects; `class_destroy()` and `device_unregister()` free them. `device_destroy()` is a no-op.

It exists to satisfy device/class API usage in code imported from the kernel. There is no sysfs or device-model behavior beyond memory ownership.
