# sources/distributed-fs/ceph-client/fs/btrfs/ioctl.c

## Purpose
`ioctl.c` is Btrfs' user-control surface for inode flags, subvolume and snapshot lifecycle, device management, scrub, balance, quotas, feature flags, tree/backref queries, encoded I/O, fs-verity delegation, sync controls, and forced shutdown. It is the switchboard behind `btrfs_ioctl()`, `btrfs_compat_ioctl()`, file attribute get/set, and the Btrfs io_uring encoded I/O command implementation. The source was read as a complete 5320-line file.

## Important APIs, Types, and Functions
Exported entry points are `btrfs_ioctl()`, `btrfs_compat_ioctl()`, `btrfs_fileattr_get()`, `btrfs_fileattr_set()`, `btrfs_ioctl_get_supported_features()`, `btrfs_sync_inode_flags_to_i_flags()`, `btrfs_update_ioctl_balance_args()`, `btrfs_uring_cmd()`, and `btrfs_uring_read_extent_endio()`. Compat-only UAPI shims define packed 32-bit variants for received-subvol timestamps, send args, and encoded I/O args.

Major helper groups are inode flag translation and validation; fitrim; subvolume and snapshot creation/deletion/status; tree search and inode/path lookup; device add/remove/resize/info/stats/replace; space-info reporting; transaction sync and wait; scrub; balance start/control/progress; quota and qgroup operations; received-subvolume metadata updates; filesystem label and feature flag updates; send ioctl adaptation; encoded read/write through ioctl and io_uring; subvolume deletion wait modes; and shutdown handling.

## Control Flow
`btrfs_ioctl()` decodes the command and dispatches directly to a command-specific helper. Mutating paths consistently check capability or ownership, call `mnt_want_write_file()` where needed, validate copied UAPI structures before changing state, then use Btrfs transactions or exclusive-operation state to serialize filesystem-wide work.

Subvolume creation flows through `btrfs_ioctl_snap_create*()` into `__btrfs_ioctl_snap_create()`, `btrfs_mksubvol()`, then either `create_subvol()` or `create_snapshot()`. New subvolumes allocate an objectid and anonymous device, reserve metadata/qgroup space, create a root item/tree block/UUID item/inode, record the new root in the transaction, set orphan cleanup state, and instantiate the dentry. Snapshots force delalloc, wait ordered extents, use `pending_snapshot`, and commit the transaction to materialize the snapshot. Deletion validates name or id, resolves out-of-mount subvolumes when requested, enforces admin or `USER_SUBVOL_RM_ALLOWED` policy, then calls `btrfs_delete_subvolume()`.

Device and allocator flows use exclusive operations. Resize parses `devid:size`, `+/-` deltas, `max`, and `cancel`, then grows in a transaction or shrinks through the volume layer. Device add/remove, balance, and device replace reject unsupported extent-tree-v2 cases where noted and use the exclusive-operation framework to avoid conflicting relocations. Scrub copies progress back even on error so userspace can resume.

Query paths either walk B-trees under allocated `btrfs_path` objects or copy aggregate in-memory state. Tree search loops through `btrfs_search_forward()` and uses fault-in plus nofault copies to avoid repeated user faults. Inode/path lookup climbs inode refs and root refs, with the unprivileged variant checking read/execute permissions while building the path.

Encoded I/O imports user iovecs, verifies access, delegates to `btrfs_encoded_read()` or `btrfs_do_write_iter()`, and accounts task I/O. io_uring encoded read can return with inode and extent locks logically held until `btrfs_uring_read_finished()` copies pages to the user iterator and releases locks in task work.

## State and Persistence Behavior
Persistent changes include root tree items, UUID tree entries, root flags, default subvolume dir items, device tree/superblock device state, qgroup items, feature flags in the superblock, filesystem label, received-subvolume UUID/time/transid fields, file inode flags/properties, and subvolume-deletion queues. Runtime-only state includes exclusive operation markers, scrub/balance/dev-replace progress structures, root and subvolume semaphores, radix/dead-root lists, pending io_uring command state, and copied UAPI buffers.

Transactions protect metadata changes, `subvol_sem` serializes root visibility and readonly flag changes, `balance_mutex` and exclusive-operation state serialize global relocation/device work, `super_lock` protects the in-memory superblock label/feature fields, and inode/extent locks protect encoded I/O ranges.

## Dependencies and Integration Points
This file integrates with VFS ioctl/fileattr/fsnotify/verity/io_uring APIs, Linux capability and usercopy helpers, Btrfs transaction/root/extent/volume/qgroup/scrub/balance/send/defrag/backref/compression/tree-log/uuid subsystems, block discard for fitrim, and userspace UAPI structures from `<linux/btrfs.h>`. It is the principal kernel endpoint for btrfs-progs operations.

## Risks and Edge Cases
High-risk areas are UAPI structure validation, compat packing, user pointer copy/fault behavior, and keeping ioctl output useful on partial failures. Mutating ioctls must not start transactions before cheap validation that avoids malicious transaction aborts, as shown by UUID tree overflow checks. Subvolume deletion by id has idmapped-mount restrictions to prevent deleting unrelated subvolumes through a remapped fd. Snapshot creation and deletion are explicitly blocked for extent-tree-v2. Encoded io_uring read deliberately spans async completion with locks held and therefore relies on explicit lockdep annotations and exact cleanup. Exclusive-operation cancellation must distinguish no-op, in-progress, and cancel states.

## Test Signals
Useful signals include xfstests for subvolume create/delete/sync, snapshot readonly transitions during send, idmapped mount deletion restrictions, tree-search v1/v2 overflow behavior, 32-bit compat ioctl packing, device add/remove/resize/cancel conflicts, balance pause/resume/cancel/progress, scrub progress on cancellation, qgroup enable/assign/limit/rescan, feature flag safe set/clear rejection, label length validation, encoded read/write and io_uring encoded read/write including `NOWAIT`/reissue, fsverity ioctl passthrough, shutdown modes, and fault injection for usercopy/allocation/transaction failures.
