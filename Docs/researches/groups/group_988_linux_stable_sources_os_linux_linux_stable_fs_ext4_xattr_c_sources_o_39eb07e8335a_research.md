# Group Research: group_988_linux_stable_sources_os_linux_linux_stable_fs_ext4_xattr_c_sources_o_39eb07e8335a

Scope verified against `Docs/research_subset_a.md`: the files belong to included tree `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/xattr.c

## Purpose
Implements ext4 extended attribute storage, lookup, listing, mutation, sharing, validation, and teardown. It supports in-inode xattrs, one external xattr block per inode, shared identical xattr blocks via mbcache, and large xattr values stored in special EA inodes.

## Main Components
- Xattr handler maps connect ext4 namespace indexes to VFS xattr handlers for `user`, `trusted`, POSIX ACL, `security`, and `hurd`.
- `check_xattrs()` validates both external xattr blocks and in-inode xattr regions: magic, block count, metadata checksum, entry bounds, name length, value bounds, EA-inode references, and maximum value size.
- `ext4_xattr_get()` first checks the inode body, then the external block, under `EXT4_I(inode)->xattr_sem`.
- `ext4_listxattr()` lists in-inode names first and then block names, filtering by namespace visibility through xattr handler permissions.
- Mutation flows through `ext4_xattr_set_handle()`, which reserves inode write access, enforces `XATTR_CREATE`/`XATTR_REPLACE`, tries ibody storage first, falls back to xattr block storage, and may use EA inode storage for large values.
- External block mutation in `ext4_xattr_block_set()` handles in-place updates for exclusive blocks, clone-on-write for shared blocks, reuse of identical cached blocks, allocation of new metadata blocks, checksum updates, and release of replaced blocks.
- `ext4_xattr_set_entry()` performs the low-level packed-entry/value layout edits, including value compaction, entry insertion/removal, hash recalculation, and EA-inode reference release.
- Large EA inode support includes hash/refcount encoding, cache lookup, creation, quota charging, read/write, refcount increment/decrement, orphan transitions, and Lustre legacy compatibility.
- Inode extra-isize expansion can move selected xattrs from ibody to external blocks and shift xattr entries to make room.
- Delete/evict paths release xattr blocks, decrement EA-inode references, free quota, clear `i_file_acl`, and defer `iput()` through `ext4_xattr_inode_array`.

## Important Behaviors
- External xattr block checksums use filesystem checksum seed plus disk block number and header contents with the checksum field zeroed.
- Shared xattr blocks are protected by buffer locks and mbcache reusable flags; blocks at `EXT4_XATTR_REFCOUNT_MAX` are not reusable.
- EA inode values are protected by CRC/hash verification; the code also accepts and warns about an older signed-char name hash variant.
- Journal credit estimation accounts for owner inode updates, old/new xattr blocks, quota updates, inline-data expansion, EA inode creation/deletion, data blocks, and reference updates.
- Fast commit is marked ineligible for xattr mutations.
- Quota accounting charges the parent inode for shared EA inode storage, while EA inodes themselves are marked `S_NOQUOTA`.

## Dependencies
Uses ext4 journaling, quota, mbcache, inode allocation, block mapping, orphan handling, fast commit state, inline-data helpers, POSIX ACL handler stubs, and metadata checksum helpers.

## Research Notes
This is a high-risk metadata file. Key invariants are packed xattr layout bounds, xattr block refcounts, EA-inode refcounts, quota symmetry, checksum/hash correctness, and transaction credit sufficiency.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/xattr.h

## Purpose
Defines ext4 on-disk extended attribute structures, constants, layout macros, namespace indexes, search helper structs, lock helpers, and exported xattr APIs.

## Main Components
- On-disk structures: `ext4_xattr_header`, `ext4_xattr_ibody_header`, and `ext4_xattr_entry`.
- Namespace indexes include user, POSIX ACL access/default, trusted, Lustre, security, system, richacl, encryption, and Hurd.
- Layout macros compute padded entry/value sizes and locate first/next entries in ibody or block storage.
- `EXT4_XATTR_SIZE_MAX` is a consistency-check ceiling larger than current `XATTR_SIZE_MAX` to avoid overflow-sensitive checks.
- `EXT4_XATTR_MIN_LARGE_EA_SIZE()` defines when external EA inode storage becomes worthwhile.
- Search and mutation carrier structs include `ext4_xattr_info`, `ext4_xattr_search`, `ext4_xattr_ibody_find`, and `ext4_xattr_inode_array`.
- Write lock helpers wrap `xattr_sem` and temporarily set `EXT4_STATE_NO_EXPAND` to avoid recursive inode expansion.

## Exported Interfaces
Declares get/set/list operations, credit estimation, ibody find/get/set helpers, inode delete/free routines, EA inode eviction, cache creation/destruction, security initialization, lockdep class setup, and inode usage accounting.

## Research Notes
This header is the contract for ext4 xattr layout. Any format or macro change has direct disk-format implications.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr_hurd.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/xattr_hurd.c

## Purpose
Provides the ext4 VFS xattr handler for the GNU/Hurd xattr namespace.

## Main Components
- `ext4_xattr_hurd_list()` exposes Hurd attributes only when the mount has `XATTR_USER`.
- Get/set operations reject unsupported mounts with `-EOPNOTSUPP`.
- Successful operations delegate to `ext4_xattr_get()` and `ext4_xattr_set()` with `EXT4_XATTR_INDEX_HURD`.

## Exported Interface
Defines `ext4_xattr_hurd_handler` with `XATTR_HURD_PREFIX`, list, get, and set callbacks.

## Research Notes
This is a thin namespace adapter; policy is mount-option gated and storage semantics are centralized in `xattr.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr_hurd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr_security.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/xattr_security.c

## Purpose
Provides ext4 handling for `security.*` extended attributes and LSM initialization labels.

## Main Components
- Get/set delegate directly to `ext4_xattr_get()` and `ext4_xattr_set()` with `EXT4_XATTR_INDEX_SECURITY`.
- `ext4_initxattrs()` iterates LSM-provided xattrs and writes each with `ext4_xattr_set_handle()` using `XATTR_CREATE`.
- `ext4_init_security()` calls `security_inode_init_security()` with the ext4 setter callback and active journal handle.

## Exported Interface
Defines `ext4_xattr_security_handler` and `ext4_init_security()` when `CONFIG_EXT4_FS_SECURITY` is enabled.

## Research Notes
Security label initialization is journal-handle aware, so new-inode label writes participate in the caller’s ext4 transaction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr_trusted.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/xattr_trusted.c

## Purpose
Provides ext4 handling for `trusted.*` extended attributes.

## Main Components
- Listing is restricted to callers with `CAP_SYS_ADMIN`.
- Get/set delegate to core ext4 xattr functions with `EXT4_XATTR_INDEX_TRUSTED`.

## Exported Interface
Defines `ext4_xattr_trusted_handler` with `XATTR_TRUSTED_PREFIX`.

## Research Notes
Capability-based visibility is handled at the namespace adapter layer; storage is shared with the rest of ext4 xattrs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr_trusted.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr_user.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/xattr_user.c

## Purpose
Provides ext4 handling for `user.*` extended attributes.

## Main Components
- Listing, get, and set are gated by the `XATTR_USER` mount option.
- Unsupported mounts return `-EOPNOTSUPP`.
- Storage operations delegate to `ext4_xattr_get()` and `ext4_xattr_set()` with `EXT4_XATTR_INDEX_USER`.

## Exported Interface
Defines `ext4_xattr_user_handler` with `XATTR_USER_PREFIX`.

## Research Notes
This file is a policy shim for user namespace availability; all layout and journaling behavior lives in `xattr.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/xattr_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/Kconfig

## Purpose
Defines kernel configuration options for F2FS filesystem support and optional features.

## Main Components
- `F2FS_FS` is a tristate depending on `BLOCK`; it selects buffer heads, NLS, CRC32, iomap, and crypto/compression helpers as needed.
- `F2FS_STAT_FS` enables debugfs status reporting.
- `F2FS_FS_XATTR`, `F2FS_FS_POSIX_ACL`, and `F2FS_FS_SECURITY` control xattrs, ACLs, and LSM label support.
- `F2FS_CHECK_FS` enables runtime consistency BUG_ON checks.
- `F2FS_FAULT_INJECTION` enables fault injection paths.
- `F2FS_FS_COMPRESSION` enables file compression, with selectable LZO, LZO-RLE, LZ4, LZ4HC, and ZSTD backends.
- `F2FS_IOSTAT` enables IO statistics through sysfs and tracepoints.
- `F2FS_UNFAIR_RWSEM` enables unfair rwsem behavior when block cgroup IO priority is configured.

## Research Notes
Compression algorithm options select the corresponding kernel compression/decompression libraries. POSIX ACL depends on xattr support and selects `FS_POSIX_ACL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/Makefile

## Purpose
Defines F2FS object composition for the kernel build.

## Main Components
- Builds `f2fs.o` when `CONFIG_F2FS_FS` is enabled.
- Core objects include directory, file, inode, name lookup, hashing, superblock, inline data, checkpoint, GC, data, node, segment, recovery, shrinker, extent cache, and sysfs support.
- Optional objects are added for stats/debug, xattrs, POSIX ACLs, fs-verity, compression, and IO statistics.

## Research Notes
This file shows that `checkpoint.o` is core F2FS, while `acl.o` and `compress.o` are conditional feature objects.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/acl.c

## Purpose
Implements F2FS POSIX ACL serialization, deserialization, get/set operations, permission-mode updates, ACL inheritance, and new-inode ACL initialization.

## Main Components
- `f2fs_acl_size()` and `f2fs_acl_count()` encode/decode the compact on-disk ACL format where the first four standard entries omit an ID field.
- `f2fs_acl_from_disk()` validates version and entry layout, converts little-endian tags/perms/ids into `struct posix_acl`, and rejects malformed sizes or tags.
- `f2fs_acl_to_disk()` serializes `struct posix_acl` back to F2FS xattr format.
- `__f2fs_get_acl()` reads ACL xattrs with indexes `F2FS_XATTR_INDEX_POSIX_ACL_ACCESS` or `DEFAULT`.
- `f2fs_set_acl()` rejects checkpoint-error filesystems with `-EIO`, then writes ACL xattrs through `f2fs_setxattr()`.
- Access ACL updates call `posix_acl_equiv_mode()` and update inode mode, including setgid clearing when the caller lacks group/capability authority.
- ACL create helpers clone and mask parent default ACLs for new inodes, applying `current_umask()` when no default ACL exists.
- `f2fs_init_acl()` writes inherited default/access ACLs during inode creation and marks inode metadata dirty.

## Dependencies
Depends on F2FS xattr helpers, inode dirtying, POSIX ACL core helpers, idmapped mount checks, and F2FS checkpoint error state.

## Research Notes
Malformed on-disk ACL data returns `-EINVAL`. The create path mirrors generic POSIX ACL logic but is local so it can pass F2FS folios into xattr operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/acl.h

## Purpose
Declares F2FS ACL on-disk structures and ACL operation prototypes.

## Main Components
- `F2FS_ACL_VERSION` is the on-disk ACL version.
- `f2fs_acl_header` stores the version.
- `f2fs_acl_entry_short` stores tag and permission for entries without an ID.
- `f2fs_acl_entry` adds a 32-bit ID for named user/group entries.
- When `CONFIG_F2FS_FS_POSIX_ACL` is enabled, prototypes are provided for get, set, and init operations.
- When disabled, ACL get/set hooks become `NULL` and `f2fs_init_acl()` is a no-op returning success.

## Research Notes
The header defines the disk ABI for F2FS ACL xattr payloads.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/checkpoint.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/checkpoint.c

## Purpose
Implements F2FS checkpoint coordination, metadata-page IO, block-address validation, dirty/orphan inode tracking, checkpoint pack validation/writing, operation freezing, and asynchronous checkpoint request merging.

## Main Components
- Lock wrappers trace elapsed lock time and can temporarily uplift task priority for selected F2FS rwsems.
- Meta folio helpers read, grab, retry, dirty, write, and readahead metadata pages through `META_MAPPING`.
- Block-address validation checks metadata and data address ranges, SIT bitmap consistency, checkpoint error state, and marks `SBI_NEED_FSCK` on serious inconsistencies.
- Inode-entry management tracks append/update/transition/orphan/flush inode sets with radix trees, lists, and slab cache entries.
- Orphan handling reserves orphan slots, writes orphan blocks into checkpoint packs, and recovers orphan inodes during mount by truncating unlinked files.
- Checkpoint validation reads both checkpoint packs, checks CRC offsets and CRC values, compares versions, and selects the newest valid pack.
- Dirty inode sync flushes dirty directory/file data and inode metadata until checkpoint can proceed.
- `block_operations()` freezes filesystem-changing operations, flushes quota, dentry, inode metadata, and node pages, and prepares checkpoint counts.
- `do_checkpoint()` writes NAT/SIT metadata, checkpoint payload, orphan blocks, summaries, optional NAT bits, checksum, device cache flush, final checkpoint page, and cleanup state.
- `f2fs_write_checkpoint()` coordinates global checkpoint locking, dirty checks, disabled checkpoint handling, NAT/SIT flushes, in-memory current segment save/restore, discard handling, timing stats, and checkpoint error propagation.
- Async checkpoint support queues requests on an llist, services them from `f2fs_ckpt-*` kthread, completes waiters, and tracks latency stats.
- Slab caches are created for inode/orphan tracking entries.

## Important Behaviors
- Checkpoint packs are double-buffered and selected by valid CRC plus newest version.
- The checkpoint writer avoids racing with node updates by holding `cp_rwsem`, `node_change`, and `node_write` in staged order.
- Quota flushing is retried and can set flags requiring later fsck when it cannot be flushed safely.
- Long checkpoint latency is recorded and rate-limited warnings include phase timings.
- Merged checkpoint mode coalesces synchronous checkpoint requests unless disabled by mount/current context.

## Dependencies
Uses F2FS node, segment, iostat, quota, discard, NAT/SIT, summary, writeback, folio, kthread, block-device cache flush, and tracepoint infrastructure.

## Research Notes
This file is central to F2FS crash consistency. Critical invariants include checkpoint pack CRC/version validity, dirty metadata drain ordering, orphan count capacity, NAT/SIT flush completion, and correct lock ordering around operation freeze/unfreeze.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/checkpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/compress.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/compress.c

## Purpose
Implements F2FS per-file compression support, including backend algorithm adapters, compression/decompression memory management, compressed-cluster writeback, compressed read completion, overwrite/truncate handling, compressed-page cache, and cache/slab initialization.

## Main Components
- `f2fs_compress_ops` abstracts backend init/destroy/compress/decompress/level validation.
- Supported conditional backends are LZO, LZ4/LZ4HC, ZSTD, and LZO-RLE.
- Page-array allocation uses a per-superblock slab for common cluster sizes and heap allocation for larger arrays.
- A mempool preallocates intermediate compressed pages, controlled by `num_compress_pages`.
- `f2fs_compress_pages()` vmaps raw cluster pages and compressed output pages, runs the backend, writes the compression header/checksum, zeros unused tail bytes, and drops unused compressed pages.
- `f2fs_decompress_cluster()` prepares decompression memory, validates compressed length, runs backend decompression, verifies optional checksum, marks corruption/fsck-needed state, and completes read IO.
- Cluster helpers compute cluster indexes, validate compressed cluster layout, count compressed/raw blocks, and decide when a cluster may be compressed.
- Overwrite handling reads and locks a full compressed cluster before partial modification so compressed data can be rewritten coherently.
- Partial truncate of a compressed cluster expands it through overwrite preparation, zeroes the truncated range, writes it back, updates page cache, and truncates block mappings.
- `f2fs_write_compressed_pages()` writes compressed output blocks out-of-place, updates node block addresses with `COMPRESS_ADDR` and `NEW_ADDR`, manages encryption bounce pages, compressed IO context, writeback state, dirty-page counts, and compressed block accounting.
- `f2fs_write_raw_pages()` is the fallback path for uncompressible clusters or raw overwrite of compressed clusters.
- Decompression contexts (`decompress_io_ctx`) hold raw pages, compressed pages, optional temporary pages, vmap buffers, refcounts, fs-verity state, and deferred free work.
- Read completion caches compressed pages when `COMPRESS_CACHE` is enabled and memory thresholds allow it.
- Compress cache uses a special `compress_inode` mapping keyed by physical block address and tagged with source inode number for invalidation.
- Init/destroy routines create CIC/DIC slab caches, per-superblock page-array cache, compression mempool, and optional compress inode.

## Important Behaviors
- Compression only proceeds for full, valid, non-atomic clusters when compression is needed and checkpoint state is healthy.
- Compression must save at least one page plus header space; otherwise it returns `-EAGAIN` and falls back to raw writes.
- Checksum mismatch marks the inode `FI_COMPRESS_CORRUPT` and sets `SBI_NEED_FSCK`.
- fs-verity verification is deferred to the fs-verity workqueue to avoid deadlocks with compressed metadata reads.
- Writeback completion waits for all compressed pages before ending writeback on the original raw cluster pages.

## Dependencies
Uses F2FS data/node/segment write paths, fscrypt, fsverity, folios, mempool, vm_map_ram, LZO/LZ4/ZSTD libraries, tracepoints, and F2FS mount/memory options.

## Research Notes
This file coordinates several fragile lifetimes: raw page locks, compressed mempool pages, encryption bounce pages, CIC/DIC contexts, and cached compressed folios. Error paths deliberately fall back to raw writes or defer cleanup to avoid IO-context deadlocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/compress.c -->