# sources/distributed-fs/ceph-client/drivers/iio/industrialio-sw-trigger.c

## Purpose
`industrialio-sw-trigger.c` implements configfs support for software-created IIO triggers. Trigger type providers register named types under `iio/triggers`, and userspace creates trigger instances by creating configfs groups below a type.

## Important APIs, types, and functions
- `iio_triggers_group` is the configfs default group registered under `iio`.
- `iio_trigger_types_list` and `iio_trigger_types_lock` track registered `struct iio_sw_trigger_type` providers.
- `iio_register_sw_trigger_type()` adds a unique type and creates the corresponding configfs default group, rolling back the list insertion on configfs failure.
- `iio_unregister_sw_trigger_type()` removes the type from the list and unregisters its group.
- `iio_sw_trigger_create()` obtains the provider module, calls `ops->probe(name)`, and stores the type on the returned trigger.
- `iio_sw_trigger_destroy()` calls provider `ops->remove()` and drops the module reference.
- `trigger_make_group()` and `trigger_drop_group()` connect configfs mkdir/rmdir to trigger create/destroy.

## Control flow
At module init, `iio_sw_trigger_init()` registers an `iio/triggers` default group under the shared IIO configfs subsystem. Providers register trigger types; each type appears as a child directory. When userspace creates an instance group below a type, configfs calls `trigger_make_group()`, which creates a trigger via the provider and returns its config group. Removing the configfs item calls `trigger_drop_group()`, which destroys the trigger and releases the item.

## State and persistence behavior
Runtime state consists of the registered trigger type list, configfs type groups, active trigger instance groups, and provider module references while instances exist. Actual trigger device state is provider-owned. Configfs-created instances disappear on removal/unload and are not persisted by this file.

## Dependencies and integration points
The file depends on configfs, `iio_configfs_subsys`, software trigger provider APIs, module reference counting, and provider implementations that usually register actual `struct iio_trigger` objects with the trigger core.

## Risks
- Provider probe/remove must correctly initialize and tear down both configfs group state and trigger-core state; this wrapper does not validate those details.
- The find helper ignores its `len` argument, matching by full string compare.
- Userspace controls instance names through configfs; providers must validate names if they map to hardware-meaningful resources.
- Type unregister while instances exist depends on configfs/provider lifetime correctness.

## Test signals
- Configfs tests should verify `iio/triggers`, type registration/unregistration, duplicate type rejection, and rollback when default-group creation fails.
- Instance tests should create/delete software triggers, verify provider probe/remove and module references, and check that trigger core registration is cleaned up.
- Negative tests should try invalid type names and provider probe failures.
