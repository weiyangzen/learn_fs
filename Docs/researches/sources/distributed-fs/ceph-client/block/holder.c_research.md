<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/holder.c -->
# sources/distributed-fs/ceph-client/block/holder.c

## Purpose
`holder.c` implements deprecated sysfs relationship links between a block device that is claimed as a slave and a gendisk that holds it. It is used by legacy stacking drivers such as device mapper to expose `/sys/block/<holder>/slaves/<slave>` and `/sys/block/<slave>/holders/<holder>`.

## Important APIs, Types, and Functions
- `struct bd_holder_disk` tracks one holder relationship with a list node, referenced holder directory kobject, and refcount.
- `bd_link_disk_holder()` creates the two symlinks and records/refcounts the relationship.
- `bd_unlink_disk_holder()` removes symlinks and drops the holder directory kobject when the relationship refcount reaches zero.
- `blk_holder_mutex` serializes relationship list and symlink operations.

## Control Flow
`bd_link_disk_holder()` rejects missing holder/slave directories and self-links, takes `bdev->bd_disk->open_mutex` to verify the slave disk is still live, and takes a kobject reference to survive past gendisk deletion. Under `blk_holder_mutex`, it either bumps the existing relationship refcount or allocates a `bd_holder_disk`, creates the holder-to-slave symlink, creates the slave-to-holder symlink, and links the record into `disk->slave_bdevs`. Partial creation failures unwind symlinks and references.

`bd_unlink_disk_holder()` looks up the relationship, decrements the refcount, and on zero removes both symlinks, drops the saved holder directory reference, deletes the list node, and frees the holder object.

## State and Persistence Behavior
There is no persistent disk format state. Runtime state is sysfs topology plus refcounted `bd_holder_disk` records on `disk->slave_bdevs`. Kobject references deliberately outlive `del_gendisk()` dropping the initial holder-dir reference so cleanup can still remove links safely.

## Dependencies and Integration Points
The file depends on `CONFIG_BLOCK_HOLDER_DEPRECATED` users, gendisk `slave_dir`, bdev `bd_holder_dir`, kobjects/sysfs, and block-device claiming semantics managed elsewhere. Both public functions are exported GPL-only.

## Risks and Edge Cases
Callers must already hold a valid claim and lifetime references; this file only validates obvious live-state conditions. Missing unlink calls leave stale topology until teardown. Symlink creation is two-phase and must unwind correctly. The typo in the doc comment (`calimed`) is harmless but indicates the interface is maintenance-only.

## Test Signals
Exercise stacked block devices that still call these helpers, verify sysfs links appear/disappear across repeated claims, check refcount behavior under duplicate links, run hot-unplug/teardown tests with live holders, and use lockdep/KASAN for kobject lifetime mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/holder.c -->
