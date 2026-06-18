<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/inode.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/inode.c

## Purpose

`inode.c` loads, validates, updates, writes, evicts, and cleans up F2FS inodes. It translates on-disk `struct f2fs_inode` fields into in-memory Linux inode and `struct f2fs_inode_info` state, assigns inode operation tables, verifies feature-dependent metadata, computes inode checksums, serializes inode state back to node pages, handles final deletion/truncation, and repairs bookkeeping after failed inode creation.

## Important APIs, Types, and Functions

- `f2fs_mark_inode_dirty_sync()` marks an inode dirty unless it is new, read-only, already dirtied, or an uncommitted atomic file.
- `f2fs_set_inode_flags()` maps F2FS flags and encryption/verity/casefold state to VFS inode flags.
- `__get_inode_rdev()` and `__set_inode_rdev()` decode/encode special device numbers in inline address slots.
- `__recover_inline_status()` restores inline data flags if inline bytes exist but in-memory state says no data exists.
- `f2fs_enable_inode_chksum()`, `f2fs_inode_chksum()`, `f2fs_inode_chksum_verify()`, and `f2fs_inode_chksum_set()` implement optional inode checksums over inode number, generation, and inode payload with the checksum field zeroed.
- `sanity_check_compress_inode()` validates compression algorithm, compressed-block count, cluster size, and compression level against configured backend support.
- `sanity_check_inode()` validates block count, inode footer identity, xattr nid, directory link count, extra attr sizing, feature flag consistency, inline data/dentry validity, casefold support, device alias invariants, and xattr nid range.
- `do_read_inode()` hydrates in-memory inode fields from the inode node page and initializes extent trees, timestamps, project quota, compression fields, inline stats, and disk-time snapshots.
- `f2fs_iget()` and `f2fs_iget_retry()` instantiate inodes and assign operation/address-space methods for meta, node, compression, regular, directory, symlink, and special inodes.
- `f2fs_update_inode()` serializes in-memory inode state back into the inode node folio.
- `f2fs_update_inode_page()` fetches the inode folio with retry/stop-checkpoint behavior and calls `f2fs_update_inode()`.
- `f2fs_write_inode()` is the VFS writeback hook for inode metadata.
- `f2fs_remove_donate_inode()`, `f2fs_evict_inode()`, and `f2fs_handle_failed_inode()` clean up donate lists, truncate/delete final inodes, maintain orphan/NID state, and handle failed new inode creation.

## Control Flow and State Behavior

`f2fs_iget()` first uses `iget_locked()`. Existing non-new metadata inodes are treated as corruption if externally requested; existing normal inodes are returned. New normal inodes are read with `do_read_inode()`, while metadata inodes skip disk hydration and receive special address-space operations. Operation tables are selected by mode: regular files use `f2fs_file_inode_operations`, `f2fs_file_operations`, and `f2fs_dblock_aops`; directories use directory ops; encrypted symlinks get encrypted symlink ops; special files use `init_special_inode()`.

`do_read_inode()` reads the inode node folio, converts all scalar fields from little-endian disk form, resets F2FS in-memory flags, loads inline info, computes inline xattr reservation compatibility, runs sanity checks, recovers inline existence if needed, repairs cold-node status for non-directories, decodes `i_rdev`, initializes project id and creation time extra attributes, loads compression fields and sets `FI_COMPRESSED_FILE`, snapshots disk timestamps, validates extent-cache state, and initializes read and age extent trees.

`f2fs_update_inode()` waits for node writeback, dirties the node folio, marks the inode synced, writes mode, ownership, links, block count, size except for uncommitted atomic files, largest read extent, inline flags, timestamps, directory depth or GC failure count, xattr nid, F2FS flags, parent ino, generation, dir level, extra attributes, project id, creation time, compression fields, and special-device encoding. Deleted inodes clear inline state. With check-fs enabled, it updates the inode checksum.

`f2fs_write_inode()` skips node/meta inodes, ignores pure lazytime updates when the inode is otherwise clean, returns errors for checkpoint failure or checkpoint-not-ready states, updates the inode page, and balances the filesystem when writeback requests actual writing. `f2fs_update_inode_page()` retries inode folio fetches for transient memory or I/O issues and stops checkpointing if it cannot safely update metadata.

`f2fs_evict_inode()` aborts atomic writes, drops COW inode links, truncates page cache, invalidates compression cache for live/bad compressed inodes, skips deletion for meta inodes, removes dirty/donate/extent state, and for unlinked inodes initializes quota, removes recovery ino entries, protects against freeze, sets `FI_NO_ALLOC`, truncates data blocks, removes the inode node page under `f2fs_lock_op()`, retries on `-ENOMEM`, and updates or flags repair state on failure. It drops quotas and stats, verifies dirty state when safe, removes the inode from dirty metadata lists, invalidates node mapping pages, re-adds recovery entries for still-linked append/update writes, returns failed free NIDs, releases fscrypt info, and clears the VFS inode.

Failed new inode handling clears nlink, updates and syncs the inode page, unlocks the new inode without marking it bad, acquires or records orphan inode state before unlocking the filesystem operation, finalizes or frees the nid based on NAT block address, and drops the inode with `iput()`.

## Persistence, Locking, and Integration Points

Inode persistence is through F2FS node pages in `NODE_MAPPING`, on-disk inode extra attributes, inline areas, extent fields, checksum fields, NAT block addresses, orphan tracking, quota state, and recovery ino lists. The file integrates with `file.c`, `dir.c`, symlink operations, node and segment managers, xattrs, compression address-space operations, fscrypt, fsverity, quota, checkpointing, extent caches, and error handling. Locking includes node folio locks/writeback waits, `f2fs_lock_op()` for inode-page removal and failed inode orphan registration, `sb_start_intwrite()` during eviction, and internal inode/donate locks.

## Risks and Edge Cases

The most sensitive areas are accepting corrupted on-disk inode fields, preserving compatibility for extra attributes and inline xattr sizing, keeping atomic-write inode size semantics correct, avoiding dirty-inode assertions during failed eviction, and not losing orphan inode records after failed creation. Feature flags must agree with superblock features, compression settings must match compiled backend support, device aliasing requires pinned files, and inline data/dentry combinations must be mode-appropriate. Eviction has many partial-failure paths that intentionally set `SBI_NEED_FSCK` or quota repair flags.

## Test Signals

Tests should cover inode checksum verification/set, malformed inode footers/block counts/xattr nids, feature-flag mismatch images, compression option validation across algorithms and levels, inline status recovery, regular/dir/symlink/special inode operation assignment, project quota and crtime extra attributes, lazytime writeback, checkpoint-error write_inode behavior, eviction of linked, unlinked, bad, compressed, atomic, COW, and device-aliasing inodes, orphan handling after failed inode creation, and fault injection for truncate/remove inode page failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/inode.c -->
