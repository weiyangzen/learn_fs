# sources/distributed-fs/ceph-client/drivers/iio/industrialio-sw-device.c

## Purpose
`industrialio-sw-device.c` implements configfs support for software-created IIO devices. It lets software device type providers register a named type under `iio/devices`, and lets userspace instantiate or remove devices by creating or deleting configfs groups under that type.

## Important APIs, types, and functions
- `iio_devices_group` is the configfs default group registered under the exported IIO configfs subsystem.
- `iio_device_types_list` and `iio_device_types_lock` track registered `struct iio_sw_device_type` providers.
- `iio_register_sw_device_type()` inserts a unique provider type and creates its default configfs group.
- `iio_unregister_sw_device_type()` removes the provider from the list and unregisters its configfs group.
- `iio_sw_device_create()` resolves a type, obtains its owner module, calls provider `ops->probe(name)`, and records the device type on success.
- `iio_sw_device_destroy()` calls provider `ops->remove()` and drops the module reference.
- `device_make_group()` and `device_drop_group()` are configfs group operations for instance creation/destruction.

## Control flow
At module init, the file registers an `iio/devices` default group. Provider modules call `iio_register_sw_device_type()` with a name, owner, and probe/remove ops. Registration rejects duplicate names under lock, appends the type to the global list, then creates a child group named after the type. Userspace creates a group below that type; configfs calls `device_make_group()`, which probes a new software device and names the returned config group. Removing the configfs item calls `device_drop_group()`, which destroys the software device and drops the config item reference.

## State and persistence behavior
State is runtime-only: registered type list, provider configfs groups, instantiated software device config groups, and provider module references while instances exist. Device-specific state is owned by provider probe/remove implementations. Configfs hierarchy contents are not persistent across reboot unless userspace recreates them.

## Dependencies and integration points
The file depends on configfs, the exported `iio_configfs_subsys`, module reference counting, and provider implementations of `struct iio_sw_device_type`. It is the generic bridge between userspace configfs operations and software IIO device providers.

## Risks
- If `configfs_register_default_group()` fails in `iio_register_sw_device_type()`, this file returns the error but does not remove the just-added device type from the list. That can leave a registered type without a configfs group.
- `__iio_find_sw_device_type()` accepts a `len` argument but ignores it, so callers rely entirely on null-terminated names.
- Provider `probe()` must initialize `d->group` correctly before returning; configfs instance creation assumes it can name and return that group.
- Provider remove paths run from configfs item teardown and must tolerate userspace-driven lifetime ordering.

## Test signals
- Configfs tests should verify `iio/devices` appears, type registration creates a child group, duplicate registration returns `-EBUSY`, and unregister removes the group.
- Instance tests should create and delete configfs groups, verify provider probe/remove calls, and check module references around active instances.
- Failure injection should cover provider probe failure and default-group registration failure to detect stale list entries.
