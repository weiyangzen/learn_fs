<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/gen_disk.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq/gen_disk.rs

## Purpose
This file wraps C `struct gendisk` creation and teardown for Rust blk-mq drivers.

## Important APIs, Types, and Functions
`GenDiskBuilder` carries `rotational`, `logical_block_size`, `physical_block_size`, and `capacity_sectors`. It provides `new`, `rotational`, `validate_block_size`, `logical_block_size`, `physical_block_size`, `capacity_sectors`, and `build`. `GenDisk<T: Operations>` owns a raw `gendisk` pointer and an `Arc<TagSet<T>>` to preserve tag-set lifetime.

## Control Flow and State
`build` converts driver queue data into a foreign pointer, guards it with `ScopeGuard`, fills `queue_limits`, allocates the disk with `__blk_mq_alloc_disk`, installs a mostly empty `block_device_operations` table, writes a NUL-terminated disk name, sets capacity, and calls `device_add_disk`. On success it dismisses the recovery guard so queue data is owned by the disk queue; on failure the guard reconstructs and drops queue data.

## State and Persistence Behavior
After successful build, the gendisk is registered in VFS/block core and owns queue data in `queue.queuedata`. `GenDisk::drop` fetches that queue data, calls `del_gendisk`, then reconstructs and drops the `ForeignOwnable` queue data. The `Arc<TagSet<T>>` field keeps the tag set alive until disk teardown.

## Dependencies and Integration Points
The file depends on blk-mq bindings, `TagSet`, `Operations`, kernel formatting, `NullTerminatedFormatter`, `ForeignOwnable`, `ScopeGuard`, and static lock-class helpers. It integrates with C block-device operations, queue limits, capacity management, and disk registration.

## Risks
`build` must handle ownership transfer exactly once. If `device_add_disk` fails after queue data is installed, the guard must recover it. Disk names must fit the C fixed buffer. The operations table currently has `owner: null_mut()` with a TODO, so module ownership protection may be incomplete. Block size validation constrains sizes to powers of two in `[512, PAGE_SIZE]`; misuse by callers can return `EINVAL`.

## Test Signals
No local tests exist. The module-level blk-mq example exercises the builder path. Runtime validation would require creating a test block driver and checking registration/teardown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/gen_disk.rs -->
