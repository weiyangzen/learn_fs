# sources/distributed-fs/ceph-client/fs/ext4 research: subset-b-005655

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/super.c -->
# sources/distributed-fs/ceph-client/fs/ext4/super.c

## Purpose
`super.c` is the ext4 superblock, mount, remount, journal, quota, and module-lifecycle hub. It registers ext4, and optionally ext2/ext3 compatibility frontends, implements the VFS `super_operations`, parses the new mount API `fs_context`, loads and validates on-disk superblock metadata, wires JBD2 journaling, initializes allocator/orphan/quota/sysfs state, and commits persistent superblock updates during mount, sync, freeze, unfreeze, error handling, and unmount.

## Important APIs, Types, And Functions
The primary VFS entrypoints are `ext4_init_fs_context()`, `ext4_get_tree()`, `ext4_fill_super()`, `ext4_reconfigure()`, `ext4_kill_sb()`, and the `ext4_sops` table. `struct ext4_fs_context` carries parsed mount parameters, option masks, quota filenames, journal device/ioprio, reserved uid/gid, lazy inode-table settings, stripe geometry, and debug knobs. `ext4_param_specs[]` and `ext4_mount_opts[]` map user options to tokens and `EXT4_MOUNT*` bits.

Mount construction centers on `__ext4_fill_super()`. It calls helpers such as `ext4_load_super()`, `ext4_init_metadata_csum()`, `ext4_set_def_opts()`, `parse_apply_sb_mount_options()`, `ext4_check_opt_consistency()`, `ext4_check_feature_compatibility()`, `ext4_block_group_meta_init()`, `ext4_handle_clustersize()`, `ext4_check_geometry()`, `ext4_group_desc_init()`, `ext4_load_and_init_journal()`, `ext4_calculate_overhead()`, `ext4_setup_super()`, `ext4_percpu_param_init()`, `ext4_mb_init()`, `ext4_register_li_request()`, `ext4_init_orphan_info()`, `ext4_enable_quotas()`, `ext4_orphan_cleanup()`, and `ext4_register_sysfs()`.

Journal handling is implemented by `ext4_load_journal()`, `ext4_open_inode_journal()`, `ext4_open_dev_journal()`, `ext4_get_journal_blkdev()`, `ext4_init_journal_params()`, `set_journal_csum_feature_set()`, `ext4_mark_recovery_complete()`, `ext4_clear_journal_err()`, `ext4_force_commit()`, and `ext4_sync_fs()`. Error reporting flows through `__ext4_error()`, `__ext4_error_inode()`, `__ext4_error_file()`, `__ext4_std_error()`, `ext4_handle_error()`, `save_error_info()`, `update_super_work()`, and `ext4_commit_super()`.

Other important exported or shared helpers include buffer I/O wrappers (`ext4_read_bh*()`, `ext4_sb_bread*()`), group descriptor accessors and checksum functions, inode cache lifecycle functions, lazy inode-table initialization (`ext4_lazyinit_thread()` and request helpers), quota operations, `ext4_statfs()`, `ext4_freeze()`, and `ext4_unfreeze()`.

## Control Flow
Module init initializes extent-status, pending trees, post-read processing, pageio, system zones, sysfs/procfs, mballoc, inode caches, fast-commit dentry caches, then registers ext3/ext2 aliases and ext4. Mount starts with `ext4_init_fs_context()`, option parsing through `ext4_parse_param()`, and `get_tree_bdev()` invoking `ext4_fill_super()`.

`ext4_fill_super()` allocates `ext4_sb_info`, chooses the superblock block, then delegates to `__ext4_fill_super()`. That function reads the superblock, validates checksums, applies defaults and persistent `s_mount_opts`, checks requested options, initializes geometry and feature compatibility, reads group descriptors, configures journal or no-journal mode, builds xattr caches and overhead accounting, reads the root inode, marks the filesystem mounted, sets reserved clusters and system zones, initializes extents/per-cpu counters/mballoc/flex_bg/lazyinit/orphan/quota paths, performs orphan cleanup and recovery completion, sets ratelimits, and finally publishes sysfs/procfs entries. Failure labels unwind resources in reverse order.

Remount uses `ext4_reconfigure()` and `__ext4_remount()`. It snapshots old options, validates immutable option changes, applies safe option changes under writepages exclusion, updates journal parameters, handles read-write/read-only transitions, validates group descriptor checksums before read-write remount, rejects unprocessed orphan state on read-write remount, manages quotas and lazyinit requests, and restores the old state on failure.

## State And Persistence Behavior
Persistent state is stored in `struct ext4_super_block` through `s_es`, group descriptors, journal superblocks, quota inodes/files, orphan metadata, and feature flags. `ext4_update_super()` copies in-memory counters, write timestamps, lifetime write statistics, and first/last error records into the on-disk superblock, then refreshes the metadata checksum. `ext4_commit_super()` writes the superblock synchronously with FUA when barriers are enabled.

Runtime state lives in `struct ext4_sb_info`: option masks, journal pointer, external journal file, buffer heads, group descriptor and flex_bg arrays under RCU, per-cpu counters, orphan list and locks, workqueues, ratelimit states, DAX state, dummy encryption policy, fast-commit queues, mballoc state, xattr caches, and lazyinit request pointers. `update_super_work()` defers journal-safe superblock error/stat updates when immediate writes would violate lock ordering.

Crash consistency depends on JBD2 feature negotiation, recovery flags, orphan cleanup, and read-only/freeze transitions. `ext4_freeze()` flushes the journal and clears recovery/orphan-present flags only when safe; `ext4_unfreeze()` sets them again. `ext4_mark_recovery_complete()` clears recovery state after successful recovery, especially for read-only mounts.

## Dependencies And Integration Points
This file binds ext4 to the VFS, block layer, buffer cache, JBD2, quota subsystem, fscrypt, fsverity, Unicode/casefolding, DAX, procfs/sysfs, fserror reporting, tracepoints, mballoc, extents, orphan file/list handling, fast commits, fsmap, and NFS export operations. It exposes mount parameters to the VFS new mount API and publishes `/proc/fs/ext4/<dev>/options`, allocator stats, fast-commit info, and sysfs attributes through `sysfs.c`.

## Risks And Edge Cases
The mount path is security- and integrity-critical: malformed superblocks, invalid block sizes, unsupported feature flags, corrupt group descriptor checksums, mismatched external journals, quota option conflicts, DAX/data-journal incompatibilities, unprocessed orphan lists, and journal recovery on read-only devices all have explicit rejection paths. Error handling intentionally avoids recursive journal/error paths and may force emergency read-only state without setting `SB_RDONLY`, which callers must understand.

The option parser has many compatibility cases for ext2/ext3 and legacy options; regressions can silently alter mount behavior. Remount restores old state on failure, but changes involving quota, system zones, MMP, and journal parameters have complicated partial-progress behavior. A notable review signal is the initial assignment of `s_resgid` from `ext4_get_resuid(es)`, which should be checked against expected reserved-GID semantics. Lazyinit scheduling uses global state and locks, so request lifetime and unmount races are important.

## Test Signals
Useful tests include mount matrices for read-only/read-write, journal/no-journal, external journals, ext2/ext3 aliases, data modes, DAX, bigalloc, metadata checksums, casefold/encryption/verity features, MMP, and unsupported feature flags. Fault-injection tests should cover superblock read/write errors, journal load/recovery failures, corrupt group descriptors, orphan cleanup failures, quota enable/disable failures, remount rollback, freeze/unfreeze, and sysfs/procfs visibility after mount/unmount. Runtime signals include ext4 tracepoints, rate-limited kernel messages, `statfs`, `/proc/fs/ext4/*`, sysfs error counters, journal abort state, and e2fsck validation after crash/recovery scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/symlink.c -->
# sources/distributed-fs/ceph-client/fs/ext4/symlink.c

## Purpose
`symlink.c` provides ext4 symlink inode operations. Most symlink behavior is delegated to generic VFS helpers; this file handles ext4-specific fast symlinks, leftover inline-data symlinks, encrypted symlinks, and block-backed symlink reads.

## Important APIs, Types, And Functions
The exported operation tables are `ext4_encrypted_symlink_inode_operations`, `ext4_symlink_inode_operations`, and `ext4_fast_symlink_inode_operations`. The main callbacks are `ext4_encrypted_get_link()`, `ext4_encrypted_symlink_getattr()`, `ext4_get_link()`, and `ext4_free_link()`.

`ext4_encrypted_get_link()` chooses the ciphertext source from either `EXT4_I(inode)->i_data` for fast symlinks or block zero via `ext4_bread()`, then delegates plaintext decoding and delayed cleanup to `fscrypt_get_symlink()`. `ext4_get_link()` handles non-encrypted regular symlinks, including old inline-data symlink leftovers via `ext4_read_inline_link()`, RCU-walk safe cached lookup through `ext4_getblk(... EXT4_GET_BLOCKS_CACHED_NOWAIT)`, and normal blocking reads through `ext4_bread()`.

## Control Flow
For encrypted symlinks, VFS `.get_link` enters `ext4_encrypted_get_link()`. A missing dentry indicates RCU-walk context and returns `-ECHILD` because fscrypt/block IO may need blocking work. Fast symlinks use in-inode data; slow symlinks read logical block zero. The resulting bytes are passed to fscrypt, then any buffer head is released.

For normal symlinks, inline-data inodes are read through ext4 inline-data support and freed with `kfree_link`. Non-inline RCU-walk attempts only a cached, uptodate buffer and otherwise returns `-ECHILD`. Blocking lookup reads block zero, validates that a block exists, installs a delayed `brelse()` callback, NUL-terminates within `inode->i_size` and block-size bounds using `nd_terminate_link()`, and returns the buffer data.

## State And Persistence Behavior
Fast symlink payloads are stored in the ext4 inode's `i_data` array. Block-backed symlinks store the target in file block zero. Inline-data symlink support here is read-only compatibility for old inodes; the comment states creating new inline symlinks is not supported. Encrypted symlink bytes persist encrypted and are interpreted through fscrypt on each lookup.

## Dependencies And Integration Points
The file integrates VFS `inode_operations`, path walk delayed calls, buffer-head lifetime management, ext4 block mapping/read helpers, ext4 inline-data helpers, xattr listing, generic `ext4_setattr()`/`ext4_getattr()`, and fscrypt symlink decoding/stat adjustment.

## Risks And Edge Cases
The important correctness boundaries are RCU-walk behavior, buffer lifetime, corrupt symlink blocks, and correct target termination. Missing dentry returns `-ECHILD` when blocking or allocation might be required. `ext4_bread()` errors propagate with `ERR_CAST`; absent block zero is reported as filesystem corruption. Encrypted symlink size and validation are delegated to fscrypt, while non-encrypted block-backed symlinks rely on `nd_terminate_link()` to avoid overrun.

## Test Signals
Tests should cover fast, slow block-backed, encrypted, and old inline-data symlinks; RCU path walk fallback; corrupt symlink inode with missing block zero; xattr listing on symlink inodes; symlink getattr size adjustment under encryption; and symlink targets at block-size and `i_size` boundaries. fscrypt test vectors are important because encrypted fast symlinks source data from the inode body rather than a buffer head.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/sysfs.c -->
# sources/distributed-fs/ceph-client/fs/ext4/sysfs.c

## Purpose
`sysfs.c` exposes ext4 per-filesystem runtime controls and counters under `/sys/fs/ext4/<sb-id>/`, exposes supported feature flags under `/sys/fs/ext4/features/`, and creates procfs diagnostic files under `/proc/fs/ext4/<sb-id>/`. It is the observability and live-tuning companion to the superblock state initialized in `super.c`.

## Important APIs, Types, And Functions
`struct ext4_attr` wraps a sysfs `attribute` with an `attr_id_t`, pointer mode, size, and either an explicit pointer or offset into `struct ext4_sb_info` / `struct ext4_super_block`. The macro family `EXT4_ATTR*`, `EXT4_RO_ATTR_ES_*`, and `EXT4_RW_ATTR_SBI_*` defines attributes compactly. `calc_ptr()` resolves offset-based attributes.

Read paths use `ext4_attr_show()` and `ext4_generic_attr_show()`. Write paths use `ext4_attr_store()` and `ext4_generic_attr_store()`. Specialized stores include `inode_readahead_blks_store()`, `reserved_clusters_store()`, `trigger_test_error()`, and `err_report_sec_store()`. Registration functions are `ext4_init_sysfs()`, `ext4_exit_sysfs()`, `ext4_register_sysfs()`, `ext4_unregister_sysfs()`, and `ext4_notify_error_sysfs()`.

## Control Flow
Module init calls `ext4_init_sysfs()`, which creates `/sys/fs/ext4`, allocates and registers the global `features` kobject, and creates `/proc/fs/ext4`. After a filesystem mount is fully initialized, `ext4_register_sysfs()` initializes the per-superblock completion, adds the superblock kobject under the ext4 root, and creates proc entries for options, extent-status shrinker info, fast-commit info, mballoc group data, and mballoc stats. Unmount calls `ext4_unregister_sysfs()` before journal destruction and before flushing delayed superblock update work.

Sysfs reads switch on `attr_id`. Some values are live counters from per-cpu or atomic state, some derive from block-device write statistics, some read little-endian on-disk superblock fields, and feature attributes simply report support. Writes parse integer text with `kstrto*`, validate bounds, and update in-memory fields or trigger controlled side effects.

## State And Persistence Behavior
Most writable attributes mutate only in-memory `ext4_sb_info` tuning knobs such as allocator scan limits, inode readahead, reserved clusters, ratelimit settings, trim minimums, and superblock update intervals. Attributes pointing into `struct ext4_super_block` display persisted error metadata and identifiers but are generally read-only in this file. `err_report_sec` controls a timer in `sbi` and can start, reschedule, or delete periodic error reporting. `trigger_fs_error` deliberately injects an ext4 error and can update persistent error state through the normal error pipeline.

## Dependencies And Integration Points
The file depends on Linux kobjects/sysfs, procfs, seq_file, block partition statistics, ext4 mballoc proc seq ops, fast-commit proc output, extent-status shrinker diagnostics, error reporting from `super.c`, and timer callback `print_daily_error_info()`. It uses `s_error_notify_mutex` to coordinate `sysfs_notify()` with kobject add/delete.

## Risks And Edge Cases
Pointer-offset attributes require exact type matching; a wrong `attr_id` or offset would cause malformed reads/writes. Writable allocator and ratelimit knobs can affect performance or error visibility immediately. `trigger_fs_error` is gated by `CAP_SYS_ADMIN`, but it intentionally drives filesystem error handling and can force read-only behavior depending on mount options. `reserved_clusters_store()` rejects values greater than or equal to total clusters and negative signed interpretations. `err_report_sec_store()` caps intervals to one year and must avoid timer races during unmount.

## Test Signals
Tests should verify sysfs and proc entries appear after mount and disappear safely on unmount, including concurrent reads of `journal_task` during journal teardown. Attribute tests should cover parsing, invalid bounds, feature presence under different kernel configs, error counter notification, timer enable/disable/reschedule, reserved cluster changes reflected in `statfs`, and proc outputs for options, mballoc, extent-status, and fast-commit state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/truncate.h -->
# sources/distributed-fs/ceph-client/fs/ext4/truncate.h

## Purpose
`truncate.h` contains small inline helpers shared by ext4 truncate/write failure paths. It centralizes the cleanup sequence for failed extending writes and computes bounded journal credit estimates for truncate transactions.

## Important APIs, Types, And Functions
`ext4_truncate_failed_write(struct inode *inode)` invalidates page cache beyond the current inode size and calls `ext4_truncate()` after a write path allocated blocks that were not successfully exposed. `ext4_blocks_for_truncate(struct inode *inode)` estimates the transaction credit budget for the next truncate chunk from `inode->i_blocks`, clamps corrupt-small values up to a safe minimum, caps large values at `EXT4_MAX_TRANS_DATA`, and adds `EXT4_DATA_TRANS_BLOCKS()`.

## Control Flow
The failed-write helper takes the inode mapping's invalidate lock, truncates cached pages to `inode->i_size`, runs ext4 block truncation, then releases the lock. It explicitly skips `ext4_break_layouts()` because the blocks being removed were never visible to userspace. The credit helper converts `i_blocks` from 512-byte sectors to filesystem blocks, applies lower and upper bounds, and returns a journal-credit count for callers that break truncate work into manageable transactions.

## State And Persistence Behavior
`ext4_truncate_failed_write()` removes page-cache state and persistent block mappings past the final visible file size. The helper assumes file size already reflects the correct exposed size. `ext4_blocks_for_truncate()` does not mutate state; it protects journal sizing from corrupt `i_blocks` values and from transactions too large for the journal.

## Dependencies And Integration Points
The helpers integrate with VFS page-cache invalidation, ext4's truncate implementation, ext4 journal credit macros, `struct inode`, `struct address_space`, and ext4 block accounting. They are intended for inclusion by write/truncate code rather than compiled as a separate translation unit.

## Risks And Edge Cases
The failed-write cleanup must hold invalidate locking so buffers are unmapped consistently with page-cache truncation. If callers pass an inode whose `i_size` was not restored correctly, valid blocks could be removed or stale blocks retained. The credit estimate intentionally tolerates corrupt `i_blocks`, but severe corruption can still make truncate behavior expensive or require multiple transactions.

## Test Signals
Useful tests include failed buffered writes after delayed allocation, ENOSPC/error injection during extending writes, mmap/page-cache coherency after failed writes, truncates of sparse and heavily fragmented files, corrupt or fuzzed inode block counts, and journal credit exhaustion boundaries around `EXT4_MAX_TRANS_DATA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/truncate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/verity.c -->
# sources/distributed-fs/ceph-client/fs/ext4/verity.c

## Purpose
`verity.c` implements ext4's `fsverity_operations`. It stores Merkle tree blocks and the fs-verity descriptor beyond normal `i_size`, starting at the next 64 KiB boundary, so metadata remains invisible to userspace while still using ext4's normal page-cache, encryption, block mapping, quota, and journaling paths.

## Important APIs, Types, And Functions
The exported table is `ext4_verityops`, with callbacks `ext4_begin_enable_verity()`, `ext4_end_enable_verity()`, `ext4_get_verity_descriptor()`, `ext4_read_merkle_tree_page()`, `ext4_readahead_merkle_tree()`, and `ext4_write_merkle_tree_block()`. Helper `ext4_verity_metadata_pos()` computes the hidden metadata base. `pagecache_read()` and `pagecache_write()` perform internal IO past `i_size` without using normal file read/write syscalls.

Descriptor layout is handled by `ext4_write_verity_descriptor()` and `ext4_get_verity_descriptor_location()`. The descriptor starts at a filesystem block boundary after the Merkle tree. Its size is stored as a little-endian 32-bit value in the last four bytes of the last allocated filesystem block, allowing lookup by finding the last extent.

## Control Flow
Enabling verity begins in `ext4_begin_enable_verity()`: DAX is rejected, concurrent enable is rejected, the inode gets a JBD2 inode and quota initialization despite the readonly file descriptor, inline data is converted out, non-extent files are rejected, post-EOF blocks are truncated to avoid confusing descriptor lookup, and the inode is added to the orphan list while `EXT4_STATE_VERITY_IN_PROGRESS` is set.

fs/verity writes Merkle tree blocks through `ext4_write_merkle_tree_block()`, which offsets writes by the hidden metadata base and writes through ext4 address-space operations. `ext4_end_enable_verity()` then writes the descriptor, waits for all data and metadata pages, starts a transaction, marks fast commit ineligible, removes the orphan entry, reserves and dirties the inode, sets `EXT4_INODE_VERITY`, and clears the in-progress state. On any failure or when fs/verity passes `desc == NULL`, cleanup truncates cached and on-disk metadata beyond `i_size`, removes orphan state, and clears in-progress state.

Reading verity metadata offsets generic Merkle page reads and readahead by the metadata base. Descriptor lookup finds the last extent, reads the trailing descriptor-size field, validates size and position bounds, and reads the descriptor into the caller buffer or returns its size.

## State And Persistence Behavior
Verity metadata is persisted as hidden file blocks past EOF. Because verity files are readonly after enabling, those blocks can be stable and invisible to userspace. The orphan-list transaction makes interrupted enable operations recoverable: if enabling fails or the system crashes before the verity flag is persisted, metadata beyond `i_size` can be truncated away. The final inode flag is persisted only after writeback of data and metadata pages, preserving crash consistency.

## Dependencies And Integration Points
This file integrates ext4 extents, inline-data conversion, truncation, orphan handling, JBD2 transactions, quota initialization, address-space `write_begin`/`write_end`, page-cache folios, fsverity generic Merkle helpers, fscrypt requirements for encrypted files, and fast-commit exclusion via `ext4_fc_mark_ineligible()`. It requires extent-based files because descriptor discovery relies on the final extent.

## Risks And Edge Cases
DAX is incompatible and rejected. Non-extent files are unsupported. Descriptor discovery depends on the last allocated block, so `ext4_begin_enable_verity()` must remove unrelated post-EOF blocks before metadata is written. `pagecache_write()` must handle short `write_end()` as `-EIO`; reads beyond `i_size` must not use normal VFS reads. Bounds checks in descriptor lookup protect against corrupt size fields, missing extents, and descriptors before the metadata base. Fast commits are explicitly made ineligible for the final enable transaction.

## Test Signals
Tests should cover enabling verity on normal, encrypted, inline-data, DAX, non-extent, sparse, and quota-controlled files; crash or fault injection at each begin/write/end phase; orphan cleanup after interrupted enable; descriptor size/location validation with corrupt extents or trailing size fields; Merkle tree read/readahead offsets; cleanup of post-EOF metadata on failure; and verification that userspace file size and reads never expose hidden metadata blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/verity.c -->
