# sources/distributed-fs/ceph-client/drivers/md/dm-sysfs.c

## Purpose
Provides the sysfs kobject and attributes under each mapped device, exposing name, UUID, suspended state, blk-mq compatibility state, and the deprecated request-based merge deadline attribute.

## Important APIs, Types, And Functions
`struct dm_sysfs_attr` wraps a sysfs attribute with mapped-device show/store callbacks. Attributes are `name`, `uuid`, `suspended`, `use_blk_mq`, and `rq_based_seq_io_merge_deadline`. Public lifecycle functions are `dm_sysfs_init()` and `dm_sysfs_exit()`.

## Control Flow
`dm_sysfs_init()` adds a `dm` kobject below the disk device kobject. Sysfs reads/writes obtain a mapped-device reference via `dm_get_from_kobject()`, call the attribute method, and drop the reference. Teardown puts the kobject and waits for release completion.

## State And Persistence
No persistent state exists. Attributes expose live mapped-device state; `use_blk_mq` always returns true for compatibility.

## Dependencies And Integration Points
Depends on Linux sysfs, DM ioctl naming, `dm-core.h`, `dm-rq.h`, mapped-device kobject release, and request-based compatibility handlers.

## Risks
Kobject lifetime and md references must prevent use-after-free during sysfs access and teardown. Compatibility attributes should remain stable for userspace.

## Test Signals
Create/remove mapped devices while reading attributes, verify suspend state changes, read/write `rq_based_seq_io_merge_deadline`, and run teardown races with refcount/KASAN debugging.
