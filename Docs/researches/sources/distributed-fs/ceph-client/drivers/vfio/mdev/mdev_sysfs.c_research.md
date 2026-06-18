# sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_sysfs.c

## Purpose

`mdev_sysfs.c` creates the userspace sysfs interface for mediated device types and instances. It exposes supported type attributes, creation entry points, per-type device links, and per-mdev removal.

## Important APIs, Types, and Functions

`struct mdev_type_attribute` wraps kobject attributes with mdev-type show/store callbacks. Core type attributes are `create`, `device_api`, `name`, `available_instances`, and optional `description`. Public helpers are `parent_create_sysfs_files()`, `parent_remove_sysfs_files()`, `mdev_create_sysfs_files()`, and `mdev_remove_sysfs_files()`. The per-mdev device attribute is write-only `remove`.

## Control Flow

Parent registration creates a `mdev_supported_types` kset under the parent device and adds each type kobject named from the parent driver string and type sysfs name. Each type gets core attributes and a `devices` kobject. Writing a UUID string to `create` parses it and calls `mdev_device_create()`. After a device is added, `mdev_create_sysfs_files()` links the mdev under the type's `devices` directory and links the mdev back to its `mdev_type`. Writing nonzero to the mdev `remove` attribute uses `device_remove_file_self()` and then calls `mdev_device_remove()`.

## State and Persistence Behavior

Sysfs kobjects and links persist while the parent/type/mdev exists. The type kobject holds a parent device reference until release. No persistent storage exists; created mdevs are kernel devices.

## Dependencies and Integration Points

The file depends on sysfs/kobject APIs, GUID parsing, mdev parent/type structures, mdev lifecycle functions, and optional parent driver callbacks such as `show_description()` and `get_available()`.

## Risks and Edge Cases

UUID input length is tightly constrained to canonical string length plus optional newline. Type removal must remove `devices_kobj`, delete the type kobject, and drop references in the right order. If creating the second sysfs link fails, the first is removed. `remove_store()` relies on `device_remove_file_self()` to avoid racing removal of the attribute being written.

## Test Signals

Test type kset creation failure, per-type add failure unwind, attribute visibility without `show_description`, UUID parsing failures, duplicate and valid create, available instance reporting with static and dynamic providers, link creation/removal, self-remove behavior, and parent removal with active type/device links.
