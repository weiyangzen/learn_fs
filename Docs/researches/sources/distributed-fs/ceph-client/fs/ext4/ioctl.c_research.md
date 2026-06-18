# sources/distributed-fs/ceph-client/fs/ext4/ioctl.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/ioctl.c` implements ext4's file and filesystem ioctl surface, plus the VFS fileattr bridge and a small superblock-overhead update helper. It is the dispatch point for user-visible controls such as inode generation get/set, online resize, move extents, extent migration, delayed-allocation flushing, boot-loader inode swap, FITRIM, fscrypt and fsverity ioctls, forced shutdown, journal checkpointing, filesystem label/UUID get/set, superblock tunables, file flags, project quota IDs, and extent-status cache inspection. The source was read as a complete 2019-line file.

## Important APIs, Types, and Functions

The external entry points are `ext4_ioctl()`, `ext4_compat_ioctl()`, `ext4_fileattr_get()`, `ext4_fileattr_set()`, `ext4_force_shutdown()`, `ext4_reset_inode_seed()`, and `ext4_update_overhead()`. The central internal dispatcher is `__ext4_ioctl()`, which switches on ioctl command numbers and delegates to specialized helpers.

Superblock update helpers are built around `typedef void ext4_update_sb_callback(...)`, with callbacks `ext4_sb_setlabel()`, `ext4_sb_setuuid()`, `ext4_sb_setparams()`, and `set_overhead()`. `ext4_update_primary_sb()`, `ext4_update_backup_sb()`, and `ext4_update_superblocks_fn()` update the primary and sparse backup superblocks, journaling the primary and up to two backups before switching remaining backups to unjournaled dirty-buffer writes.

File and inode mutation helpers include `swap_inode_boot_loader()`, `swap_inode_data()`, `memswap()`, `ext4_ioctl_check_immutable()`, `dax_compatible()`, `ext4_dax_dontcache()`, `ext4_ioctl_setflags()`, and `ext4_ioctl_setproject()`. Filesystem-control helpers include `ext4_ioctl_group_add()`, `ext4_ioctl_shutdown()`, `ext4_ioc_getfsmap()`, `ext4_getfsmap_format()`, `ext4_ioctl_get_es_cache()`, `ext4_ioctl_checkpoint()`, `ext4_ioctl_setlabel()`, `ext4_ioctl_getlabel()`, `ext4_ioctl_getuuid()`, `ext4_ioctl_setuuid()`, `ext4_ioctl_get_tune_sb()`, and `ext4_ioctl_set_tune_sb()`.

Important data shapes include `struct getfsmap_info`, user ABI structures such as `struct fsmap_head`, `struct fsuuid`, `struct ext4_tune_sb_params`, `struct fiemap`, `struct move_extent`, and `struct ext4_new_group_data`, plus persistent ext4 objects `struct ext4_super_block`, `struct ext4_sb_info`, `struct ext4_inode_info`, `struct ext4_iloc`, and JBD2 `handle_t`.

## Control Flow

`ext4_ioctl()` is a thin wrapper over `__ext4_ioctl()`. The dispatcher obtains the file inode, superblock, and mount idmap, logs the command through `ext4_debug()`, and handles each supported ioctl with command-specific permission checks, user-copy validation, mount-write acquisition, inode locking, journaling, and subsystem delegation. Unsupported commands return `-ENOTTY`; compat ioctl translation maps selected 32-bit commands to native commands and uses `compat_ptr()` for shared handlers.

Simple metadata reads return data directly to userspace: version get returns `i_generation`, file label and UUID getters lock the superblock buffer and copy stable snapshots, get state reports selected in-memory inode state bits, and `FS_IOC_GETFSMAP` copies a header, validates reserved fields and offset constraints, converts VFS keys to ext4 fsmap keys, streams records through `ext4_getfsmap_format()`, and copies the final header back.

Write paths generally follow a common pattern: validate capability or owner checks, call `mnt_want_write_file()`, acquire any needed inode or resize locks, start an ext4 journal transaction if persistent metadata is being modified, update in-memory inode or superblock state, mark buffers or inode locations dirty, stop the journal, and drop the write reference. Examples include generation setting, flag setting, project ID changes, online resize, group add/extend, filesystem label and UUID changes, superblock tuning, and overhead update.

Online resize commands are serialized with `ext4_resize_begin()` and `ext4_resize_end()`. `EXT4_IOC_GROUP_EXTEND`, `EXT4_IOC_GROUP_ADD`, and `EXT4_IOC_RESIZE_FS` reject bigalloc where unsupported, call the corresponding resize helper, mark fast commits ineligible for resize, flush the journal if present, and register lazy inode-table initialization when group descriptor checksums and `INIT_INODE_TABLE` require it.

`EXT4_IOC_SWAP_BOOT` delegates to `swap_inode_boot_loader()`, which loads `EXT4_BOOT_LOADER_INO`, locks both inodes, rejects unsafe file types and flags, writes and invalidates page cache, waits for direct I/O, starts a journal transaction, initializes the boot loader inode if unused, swaps ext4 inode data and size/version fields, updates generation numbers and checksum seeds, adjusts quota accounting, marks both inodes dirty, and reverts the swap on selected failures.

The fileattr bridge has separate control flow from ioctl dispatch: `ext4_fileattr_get()` maps ext4 visible flags and project IDs into `struct file_kattr`; `ext4_fileattr_set()` masks requested flags to user-modifiable bits, checks immutable restrictions, calls `ext4_ioctl_setflags()`, and then calls `ext4_ioctl_setproject()`.

## State and Persistence Behavior

Persistent inode state changes include `i_generation`, timestamps, i_version, ext4 inode flags, extent-vs-indirect format migration, journal-data mode, project quota ID, boot-loader inode contents, and quota accounting. Inode flag updates reserve and dirty the inode location inside a journal transaction, while later journal-data or extent-format transitions call dedicated migration helpers after the flag transaction.

Persistent filesystem state changes are concentrated in superblock updates. `ext4_update_superblocks_fn()` guards against concurrent online resize with `EXT4_FLAGS_RESIZING`, journals the primary superblock and at most two backup superblocks, then updates remaining sparse backups without a journal. It recalculates superblock checksums where needed and syncs each dirty buffer. Label, UUID, tunable, and overhead updates all use this callback mechanism.

Forced shutdown modifies in-memory mount state by setting `EXT4_FLAGS_SHUTDOWN`, optionally freezing/thawing the block device or flushing and aborting the JBD2 journal, clearing discard, and reporting shutdown through `fserror_report_shutdown()`. Checkpointing persists journal state by calling `jbd2_journal_flush()` with optional discard or zeroout flags but does not directly modify file data.

Several ioctls intentionally invalidate or synchronize transient state. Setting immutable flushes regular-file direct I/O and dirty pages before setting the flag. DAX flag changes can mark an inode as not cacheable in dcache. Extent-status cache queries expose in-memory extent cache state through fiemap formatting, and `EXT4_IOC_CLEAR_ES_CACHE` drops that cache for an owner-capable caller.

## Dependencies and Integration Points

The file integrates with VFS ioctl dispatch, fileattr APIs, idmapped mounts, user-copy helpers, Linux capability checks, quota initialization and transfer, JBD2 journaling, fscrypt, fsverity, fsmap, fiemap, FITRIM/discard, block-device freeze/thaw, ext4 online resize, extent migration and move-extents, delayed allocation, extent-status cache, fast commit eligibility tracking, lazy inode-table initialization, ext4 tracing, and filesystem error reporting.

Header dependencies include `ext4_jbd2.h`, `ext4.h`, `fsmap.h`, `trace/events/ext4.h`, and Linux core headers for capabilities, compat ioctls, mount writes, quota operations, UUIDs, file attributes, and userspace access. User-visible ABI compatibility depends on command numbers and structures defined outside this file.

## Risks and Edge Cases

The highest-risk paths combine userspace ABI parsing, permissions, journaling, and persistent metadata updates. Superblock tuning can enable selected features online; validation must prevent unsupported feature clearing, incompatible encoding changes, excessive reserved blocks, invalid default hash algorithms, missing checksum seed support for UUID changes, and stable-inode UUID mutation. Backup superblock updates tolerate bad backup checksums but still require careful journal and buffer lifetime handling.

`swap_inode_boot_loader()` is particularly sensitive because it swaps inode data, sizes, quota usage, block counts, generation numbers, and checksum seeds while juggling page-cache invalidation and rollback. Incomplete rollback after one inode is dirtied could leave quota or boot-loader inode state inconsistent.

Flag mutation has subtle compatibility constraints: immutable files can only change in narrow ways, journal-data changes are capability-gated and rejected for active DAX inodes, casefold can only be toggled on empty directories with filesystem support, and DAX is mutually exclusive with verity-in-progress and inline/journal-data/encrypted semantics. Project quota transfer must account for xattr inode references under `xattr_sem`.

Resize and trim paths must reject unsupported bigalloc or noload+journal combinations. Compat ioctl translation is another ABI risk: command remapping must preserve pointer width and structure layout expectations. User-copy failure paths throughout the file return `-EFAULT` and must avoid partially committed changes before validation is complete.

## Test Signals

Useful coverage includes xfstests for `chattr`/fileattr flags, project quotas, immutable/append-only behavior, DAX flag interactions, casefold enablement, online grow/group add/group extend, `EXT4_IOC_MOVE_EXT`, `EXT4_IOC_SWAP_BOOT`, FITRIM, delayed-allocation block allocation, fscrypt policy/key ioctls, fsverity ioctls, forced shutdown modes, journal checkpoint flags, filesystem label and UUID get/set, and tune-superblock feature toggling.

Important negative tests should inject bad userspace pointers, unsupported feature masks, missing capabilities, readonly mounts, quota files, bigalloc resize attempts, metadata checksum generation changes, stable-inode UUID mutation, invalid fsmap keys, invalid checkpoint flag combinations, zeroout checkpoint warnings, and journal or buffer I/O errors. Runtime signals include `trace_ext4_update_sb`, `trace_ext4_shutdown`, `trace_ext4_getfsmap_*`, `ext4_msg()` errors, `ext4_warning()` messages, and `ext4_std_error()` propagation.
