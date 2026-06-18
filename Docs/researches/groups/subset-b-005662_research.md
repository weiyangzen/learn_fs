# subset-b-005662 Research

Grouped research for the requested F2FS and FAT files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/super.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/super.c

## Purpose
`super.c` is the F2FS superblock and filesystem-type implementation. It wires F2FS into the VFS mount API, parses and applies mount options, validates raw on-disk superblocks and checkpoints, initializes per-mount state, registers superblock operations, handles remount/freeze/unfreeze/sync/shutdown, manages quota integration, records critical filesystem errors, and owns module-level cache/sysfs/shrinker registration.

## Important APIs, Types, And Functions
The central local type is `struct f2fs_fs_context`, which holds a pending `struct f2fs_mount_info`, an option bitmask, a specification bitmask, and quota filename change state while VFS parses a mount or remount. The file exports or defines `f2fs_printk()`, `f2fs_sync_fs()`, `f2fs_sanity_check_ckpt()`, `f2fs_commit_super()`, `f2fs_handle_error()`, `f2fs_stop_checkpoint()`, `max_file_blocks()`, quota helpers such as `f2fs_dquot_initialize()` and `f2fs_do_quota_sync()`, and the module entry points `init_f2fs_fs()` and `exit_f2fs_fs()`.

Mount parsing is table driven through `f2fs_param_specs`, `f2fs_parse_param()`, enum option tokens, and constant tables for background GC, allocation mode, fsync mode, compression mode, discard unit, memory mode, errors behavior, and lookup mode. Consistency checks are split into `f2fs_check_quota_consistency()`, `f2fs_check_test_dummy_encryption()`, `f2fs_check_compression()`, `f2fs_check_opt_consistency()`, and `f2fs_sanity_check_options()`. Application is handled by `f2fs_apply_options()` plus dedicated quota, dummy encryption, and compression apply functions.

The VFS integration points are `f2fs_sops`, `f2fs_export_ops`, optional `f2fs_cryptops`, optional `f2fs_verityops`, `f2fs_context_ops`, and `f2fs_fs_type`. `f2fs_fill_super()` is the main mount routine called through `get_tree_bdev()`, while `__f2fs_remount()` backs `->reconfigure`.

## Control Flow
Mount setup starts in `f2fs_init_fs_context()`, where VFS receives a private context and `f2fs_context_ops`. `f2fs_parse_param()` records user options without immediately mutating mounted state. `f2fs_get_tree()` calls `f2fs_fill_super()`, which allocates `struct f2fs_sb_info`, initializes locks, sets the block size, reads both raw superblock copies with `read_raw_super_block()`, applies defaults and parsed options, installs superblock operations, and initializes F2FS subsystems in a strict order.

`f2fs_fill_super()` then reads the meta inode and checkpoint, initializes devices including multi-device and zoned-device state, starts checkpoint machinery, builds segment and node managers, reads root and node inodes, initializes compression state, registers sysfs/procfs entries, enables quotas when needed, recovers orphan inodes and fsync data, handles checkpoint-disabled state, optionally starts GC, repairs a bad backup superblock, joins the global shrinker list, and returns with `SBI_POR_DOING` cleared. Every failure label unwinds only the resources initialized so far.

Remount follows a save, validate, apply, activate pattern. `__f2fs_remount()` snapshots old mount options and quota names, attempts pending superblock recovery, reapplies defaults, validates the new context, applies options, and then starts or stops GC, flush, discard, checkpoint, and quota machinery according to the requested read-only state and option changes. On failure, it rolls runtime threads and options back using the saved state.

Unmount and shutdown paths are split between `kill_f2fs_super()` and `f2fs_put_super()`. `kill_f2fs_super()` stops GC/discard, writes a final checkpoint when needed, and calls `kill_block_super()`. `f2fs_put_super()` unregisters sysfs early, turns quotas off, stops checkpoint work, writes an umount checkpoint if dirty, drains discards and merged writes, validates page counters, destroys all per-mount managers and caches, releases raw super/checkpoint buffers, unloads Unicode state, and invalidates block devices.

## State And Persistence Behavior
Persistent state includes the raw F2FS superblock copies, checkpoint packs, quota files or quota inodes, feature flags, stop reasons, error bits, extension lists, and recovered fsync/orphan metadata. `sanity_check_raw_super()` validates magic, checksums, block geometry, segment layout, area boundaries, device segment totals, extension counts, payload sizes, and reserved inode numbers before mount continues. `f2fs_sanity_check_ckpt()` validates checkpoint counters, current segment positions, SIT/NAT bitmap sizes, payload placement, NAT bits sizing, and error flags.

Superblock writes use `f2fs_commit_super()` and `__f2fs_commit_super()`, writing backup first, optionally updating CRC, and using synchronous prefush/FUA I/O. If write access is unavailable, recovery is recorded with `SBI_NEED_SB_WRITE` so a later writable remount can repair. Critical errors set `CP_ERROR_FLAG`, persist `s_errors` and `s_stop_reason` asynchronously through `s_error_work`, and follow the mount `errors=` policy: continue, panic, or stop future updates and behave as read-only without directly changing `SB_RDONLY` outside remount locking.

Checkpoint enable and disable are active state transitions. `f2fs_disable_checkpoint()` may run urgent foreground GC until unusable blocks fit the requested cap, writes a pause checkpoint, sets `SBI_CP_DISABLED`, and records unusable blocks. `f2fs_enable_checkpoint()` flushes dirty/skipped data, clears checkpoint-disabled state, marks the filesystem dirty, syncs a checkpoint, and flushes the checkpoint thread.

## Dependencies And Integration Points
This file is tightly coupled to nearly every F2FS subsystem: node manager, segment manager, checkpoint, recovery, GC, discard, compression, xattr, iostat, sysfs, extent cache, post-read processing, and shrinker registration. Kernel dependencies include VFS superblock and fs_context APIs, block devices, quota, fscrypt, fsverity, Unicode casefolding, KUnit-visible module init behavior, shrinkers, workqueues, procfs/sysfs, and zoned block device reporting.

The file also exposes F2FS behavior to users through mount options, `/proc/mounts` show-options output, `statfs`, NFS export handles, quota operations, freeze/unfreeze, shutdown, and module registration under filesystem name `f2fs`.

## Risks
The highest-risk areas are mount/remount rollback, checkpoint-disabled transitions, quota state changes, and raw metadata validation because they combine persistent media state with live kernel threads and VFS flags. Option interactions are complex: zoned devices require discard and LFS-compatible settings, device aliasing requires extent cache, readonly features restrict writable mounts, and several options cannot be switched dynamically. Error handling must avoid deadlocks because it may run from I/O completion or recovery paths. Any change to cleanup labels in `f2fs_fill_super()` can leak inodes, kobjects, block devices, or leave background threads running.

## Test Signals
Useful signals include mounting clean and unclean images, corrupt-superblock and corrupt-checkpoint tests, remount option matrices, checkpoint disable/enable stress, quota-on/quota-off and journaled quota tests, fscrypt/fsverity mount combinations, zoned block device tests, fault injection through `CONFIG_F2FS_FAULT_INJECTION`, freeze/thaw tests, `statfs` with project quotas, and teardown leak checks from F2FS page counters and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/sysfs.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/sysfs.c

## Purpose
`sysfs.c` implements F2FS runtime observability and tuning through `/sys/fs/f2fs`, per-mount sysfs directories, feature-list kobjects, and `/proc/fs/f2fs/<device>` debug files. It exposes mount and allocator state, GC controls, discard controls, node-manager settings, checkpoint-thread priority, compression counters, atomic-write counters, age extent cache tuning, zoned-device knobs, and feature capability reporting.

## Important APIs, Types, And Functions
The main local descriptors are `struct f2fs_attr` for per-superblock attributes and `struct f2fs_base_attr` for global base attributes. `__struct_ptr()` maps an attribute's `struct_type` to the live object that stores the value: GC thread, segment manager, discard command control, node manager, `f2fs_sb_info`, fault-injection state, stat info, checkpoint request control, or ATGC state.

Generic show/store helpers include `f2fs_sbi_show()`, `__sbi_show_value()`, `f2fs_sbi_store()`, `__sbi_store()`, `f2fs_attr_show()`, `f2fs_attr_store()`, `f2fs_base_attr_show()`, and `f2fs_base_attr_store()`. Registration is handled by `f2fs_init_sysfs()`, `f2fs_exit_sysfs()`, `f2fs_register_sysfs()`, and `f2fs_unregister_sysfs()`. Procfs seq emitters include `segment_info_seq_show()`, `segment_bits_seq_show()`, `victim_bits_seq_show()`, `discard_plist_seq_show()`, `disk_map_seq_show()`, `donation_list_seq_show()`, and optional `inject_stats_seq_show()`.

## Control Flow
At module initialization, `f2fs_init_sysfs()` registers the `f2fs` kset under `fs_kobj`, adds global `features` and `tuning` kobjects, and creates `/proc/fs/f2fs`. At mount time, `f2fs_register_sysfs()` adds a per-superblock kobject named after `sb->s_id`, creates `stat` and `feature_list` child kobjects, and creates procfs diagnostic files bound to the mounted superblock. Unregistration removes the proc subtree first, then drops child and parent kobjects and waits for completion callbacks.

Attribute definitions are generated through macros such as `F2FS_RW_ATTR`, `F2FS_RO_ATTR`, `F2FS_GENERAL_RO_ATTR`, `F2FS_FEATURE_RO_ATTR`, and `F2FS_SB_FEATURE_RO_ATTR`. Most simple attributes are offset-based reads or writes into live structs. Special cases in `f2fs_sbi_show()` and `__sbi_store()` handle extension lists, checkpoint-thread I/O priority, compression counters, GC modes, current and peak atomic write counters, fault injection, reserved blocks, discard policy bounds, iostat controls, compression watermarks, ATGC ratios, file donation, allocation hints, and scheduling priorities.

## State And Persistence Behavior
Most sysfs writes mutate only live in-memory mount state. A notable exception is `extension_list`: writes update the raw superblock extension list under `sb_lock` and call `f2fs_commit_super()`, rolling back the in-memory list if persistence fails. Counter reset attributes such as compression and atomic-write counters require a zero write. Feature attributes are read-only and report either kernel-supported capabilities or per-filesystem on-disk feature flags.

Some writes immediately affect background work. `gc_urgent` wakes the GC thread and discard thread for urgent modes. `ckpt_thread_ioprio` updates the checkpoint thread task if checkpoint merging is active. `critical_task_priority` requires `CAP_SYS_NICE` and updates checkpoint and GC task niceness. Procfs views read live SIT, dirty segment, discard, disk-map, donation, and fault-injection state without persisting data.

## Dependencies And Integration Points
This file depends on F2FS internals from `f2fs.h`, `segment.h`, `gc.h`, and `iostat.h`, plus kernel sysfs, procfs, seq_file, Unicode, and I/O priority APIs. It integrates with `super.c` through module-level sysfs init/exit and per-mount register/unregister calls. It also integrates with GC/discard threads, the checkpoint request control, segment/node managers, compression accounting, iostat processing, fault injection, and optional zoned-block-device support.

## Risks
The main risk is unsafe mutation of live kernel state from sysfs. Many stores validate ranges, feature modes, and capabilities, but they still alter scheduling, GC, discard, allocation, and cache behavior on a mounted filesystem. Kobject lifetime ordering is important because per-mount sysfs/procfs entries reference `struct f2fs_sb_info`; unregistering early during unmount avoids users racing teardown. Offset-based attributes are compact but fragile if a macro points to the wrong struct or field size. Procfs debug views can be expensive on large filesystems because they iterate all segments or sections.

## Test Signals
Test signals include sysfs file presence after mount and removal after unmount, read/write permission checks, invalid value rejection, GC wakeup behavior after `gc_urgent`, extension-list persistence across remount, feature-list accuracy for images with different mkfs features, procfs output smoke tests, fault-injection counters when enabled, lockdep around unmount races, and KASAN/KCSAN coverage for concurrent sysfs reads and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/verity.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/verity.c

## Purpose
`verity.c` implements F2FS support for fs-verity. It stores the Merkle tree and fsverity descriptor beyond normal file size at the next 64 KiB boundary after `i_size`, and stores only a small F2FS verity xattr that points to the descriptor location. This avoids xattr size limits and ensures verity metadata is encrypted with file data when fscrypt is used.

## Important APIs, Types, And Functions
The exported integration object is `const struct fsverity_operations f2fs_verityops`, consumed by `super.c` through `sb->s_vop`. It provides `begin_enable_verity`, `end_enable_verity`, `get_verity_descriptor`, `read_merkle_tree_page`, `readahead_merkle_tree`, and `write_merkle_tree_block`.

`f2fs_verity_metadata_pos()` computes the metadata base as `round_up(inode->i_size, 65536)`. `pagecache_read()` and `pagecache_write()` read and write beyond `i_size` through the file mapping rather than VFS read/write helpers. The on-disk xattr payload is `struct fsverity_descriptor_location`, containing version, descriptor size, and descriptor file position.

## Control Flow
Enabling verity starts in `f2fs_begin_enable_verity()`. It rejects concurrent verity enablement, rejects atomic files, initializes quota accounting because the file is opened read-only, converts inline data to regular blocks, and sets `FI_VERITY_IN_PROGRESS`.

During fs-verity construction, `f2fs_write_merkle_tree_block()` writes Merkle blocks at offsets relative to the hidden metadata base. `f2fs_end_enable_verity()` then appends the descriptor after the Merkle tree, writes and waits for all mapping pages, creates the verity xattr with descriptor location, sets the VFS verity flag, persists inode flags, marks the inode dirty, and clears `FI_VERITY_IN_PROGRESS`. If any step fails, it truncates pages and blocks beyond `i_size` while holding `i_gc_rwsem[WRITE]`, clears in-progress state, and marks the filesystem for fsck if cleanup truncation fails.

At file-open or verification time, `f2fs_get_verity_descriptor()` reads the location xattr, validates version, size, overflow, maximum file blocks, and minimum metadata position, then reads the descriptor from page cache. Merkle page reads and readahead translate fs-verity-relative indexes by adding the metadata base page offset before calling generic helpers.

## State And Persistence Behavior
Persistent state is split between hidden file data blocks and xattr metadata. The Merkle tree and descriptor are stored in the inode mapping beyond visible EOF. The xattr `F2FS_XATTR_INDEX_VERITY/F2FS_XATTR_NAME_VERITY` stores only the descriptor location. The inode verity flag is set only after metadata pages are written and waited on, which gives crash consistency ordering: metadata first, xattr next, inode flag last.

## Dependencies And Integration Points
This file depends on fs-verity core APIs, F2FS xattr functions, quota initialization, inline-data conversion, inode dirtying, truncation, GC locking, and max file block calculations from `super.c`. It integrates with fscrypt implicitly by storing metadata in encrypted file contents rather than plaintext xattrs.

## Risks
The critical risks are crash ordering, cleanup after failed enablement, and bounds validation for hidden metadata offsets. If `FI_VERITY_IN_PROGRESS` is cleared too early, pages beyond `i_size` may not be written correctly. If cleanup races GC, stale hidden metadata could be reintroduced, which is why the cleanup path takes the write side of the GC inode semaphore. Corrupt xattrs must be treated as filesystem corruption because they can point outside valid metadata space.

## Test Signals
Test signals include fs-verity enable and verify tests on regular, encrypted, compressed-disabled, and inline-data files; rejection on atomic files; interruption/failure injection during descriptor or xattr writes; corrupted verity xattr handling; cleanup verification after failed enablement; and reads on architectures or configurations with different page sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/verity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/xattr.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/xattr.c

## Purpose
`xattr.c` implements F2FS extended attribute support. It provides VFS xattr handlers for user, trusted, security, and F2FS-specific advise attributes, reads and writes the combined inline and external xattr storage format, initializes security xattrs, exposes list/get/set operations, detects corrupted xattr layouts, and manages a slab cache for common inline-sized xattr buffers.

## Important APIs, Types, And Functions
The VFS-visible handlers are `f2fs_xattr_user_handler`, `f2fs_xattr_trusted_handler`, `f2fs_xattr_advise_handler`, `f2fs_xattr_security_handler`, and `f2fs_xattr_handlers`. Public F2FS functions are `f2fs_getxattr()`, `f2fs_listxattr()`, `f2fs_setxattr()`, optional `f2fs_init_security()`, `f2fs_init_xattr_cache()`, and `f2fs_destroy_xattr_cache()`.

Storage helpers include `xattr_alloc()`, `xattr_free()`, `read_inline_xattr()`, `read_xattr_block()`, `lookup_all_xattrs()`, `read_all_xattrs()`, `write_all_xattrs()`, `__find_xattr()`, `__find_inline_xattr()`, and `__f2fs_setxattr()`. The common in-memory buffer contains the inline xattr area followed by the external xattr node block, plus padding.

## Control Flow
VFS get/set calls enter generic handlers that validate the namespace and mount options, then call F2FS get/set. `f2fs_getxattr()` validates name length, takes `i_xattr_sem` unless an inode folio is already provided by metadata initialization, calls `lookup_all_xattrs()`, checks the value fits the supplied buffer and backing area, copies the value, and returns its size.

`f2fs_listxattr()` reads all xattrs, walks entries with `list_for_each_xattr`, maps internal indexes to namespace prefixes through `f2fs_xattr_prefix()`, enforces list permissions such as trusted requiring `CAP_SYS_ADMIN`, and emits null-terminated names. It detects entries that cross the valid xattr area and marks the filesystem for fsck.

`f2fs_setxattr()` performs checkpoint and quota readiness checks, initializes dquot state, balances the filesystem, locks global F2FS operations and the inode xattr semaphore, and delegates to `__f2fs_setxattr()`. The inner setter reads all xattrs, finds the entry, honors `XATTR_CREATE` and `XATTR_REPLACE`, computes free space, removes the old entry with `memmove`, writes a new aligned entry if a value is present, terminates the list with zero, and persists through `write_all_xattrs()`. Directory xattr updates request checkpoint or add an xattr-dir inode entry depending on fsync mode.

## State And Persistence Behavior
F2FS xattrs can live partly inline in the inode node page and partly in a separate xattr node referenced by `F2FS_I(inode)->i_xattr_nid`. `write_all_xattrs()` allocates a new xattr node nid when the new header size exceeds inline capacity, writes inline bytes back to the inode folio, writes external bytes to the xattr node folio, or truncates the external node when the updated set fits inline. New xattr buffers are initialized with `F2FS_XATTR_MAGIC` and refcount 1 if no xattrs existed.

Encryption context xattrs trigger `f2fs_set_encrypted_inode()`. Advise xattrs update `F2FS_I(inode)->i_advise` rather than the normal entry table. Security xattrs are initialized through LSM `security_inode_init_security()`. Corruption detection sets `SBI_NEED_FSCK` and calls `f2fs_handle_error(..., ERROR_CORRUPTED_XATTR)`.

## Dependencies And Integration Points
This file depends on VFS xattr APIs, POSIX ACL xattr handlers, Linux security hooks, F2FS node folio helpers, dnode allocation, checkpoint readiness, quota initialization, global operation locks, inode dirtying, encryption state, fsync policy, and error handling from `super.c`. Its format constants and macros come from `xattr.h`.

## Risks
The main risks are bounds errors in variable-length xattr entry walking, inconsistent inline versus external xattr updates, nid allocation failure handling, and races with inode metadata initialization. The code must preserve zero-terminated entry lists and 4-byte alignment. Any missed validation can turn malformed on-disk xattrs into out-of-bounds reads or writes. The setter also has to avoid creating metadata updates when the filesystem is in checkpoint error or checkpoint-disabled no-space states.

## Test Signals
Useful tests include xfstests for xattrs, ACLs, SELinux/security labels, trusted namespace permissions, create/replace/remove semantics, inline-to-external and external-to-inline transitions, long name and large value rejection, fault injection on nid allocation and folio reads, corrupted xattr image handling, fscrypt policy xattr setting, and fsck-required flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/xattr.h -->
# sources/distributed-fs/ceph-client/fs/f2fs/xattr.h

## Purpose
`xattr.h` defines the F2FS on-disk extended attribute format, namespace indexes, layout and alignment helpers, capacity calculations, and public xattr/security function declarations. It is the contract shared by `xattr.c`, encryption, verity, ACL, and inode metadata code.

## Important APIs, Types, And Macros
The core on-disk structures are `struct f2fs_xattr_header` and `struct f2fs_xattr_entry`. The header carries magic, refcount, and reserved words. Each entry stores namespace index, name length, value size, then inline name and value bytes. Namespace constants include user, POSIX ACL access/default, trusted, Lustre, security, advise, encryption, and verity. Special names include `system.advise`, encryption context name `c`, and verity name `v`.

Layout macros include `XATTR_HDR`, `XATTR_ENTRY`, `XATTR_FIRST_ENTRY`, `XATTR_ALIGN`, `ENTRY_SIZE`, `XATTR_NEXT_ENTRY`, `IS_XATTR_LAST_ENTRY`, and `list_for_each_xattr`. Capacity macros include `VALID_XATTR_BLOCK_SIZE`, `XATTR_PADDING_SIZE`, `XATTR_SIZE`, `MIN_OFFSET`, `MAX_VALUE_LEN`, `MIN_INLINE_XATTR_SIZE`, `MAX_INLINE_XATTR_SIZE`, and `DEFAULT_XATTR_SLAB_SIZE`.

## Control Flow
This header has no executable control flow, but its iterator and sizing macros define how `xattr.c` walks and mutates xattr tables. `list_for_each_xattr` starts after the header and advances by aligned entry size until a zero dword terminator. `XATTR_SIZE()` composes the optional external xattr block size with the inode's inline xattr size, and `MIN_OFFSET()` defines the upper bound used for free-space checks.

## State And Persistence Behavior
The documented on-disk layout places the xattr header, variable entries, free space, and node footer in a combined logical xattr area. F2FS uses inline xattr space plus at most one xattr block. The macros encode the persistence contract that entries are packed, 4-byte aligned, and terminated by zero. `MAX_VALUE_LEN()` bounds a single xattr value by the total usable xattr area minus header and entry overhead.

## Dependencies And Integration Points
The header depends on Linux xattr declarations and F2FS inode/layout constants such as `node_footer`, `DEF_ADDRS_PER_INODE`, extra-attr sizes, inline reserved sizes, and inline dentry sizes. It declares `f2fs_xattr_handlers`, `f2fs_setxattr()`, `f2fs_getxattr()`, `f2fs_listxattr()`, xattr cache init/destroy, and optional `f2fs_init_security()` stubs depending on Kconfig.

## Risks
Because the file defines raw on-disk parsing macros, changes can break compatibility or cause memory-safety bugs in xattr walking. The `IS_XATTR_LAST_ENTRY()` zero-dword test assumes enough bounds checking by callers before dereference. Capacity macros must remain consistent with inode layout changes, flexible inline xattr support, compression/encryption feature growth, and node footer size.

## Test Signals
Test signals include build coverage with and without `CONFIG_F2FS_FS_XATTR` and `CONFIG_F2FS_FS_SECURITY`, xattr boundary tests around inline size and maximum value length, ACL/security/verity/encryption xattr integration, and corrupted xattr images that exercise caller-side bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/Kconfig -->
# sources/distributed-fs/ceph-client/fs/fat/Kconfig

## Purpose
`Kconfig` declares build-time configuration for Linux FAT-family filesystems. It defines the shared FAT core, the MSDOS and VFAT filesystem drivers, default FAT character conversion settings, default UTF-8 mount-option behavior, and optional FAT KUnit tests.

## Important Config Symbols
`FAT_FS` is a tristate core selected by both `MSDOS_FS` and `VFAT_FS`; it selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`. `MSDOS_FS` enables classic 8.3-name DOS FAT support and builds module `msdos`. `VFAT_FS` enables Windows 95-style long filename support and builds module `vfat`. `FAT_DEFAULT_CODEPAGE` sets the default codepage for FAT mounts. `FAT_DEFAULT_IOCHARSET` sets the default VFAT I/O charset. `FAT_DEFAULT_UTF8` controls whether the `utf8` mount option is on by default. `FAT_KUNIT_TEST` builds FAT KUnit tests when KUnit is enabled.

## Control Flow
Kconfig control flow is dependency and selection based. Enabling MSDOS or VFAT selects the common FAT core. Charset defaults are visible only when their filesystem prerequisites are enabled. `FAT_KUNIT_TEST` defaults to `KUNIT_ALL_TESTS`, allowing global KUnit configuration to pull the tests in automatically.

## State And Persistence Behavior
This file has no runtime state. Its persistent effect is the generated kernel configuration, which controls whether FAT support is built in, modular, or absent, and which defaults are compiled into the FAT/VFAT mount behavior. Mount options can override the compiled defaults at runtime.

## Dependencies And Integration Points
The symbols integrate with `fs/fat/Makefile`, native language support, buffer-head based block I/O, legacy direct I/O, and KUnit. The help text points users to VFAT documentation and explains module naming constraints: if common FAT support is a module, FAT-based filesystems must also be modules.

## Risks
Misconfigured charset defaults can produce unexpected filename conversion behavior. Enabling UTF-8 by default is explicitly cautioned against in the help text because FAT filesystems often need a specific charset. Tristate relationships matter: the shared core must be compatible with the selected front-end filesystems.

## Test Signals
Test signals include Kconfig dependency resolution, `oldconfig`/`menuconfig` visibility, built-in versus module builds for FAT/MSDOS/VFAT, mount tests with default and overridden `codepage`, `iocharset`, and `utf8` options, and `FAT_KUNIT_TEST` execution under KUnit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/Makefile -->
# sources/distributed-fs/ceph-client/fs/fat/Makefile

## Purpose
`Makefile` maps FAT-family Kconfig symbols to kernel objects. It builds the common FAT core, VFAT long-name layer, MSDOS name layer, and optional FAT KUnit test object.

## Important Build Rules
`obj-$(CONFIG_FAT_FS) += fat.o` builds the common FAT module or built-in object. `obj-$(CONFIG_VFAT_FS) += vfat.o` and `obj-$(CONFIG_MSDOS_FS) += msdos.o` build the two front-end filesystem modules. `fat-y` is composed of `cache.o`, `dir.o`, `fatent.o`, `file.o`, `inode.o`, `misc.o`, and `nfs.o`. `vfat-y` contains `namei_vfat.o`, while `msdos-y` contains `namei_msdos.o`. `obj-$(CONFIG_FAT_KUNIT_TEST) += fat_test.o` adds the unit test object.

## Control Flow
This is declarative kbuild logic. The selected Kconfig symbols determine which composite objects are linked. The common core is separate from the VFAT and MSDOS namespace implementations, so both front ends can share allocation, inode, directory, FAT-entry, file, misc, and NFS export code.

## State And Persistence Behavior
There is no runtime state in this file. Its persistent output is the build artifact layout: `fat.o`, `vfat.o`, `msdos.o`, and optionally `fat_test.o` as built-in or module objects depending on Kconfig tristate values.

## Dependencies And Integration Points
The file integrates with `fs/fat/Kconfig` symbols and the kernel kbuild system. It establishes module composition that must match module names described in Kconfig help. Runtime behavior is provided by the listed C objects elsewhere in `fs/fat`.

## Risks
The main risk is build/link drift: adding a new FAT core source without updating `fat-y`, or moving namei code without updating the front-end composite objects, can produce unresolved symbols or missing functionality. KUnit test object selection must remain aligned with `FAT_KUNIT_TEST`.

## Test Signals
Test signals include allmodconfig/allnoconfig build coverage, built-in and modular FAT/VFAT/MSDOS combinations, `modinfo` or module artifact checks for expected object names, and KUnit build/run coverage when `CONFIG_FAT_KUNIT_TEST` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fat/Makefile -->
