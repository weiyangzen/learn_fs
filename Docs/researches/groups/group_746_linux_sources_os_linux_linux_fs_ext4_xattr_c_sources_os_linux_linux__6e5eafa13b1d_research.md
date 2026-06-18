# Group Research: group_746_linux_sources_os_linux_linux_fs_ext4_xattr_c_sources_os_linux_linux__6e5eafa13b1d

Scope checked against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/linux/linux`. All 12 listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr.c -->
# File Research: sources/os/linux/linux/fs/ext4/xattr.c

## Purpose
Implements ext4 extended attribute storage, lookup, listing, mutation, sharing, checksum validation, large-value EA inodes, inode-expansion migration, and cleanup. It is the core backend used by ext4 namespace handlers in `xattr_user.c`, `xattr_trusted.c`, `xattr_security.c`, and `xattr_hurd.c`.

## Main Responsibilities
- Supports both in-inode xattrs and external xattr blocks referenced by `EXT4_I(inode)->i_file_acl`.
- Shares identical external xattr blocks through `mb_cache` and reference counts.
- Supports large xattr values stored in separate EA inodes when `ea_inode` feature is enabled.
- Validates on-disk xattr structure, value offsets, checksums, ea-inode references, and size limits before use.
- Provides public operations: `ext4_xattr_get`, `ext4_listxattr`, `ext4_xattr_set`, `ext4_xattr_set_handle`, `ext4_xattr_delete_inode`, `ext4_expand_extra_isize_ea`, cache create/destroy helpers, and inode usage accounting.

## Key Data Flow
- Get path: `ext4_xattr_get()` takes `xattr_sem` read lock, searches inode body first via `ext4_xattr_ibody_get()`, then external block via `ext4_xattr_block_get()`.
- List path: `ext4_listxattr()` lists in-inode entries then block entries, filtering prefixes with namespace handlers and permissions.
- Set path: `ext4_xattr_set()` computes journal credits, starts a transaction, and delegates to `ext4_xattr_set_handle()`.
- Mutation path: `ext4_xattr_set_handle()` locks xattrs for write, finds existing inode/block entries, applies create/replace/remove semantics, chooses in-inode, xattr block, or EA inode storage, updates ctime/iversion, and marks fast commit ineligible.
- Delete path: `ext4_xattr_delete_inode()` decrements EA inode refs, releases xattr block refs, frees blocks, and clears `i_file_acl`.

## Important Implementation Details
- `check_xattrs()` is the core corruption gate. It validates xattr block headers, in-inode magic, entry list bounds, names without embedded NUL mismatch, EA inode feature constraints, value bounds, and overlap between name table and value area.
- Metadata checksums are handled by `ext4_xattr_block_csum()`, `ext4_xattr_block_csum_verify()`, and `ext4_xattr_block_csum_set()` when `metadata_csum` is enabled.
- `xattr_find_entry()` supports sorted external block lookup and unsorted in-inode lookup.
- `ext4_xattr_set_entry()` performs the packed entry/value layout edits, including inserting/removing names, moving value regions, zeroing padding, updating inline data offset, and recalculating entry/block hashes.
- `ext4_xattr_block_set()` handles copy-on-write for shared xattr blocks, mbcache reuse of identical blocks, quota charging, refcount saturation, allocation of new xattr blocks, and release of old blocks.
- EA inode support stores refcount in ctime/iversion and value hash in atime. It verifies stored value hashes and has compatibility handling for older Lustre-style EA inodes.
- `ext4_expand_extra_isize_ea()` makes room for larger inode extra fields by shifting in-inode xattrs or migrating selected xattrs to an external block.

## Concurrency and Journaling
- `EXT4_I(inode)->xattr_sem` protects `i_file_acl` and in-inode xattr state.
- External xattr blocks are only modified in place if exclusive; otherwise they are cloned.
- Buffer locks protect xattr block refcount/cache races.
- Journal credit estimation accounts for inode updates, xattr block ref/refree operations, quotas, inline-data expansion, EA inode allocation/data blocks, and old EA inode dereference.
- `ext4_journal_ensure_credits_fn()` is used during bulk EA inode ref decrements to safely survive transaction restarts.

## Edge Cases and Failure Modes
- Returns `-EFSCORRUPTED` or `-EFSBADCRC` for malformed or checksum-invalid metadata.
- Treats xattr names longer than 255 as `-ERANGE`.
- Avoids xattr recursion during write lock by overloading `EXT4_STATE_NO_EXPAND` through helpers in `xattr.h`.
- Refcount wraparound on EA inodes is detected and reported.
- Shared block refcount cannot exceed `EXT4_XATTR_REFCOUNT_MAX`; saturated blocks are marked non-reusable.
- Large values may retry storage as EA inodes if they do not fit in xattr block storage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr.h -->
# File Research: sources/os/linux/linux/fs/ext4/xattr.h

## Purpose
Defines ext4 xattr on-disk formats, constants, layout macros, helper structs, lock helpers, and exported xattr APIs.

## Key Definitions
- Magic and limits: `EXT4_XATTR_MAGIC`, `EXT4_XATTR_REFCOUNT_MAX`, `EXT4_XATTR_SIZE_MAX`.
- Namespace indexes: user, POSIX ACL access/default, trusted, Lustre, security, system, richacl, encryption, and Hurd.
- On-disk structures: `ext4_xattr_header`, `ext4_xattr_ibody_header`, and `ext4_xattr_entry`.
- Layout macros: `EXT4_XATTR_LEN`, `EXT4_XATTR_NEXT`, `EXT4_XATTR_SIZE`, `IHDR`, `ITAIL`, `IFIRST`, `BHDR`, `BFIRST`, `IS_LAST_ENTRY`.
- `EXT4_INODE_HAS_XATTR_SPACE()` verifies that an inode has enough extra inode area to host an in-inode xattr header and padding.

## API Surface
Declares get/list/set paths, journal-credit helpers, inode deletion cleanup, extra-isize expansion, EA inode eviction, ibody find/set/get helpers, mbcache create/destroy, inode usage accounting, and xattr handler arrays.

## Notable Design Detail
The inline xattr write lock helpers save and restore `EXT4_STATE_NO_EXPAND`. That state is intentionally overloaded to mean both “do not try further inline expansion” and “xattr write lock is held, avoid recursive expansion.”
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr_hurd.c -->
# File Research: sources/os/linux/linux/fs/ext4/xattr_hurd.c

## Purpose
Provides the ext4 xattr handler for GNU/Hurd-prefixed extended attributes.

## Behavior
- Uses prefix `XATTR_HURD_PREFIX`.
- Lists, gets, and sets only when the filesystem has `XATTR_USER` mount option enabled.
- Maps all operations to `EXT4_XATTR_INDEX_HURD` through `ext4_xattr_get()` and `ext4_xattr_set()`.

## Integration
Registered as `ext4_xattr_hurd_handler`, included in ext4 handler arrays unconditionally.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr_hurd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr_security.c -->
# File Research: sources/os/linux/linux/fs/ext4/xattr_security.c

## Purpose
Provides ext4 support for `security.*` extended attributes and LSM security initialization.

## Behavior
- Maps get/set to `EXT4_XATTR_INDEX_SECURITY`.
- `ext4_init_security()` calls `security_inode_init_security()` and stores returned initial labels using `ext4_xattr_set_handle()` inside the caller-provided journal handle.
- Initial xattrs are created with `XATTR_CREATE`.

## Integration
Registered as `ext4_xattr_security_handler` when `CONFIG_EXT4_FS_SECURITY` is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr_trusted.c -->
# File Research: sources/os/linux/linux/fs/ext4/xattr_trusted.c

## Purpose
Provides ext4 support for `trusted.*` extended attributes.

## Behavior
- Uses prefix `XATTR_TRUSTED_PREFIX`.
- Listing is restricted to callers with `CAP_SYS_ADMIN`.
- Get/set map to `EXT4_XATTR_INDEX_TRUSTED`.

## Integration
Registered as `ext4_xattr_trusted_handler` and included in ext4 handler arrays.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr_trusted.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr_user.c -->
# File Research: sources/os/linux/linux/fs/ext4/xattr_user.c

## Purpose
Provides ext4 support for `user.*` extended attributes.

## Behavior
- Uses prefix `XATTR_USER_PREFIX`.
- List/get/set are enabled only when the ext4 `XATTR_USER` mount option is set.
- Get/set map to `EXT4_XATTR_INDEX_USER`.

## Integration
Registered as `ext4_xattr_user_handler` and included in ext4 handler arrays.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/xattr_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/Kconfig -->
# File Research: sources/os/linux/linux/fs/f2fs/Kconfig

## Purpose
Defines F2FS kernel configuration options and dependency wiring.

## Key Options
- `F2FS_FS`: main filesystem support, depends on `BLOCK`, selects buffer heads, NLS, CRC32, iomap, and encryption/xattr helpers when needed.
- `F2FS_STAT_FS`: debugfs status reporting.
- `F2FS_FS_XATTR`: extended attributes, default enabled.
- `F2FS_FS_POSIX_ACL`: POSIX ACLs, depends on xattrs and selects `FS_POSIX_ACL`.
- `F2FS_FS_SECURITY`: security labels through xattrs.
- `F2FS_CHECK_FS`: runtime consistency checking.
- `F2FS_FAULT_INJECTION`: test fault injection.
- `F2FS_FS_COMPRESSION`: filesystem-level compression.
- Compression backends: LZO, LZO-RLE, LZ4, LZ4HC, ZSTD.
- `F2FS_IOSTAT`: sysfs and tracepoint IO statistics.
- `F2FS_UNFAIR_RWSEM`: unfair rwsem behavior for block-cgroup priority systems.

## Build Impact
This file controls which optional objects in the F2FS Makefile are compiled, especially `xattr.o`, `acl.o`, `compress.o`, `debug.o`, and `iostat.o`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/Makefile -->
# File Research: sources/os/linux/linux/fs/f2fs/Makefile

## Purpose
Defines the F2FS composite kernel object and optional object inclusion.

## Object Composition
- Core `f2fs-y`: `dir.o`, `file.o`, `inode.o`, `namei.o`, `hash.o`, `super.o`, `inline.o`, `checkpoint.o`, `gc.o`, `data.o`, `node.o`, `segment.o`, `recovery.o`, `shrinker.o`, `extent_cache.o`, `sysfs.o`.
- Optional objects:
  - `debug.o` for `CONFIG_F2FS_STAT_FS`
  - `xattr.o` for `CONFIG_F2FS_FS_XATTR`
  - `acl.o` for `CONFIG_F2FS_FS_POSIX_ACL`
  - `verity.o` for `CONFIG_FS_VERITY`
  - `compress.o` for `CONFIG_F2FS_FS_COMPRESSION`
  - `iostat.o` for `CONFIG_F2FS_IOSTAT`
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/acl.c -->
# File Research: sources/os/linux/linux/fs/f2fs/acl.c

## Purpose
Implements F2FS POSIX ACL conversion, retrieval, setting, and inode-initialization behavior using F2FS xattrs.

## Main Responsibilities
- Converts between F2FS compact on-disk ACL encoding and VFS `struct posix_acl`.
- Retrieves access/default ACLs through `f2fs_getxattr()`.
- Stores ACLs through `f2fs_setxattr()`.
- Updates inode mode bits when access ACLs are equivalent or when permissions must be masked.
- Initializes new inode ACLs from parent default ACLs.

## Key Functions
- `f2fs_acl_size()` and `f2fs_acl_count()` calculate compact ACL storage sizes and entry counts.
- `f2fs_acl_from_disk()` validates version, decodes short/full ACL entries, maps ids through `init_user_ns`, and returns a VFS ACL.
- `f2fs_acl_to_disk()` encodes VFS ACLs into F2FS disk format.
- `f2fs_get_acl()` rejects RCU lookup with `-ECHILD` and delegates to xattr-backed lookup.
- `f2fs_set_acl()` rejects checkpoint-error filesystems with `-EIO`, then calls `__f2fs_set_acl()`.
- `f2fs_init_acl()` derives default/access ACLs for newly created inodes and marks inode metadata dirty.

## Edge Cases
- Non-directory default ACL set returns `-EACCES` when an ACL is supplied.
- Symlinks and non-POSIXACL parents skip inherited ACL creation.
- If inherited ACL is equivalent to mode bits, the access ACL is dropped and only mode is updated.
- Invalid on-disk ACL tags, sizes, or version return `-EINVAL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/acl.h -->
# File Research: sources/os/linux/linux/fs/f2fs/acl.h

## Purpose
Defines F2FS POSIX ACL on-disk structures and function declarations.

## Key Definitions
- `F2FS_ACL_VERSION` is `0x0001`.
- `f2fs_acl_header` stores ACL version.
- `f2fs_acl_entry_short` stores tag and permission for entries without ids.
- `f2fs_acl_entry` stores tag, permission, and user/group id.

## Conditional API
When `CONFIG_F2FS_FS_POSIX_ACL` is enabled, declares `f2fs_get_acl()`, `f2fs_set_acl()`, and `f2fs_init_acl()`. Otherwise get/set are `NULL` and init is a no-op.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/checkpoint.c -->
# File Research: sources/os/linux/linux/fs/f2fs/checkpoint.c

## Purpose
Implements F2FS checkpoint coordination, metadata page IO, checkpoint pack validation/writing, orphan inode tracking/recovery, dirty inode synchronization, checkpoint request merging, and checkpoint-thread lifecycle.

## Main Responsibilities
- Wraps F2FS rwsem operations with optional priority uplift and lock latency tracing.
- Reads, writes, dirties, validates, and readaheads metadata folios.
- Validates block addresses against metadata/data regions and SIT bitmaps.
- Tracks inode sets for orphan, append, update, transition-directory, and flush state using radix trees and lists.
- Recovers orphan inodes at mount and writes orphan lists during checkpoints.
- Selects valid checkpoint packs by CRC and version.
- Freezes filesystem operations for checkpoint, flushes dirty dentry/node/inode metadata, writes NAT/SIT/summary/checkpoint data, and commits the final checkpoint page with flush semantics.
- Supports asynchronous merged checkpoint requests through a kernel thread.

## Key Functions and Flows
- Metadata IO: `f2fs_grab_meta_folio()`, `f2fs_get_meta_folio()`, `f2fs_ra_meta_pages()`, `f2fs_sync_meta_pages()`, and `f2fs_meta_aops`.
- Address validation: `f2fs_is_valid_blkaddr()` and raw variant enforce legal ranges for NAT/SIT/SSA/CP/POR/data/meta access.
- Orphans: `f2fs_acquire_orphan_inode()`, `f2fs_add_orphan_inode()`, `f2fs_recover_orphan_inodes()`, and `write_orphan_inodes()`.
- Checkpoint loading: `validate_checkpoint()` checks first/last CP block versions and CRC, while `f2fs_get_valid_checkpoint()` chooses the newest valid pack.
- Dirty inode sync: `f2fs_update_dirty_folio()`, `f2fs_sync_dirty_inodes()`, and `f2fs_sync_inode_meta()`.
- Checkpoint write: `f2fs_write_checkpoint()` locks global checkpoint state, blocks filesystem operations, flushes NAT/SIT, then calls `do_checkpoint()`.
- Commit: `do_checkpoint()` updates checkpoint fields, writes bitmaps, checkpoint payload, orphan blocks, summaries, flushes metadata, flushes devices, commits the final CP page, and flips current CP pack.
- Async checkpoints: `f2fs_issue_checkpoint()`, `issue_checkpoint_thread()`, and related request-control helpers merge synchronous checkpoint requests when configured.

## Concurrency and Recovery Notes
- `cp_rwsem`, `cp_global_sem`, `node_change`, `node_write`, and `gc_lock` enforce checkpoint ordering.
- `block_operations()` loops until quotas, dirty dentries, inode metadata, and dirty node pages are quiesced.
- Checkpoint errors cause early `-EIO`, stop checkpointing, and may mark `SBI_NEED_FSCK`.
- `commit_checkpoint()` writes the last checkpoint block with `META_FLUSH`, making it the atomic commit point for the pack.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/checkpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/compress.c -->
# File Research: sources/os/linux/linux/fs/f2fs/compress.c

## Purpose
Implements F2FS compression and decompression support, including backend dispatch, cluster compression, compressed writeback, compressed read completion, overwrite/truncate handling, cache support, and slab/mempool lifecycle.

## Main Responsibilities
- Provides backend abstraction through `struct f2fs_compress_ops`.
- Supports LZO, LZO-RLE, LZ4/LZ4HC, and ZSTD depending on Kconfig.
- Allocates intermediate compressed pages from a mempool and per-mount page-array slabs.
- Compresses full clusters and writes them as `COMPRESS_ADDR` header plus compressed data blocks.
- Decompresses read clusters, verifies optional compression checksums, and integrates with fsverity.
- Falls back to raw page writeback when compression is unsuitable or not beneficial.
- Maintains optional compressed-page cache through a special compress inode mapping.

## Key Functions and Flows
- Context setup: `f2fs_init_compress_ctx()`, `f2fs_destroy_compress_ctx()`, and `f2fs_compress_ctx_add_page()`.
- Backend readiness and levels: `f2fs_is_compress_backend_ready()` and `f2fs_is_compress_level_valid()`.
- Compression: `f2fs_compress_pages()` vmaps raw and compressed pages, calls backend compression, writes header/checksum/reserved fields, zeroes tail bytes, and trims unused cpages.
- Writeback: `f2fs_write_multi_pages()` tries compression for eligible full clusters, otherwise falls back to `f2fs_write_raw_pages()`.
- Compressed write: `f2fs_write_compressed_pages()` updates node block addresses, invalidates replaced blocks, handles encryption bounce pages, submits out-of-place writes, updates compressed-block accounting, and completes via `f2fs_compress_write_end_io()`.
- Decompression: `f2fs_alloc_dic()` prepares decompress context and pages; `f2fs_end_read_compressed_page()` triggers `f2fs_decompress_cluster()` after all compressed pages complete; `f2fs_decompress_end_io()` marks/unlocks output pages or schedules fsverity verification.
- Overwrite/truncate: `f2fs_prepare_compress_overwrite()` reads and locks an existing compressed cluster before modification; `f2fs_truncate_partial_cluster()` zeroes partial cluster tails and rewrites safely.
- Cache: `f2fs_cache_compressed_page()`, `f2fs_load_compressed_folio()`, and invalidation helpers cache compressed disk pages by block address when `COMPRESS_CACHE` is enabled.

## Edge Cases
- Compression is skipped for atomic files, incomplete clusters, invalid data beyond EOF, checkpoint-error filesystems, and low-benefit results.
- Decompression checks compressed length bounds and optional checksum; checksum mismatch marks the inode corrupt and sets `SBI_NEED_FSCK`.
- fsverity verification is moved to the fsverity workqueue to avoid decompression workqueue deadlocks.
- Quota inode compressed writeback uses `node_write` locking to avoid checkpoint allocation races.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/compress.c -->