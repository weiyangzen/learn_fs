# sources/distributed-fs/ceph-client/fs/nilfs2/nilfs.h

## Purpose

`nilfs.h` is the local umbrella header for the NILFS2 filesystem implementation. It defines the in-memory NILFS inode wrapper, dynamic inode state bits, transaction context layout, inode-number classification macros, mount/error message helpers, and prototypes for major internal subsystems.

## Important APIs, Types, and Functions

`struct nilfs_inode_info` embeds `struct inode` and stores NILFS-specific state: file flags and type bits, dynamic state bits, bmap storage, xattr block pointer, directory lookup cursor, GC checkpoint number, associated cache inode, dirty-list linkage, optional xattr semaphore, raw inode buffer, root pointer, and VFS inode.

`NILFS_I()` and `NILFS_BMAP_I()` convert from generic VFS/bmap objects to NILFS-private structures. `NILFS_I_*` state bits describe new, dirty, queued, busy, collected, updated, inode-sync, and bmap-cache state. `NILFS_I_TYPE_*` distinguishes normal, GC, btree-node-cache, and shadow-cache inodes.

`struct nilfs_transaction_info` tracks nested NILFS transactions in `current->journal_info`, with flags for dynamic allocation, synchronous construction, GC context, commit occurrence, and writer context. Prototypes expose `nilfs_transaction_begin()`, `nilfs_transaction_commit()`, and `nilfs_transaction_abort()`.

The header also declares internal operations from directory, file, ioctl, inode, superblock, GC inode, sysfs, address-space, and filesystem registration modules. Message macros wrap `__nilfs_msg()` and `__nilfs_error()`.

## Control Flow

Most mutating filesystem code includes this header and follows the transaction pattern defined here: begin a transaction, mutate inode/directory/metadata state, mark inodes dirty, then commit or abort. Segment construction tests transaction flags such as `NILFS_TI_GC` and `NILFS_TI_WRITER` to decide whether writes are normal, GC, or constructor-owned.

Inode code uses `NILFS_VALID_INODE()`, `NILFS_MDT_INODE()`, and `NILFS_PRIVATE_INODE()` to distinguish user-visible files, root/system files, metadata files, and private inodes. Superblock and mount code use the declared `nilfs_read_super_block()`, feature checks, log cursor, commit, cleanup, resize, checkpoint attach, and checkpoint mount-test helpers.

## State and Persistence Behavior

The header separates volatile inode state (`i_state`, dirty lists, associated cache inodes) from persistent inode fields stored in `struct nilfs_inode` on disk. `i_bh` pins the buffer containing a dirty on-disk inode while the segment constructor collects and writes it.

Transaction state is per-task and not persistent; its role is to serialize modifications against segment construction and to trigger eventual log writing. Persistent effects are committed through the segment constructor and superblock routines declared here.

## Dependencies and Integration Points

`nilfs.h` pulls in Linux kernel, buffer-head, block-device, filesystem, NILFS on-disk API, `the_nilfs.h`, and bmap definitions. It is included by almost every NILFS2 implementation file and ties VFS operations, metadata files, block mapping, checkpoint/root management, sysfs, ioctl, and log writing together.

## Risks and Edge Cases

Because this is a central header, type or flag changes have wide blast radius. `current->journal_info` reuse must preserve any foreign filesystem pointer via `ti_save`; errors there can corrupt unrelated filesystem state in stacked paths. The inode-number macros rely on constants fitting in bit operations for low system inode numbers. The disabled POSIX ACL block explicitly errors if enabled, so configuration drift can break builds.

## Test Signals

Build coverage across NILFS2 configs is essential. Runtime tests should watch dirty/busy/queued inode state transitions, nested transaction begin/commit/abort, GC transaction flags, system inode validation, mount option error handling, and message/error behavior that sets `NILFS_ERROR_FS` through `nilfs_error()`.
