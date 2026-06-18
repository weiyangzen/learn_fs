# sources/distributed-fs/ceph-client/drivers/iio/iio_core.h

Purpose: Private header for Industrial I/O core internals. It declares core-only device types, buffer/file operation wrappers, ioctl handler registration, sysfs/channel helper functions, and event-interface helpers.

Important APIs/types/functions: `iio_device_type` identifies IIO devices. `struct iio_dev_buffer_pair` associates a device and buffer. `struct iio_ioctl_handler` is a list node plus ioctl callback, registered by `iio_device_ioctl_handler_register()` / `unregister()`. `__iio_add_chan_devattr()` and `iio_free_chan_devattr_list()` manage channel sysfs attributes. `iio_device_register_sysfs_group()` adds extra groups. `iio_format_value()` formats IIO values. Under `CONFIG_IIO_BUFFER`, wrapper declarations connect buffer poll/read/write operations and lifecycle helpers; otherwise inline stubs/null addresses are provided. Event helpers register/unregister/wake event sets and query enabled events.

Control flow: No implementation here; compile-time `CONFIG_IIO_BUFFER` selects real buffer hooks or inert stubs used by the core.

State and persistence: Defines structures that participate in core lists and file operations. It does not own state itself.

Dependencies and integration points: Internal to `drivers/iio`; individual drivers should not include it. Integrates IIO character device operations, sysfs creation, buffers, and events.

Risks: Because this is private core API, accidental driver inclusion can create brittle dependencies. Stub behavior under `!CONFIG_IIO_BUFFER` must preserve core build/runtime semantics. `IIO_IOCTL_UNHANDLED` is a positive sentinel distinct from negative errno and must be interpreted correctly by callers.

Test signals: Build IIO with and without buffer support, exercise ioctl handler registration order, channel sysfs creation/freeing, event set lifecycle, and buffer file operation wrappers.
