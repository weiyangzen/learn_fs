# Group Research: group_979_linux_stable_sources_os_linux_linux_stable_fs_ext2_super_c_sources_o_06b28306ae84

Scope checked against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/super.c

## Purpose

`super.c` is the ext2 filesystem mount, superblock, lifecycle, quota, and module registration implementation. It wires ext2 into the Linux VFS through `file_system_type`, `super_operations`, `export_operations`, and `fs_context_operations`.

## Main Responsibilities

- Reports and handles filesystem errors via `ext2_error()`, including setting `EXT2_ERROR_FS`, syncing the superblock, panic-on-error, and remount-readonly behavior.
- Manages in-core ext2 superblock state in `struct ext2_sb_info`, including group descriptors, counters, reservation state, xattr block cache, DAX device reference, and quota hooks.
- Allocates and frees ext2 inode cache objects through `ext2_inode_cachep`, `ext2_alloc_inode()`, `ext2_free_in_core_inode()`, and `init_once()`.
- Parses mount parameters using the modern fs_context parser in `ext2_parse_param()`.
- Loads and validates the on-disk ext2 superblock and group descriptors in `ext2_fill_super()`.
- Provides remount/reconfigure logic in `ext2_reconfigure()`.
- Implements `statfs`, sync, freeze, unfreeze, NFS export inode lookup, and optional quota file I/O.
- Registers/unregisters the `ext2` filesystem module.

## Key Data and Operations

- `ext2_sops` provides VFS super operations: inode allocation/freeing, write/evict inode, put_super, sync, freeze/unfreeze, statfs, option display, and quota read/write when enabled.
- `ext2_export_ops` supports NFS export using 32-bit inode file handles and `ext2_get_parent`.
- `ext2_param_spec` accepts options such as `bsddf`, `minixdf`, `grpid`, `resuid`, `resgid`, `sb`, `errors=`, `nouid32`, `debug`, `oldalloc`, `orlov`, `user_xattr`, `acl`, `dax`, quotas, and `reservation`.
- `struct ext2_fs_context` records parsed mount options separately from persistent superblock state until mount/reconfigure applies them.
- `ext2_set_options()` combines parsed options with on-disk defaults, including default error behavior and reserved uid/gid.
- `ext2_fill_super()` performs the critical mount path: allocate `sbi`, set block size, read superblock, validate feature flags, validate block/inode geometry, read group descriptors, initialize counters, create xattr cache, set VFS operations, load root inode, and mark the filesystem mounted.
- `ext2_check_descriptors()` verifies each group’s block bitmap, inode bitmap, and inode table lie inside the group.
- `ext2_max_size()` computes ext2 maximum file size from block size and indirect block limits.
- `descriptor_loc()` handles descriptor block placement, including meta block groups.
- `ext2_sync_super()`, `ext2_sync_fs()`, `ext2_freeze()`, and `ext2_unfreeze()` update free counts, timestamps, and valid/error state.
- Quota support directly reads/writes quota files through `ext2_get_block()` and buffer heads, bypassing page cache assumptions.

## Notable Behavior

- DAX mount support is present but emits a deprecation warning saying ext2 DAX support will be removed at the end of 2025 and recommends ext4.
- Unsupported incompatible features abort mount; unsupported readonly-compatible features abort read-write mount.
- Ext3-with-journal filesystems can be mounted as ext2 with a warning.
- Remount refuses to change the DAX flag while busy inodes may exist.
- Read-only remount restores valid filesystem state only when appropriate; read-write remount rechecks readonly-compatible feature support.
- On writeable mounts, `ext2_setup_super()` increments mount count and warns about unchecked, errored, over-mounted, or stale-checktime filesystems.

## Dependencies

- Uses `ext2.h`, `xattr.h`, and `acl.h` for ext2 layout, xattr, and ACL integration.
- Relies on Linux VFS, buffer heads, fs_context, quota, DAX, exportfs, percpu counters, and block device helpers.
- Calls into other ext2 units such as inode loading/writing, block counting, reservation windows, group descriptor helpers, and xattr cache creation/destruction.

## Research Notes

This file is the best entry point for understanding ext2 mount-time trust boundaries. The mount path is heavily validation-oriented: feature bits, block size, inode size, group descriptor placement, group/inode counts, root inode shape, and backing-device size are all checked before the filesystem becomes live.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/symlink.c

## Purpose

Defines ext2 inode operations for normal and fast symbolic links.

## Main Responsibilities

- Provides `ext2_symlink_inode_operations` for page-backed symlinks.
- Provides `ext2_fast_symlink_inode_operations` for inline fast symlinks.
- Connects symlink inodes to common ext2 getattr, setattr, and xattr listing behavior.

## Key Operations

- Normal symlinks use `.get_link = page_get_link`.
- Fast symlinks use `.get_link = simple_get_link`.
- Both operation tables expose:
  - `.getattr = ext2_getattr`
  - `.setattr = ext2_setattr`
  - `.listxattr = ext2_listxattr`

## Dependencies

- Includes `ext2.h` for inode attribute helpers.
- Includes `xattr.h` for `ext2_listxattr`.

## Research Notes

The file is intentionally small because generic VFS/pagecache symlink helpers handle most symlink behavior. The ext2-specific part is operation table selection between page-backed and fast symlink storage.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/trace.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/trace.c

## Purpose

Instantiates ext2 tracepoints declared in `trace.h`.

## Main Responsibilities

- Includes `ext2.h` and `<linux/uio.h>`.
- Defines `CREATE_TRACE_POINTS` before including `trace.h`, causing tracepoint storage/definitions to be generated in this translation unit.

## Dependencies

- Directly paired with `fs/ext2/trace.h`.
- Tracepoints use Linux tracepoint infrastructure.

## Research Notes

This file has no runtime logic of its own. Its role is build/linkage: one C file must define `CREATE_TRACE_POINTS` for the trace events declared in the corresponding trace header.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/trace.h -->
# File Research: sources/os/linux/linux-stable/fs/ext2/trace.h

## Purpose

Declares ext2 trace events for direct I/O read/write paths.

## Main Responsibilities

- Sets `TRACE_SYSTEM ext2`.
- Defines an event class `ext2_dio_class` for common direct I/O fields.
- Defines direct I/O read/write events from that class.
- Defines a distinct endio event for write completion.

## Key Trace Events

- `ext2_dio_write_begin`
- `ext2_dio_write_end`
- `ext2_dio_write_buff_end`
- `ext2_dio_read_begin`
- `ext2_dio_read_end`
- `ext2_dio_write_endio`

## Captured Fields

The common event class records:

- Device major/minor.
- Inode number.
- File size.
- I/O position.
- Requested iterator count.
- `ki_flags`.
- Whether the I/O is async.
- Return value.

`ext2_dio_write_endio` records similar context but uses completed size and integer return status.

## Dependencies

- Uses `<linux/tracepoint.h>`.
- Uses `file_inode()`, `iov_iter_count()`, `is_sync_kiocb()`, and `TRACE_IOCB_STRINGS`.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace`, and `<trace/define_trace.h>`.

## Research Notes

The tracepoints are focused narrowly on direct I/O observability, not broad ext2 metadata tracing. They are useful for correlating direct I/O submission/completion with inode size, position, length, flags, and async status.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/xattr.c

## Purpose

Implements ext2 extended attribute storage, lookup, listing, mutation, sharing, caching, and cleanup.

## On-Disk Model

Ext2 xattrs live in external filesystem blocks referenced by `EXT2_I(inode)->i_file_acl`. Each xattr block contains:

- `struct ext2_xattr_header`.
- Sorted variable-length xattr entries growing downward.
- A null terminator.
- Attribute values packed from the end of the block upward.

Identical xattr blocks can be shared by multiple inodes. Sharing is controlled by the xattr block header refcount and an `mb_cache` keyed by block content hash.

## Main Responsibilities

- Maps xattr namespace indexes to Linux xattr handlers.
- Gets xattr values with `ext2_xattr_get()`.
- Lists xattr names with `ext2_listxattr()` via `ext2_xattr_list()`.
- Creates, replaces, or removes xattrs with `ext2_xattr_set()`.
- Updates the superblock compat feature when xattrs are first introduced.
- Handles xattr block copy-on-write and sharing with `ext2_xattr_set2()`.
- Releases xattr blocks on inode deletion with `ext2_xattr_delete_inode()`.
- Maintains xattr block cache entries and hashes.

## Key Validation

- `ext2_xattr_header_valid()` requires `EXT2_XATTR_MAGIC` and exactly one disk block.
- `ext2_xattr_entry_valid()` rejects entries that run beyond the block, reference external value blocks, or point values beyond the permitted region.
- `ext2_xattr_cmp_entry()` relies on sorted namespace/name order.
- Bad xattr blocks call `ext2_error()` and return `-EIO`.

## Mutation Flow

`ext2_xattr_set()`:

- Validates name and value length.
- Initializes quotas.
- Takes `xattr_sem` for write.
- Reads existing xattr block if present.
- Locates the target sorted entry or insertion point.
- Computes free space.
- Enforces `XATTR_CREATE` and `XATTR_REPLACE`.
- Modifies in place only when the block refcount is one and no cache user is trying to reuse it.
- Otherwise clones the block into memory.
- Inserts/removes entry names and repacks values.
- Rehashes entries and delegates filesystem updates to `ext2_xattr_set2()`.

`ext2_xattr_set2()`:

- Searches for an identical cached xattr block.
- Reuses a found block by incrementing refcount and quota accounting.
- Keeps the old block if it was safely modified in place.
- Allocates a new block if no reusable block exists.
- Updates `i_file_acl`, inode ctime, inode metadata, and releases no-longer-used old blocks.

## Cache and Sharing

- `ext2_xattr_cache_insert()` inserts hash/block mappings into `mb_cache`, ignoring duplicate `-EBUSY`.
- `ext2_xattr_cache_find()` scans matching hash entries, reads candidate blocks, locks them, checks refcount ceiling, compares full block contents, and returns a locked matching buffer.
- `ext2_xattr_release_block()` either frees a singly referenced block or decrements refcount on a shared block, carefully serializing against concurrent reuse through `mb_cache_entry_delete_or_get()`.

## Dependencies

- Includes buffer heads, mbcache, quotaops, rwsems, security, `ext2.h`, `xattr.h`, and `acl.h`.
- Depends on ext2 allocation/freeing helpers, quota helpers, inode dirtying, and superblock feature update logic.

## Research Notes

This file is a compact copy-on-write metadata subsystem. The most important correctness concerns are block validation, sorted entries, packed value offsets, shared-block refcounts, and cache synchronization. The code avoids holding multiple buffer locks simultaneously to reduce deadlock risk.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/ext2/xattr.h

## Purpose

Defines ext2 xattr on-disk structures, namespace indexes, alignment macros, and public xattr APIs.

## Main Definitions

- `EXT2_XATTR_MAGIC`: magic for xattr blocks.
- `EXT2_XATTR_REFCOUNT_MAX`: maximum shared xattr block references.
- Namespace indexes:
  - `EXT2_XATTR_INDEX_USER`
  - `EXT2_XATTR_INDEX_POSIX_ACL_ACCESS`
  - `EXT2_XATTR_INDEX_POSIX_ACL_DEFAULT`
  - `EXT2_XATTR_INDEX_TRUSTED`
  - `EXT2_XATTR_INDEX_LUSTRE`
  - `EXT2_XATTR_INDEX_SECURITY`
- `struct ext2_xattr_header`: magic, refcount, block count, hash, reserved fields.
- `struct ext2_xattr_entry`: name metadata, value offset/block/size, hash, flexible name.
- Alignment helpers:
  - `EXT2_XATTR_LEN()`
  - `EXT2_XATTR_NEXT()`
  - `EXT2_XATTR_SIZE()`

## Conditional API Surface

When `CONFIG_EXT2_FS_XATTR` is enabled, declares:

- xattr handlers for user/trusted/security namespaces.
- `ext2_listxattr()`.
- `ext2_xattr_get()` and `ext2_xattr_set()`.
- `ext2_xattr_delete_inode()`.
- xattr mbcache create/destroy helpers.
- `ext2_xattr_handlers`.

When xattrs are disabled:

- `ext2_xattr_get()` and `ext2_xattr_set()` return `-EOPNOTSUPP`.
- `ext2_xattr_delete_inode()` and cache destroy are no-ops.
- `ext2_xattr_handlers` and `ext2_listxattr` collapse to `NULL`.

When `CONFIG_EXT2_FS_SECURITY` is disabled:

- `ext2_init_security()` is an inline no-op returning success.

## Dependencies

- Includes `<linux/init.h>` and `<linux/xattr.h>`.
- Forward declares `struct mb_cache`.

## Research Notes

This header is the contract between ext2 inode/superblock code and xattr implementation files. The conditional stubs let non-xattr builds compile away xattr behavior cleanly while preserving call sites.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr_security.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/xattr_security.c

## Purpose

Implements ext2 `security.*` extended attribute handling and security label initialization.

## Main Responsibilities

- Provides get/set wrappers for the security xattr namespace.
- Initializes new inode security xattrs through Linux Security Module hooks.
- Exposes `ext2_xattr_security_handler`.

## Key Operations

- `ext2_xattr_security_get()` calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_SECURITY`.
- `ext2_xattr_security_set()` calls `ext2_xattr_set()` with `EXT2_XATTR_INDEX_SECURITY`.
- `ext2_initxattrs()` iterates the xattrs supplied by the security layer and stores each as a security xattr.
- `ext2_init_security()` calls `security_inode_init_security()` with `ext2_initxattrs`.

## Dependencies

- Includes `ext2.h`, `<linux/security.h>`, and `xattr.h`.
- Depends on `CONFIG_EXT2_FS_SECURITY` declarations from `xattr.h`.

## Research Notes

This file is the bridge between ext2’s xattr storage and LSM-managed labels such as SELinux labels. It contains no policy decisions; it stores labels requested by the security framework.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr_trusted.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/xattr_trusted.c

## Purpose

Implements ext2 `trusted.*` extended attribute handling.

## Main Responsibilities

- Restricts listing of trusted xattrs to callers with `CAP_SYS_ADMIN`.
- Provides get/set wrappers for the trusted xattr namespace.
- Exposes `ext2_xattr_trusted_handler`.

## Key Operations

- `ext2_xattr_trusted_list()` returns `capable(CAP_SYS_ADMIN)`.
- `ext2_xattr_trusted_get()` calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_TRUSTED`.
- `ext2_xattr_trusted_set()` calls `ext2_xattr_set()` with `EXT2_XATTR_INDEX_TRUSTED`.

## Dependencies

- Includes `ext2.h` and `xattr.h`.
- Uses Linux xattr handler prefix `XATTR_TRUSTED_PREFIX`.

## Research Notes

Trusted xattrs are privileged metadata. This file delegates persistence to the generic ext2 xattr block code and only adds namespace selection plus list permission filtering.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr_trusted.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr_user.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/xattr_user.c

## Purpose

Implements ext2 `user.*` extended attribute handling.

## Main Responsibilities

- Gates user xattr listing, get, and set on the ext2 `XATTR_USER` mount option.
- Provides get/set wrappers for the user xattr namespace.
- Exposes `ext2_xattr_user_handler`.

## Key Operations

- `ext2_xattr_user_list()` checks `test_opt(dentry->d_sb, XATTR_USER)`.
- `ext2_xattr_user_get()` returns `-EOPNOTSUPP` when user xattrs are disabled, otherwise calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_USER`.
- `ext2_xattr_user_set()` applies the same mount-option gate and calls `ext2_xattr_set()` with `EXT2_XATTR_INDEX_USER`.

## Dependencies

- Includes Linux init/string headers, `ext2.h`, and `xattr.h`.
- Uses `XATTR_USER_PREFIX`.

## Research Notes

The file enforces the mount-level policy for user-visible xattrs. Actual block format, validation, quota, and sharing behavior live in `xattr.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/xattr_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ext4/Kconfig

## Purpose

Defines kernel configuration options for building and enabling ext4 functionality.

## Main Options

- `EXT4_FS`: tristate ext4 filesystem support.
- `EXT4_USE_FOR_EXT2`: allows ext4 driver code to mount ext2 filesystems when the ext2 driver is not built.
- `EXT4_FS_POSIX_ACL`: enables ext4 POSIX ACL support and selects `FS_POSIX_ACL`.
- `EXT4_FS_SECURITY`: enables ext4 security labels through xattrs.
- `EXT4_DEBUG`: enables runtime ext4 debugging messages through dynamic debug.
- `EXT4_KUNIT_TESTS`: builds ext4 KUnit tests.

## Dependencies and Selections

`EXT4_FS` selects:

- `BUFFER_HEAD`
- `JBD2`
- `CRC16`
- `CRC32`
- `FS_IOMAP`
- `FS_ENCRYPTION_ALGS` when `FS_ENCRYPTION` is enabled

`EXT4_KUNIT_TESTS` depends on `EXT4_FS && KUNIT` and defaults to `KUNIT_ALL_TESTS`.

## Research Notes

The configuration describes ext4 as the successor to ext3 and notes it can mount ext3-compatible filesystems. Optional feature blocks map directly to conditional objects in the Makefile, especially ACL, security xattrs, encryption, verity, and tests.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ext4/Makefile

## Purpose

Builds the ext4 filesystem module/object set.

## Main Build Rules

- `obj-$(CONFIG_EXT4_FS) += ext4.o`
- `ext4-y` includes core ext4 implementation files:
  - allocation, bitmaps, block validity, directories, journaling, extents, file operations, fsmap, fsync, hashing, inode allocation, indirect blocks, inline data, inode logic, ioctls, multiblock allocation, migration, MMP, move extent, namei, page I/O, readpage, resize, superblock, symlink, sysfs, xattrs, trusted/user xattrs, fast commit, and orphan handling.
- `ext4-$(CONFIG_EXT4_FS_POSIX_ACL) += acl.o`
- `ext4-$(CONFIG_EXT4_FS_SECURITY) += xattr_security.o`
- `obj-$(CONFIG_EXT4_KUNIT_TESTS) += ext4-test.o`
- `ext4-$(CONFIG_FS_VERITY) += verity.o`
- `ext4-$(CONFIG_FS_ENCRYPTION) += crypto.o`

## Test Objects

`ext4-test-objs` includes:

- `inode-test.o`
- `mballoc-test.o`
- `extents-test.o`

## Research Notes

The Makefile shows ext4 is a broad monolithic filesystem object with feature-gated additions. The files in this research group cover early entries in `ext4-y` plus optional ACL/encryption support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/acl.c

## Purpose

Implements ext4 POSIX ACL conversion, retrieval, setting, and new-inode ACL initialization.

## Main Responsibilities

- Converts ACL xattr bytes from disk format into `struct posix_acl`.
- Converts `struct posix_acl` back into ext4 on-disk ACL xattr format.
- Implements VFS ACL hooks `ext4_get_acl()` and `ext4_set_acl()`.
- Initializes inherited ACLs for newly created inodes via `ext4_init_acl()`.

## Key Operations

- `ext4_acl_from_disk()` validates ACL version, computes entry count, allocates a POSIX ACL, converts tags/perms/ids, and rejects malformed sizes or unknown tags.
- `ext4_acl_to_disk()` serializes POSIX ACL entries into the compact ext4 ACL format, using short entries for owner/group/mask/other and full entries for named users/groups.
- `ext4_get_acl()` chooses access/default ACL xattr namespace, fetches the xattr with `ext4_xattr_get()`, and converts it.
- `__ext4_set_acl()` serializes ACL data and stores it with `ext4_xattr_set_handle()` inside a journal transaction.
- `ext4_set_acl()` initializes quotas, computes xattr journal credits, starts a journal handle, updates inode mode for access ACLs through `posix_acl_update_mode()`, sets the xattr, marks inode dirty if mode changed, and retries on ENOSPC when appropriate.
- `ext4_init_acl()` uses `posix_acl_create()` to derive inherited default/access ACLs and creates corresponding xattrs on a new inode.

## Dependencies

- Includes quotaops, `ext4_jbd2.h`, `ext4.h`, `xattr.h`, and `acl.h`.
- Uses ext4 journaling, quota initialization, xattr credit calculation, inode dirtying, and allocation retry support.

## Research Notes

ACL changes are journaled metadata updates. The file carefully couples xattr mutation with inode mode updates, so POSIX mode bits and access ACL state remain consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/acl.h

## Purpose

Defines ext4 ACL on-disk structures, sizing helpers, and conditional ACL API declarations.

## Main Definitions

- `EXT4_ACL_VERSION`
- `ext4_acl_entry`: tag, permission, and id for named ACL entries.
- `ext4_acl_entry_short`: tag and permission for entries without ids.
- `ext4_acl_header`: ACL format version.

## Helpers

- `ext4_acl_size(count)` computes serialized ACL size.
- `ext4_acl_count(size)` computes ACL entry count from serialized size and rejects misaligned/malformed sizes.

## Conditional API Surface

When `CONFIG_EXT4_FS_POSIX_ACL` is enabled:

- Declares `ext4_get_acl()`.
- Declares `ext4_set_acl()`.
- Declares `ext4_init_acl()`.

When disabled:

- `ext4_get_acl` and `ext4_set_acl` are `NULL`.
- `ext4_init_acl()` is an inline no-op.

## Dependencies

- Includes `<linux/posix_acl_xattr.h>`.
- The enabled API references ext4 journal handles and inodes.

## Research Notes

The header’s size/count helpers encode ext4’s compact ACL disk format where the first four common ACL entries can omit ids. This format detail is central to validation in `acl.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/balloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/balloc.c

## Purpose

Implements ext4 block group allocation support, bitmap loading/validation, free-space accounting, metadata block allocation helpers, backup superblock/GDT placement calculations, and allocation goal selection.

## Main Responsibilities

- Maps filesystem block numbers to block groups and bitmap offsets.
- Initializes uninitialized block bitmaps.
- Computes per-group metadata overhead and free clusters.
- Loads group descriptors and group info structures.
- Reads and validates block allocation bitmaps.
- Checks and claims free cluster availability.
- Retries allocations after ENOSPC when journal/discard progress may free blocks.
- Allocates metadata blocks through ext4 multiblock allocator.
- Counts free clusters across block groups.
- Computes backup superblock/group descriptor placement.
- Chooses inode-local allocation goal blocks.

## Key Operations

- `ext4_get_group_number()` and `ext4_get_group_no_and_offset()` convert block addresses to group/offset values, accounting for cluster size.
- `ext4_num_overhead_clusters()` counts base metadata, inode table clusters, and bitmap clusters while avoiding double counting.
- `ext4_init_block_bitmap()` zeros an uninitialized bitmap, marks metadata clusters used, marks bitmap padding, and verifies group descriptor checksum.
- `ext4_free_clusters_after_init()` estimates free clusters for uninitialized block bitmaps.
- `ext4_get_group_desc()` returns a group descriptor from the RCU-managed descriptor buffer array and validates group bounds.
- `ext4_valid_block_bitmap()` checks that block bitmap, inode bitmap, and inode table bits are set in a loaded bitmap.
- `ext4_validate_block_bitmap()` verifies checksum, structural bitmap correctness, and end padding, then marks the buffer verified.
- `ext4_read_block_bitmap_nowait()` gets/loads a bitmap buffer, initializes uninitialized bitmaps when permitted, submits async metadata reads, and validates already-present bitmaps.
- `ext4_wait_block_bitmap()` waits for async bitmap I/O and validates the loaded bitmap.
- `ext4_read_block_bitmap()` wraps nowait plus wait.
- `ext4_has_free_clusters()` accounts for free clusters, dirty clusters, reserved blocks, root-reserved blocks, and privileged allocation flags.
- `ext4_claim_free_clusters()` reserves dirty clusters if space is available.
- `ext4_should_retry_alloc()` retries ENOSPC up to three times when journal commits or discard work might release blocks.
- `ext4_new_meta_blocks()` allocates metadata blocks through `ext4_mb_new_blocks()`.
- `ext4_count_free_clusters()` sums free clusters from group descriptors, skipping corrupt bitmap groups.
- `ext4_bg_has_super()`, `ext4_bg_num_gdb()`, and `ext4_num_base_meta_blocks()` calculate backup superblock and descriptor metadata placement for sparse/meta_bg variants.
- `ext4_inode_to_goal_block()` chooses an allocation goal based on inode group, flex_bg layout, file type, delayed allocation, and process-derived color.

## Dependencies

- Includes ext4 core headers, journaling header, mballoc header, trace events, and KUnit static stubs.
- Depends on metadata checksum helpers, group locking, bitmap helpers, ext4 error reporting, buffer heads, JBD2, quota accounting, and multiblock allocator APIs.

## Research Notes

This file is defensive around allocator metadata. Bitmap data is not trusted until descriptor checksums, bitmap checksums, required metadata bits, and padding bits validate. It also contains important policy around reserved clusters and privileged allocation access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/bitmap.c

## Purpose

Provides ext4 bitmap free-bit counting and metadata checksum helpers for inode and block bitmaps.

## Main Responsibilities

- Counts free bits in a bitmap buffer.
- Verifies inode bitmap checksums.
- Sets inode bitmap checksums.
- Verifies block bitmap checksums.
- Sets block bitmap checksums.

## Key Operations

- `ext4_count_free()` returns total bits minus `memweight()`.
- `ext4_inode_bitmap_csum_verify()` checks `bg_inode_bitmap_csum_lo` and optional high checksum field when `metadata_csum` is enabled.
- `ext4_inode_bitmap_csum_set()` computes and stores inode bitmap checksum fields.
- `ext4_block_bitmap_csum_verify()` checks block bitmap checksum using cluster count.
- `ext4_block_bitmap_csum_set()` computes and stores block bitmap checksum fields.

## Dependencies

- Includes `<linux/buffer_head.h>` and `ext4.h`.
- Uses `ext4_chksum()`, superblock checksum seed, descriptor size, and metadata checksum feature detection.

## Research Notes

These helpers are called by allocation and inode-allocation code to detect metadata corruption. Checksumming is feature-gated; without `metadata_csum`, verification succeeds and setters return without changing descriptors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/block_validity.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/block_validity.c

## Purpose

Tracks ext4 filesystem metadata block ranges that must not be used as ordinary file or directory data blocks.

## Main Responsibilities

- Maintains an RCU-protected red-black tree of system zones.
- Adds and merges metadata block ranges.
- Builds the system-zone tree at mount/remount time.
- Releases the tree safely after RCU grace period.
- Validates inode block mappings and indirect block references against system zones.

## Key Data Structures

- `struct ext4_system_zone`: rbtree node containing start block, block count, and owning inode number.
- `ext4_system_zone_cachep`: slab cache for system-zone nodes.
- `struct ext4_system_blocks`: referenced through `sbi->s_system_blks`.

## Key Operations

- `ext4_init_system_zone()` and `ext4_exit_system_zone()` manage the slab cache.
- `add_system_zone()` inserts a non-overlapping metadata range and merges adjacent ranges with the same inode owner.
- `ext4_protect_reserved_inode()` maps blocks of special reserved inodes, such as the journal inode, and adds them as protected ranges.
- `ext4_setup_system_zone()` builds a complete tree from base metadata, block bitmaps, inode bitmaps, inode tables, and journal inode blocks, then publishes it with `rcu_assign_pointer()`.
- `ext4_release_system_zone()` clears the published pointer and frees the old tree after RCU grace period.
- `ext4_sb_block_valid()` rejects out-of-range blocks and blocks overlapping system zones, except when the overlapping zone belongs to the same inode.
- `ext4_inode_block_valid()` wraps superblock validation for an inode.
- `ext4_check_blockref()` scans 32-bit block references and reports `EFSCORRUPTED` if any reference targets invalid metadata space.

## Dependencies

- Includes VFS, namei, quota, buffer heads, swap, pagemap, blkdev, slab, and `ext4.h`.
- Uses ext4 group descriptor, metadata layout, block mapping, inode loading, and error-reporting helpers.

## Research Notes

This file is a mount-time metadata protection layer. It prevents corrupt or malicious metadata from causing ext4 to treat core filesystem structures as file data. The RCU swap pattern lets remount change block validity settings without racing readers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/block_validity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/crypto.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/crypto.c

## Purpose

Integrates ext4 with Linux fscrypt for encrypted filenames, encryption policy context storage, password salt ioctl support, and fscrypt operation registration.

## Main Responsibilities

- Converts `fscrypt_name` into ext4’s `ext4_filename`.
- Prepares encrypted/casefold-aware filenames for create and lookup.
- Frees filename crypto and casefold buffers.
- Implements `EXT4_IOC_GET_ENCRYPTION_PWSALT` behavior.
- Gets and sets encryption context xattrs.
- Registers ext4 fscrypt operations.

## Key Operations

- `ext4_fname_setup_filename()` calls `fscrypt_setup_filename()`, maps fields into `ext4_filename`, and sets up case-insensitive filename state.
- `ext4_fname_prepare_lookup()` calls `fscrypt_prepare_lookup()` for dentries and then prepares ext4 casefold state.
- `ext4_fname_free_filename()` releases fscrypt and ext4 casefold filename buffers.
- `ext4_ioctl_get_encryption_pwsalt()` lazily generates `s_encrypt_pw_salt` in the superblock under a journal transaction, updates checksum, dirties metadata, and copies the 16-byte salt to userspace.
- `ext4_get_context()` reads the encryption context xattr.
- `ext4_set_context()` stores encryption context xattrs, refuses root inode encryption, rejects DAX conflicts, converts inline data, handles new-inode inherited context with caller-supplied handle, and otherwise starts its own journal transaction with ENOSPC retry support.
- `ext4_get_dummy_policy()` exposes the dummy encryption policy from `sbi`.
- `ext4_has_stable_inodes()` reports the stable inode feature to fscrypt.

## fscrypt Operations

`ext4_cryptops` sets:

- inode crypto info offset.
- bounce-page requirement.
- 32-bit inode support.
- subblock data unit support.
- legacy key prefix `ext4:`.
- context get/set callbacks.
- dummy policy callback.
- empty-directory callback.
- stable-inode callback.

## Dependencies

- Includes quotaops, uuid helpers, `ext4.h`, `xattr.h`, and `ext4_jbd2.h`.
- Uses fscrypt, ext4 xattrs, journaling, inline-data conversion, inode flag updates, and superblock checksums.

## Research Notes

Encryption state is persisted as an xattr and journaled metadata. The file deliberately blocks encryption of the root inode and DAX-encrypted conflicts. Filename preparation also composes fscrypt with ext4 casefold support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/dir.c

## Purpose

Implements ext4 directory reading, directory entry validation, htree indexed directory iteration, directory seek behavior, and directory file operations.

## Main Responsibilities

- Detects htree-indexed directories.
- Validates ext4 directory entries.
- Implements linear and htree-backed `readdir`.
- Handles encrypted directory names during emit.
- Handles inline-data directories.
- Converts htree hash values to/from file positions.
- Stores htree results in a red-black tree ordered by hash.
- Provides ext4 directory file operations.

## Key Operations

- `is_dx_dir()` detects directories using, or eligible for, htree indexing based on `dir_index`, inode index flag, one-block size, or inline data.
- `is_fake_dir_entry()` identifies dot entries and checksum tail entries for validation sizing.
- `__ext4_check_dir_entry()` validates record length, alignment, name length, block bounds, checksum-tail spacing, inode bounds, and invalid final `.` placement. It reports errors through file or inode error paths.
- `ext4_readdir()` prepares fscrypt, tries htree iteration first, falls back for bad non-checksummed htree directories, handles inline data, reads mapped directory blocks, verifies directory block checksums, rescans when inode version changes, validates entries, decrypts names when needed, and emits entries with `dir_emit()`.
- `hash2pos()`, `pos2maj_hash()`, `pos2min_hash()`, and `ext4_get_htree_eof()` encode htree hash positions for 32-bit and 64-bit APIs.
- `ext4_dir_llseek()` uses hash-position seeking for htree directories and normal ext4 llseek otherwise.
- `struct fname` stores htree directory entries by hash/minor hash with a collision chain.
- `free_rb_tree_fname()` frees cached htree entries.
- `ext4_htree_init_dir_info()` initializes per-open directory htree state.
- `ext4_htree_free_dir_info()` frees per-open state.
- `ext4_htree_store_dirent()` inserts decoded htree entries into the rb tree.
- `call_filldir()` emits entries from a hash collision chain and remembers the next entry if the caller’s buffer fills.
- `ext4_dx_readdir()` fills and drains the htree rb tree, restarts when `f_pos` changes or directory version changes, and sets htree EOF.
- `ext4_check_all_de()` validates every dirent in a buffer.
- `ext4_dir_open()` allocates `dir_private_info`.
- `ext4_release_dir()` frees per-open directory state.

## File Operations

`ext4_dir_operations` provides:

- `.open = ext4_dir_open`
- `.llseek = ext4_dir_llseek`
- `.read = generic_read_dir`
- `.iterate_shared = ext4_readdir`
- `.unlocked_ioctl = ext4_ioctl`
- optional `.compat_ioctl`
- `.fsync = ext4_sync_file`
- `.release = ext4_release_dir`
- `.setlease = generic_setlease`

## Dependencies

- Includes VFS, buffer heads, file locking, slab, inode versioning, unicode, `ext4.h`, and `xattr.h`.
- Uses fscrypt, ext4 htree fill, inline directory handling, block mapping, block checksums, directory checksums, inode versioning, and dtype conversion.

## Research Notes

This file is a high-value correctness surface because directory parsing is exposed to untrusted disk data. Validation is layered: block checksum first, then per-entry record validation, then inode bounds. Htree iteration decouples disk order from userspace order by caching entries in hash order.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/dir.c -->