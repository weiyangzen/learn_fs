# File Research: sources/block-storage/linux-dm/drivers/md/dm-sysfs.c

## Purpose
Provides sysfs integration for mapped devices by creating a `dm` kobject under the disk device and registering common DM attributes.

## Main Objects
- `struct dm_sysfs_attr`: wraps a sysfs `attribute` with mapped-device show/store callbacks.
- `dm_ktype`: kobject type with DM sysfs ops, default attributes, and release callback.

## Attributes
Read-only:
- `name`
- `uuid`
- `suspended`
- `use_blk_mq`

Read/write:
- `rq_based_seq_io_merge_deadline`

The read/write attribute is declared here through the macro; its show/store functions are supplied through included DM request-queue code.

## Control Flow
- `dm_attr_show()` resolves `mapped_device` from the kobject, calls the attribute-specific show handler, and drops the reference.
- `dm_attr_store()` does the same for store handlers.
- `dm_attr_name_show()` and `dm_attr_uuid_show()` copy the mapped-device name/UUID and append a newline.
- `dm_attr_suspended_show()` reports `dm_suspended_md()`.
- `dm_attr_use_blk_mq_show()` always reports true for userspace compatibility.
- `dm_sysfs_init()` initializes and adds the `dm` kobject below the disk kobject.
- `dm_sysfs_exit()` drops the kobject and waits for release completion.

## Dependencies
- `dm-core.h` for mapped-device kobject/name/UUID/reference helpers.
- `dm-rq.h` for request-queue attribute functions.
- Linux sysfs/kobject APIs.

## Risk and Test Focus
- Correct reference acquisition through `dm_get_from_kobject()` is central to avoiding use-after-free in sysfs callbacks.
- `dm_sysfs_exit()` waits for release completion; teardown ordering must ensure no stale sysfs callbacks survive mapped-device destruction.
