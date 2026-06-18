# Group Research: group_991_linux_stable_sources_os_linux_linux_stable_fs_f2fs_file_c_sources_os_3c373ae23d46

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/file.c

`file.c` implements the main F2FS regular-file VFS surface. It provides file operations, file inode operations, mmap fault handling, fsync, llseek with `SEEK_DATA`/`SEEK_HOLE`, open/release/flush, setattr/getattr, fallocate modes, many F2FS ioctls, and direct/buffered read-write iterators.

The mmap path wraps generic filemap faults for iostat accounting and implements `page_mkwrite` with F2FS-specific checks: checkpoint/error state, compression release state, inline-data conversion, large-folio write rejection, block allocation or pinned-file validation, writeback waits, GC writeback waits, EOF zeroing, dirtying, and mapped-write accounting.

Fsync is centered on `f2fs_do_sync_file()`. It first writes data, then decides whether roll-forward recovery metadata is enough or whether a full checkpoint is required. Checkpoint reasons include non-regular files, compressed files, hardlinks, wrong parent inode, insufficient roll-forward space, dirty parent/dentry/xattr state, strict fsync recovery needs, fastboot mode, and active-log layout. When no checkpoint is needed it writes fsync node chains, waits on node writeback unless atomic ordering is used, and issues flushes unless barriers are disabled.

Truncation and hole manipulation operate directly on dnodes and data block addresses. `f2fs_truncate_data_blocks_range()` clears block addresses, invalidates contiguous physical runs, updates compressed-cluster accounting, read/age extent caches, valid block counts, and request time. Higher-level truncate paths handle inline-data truncation, device-alias extents, compressed cluster alignment, partial-page zeroing, and VFS page-cache invalidation.

The fallocate implementation supports punch hole, collapse range, zero range, insert range, and preallocation. Collapse/insert/move-range paths use `__exchange_data_block()` and helpers that read block address arrays, decide whether checkpointed blocks must be copied through page cache versus replaced directly, roll back on failure, and keep i_size consistent. Preallocation handles normal and pinned files differently; pinned files allocate whole pinned sections and may trigger foreground GC to reserve contiguous sections.

The file-attribute path maps between F2FS inode flags and common FS flags, supports project quota transfer, exposes statx birth time and DIO alignment, and enforces restrictions around immutable/append-only files, casefold, compression, pinned files, released compressed blocks, and device-alias files.

The ioctl dispatcher covers atomic write start/commit/abort with COW tmpfile inodes, shutdown modes, FITRIM, fscrypt policy/key operations, manual GC and GC range, checkpoint write, defragmentation, move range, flush device, feature query, pin-file controls, device-alias query, I/O priority hints, extent precache, filesystem resize, fs-verity, volume labels, compression block release/reserve/query, secure file trim, compression options, and user-triggered compress/decompress of whole files.

Read/write iterators choose between direct I/O and buffered I/O through `f2fs_should_use_dio()`. Direct I/O is forced off for unsupported encryption, verity, compression, inline reads, multi-device alignment gaps, checkpoint-disabled state, and most zoned-device writes. Writes perform generic checks, EOF zeroing, optional block preallocation, inline conversion, atomic/pinned-file restrictions, iomap DIO with F2FS counters, buffered fallback for partial DIO, O_DIRECT page-cache flushing, and truncation of unused preallocated blocks past i_size.

Important dependencies are `data.c` for mapping/I/O/writeback helpers, `node.c` for dnode and inode-page access, `segment.c` and `gc.c` for allocation/GC, `inline.c`, compression helpers, extent cache, fscrypt, fsverity, quotas, checkpoint/recovery state, and trace/iostat code. The key invariants are block-address validation before mutation or I/O, correct lock ordering around inode locks, `i_gc_rwsem`, `filemap_invalidate_lock`, and `lock_op`, preserving recovery ordering for fsync and atomic writes, and keeping compressed, pinned, device-alias, and inline-data modes from entering unsupported mutation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/gc.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/gc.c

`gc.c` implements F2FS garbage collection, victim selection, background GC threading, block migration, pinned-section handling, GC range execution, and online filesystem shrink support.

The background GC thread sleeps adaptively, wakes for ordinary background GC, urgent modes, zoned-device pressure, and `GC_MERGE` foreground waiters. It skips readonly/frozen/busy filesystems, checks IO idleness, adjusts sleep time based on pressure, chooses sync or async GC, invokes `f2fs_gc()`, wakes foreground waiters, and periodically calls background filesystem balancing.

Victim selection supports greedy, cost-benefit, age-threshold GC, SSR, and age-threshold SSR. `select_policy()` chooses dirty bitmaps, search windows, offsets, and policy based on GC type, allocation mode, large-section layout, urgent/idle GC mode, and random-segment policy. `f2fs_get_victim()` scans dirty segments or sections, skips current/in-use/pinned/invalid candidates, honors checkpoint-disabled constraints, remembers background victims, tracks last victim offsets, and records foreground victim sections.

Age-threshold GC builds a temporary rb-tree of `victim_entry` objects keyed by section mtime. ATGC chooses among older candidate sections using a weighted age/free-space cost, while AT-SSR searches around an age target and prefers low checkpoint-valid block counts. The file owns the `f2fs_victim_entry` slab cache for these temporary candidates.

Pinned-file handling prevents GC from freely moving pinned file blocks. Foreground GC can pin whole sections and retry later; repeated failure increments the inode’s GC failure count through `f2fs_pin_file_control()`. Foreground GC can unpin all sections and retry if no normal victim remains.

Node GC validates the SIT valid map, readaheads NAT and node pages in phases, compares summary entries with NAT node info, and moves live node folios with cold status. Data GC is also phased: it readaheads NAT and node pages, validates summary version and parent-node block addresses with `is_alive()`, reads data pages or meta-inode GC cache pages, records referenced inodes in a radix/list cache, waits against regular-file GC semaphores and DIO, then migrates blocks through `move_data_page()` or `move_data_block()`.

`move_data_page()` handles normal data migration by dirtying pages for background GC or synchronously writing them for foreground GC. `move_data_block()` handles meta-inode-required migration by reading the old block through `META_MAPPING`, allocating a new block, copying encrypted/raw contents, submitting a sync write, updating the dnode block address, and rolling back allocation if the update fails.

`do_garbage_collect()` processes one section or a migration window, loads summary blocks, verifies summary/SIT type consistency, skips current segments, invokes node or data GC per segment, submits merged writes, tracks migrated/reclaimed segments, and records next-victim state for large sections and zoned devices. `f2fs_gc()` wraps this in the full reclaim loop, escalating to foreground GC when free sections are low, checkpointing prefree segments when useful, retrying around skipped inode locks, reclaiming until requested free sections are available, and returning `-EAGAIN` when requested GC made no section progress.

The resize path uses GC to evacuate the tail of the main area before shrinking. `f2fs_resize_fs()` validates section alignment, multi-device limits, fsck/checkpoint state, free-space feasibility, locks out GC/checkpoint races, dry-runs evacuation, freezes the superblock, evacuates for real, updates superblock and in-memory metadata, commits the superblock, checkpoints, and marks `SBI_NEED_FSCK` on unrecoverable resize failure.

Important dependencies are SIT/dirty/free segment maps, summary blocks, NAT/node lookup, data writeback, inode lookup, checkpointing, segment allocation, extent/page cache helpers, zoned-device geometry, and F2FS trace/stat counters. The central invariants are never migrating stale summary entries, never GCing current sections, respecting pinned files and checkpoint-disabled constraints, preserving lock ordering around `gc_lock`, `sentry_lock`, inode GC semaphores, and summary pages, and keeping resize metadata updates recoverable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/gc.h -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/gc.h

`gc.h` defines F2FS garbage-collection tuning constants, GC thread state, victim-entry data structures, and inline free-space/pressure helpers used by `gc.c` and allocation policy.

The constants define default background GC sleep times, urgent sleep time, zoned-device sleep times, age-threshold GC parameters, invalid/free block pressure limits, zoned GC boost thresholds, migration window defaults, pinned-file GC failure limits, victim search limit, and the extra checkpoint sections required during GC pressure.

`struct f2fs_gc_kthread` stores the background GC task, wait queues, sleep-time knobs, urgent wake flag, foreground-GC merge wait queue, zoned GC thresholds, one-time GC valid-block threshold, and boost controls. `struct gc_inode_list` is a temporary radix-tree/list cache of inodes referenced during data GC. `struct victim_entry` is the rb-tree/list node used by age-threshold victim selection.

The free-space helpers account for zoned-device zone capacity. `free_segs_blk_count_zoned()` sums usable blocks in currently free segments instead of assuming all segments have full segment capacity. `free_user_blocks()` subtracts overprovisioned blocks, and the limit helpers compute invalid/free thresholds as percentages of user or reclaimable blocks.

Sleep helpers increase or decrease background GC wait time within configured bounds, with special handling for the no-GC sleep interval. `has_enough_free_blocks()`, `has_enough_invalid_blocks()`, and `need_to_boost_gc()` provide the pressure signals that decide whether background GC should run more aggressively, with zoned devices using free-section percentage rather than invalid-block ratio.

This header is small but policy-critical: changing the constants affects GC latency, write amplification, zoned-device behavior, and when pinned files are eventually unpinned or rejected.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/hash.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/hash.c

`hash.c` computes F2FS directory-entry name hashes. It uses the ext3-derived TEA hash for ordinary byte-string names and fscrypt SipHash for encrypted casefolded plaintext names.

`TEA_transform()` and `str2hashbuf()` implement the legacy TEA block transform and filename block packing. `TEA_hash_name()` initializes the fixed hash seed, hashes the name in 16-byte chunks, and clears `F2FS_HASH_COL_BIT` from the returned hash.

`f2fs_hash_filename()` is the exported entry point. It requires `fname->disk_name`, returns hash zero for `.` and `..`, and normally hashes the on-disk name. For casefolded directories it prefers the normalized casefolded name; if the name is not valid Unicode it falls back to the user plaintext name. For encrypted casefolded directories it hashes the plaintext qstr with `fscrypt_fname_siphash()` so lookup remains stable across ciphertext names.

This file depends on filename preparation in `dir.c`, Unicode casefold support, and fscrypt. The key invariant is that the hash must match the lookup name semantics: bytewise for ordinary directories, normalized plaintext for casefolded directories, and fscrypt-safe SipHash when encryption and casefolding combine.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/inline.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/inline.c

`inline.c` implements inline data and inline dentry support, where small regular files, symlinks, or directories store payload inside the inode node page instead of separate data blocks.

Inline-data eligibility rejects atomic-write files, non-regular/non-symlink files, oversized files, and post-read-required files such as encrypted/verity/compressed data. Sanity checks detect impossible inline states, such as inline-data inodes that also have block pointers or unsupported feature combinations.

The read/write helpers copy inline payload between the inode node page and page-cache folio zero. `f2fs_do_read_inline_data()` copies inode-resident bytes and zeroes the rest of the folio; `f2fs_write_inline_data()` copies dirty page-cache data back into the inode page, marks append/data-exist state, and clears the page-cache dirty tag. `f2fs_truncate_inline_inode()` zeroes inline bytes from a truncation offset and clears `FI_DATA_EXIST` when truncating to zero.

Inline-to-block conversion is handled by `f2fs_convert_inline_inode()` and `f2fs_convert_inline_folio()`. They reserve block zero, verify the reserved address is `NEW_ADDR`, copy inline data into a page-cache folio, submit an out-of-place write, wait for completion, mark the inode recoverable through `FI_APPEND_WRITE`, clear inline bytes and inline flags, and update inline inode stats. Corrupt inline block state sets fsck-needed state and reports an invalid block address.

Recovery support reconciles roll-forward inode pages with current inline state. `f2fs_recover_inline_data()` handles all combinations of previous and recovered inline flags: copy inline data, remove inline data and recover blocks, truncate blocks and restore inline data, or leave block recovery to the normal path.

Inline directory support includes lookup, empty-dir initialization, insertion, deletion, readdir, empty-dir checks, and conversion to normal dentry blocks. If an inline directory overflows, level-zero directories copy the inline dentry structure into block zero; hashed/rehashed directories back up inline dentries, clear inline storage, and reinsert entries through regular directory insertion so hashes and placement are rebuilt. Failure paths restore inline contents or truncate partially created dentry pages.

`f2fs_inline_data_fiemap()` reports inline regular/symlink data or inline dentries as FIEMAP inline extents, optionally syncing the inode node first and calculating the byte address inside the inode block when the inode node has a valid physical address.

Important dependencies are inode node pages, dnode/block reservation, data writeback, directory entry helpers, filename setup, fiemap, node info, inline xattr sizing, and F2FS recovery flags. The main invariants are that inline inodes cannot simultaneously own separate data blocks, conversion must not expose uninitialized dentry memory, and inline flag/stat changes must be synchronized with inode-page dirtiness and recovery expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/inline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/inode.c

`inode.c` implements F2FS inode lifecycle operations: marking dirty inodes, translating F2FS flags to VFS inode flags, reading and validating on-disk inode nodes, installing inode/file/address-space operations, updating inode nodes, writing inodes, evicting inodes, and handling failed inode creation.

`f2fs_mark_inode_dirty_sync()` suppresses dirtying for new, readonly, already-dirtied, or uncommitted atomic-write inodes. `f2fs_set_inode_flags()` maps F2FS sync, append, immutable, noatime, dirsync, encryption, verity, and casefold flags onto VFS inode flags.

The inode checksum helpers enable, compute, verify, and set inode checksums when the superblock feature and extra inode fields support them. The checksum includes inode number, generation, and the inode body with the checksum field zeroed.

`sanity_check_inode()` validates many on-disk invariants before the inode is accepted: nonzero block count, matching inode footer ino/nid, xattr nid range, directory link count, extra-attribute feature compatibility and size, compression algorithm/cluster/level/block counts, flexible inline xattr bounds, project quota/inode checksum/crtime/compression feature dependencies, inline-data and inline-dentry legality, casefold feature availability, and device-alias requirements. Failures set fsck-needed state through callers and usually return `-EFSCORRUPTED`.

`do_read_inode()` loads fields from the inode node into VFS and F2FS-private state: mode, uid/gid, links, size, blocks, timestamps, generation, directory depth, GC failures, xattr nid, flags, advice, parent ino, dir level, inline info, extra attribute size, inline xattr size, project id, crtime, compression context, and extent-cache metadata. It also recovers missing inline-data existence state, fixes cold-node marking for non-directories, initializes read and age extent trees, and updates debug stats.

`f2fs_iget()` wraps `iget_locked()`, rejects external access to meta inodes already present in cache, reads normal inodes, sets VFS flags, and installs the correct operations: node/meta/compress address spaces for meta inodes, F2FS file ops and data aops for regular files, directory ops for directories, encrypted or plain symlink ops, and special inode initialization for device/FIFO/socket inodes. `f2fs_iget_retry()` retries only `-ENOMEM`.

`f2fs_update_inode()` writes in-memory inode state back to the inode node page, including mode, ownership, links, block count, size except for uncommitted atomic writes, largest read extent, inline flags, timestamps, depth/GC failures, xattr nid, flags, parent ino, generation, dir level, extra attributes, project id, crtime, compression fields, and rdev encoding. Deleted inodes clear inline state, disk-time snapshots are refreshed, and inode checksums are set under check-fs builds.

`f2fs_write_inode()` skips meta inodes and clean lazytime-only cases, returns errors for checkpoint failure or checkpoint-not-ready state, writes the inode page, and balances the filesystem when writeback requested progress. `f2fs_update_inode_page()` retries inode-page lookup and stops checkpointing if the inode page cannot be updated safely.

`f2fs_evict_inode()` aborts atomic writes, drops COW inode links, truncates page cache, invalidates compression cache when needed, removes dirty/donate/extent state, and for unlinked normal inodes initializes quotas, removes recovery inode entries, protects against freeze, truncates data blocks, removes the inode node, handles ENOMEM retry, marks fsck-needed on inconsistent dirty failures, drops quotas and stats, clears dirty inode state, invalidates node/xattr pages, preserves roll-forward entries for still-linked append/update inodes, and returns failed free nids when necessary.

`f2fs_handle_failed_inode()` cleans up an inode whose creation failed after allocation. It clears nlink, writes and syncs the inode state, unlocks the new inode, tries to add it to the orphan list before releasing `lock_op`, marks fsck-needed if orphan preservation cannot be guaranteed, finalizes or returns the nid, and drops the inode reference.

Important dependencies are node-page access, extent cache initialization/destruction, inline-data helpers, compression configuration, xattr/quota/orphan handling, checkpoint state, fscrypt, fsverity, directory/namei operation tables, and debug stats. The key invariants are accepting only feature-compatible inode layouts, keeping inode dirty state consistent with checkpoint/recovery lists, never exposing meta inodes as normal files, and ensuring eviction either frees all inode-owned resources or leaves enough recovery/fsck state to repair them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/inode.c -->