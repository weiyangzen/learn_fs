# sources/distributed-fs/ceph-client/drivers/iio/industrialio-core.c

## Purpose
`industrialio-core.c` is the central IIO bus, device, sysfs, debugfs, character-device, ioctl, timestamp, and registration implementation. It allocates `iio_dev` objects, assigns stable numeric IDs, formats and parses IIO ABI values, builds channel attributes from `iio_chan_spec`, registers event and buffer support, exposes `/dev/iio:deviceN`, and tears devices down safely while file descriptors may still exist.

## Important APIs, types, and functions
- `iio_bus_type`, `iio_devt`, `iio_ida`, and `iio_debugfs_dentry` are the global bus, char-device number space, ID allocator, and debugfs root.
- Naming tables map channel types, modifiers, info masks, directions, clocks, and event-independent channel ABI pieces to sysfs names.
- `iio_device_alloc()`, `devm_iio_device_alloc()`, `iio_device_free()`, `__iio_device_register()`, `iio_device_unregister()`, and `__devm_iio_device_register()` are the core lifetime APIs.
- `iio_format_value()` and `iio_str_to_fixpoint()` implement common fixed-point sysfs ABI conversion.
- `iio_read_channel_info()`, `iio_write_channel_info()`, `iio_read_channel_info_avail()`, and ext-info helpers dispatch channel sysfs operations to driver `iio_info` callbacks.
- `__iio_add_chan_devattr()` and `iio_device_add_channel_sysfs()` dynamically create channel attributes from info masks, labels, ext_info, shared scopes, modifiers, differential channels, and indexed channels.
- `iio_device_register_sysfs_group()` appends attribute groups to the device group list consumed by `device_add`.
- `iio_chrdev_open()`, `iio_chrdev_release()`, `iio_ioctl()`, and the buffer/event file operation tables multiplex legacy buffer/event ioctls and reads through registered ioctl handlers.
- `iio_device_set_clock()`, `iio_device_get_clock()`, and `iio_get_time_ns()` own timestamp clock selection and timestamp reads.
- `iio_active_scan_mask_index()` helps drivers identify the active scan mask in `available_scan_masks`.

## Control flow
`subsys_initcall(iio_init)` registers the IIO bus, allocates up to 256 char-device minors, and creates the debugfs root. `iio_device_alloc()` allocates the opaque object plus optional driver private storage, assigns an ID, initializes locks and lists, names the device `iio:deviceN`, and initializes the embedded `struct device`.

Device registration first validates that `indio_dev->info` exists, records the owning module, sets the firmware node, reads an optional `label`, checks duplicate scan indexes and `read_label` versus `extend_name`, registers debugfs, creates buffer sysfs and masks, sanity-checks available scan masks, creates channel sysfs, registers event sysfs, registers trigger consumer sysfs when needed, installs noop setup ops for buffered devices that omitted setup ops, chooses buffer or event file operations for the cdev, assigns device groups, and calls `cdev_device_add()`.

Channel sysfs creation walks every `iio_chan_spec`. It builds names based on direction, type, index, differential endpoints, modifier, `extend_name`, and shared scope. Reads dispatch to `read_raw_multi()` or `read_raw()` and format according to the returned `IIO_VAL_*` type. Writes parse according to optional `write_raw_get_fmt()` and call `write_raw()`. Available values use `read_avail()` and list/range formatting. Labels come from `read_label()` or `extend_name`.

Unregistration removes the cdev/device, enters `info_exist_lock`, removes debugfs, disables all buffers, sets `indio_dev->info = NULL`, wakes event and buffer waiters, then frees buffer sysfs and masks. Final object release unregisters trigger consumers and event/sysfs resources, detaches buffers, destroys locks, frees the ID, and frees the opaque allocation.

## State and persistence behavior
All state is runtime kernel state: allocated IDs, sysfs group arrays, channel attribute lists, device locks, current mode, clock ID, char-device busy bits, ioctl handler list, debugfs cached register address, and buffer/event registrations. No state persists across unload or reboot. Timestamp clock changes are rejected while events or buffers are enabled, preventing live ABI clock switches.

## Dependencies and integration points
The core integrates with the Linux device model, bus registration, cdevs, sysfs, debugfs, anon-inode driven buffer/event helpers, firmware-node properties, IIO buffer/event/trigger modules, driver-provided `struct iio_info`, channel metadata, lockdep keys, and devm actions.

## Risks
- Dynamic sysfs name construction is broad; invalid channel metadata can create duplicate names, impossible differential names, or out-of-range table accesses.
- Open character devices can outlive unregister; `info_exist_lock` and `indio_dev->info = NULL` are central to avoiding use-after-unregister.
- `available_scan_masks` handling has known limitations for multi-long masks and warns rather than fully supporting every pattern.
- `iio_write_channel_info()` fixed-point parsing depends on `write_raw_get_fmt()`; wrong format declarations can silently pass wrong integer/fraction pairs to drivers.
- `iio_device_unregister()` frees only part of registration state immediately; final cleanup is split with device release, so ordering with open fds matters.

## Test signals
- Core registration tests should cover devices with no buffers/events, event-only devices, buffered devices, labels, ext_info, available values, shared attributes, differential channels, and duplicate scan-index rejection.
- ABI tests should verify formatting/parsing for all common `IIO_VAL_*` forms, including negative fractional values, dB suffixes, chars, 64-bit values, lists, and ranges.
- Lifetime tests should open `/dev/iio:deviceN`, unregister the device, and verify reads/ioctls return `-ENODEV` without hangs or use-after-free.
- Timestamp tests should cover all accepted clock names and `-EBUSY` while buffers/events are enabled.
- Debugfs tests should check direct register read/write behavior and cleanup.
