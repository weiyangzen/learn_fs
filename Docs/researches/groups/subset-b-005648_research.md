# subset-b-005648 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ext4.h -->
# sources/distributed-fs/ceph-client/fs/ext4/ext4.h

## Purpose
`ext4.h` is the central private header for the ext4 implementation in this source tree. It defines the filesystem's core scalar types, on-disk metadata structures, in-memory inode and superblock state, feature-bit accessors, mount/state flags, allocation and mapping request formats, directory-entry formats, and cross-module function prototypes. Most ext4 `.c` files include this header directly or through focused headers such as `ext4_jbd2.h` and `ext4_extents.h`.

The header is both an ABI description and an internal integration contract. Structures such as `struct ext4_inode`, `struct ext4_group_desc`, `struct ext4_super_block`, `struct ext4_dir_entry_2`, and `struct mmp_struct` must match on-disk layout. Structures such as `struct ext4_inode_info`, `struct ext4_sb_info`, `struct ext4_map_blocks`, `struct ext4_allocation_request`, `struct ext4_io_end`, `struct ext4_group_info`, and `struct ext4_iloc` describe live kernel state and module-to-module call conventions.

## Important APIs, types, and constants
The file establishes ext4 numbering types: `ext4_fsblk_t` for filesystem physical blocks, `ext4_lblk_t` for file logical blocks, `ext4_group_t` for block groups, and `ext4_grpblk_t` for group-local block offsets. Mapping and allocation are expressed through `struct ext4_map_blocks` and `struct ext4_allocation_request`, with flags such as `EXT4_MAP_MAPPED`, `EXT4_MAP_UNWRITTEN`, `EXT4_GET_BLOCKS_CREATE`, `EXT4_GET_BLOCKS_CONVERT`, `EXT4_GET_BLOCKS_CONVERT_UNWRITTEN`, and `EXT4_GET_BLOCKS_QUERY_LAST_IN_LEAF`.

The on-disk inode and superblock definitions are the largest persistence contract. `struct ext4_inode` stores mode, owner ids, timestamps, block/extents payload in `i_block`, generation, file ACL, size high bits, checksum fields, creation time, version high bits, and project id. `struct ext4_super_block` stores global counts, feature masks, UUID, journal backing data, default options, MMP, quota inodes, error telemetry, encoding flags, orphan-file inode, and checksum. Helper macros and inline functions convert split 64-bit counters and timestamps, including `ext4_blocks_count()`, `ext4_free_blocks_count()`, `ext4_isize()`, `ext4_encode_extra_time()`, and `ext4_decode_extra_time()`.

The in-memory inode state in `struct ext4_inode_info` layers ext4-specific fields around `struct inode`: raw block payload, deletion time, file ACL block, allocation locality, xattr lock, orphan tracking, fast-commit queues and ranges, `i_disksize`, `i_data_sem`, JBD2 inode linkage, extent status tree, delayed allocation reservations, pending cluster reservations, inline-data coordinates, completed IO conversion lists, fsync transaction ids, inode checksum seed, project id, quota pointers, and optional fscrypt state. The in-memory superblock state in `struct ext4_sb_info` is the mount-wide nexus for block group geometry, descriptors, mount options, journaling, orphan tracking, buddy allocator state, workqueues, error handling, DAX, MMP, fast commit, shrinkers, checksum seeds, and runtime flags.

Feature management is generated through macros such as `EXT4_FEATURE_COMPAT_FUNCS`, `EXT4_FEATURE_RO_COMPAT_FUNCS`, and `EXT4_FEATURE_INCOMPAT_FUNCS`, which produce `ext4_has_feature_*`, `ext4_set_feature_*`, and `ext4_clear_feature_*` accessors. Supported masks distinguish ext2, ext3, and ext4 capability sets. The header also defines mount options (`EXT4_MOUNT_*`, `EXT4_MOUNT2_*`), inode flags (`EXT4_*_FL` and `EXT4_INODE_*`), directory file types, error codes, special inode numbers, block and cluster conversion macros, and KUnit export support.

## Control flow and integration
This header does not implement major filesystem algorithms, but it shapes their control flow. Block mapping flows pass `struct ext4_map_blocks` plus `EXT4_GET_BLOCKS_*` flags into `ext4_map_blocks()`, `ext4_map_query_blocks()`, `ext4_map_create_blocks()`, `ext4_ext_map_blocks()`, or `ext4_ind_map_blocks()` depending on whether extents or indirect blocks are in use. Allocation flows pass `struct ext4_allocation_request` into `ext4_mb_new_blocks()` and use mballoc criteria from `CR_POWER2_ALIGNED` through `CR_ANY_FREE`.

Directory flows consume `struct ext4_filename`, `struct dx_hash_info`, `struct dir_private_info`, `struct ext4_dir_entry_2`, and helpers such as `ext4_dir_rec_len()`, `ext4_rec_len_from_disk()`, `ext4_rec_len_to_disk()`, `ext4_set_de_type()`, `ext4_check_dir_entry()`, and htree prototypes. The file also exposes inline decision points such as `is_dx()`, `EXT4_DIR_LINK_MAX()`, `ext4_hash_in_dirent()`, `ext4_has_inline_data()`, and `is_special_ino()`.

Journaling integration appears through inclusion of `<linux/jbd2.h>`, `handle_t`, `journal_t`, JBD2 inode fields, journal triggers, `struct ext4_io_end`, and prototypes for journal-aware mutation paths. Fast commit integration appears in `struct ext4_inode_info`, `struct ext4_sb_info`, `fast_commit.h`, fast-commit feature bits, `EXT4_FC_REPLAY`, and many `ext4_fc_*` prototypes.

## State and persistence behavior
The file clearly separates durable little-endian metadata from runtime state. On-disk fields use `__le16`, `__le32`, and `__le64`, while helpers convert to CPU order. Persistent checksums cover group descriptors, bitmaps, inodes, orphan-file blocks, directory tails, MMP blocks, and the superblock; the header defines seeds and trigger scaffolding while implementation lives elsewhere.

`i_disksize` is a notable persistence boundary: it records the inode size known to be on disk and may lag `i_size` during truncate or growth. `ext4_update_i_disksize()` and `ext4_update_inode_size()` serialize through `i_data_sem` and require inode locking for regular files. Orphan tracking is represented by either an orphan list node or orphan-file index and recovery-related feature/state flags.

Mount-level state includes clean/error/orphan/fast-commit-replay flags, emergency shutdown/read-only flags, journal destroy flags, writeback error sequence tracking, periodic superblock update work, and MMP thread data. Group and flex-group counters are mirrored in memory with atomic/percpu counters and must be reconciled with on-disk descriptors and superblock totals.

## Dependencies and integration points
The header depends on core kernel filesystem, block, quota, percpu, RCU, crypto checksum, fscrypt, fsverity, fiemap, rbtree, xarray, workqueue, and JBD2 facilities. It includes local `extents_status.h` and `fast_commit.h`, and it declares interfaces implemented by many ext4 compilation units: `bitmap.c`, `balloc.c`, `dir.c`, `fsync.c`, `hash.c`, `ialloc.c`, `fast_commit.c`, `mballoc.c`, `inode.c`, `indirect.c`, `ioctl.c`, `namei.c`, `resize.c`, `super.c`, `extents.c`, `move_extent.c`, `page-io.c`, `mmp.c`, `verity.c`, `orphan.c`, `inline.c`, `readpages.c`, `symlink.c`, `sysfs.c`, and block-validity code.

It integrates directly with VFS through `struct inode`, `struct super_block`, inode/file operations, address-space operations, folios, readahead, ioctl, file attributes, dentry lookups, and quota structures. It integrates with block IO through `buffer_head`, `bio`, block devices, DAX, and writeback controls.

## Risks and review notes
Because this file defines on-disk layout, any field reordering, type-size change, endian misuse, or feature-bit mismatch can corrupt filesystems or break compatibility with e2fsprogs and older kernels. The compile-time flag checks in `ext4_check_flag_values()` reduce the risk of inode flag drift but do not protect all on-disk structures.

The inline helpers encode assumptions about locking and mount state. Misusing `ext4_update_i_disksize()` without inode serialization, using feature setters without journaled superblock updates, dereferencing RCU arrays without the provided accessor pattern, or bypassing emergency state checks can produce races or inconsistent persistence. Many counters are split between on-disk descriptors, percpu counters, atomic counters, and runtime caches, so allocator and resize paths require careful synchronization.

The header is also highly conditional on kernel config. Quota, encryption, verity, DAX, unicode/casefold, KUnit, SMP, and debug options alter available fields or behavior. Callers must use capability helpers instead of assuming a feature is compiled or mounted.

## Test signals
Testable invariants include inode flag bit/value parity, feature compatibility masks, endian round trips for block counts and inode sizes, timestamp encoding boundaries, directory record length conversions, extent-mode vs bitmap-mode maxbytes, special inode detection, inline-data detection, emergency-state behavior, and block group lock contention helpers. The KUnit-facing `EXPORT_SYMBOL_FOR_EXT4_TEST` and the dedicated extents test in this subset show that some internal helpers are intended to be exercised through KUnit rather than only whole-filesystem tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ext4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ext4_extents.h -->
# sources/distributed-fs/ceph-client/fs/ext4/ext4_extents.h

## Purpose
`ext4_extents.h` defines the on-disk extent tree format and small helper API used by ext4 extent mapping, allocation, split, conversion, truncate, fiemap, and test code. It is included by extent implementation code and by the KUnit extent split/conversion tests.

## Important APIs, types, and constants
The on-disk extent tree is described by `struct ext4_extent_header`, `struct ext4_extent`, `struct ext4_extent_idx`, and `struct ext4_extent_tail`. The header stores magic, entry count, max capacity, depth, and generation. Leaf extents store first logical block, encoded length, and the split high/low physical block. Index entries store the logical starting key and physical child block. Non-inode extent blocks carry `struct ext4_extent_tail`, a checksum slot placed after the max extent array.

`struct ext4_ext_path` is the traversal cursor used by lookup, insert, split, and truncate code. Each path element records the current physical block, depth, max depth, selected leaf extent or index, header pointer, and buffer head. `struct partial_cluster` records bigalloc partial clusters during removal with `initial`, `tofree`, and `nofree` state.

Key constants include `EXT4_EXT_MAGIC`, `EXT4_MAX_EXTENT_DEPTH`, `EXT_INIT_MAX_LEN`, and `EXT_UNWRITTEN_MAX_LEN`. The high bit of `ee_len` encodes unwritten status, except the special `0x8000` value which remains an initialized extent of length 32768. Macros such as `EXT_FIRST_EXTENT`, `EXT_LAST_EXTENT`, `EXT_FIRST_INDEX`, `EXT_LAST_INDEX`, `EXT_MAX_EXTENT`, `EXT_MAX_INDEX`, and `EXT_HAS_FREE_INDEX` provide typed pointer arithmetic over extent blocks.

Inline helpers include `ext_inode_hdr()`, `ext_block_hdr()`, `ext_depth()`, `ext4_ext_mark_unwritten()`, `ext4_ext_is_unwritten()`, `ext4_ext_get_actual_len()`, `ext4_ext_mark_initialized()`, `ext4_ext_pblock()`, `ext4_idx_pblock()`, `ext4_ext_store_pblock()`, and `ext4_idx_store_pblock()`.

## Control flow and integration
Extent lookup starts from `ext_inode_hdr(inode)`, descends through `struct ext4_extent_idx` entries, and records the route in `struct ext4_ext_path`. Leaf operations then inspect or update `struct ext4_extent` entries. Split and conversion code relies on the encoded `ee_len` state to distinguish initialized and unwritten extents, and on path capacity helpers to decide whether an insert can happen in-place or requires splitting/growing the tree.

The header declares implementation entry points used elsewhere: `__ext4_ext_dirty()` to journal/dirty an extent path, `ext4_ext_zeroout()` for zeroing unwritten ranges, and KUnit-only hooks `ext4_ext_space_root_idx_test()` and `ext4_split_convert_extents_test()` when `CONFIG_EXT4_KUNIT_TESTS` is enabled.

## State and persistence behavior
All extent tree structures in this header are persistent little-endian metadata. The root extent header lives in `EXT4_I(inode)->i_data`, which corresponds to the on-disk inode `i_block` area for extent-enabled inodes. Child extent/index blocks are normal metadata blocks and may include checksum tails. Physical block numbers are stored as low 32 bits plus high 16 bits; helpers must be used to avoid truncation.

Unwritten state is persisted in `ee_len`, not in a separate flag field. That compact encoding is central to fallocate, delayed allocation, direct IO completion, and conversion paths. Any code that changes extent length must preserve the encoding convention and the maximum length rules.

## Dependencies and integration points
This header depends on `ext4.h` for core types, inode access, block numbers, and JBD2 handle declarations. It integrates with `extents.c`, `inode.c`, `move_extent.c`, fiemap, fast commit replay extent updates, and the KUnit test in `extents-test.c`.

## Risks and review notes
The main risks are off-by-one and endian mistakes in extent pointer arithmetic, length encoding, and physical block split/join helpers. `EXT_LAST_EXTENT()` and similar macros assume `eh_entries` is nonzero; callers must validate tree headers before dereferencing. `ext4_ext_mark_unwritten()` has a `BUG_ON` for zero-length unwritten extents, which is appropriate for an invariant breach but dangerous if reachable from corrupted metadata without prior validation.

Checksum-tail placement relies on `eh_max` and block-size geometry. If a caller corrupts `eh_max`, `find_ext4_extent_tail()` can point at the wrong location. Tree depth is capped by `EXT4_MAX_EXTENT_DEPTH`; validation paths must enforce that before recursion or path allocation.

## Test signals
The KUnit hooks exported under `CONFIG_EXT4_KUNIT_TESTS` are direct test signals. Useful invariants include physical block round trips through store/load helpers, initialized/unwritten length transitions around `0x8000`, root header access through inode private data, checksum-tail offset computation, and extent/index pointer macros over synthetic headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ext4_extents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ext4_jbd2.c -->
# sources/distributed-fs/ceph-client/fs/ext4/ext4_jbd2.c

## Purpose
`ext4_jbd2.c` implements ext4's concrete wrappers around the JBD2 journal. It chooses per-inode data journaling mode, starts and stops transactions, handles no-journal mounts, reserves and extends credits, obtains metadata write/create access, forgets or revokes freed blocks, detects block-device writeback errors in no-journal mode, and dirties metadata buffers.

## Important APIs and functions
`ext4_inode_journal_mode()` returns one of `EXT4_INODE_JOURNAL_DATA_MODE`, `EXT4_INODE_ORDERED_DATA_MODE`, or `EXT4_INODE_WRITEBACK_DATA_MODE`. It falls back to writeback when no journal exists; selects full data journaling for non-regular files, EA inodes, journal-data mount mode, or per-inode journal-data flag without delayed allocation; downgrades encrypted regular-file data to ordered mode; and otherwise follows the mount data mode.

`__ext4_journal_start_sb()` checks mount/journal state, traces the start event, then either returns a no-journal pseudo-handle or calls `jbd2__journal_start()`. `__ext4_journal_stop()` drops no-journal pseudo-handles, stops real JBD2 handles, and reports transaction errors through `__ext4_std_error()`. `__ext4_journal_start_reserved()` starts a pre-reserved handle after rechecking mount state. `__ext4_journal_ensure_credits()` verifies available buffer and revoke credits and extends the transaction when needed.

`__ext4_journal_get_write_access()` and `__ext4_journal_get_create_access()` wrap JBD2 buffer access calls and attach metadata checksum triggers when requested and supported. `__ext4_forget()` chooses between buffer forget and journal revoke based on no-journal mode, metadata/data classification, full data journaling, and per-inode data journaling. `__ext4_handle_dirty_metadata()` marks buffers metadata/prioritized/uptodate and either journals them or directly marks/syncs them dirty on no-journal filesystems.

Internal helpers include `ext4_get_nojournal()` and `ext4_put_nojournal()`, which encode a nested no-journal reference count in `current->journal_info`; `ext4_journal_check_start()`, which rejects emergency, read-only, frozen, or aborted-journal states; `ext4_journal_abort_handle()`, which records `h_err` and aborts the JBD2 handle; and `ext4_check_bdev_write_error()`, which advances the block device errseq and reports asynchronous metadata writeback errors.

## Control flow
The normal mutation path starts by calling a macro from `ext4_jbd2.h`, which supplies function/line metadata and reaches `__ext4_journal_start_sb()`. That function calls `ext4_journal_check_start()`. If the filesystem has no journal or is in fast-commit replay, it creates/increments a no-journal pseudo-handle; otherwise it starts a JBD2 transaction with GFP_NOFS allocation and the caller's credit request.

Metadata update paths then call write/create access wrappers before changing buffer contents, optionally install checksum triggers, and later call `ext4_handle_dirty_metadata()` to journal or dirty the buffer. On any JBD2 access error, `ext4_journal_abort_handle()` records the error on the handle and aborts the transaction. Finally `ext4_journal_stop()` stops the handle and reports errors to the superblock error path.

Freeing blocks flows through `__ext4_forget()`. Without a valid handle, it clears and forgets the buffer after waiting for IO. With a real journal, full data journaling and non-journaled data blocks use `jbd2_journal_forget()`, while metadata and journaled data use `jbd2_journal_revoke()` so old metadata cannot be replayed after reuse.

## State and persistence behavior
Real JBD2 transactions persist metadata updates through the journal and track errors in `handle->h_err`. No-journal pseudo-handles provide a common calling convention but do not journal; direct dirtying and synchronous buffer writeback are used where required. The pseudo-handle refcount is stored in `current->journal_info` as a small integer, making nested no-journal scopes cheap but requiring strict balance.

Checksum trigger installation persists correct metadata checksums during journal commit for trigger types such as orphan-file blocks. Revoke records are persistence-critical: they prevent stale journal contents from resurrecting freed metadata/data blocks after crash recovery. Block-device errseq checking protects no-journal metadata writes from silently reusing stale buffers after asynchronous writeback errors.

## Dependencies and integration points
The file includes `ext4_jbd2.h` and `trace/events/ext4.h`, and calls into JBD2 APIs such as `jbd2__journal_start()`, `jbd2_journal_stop()`, `jbd2_journal_start_reserved()`, `jbd2_journal_extend()`, `jbd2_journal_get_write_access()`, `jbd2_journal_get_create_access()`, `jbd2_journal_forget()`, `jbd2_journal_revoke()`, and `jbd2_journal_dirty_metadata()`. It uses ext4 helpers from `ext4.h` for mount options, emergency state, metadata checksum features, buffer metadata tracking, error reporting, and inode flags.

## Risks and review notes
The journaling mode decision must stay aligned with delayed allocation, encryption, and data mode constraints. Accidentally enabling full data journaling with delayed allocation or encrypted regular files would violate assumptions elsewhere. No-journal pseudo-handles are pointer-like values below `EXT4_NOJOURNAL_MAX_REF_COUNT`; code must never pass NULL or arbitrary small values as real handles.

Credit handling is a common correctness risk. Underestimating buffer or revoke credits can force restart paths at unsafe points or fail metadata updates. Forget/revoke decisions are crash-consistency critical, especially for metadata blocks and journaled data. Error paths must preserve the first meaningful `h_err` and propagate failures to ext4's error machinery.

## Test signals
Important test signals include journal mode selection across mount modes, encrypted files, EA inodes, delayed allocation, and no-journal filesystems; nested no-journal start/stop balancing; aborted journal startup rejection; access wrapper trigger installation when metadata checksums are enabled; revoke vs forget behavior for metadata and data blocks; dirty metadata behavior with and without handles; and errseq-driven writeback error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ext4_jbd2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ext4_jbd2.h -->
# sources/distributed-fs/ceph-client/fs/ext4/ext4_jbd2.h

## Purpose
`ext4_jbd2.h` is the public ext4-internal journaling interface. It declares transaction credit formulas, handle operation type identifiers, inode dirtying entry points, wrapper macros that capture callsite information, no-journal handle semantics, transaction start/stop/restart helpers, fsync transaction tracking, data journaling mode predicates, revoke-credit calculations, dioread-nolock eligibility, and journal teardown.

## Important APIs, types, and constants
`EXT4_JOURNAL(inode)` retrieves `EXT4_SB(inode->i_sb)->s_journal`. Transaction credit macros include `EXT4_SINGLEDATA_TRANS_BLOCKS()`, `EXT4_XATTR_TRANS_BLOCKS`, `EXT4_DATA_TRANS_BLOCKS()`, `EXT4_META_TRANS_BLOCKS()`, `EXT4_MAX_TRANS_DATA`, `EXT4_RESERVE_TRANS_BLOCKS`, `EXT4_INDEX_EXTRA_TRANS_BLOCKS`, quota credit macros, and `EXT4_MAXQUOTAS_*` aggregations. These formulas encode how many journal credits typical data, xattr, quota, directory-index, and metadata operations should reserve.

Handle type constants `EXT4_HT_*` classify transaction callers for logging and diagnostics. Inode write APIs include `ext4_reserve_inode_write()`, `ext4_mark_iloc_dirty()`, `ext4_mark_inode_dirty()`, `__ext4_mark_inode_dirty()`, and `ext4_expand_extra_isize()`.

The core wrapper declarations correspond to implementations in `ext4_jbd2.c`: `__ext4_journal_get_write_access()`, `__ext4_forget()`, `__ext4_journal_get_create_access()`, `__ext4_handle_dirty_metadata()`, `__ext4_journal_start_sb()`, `__ext4_journal_stop()`, `__ext4_journal_start_reserved()`, and `__ext4_journal_ensure_credits()`. Macros such as `ext4_journal_get_write_access()`, `ext4_forget()`, and `ext4_handle_dirty_metadata()` attach `__func__` and `__LINE__`.

Inline helpers cover handle validation, sync marking, abort testing, revoke credit calculation, starting transactions from a superblock or inode, extending/restarting transactions, ensuring credits with optional cleanup callback, querying blocks per folio, forcing commits, registering inode write/wait ranges with JBD2, tracking fsync transaction ids, checking data journaling mode, computing data revoke credits, checking direct-IO read no-lock eligibility, and destroying a journal.

## Control flow
Callers normally use `ext4_journal_start()`, `ext4_journal_start_sb()`, `ext4_journal_start_with_reserve()`, or `ext4_journal_start_with_revoke()` to obtain a handle with typed credits and default revoke credits. The wrappers funnel into `__ext4_journal_start_sb()` in the `.c` file. Metadata buffers are protected with access wrappers and finalized with `ext4_handle_dirty_metadata()`. Long operations use `ext4_journal_ensure_credits()` or `ext4_journal_ensure_credits_fn()` to extend or restart transactions when credits run low.

`ext4_journal_ensure_credits_fn()` is a control-flow macro with a local label. It first calls `__ext4_journal_ensure_credits()`. If the current handle has enough credits or extension succeeds, it returns that status. If a restart is needed, it executes the caller-provided cleanup expression, restarts the journal with the requested credits, and returns `1` on successful restart.

`ext4_journal_destroy()` coordinates teardown by setting `EXT4_MF_JOURNAL_DESTROY`, forcing a commit, flushing pending superblock update work, destroying the JBD2 journal, and clearing `sbi->s_journal`.

## State and persistence behavior
This header defines how ext4 accounts for journal capacity before persistent metadata changes. The credit formulas are conservative persistence contracts: they reserve space for inode blocks, bitmaps, group descriptors, superblock summaries, xattrs, quotas, extent tree levels, and revoke records. `ext4_free_metadata_revoke_credits()` scales revoke credits by cluster ratio because freeing metadata blocks may free clusters under bigalloc.

`ext4_update_inode_fsync_trans()` stores the current transaction id in `i_sync_tid` and optionally `i_datasync_tid`, linking inode fsync behavior to JBD2 transaction persistence. `ext4_jbd2_inode_add_write()` and `ext4_jbd2_inode_add_wait()` register byte ranges that JBD2 must write or wait on for ordered semantics.

No-journal handles are explicitly treated as invalid by `ext4_handle_valid()`, allowing most wrappers to become no-ops while keeping callers structurally identical. Data journaling mode predicates drive persistence ordering: full data journaling writes data through the journal, ordered mode orders data before commit, and writeback mode does not provide data-before-metadata ordering.

## Dependencies and integration points
The header depends on Linux VFS and JBD2 headers plus `ext4.h`. It integrates with inode, xattr, directory, truncate, quota, resize, migrate, move-extents, writepage, and extent-conversion code through handle type constants and credit formulas. It also coordinates with superblock error update work and mount flags for journal destruction.

## Risks and review notes
Transaction credit formulas are easy to under-maintain when metadata formats evolve. Adding extent tree levels, quota behavior, xattr writes, or directory-index operations without updating credits can cause hard-to-reproduce ENOSPC or journal restart failures. Conversely, over-reserving credits reduces concurrency and journal capacity.

The handle validity scheme depends on no-journal pseudo-handles being small integer values and real JBD2 pointers not occupying that range. Callers must use `ext4_handle_valid()` before dereferencing a handle. `ext4_should_dioread_nolock()` deliberately rejects non-regular, non-extent, journal-data, and non-delalloc cases because those paths conflict with direct IO assumptions and JBD2 use of `b_private`.

`ext4_journal_destroy()` assumes only the commit thread and superblock update work can still operate on the journal at teardown. Reordering that sequence could leave queued work using a destroyed journal.

## Test signals
Useful tests cover credit formulas under extents vs indirect files, quota enabled/disabled, revoke credit calculations with bigalloc cluster ratios, no-journal handle validation, `ext4_journal_ensure_credits_fn()` restart behavior, fsync transaction id updates, `ext4_should_dioread_nolock()` gating, data journaling predicates, and journal destroy ordering with pending superblock update work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ext4_jbd2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/extents-test.c -->
# sources/distributed-fs/ceph-client/fs/ext4/extents-test.c

## Purpose
`extents-test.c` is a KUnit suite for ext4 extent split and conversion behavior. It targets `ext4_split_convert_extents()` directly through a test-only wrapper and indirectly through `ext4_map_query_blocks()` plus `ext4_map_create_blocks()`. The tests verify initialized-to-unwritten conversion, unwritten-to-initialized conversion, fallback zeroout behavior when extent insertion fails, and extent-status cache synchronization for high-level mapping paths.

## Important APIs, types, and fixtures
The test uses a minimal synthetic ext4 mount, inode, extent tree, extent-status tree, and data buffer. Constants `EXT_DATA_PBLK`, `EXT_DATA_LBLK`, and `EXT_DATA_LEN` create one three-block extent mapping logical block 10 to physical block 100. `struct kunit_ctx` holds the allocated `struct ext4_inode_info` and an in-memory data area used to model disk contents for zeroout tests.

`struct kunit_ext_test_param` drives all parameterized cases. It records a description, test type (`TEST_SPLIT_CONVERT` or `TEST_CREATE_BLOCKS`), initial unwritten state, split flags, target `struct ext4_map_blocks`, whether zeroout is disabled, expected extent states, whether this is a zeroout test, and expected data-buffer segments after zeroing. `struct kunit_ext_state` and `struct kunit_ext_data_state` express the expected tree and data results.

Static stubs replace selected ext4 internals: `__ext4_ext_dirty_stub()` suppresses real journal dirtying, `ext4_ext_insert_extent_stub()` returns `-ENOSPC` to force fallback zeroout, `ext4_ext_zeroout_stub()` and `ext4_issue_zeroout_stub()` zero the synthetic data buffer instead of issuing real block IO.

## Control flow
`extents_kunit_init()` creates a fake superblock with 4 KiB blocks, allocates `struct ext4_sb_info`, registers the extent status shrinker, allocates a mock ext4 inode, initializes its extent status tree and locks, marks it extent-enabled, allocates a three-block data buffer filled with `'X'`, and builds a depth-0 extent tree rooted in `i_data`. It inserts a matching extent status entry and activates the common static stubs.

`test_split_convert()` optionally activates the insert-failure stub for zeroout cases, finds the initial extent, verifies starting logical block, length, and unwritten state, populates a map from the current parameter, and dispatches either to `ext4_split_convert_extents_test()` or to `ext4_map_create_blocks_helper()`. The helper first calls `ext4_map_query_blocks()` to populate map details and then `ext4_map_create_blocks()` to perform split/conversion, avoiding the need to mock the full `ext4_map_blocks()` path.

After mutation, the test refinds the extent tree and iterates expected extents. For high-level create-blocks cases, it also looks up each extent in the extent-status cache and verifies containment, physical block alignment, and written/unwritten status. For zeroout cases, it verifies the synthetic data buffer has zeroes only in the expected unwritten portions and preserves `'X'` in ranges that should remain data.

The suite registers three parameter groups: direct split/convert cases, initialized-to-unwritten cases through `convert_initialized_extent()`, and unwritten handling cases through `ext4_ext_handle_unwritten_extents()`.

## State and persistence behavior
The test does not mount or persist a real filesystem. It models persistent extent metadata in `k_ei->i_data` and models disk data in `k_ctx.k_data`. The synthetic extent status tree is kept in memory and validated only for paths that should update it. Zeroout behavior is persistence-relevant even in this fake setup: the test ensures fallback conversion to one initialized extent does not leak stale data in ranges that remain logically unwritten.

Resource cleanup in `extents_kunit_exit()` unregisters the shrinker, deactivates the superblock, frees `sbi`, the mock inode, and the data buffer. Failure paths in init free partially allocated state and deactivate the superblock.

## Dependencies and integration points
The file depends on KUnit, KUnit static stubs, ext4 core headers, extents helpers, extent status APIs, superblock lifecycle helpers, and the KUnit-only exports declared in `ext4_extents.h` and `ext4.h`. It reaches into internal ext4 functions rather than public VFS behavior, so it is a focused unit test for extent algorithms.

## Risks and review notes
The test intentionally uses a minimal mock inode and superblock, so it may not catch bugs involving full journal handles, real block allocation, quota, locking, checksum tails, multi-level extent trees, or IO error handling. Static stubs can mask interactions with dirtying and block IO. Because the fixture creates only one depth-0 extent of length three, it has strong coverage of split shapes within a small extent but not broader tree balancing or large extent limits.

The global `k_ctx` means cases assume KUnit serializes suite state or invokes init/exit cleanly per case. Any future parallelization or additional shared state should avoid cross-test contamination.

## Test signals
The parameter tables cover two-extent and three-extent splits at the beginning, end, and middle of an extent; unwritten-to-written and written-to-unwritten transitions; direct split conversion; high-level create-block paths; endio and non-endio unwritten handling; forced `-ENOSPC` zeroout fallback; data preservation around zeroed ranges; and extent status cache consistency for high-level paths. These are strong regression signals for extent conversion correctness and stale-data avoidance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/extents-test.c -->
