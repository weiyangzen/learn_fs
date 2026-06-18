# Group Research: group_217_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_vfs_fs_c_sources_cow_18b0cab5e496

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fs.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fs.c

Implements the main bcachefs VFS bridge: inode cache lifecycle, inode btree synchronization, namespace operations, file/directory/symlink operation tables, export/NFS handles, mount/reconfigure plumbing, superblock operations, and per-filesystem VFS resource initialization.

Key entry points:
- `bch2_vfs_inode_get()` / `bch2_vfs_inode_get_trans()` locate or instantiate VFS inodes from `(subvol, inum)` btree inode records.
- `__bch2_create()` creates regular files, directories, device nodes, tmpfiles, subvolumes, and snapshots through common inode/dirent transaction logic.
- `bch2_lookup()`, `bch2_link()`, `__bch2_unlink()`, `bch2_symlink()`, `bch2_rename2()`, `bch2_tmpfile()`, and `bch2_vfs_readdir()` implement core inode and directory operations.
- `bch2_setattr()`, `bch2_setattr_nonsize()`, `bch2_getattr()`, `bch2_fileattr_get()`, and `bch2_fileattr_set()` translate VFS stat/attribute requests into bcachefs inode updates.
- `bch2_encode_fh()`, `bch2_fh_to_dentry()`, `bch2_fh_to_parent()`, `bch2_get_parent()`, and `bch2_get_name()` provide export operations for NFS/file handles.
- `bch2_fs_get_tree()`, `bch2_fs_parse_param()`, `bch2_fs_reconfigure()`, and `bch2_kill_sb()` implement the Linux filesystem type mount lifecycle.
- `bch2_fs_vfs_init()`, `bch2_fs_vfs_init_rw()`, `bch2_fs_vfs_exit()`, `bch2_vfs_init()`, and `bch2_vfs_exit()` allocate and release VFS-wide tables, biosets, mempools, workqueues, inode cache, and filesystem registration.

Core mechanics:
- `bch2_inode_update_after_write()` is the central synchronization point from `struct bch_inode_unpacked` to `struct inode` and `struct bch_inode_info`, updating nlink, uid/gid, mode, size, times, cached inode copy, and VFS flags.
- `bch2_write_inode()` wraps inode btree mutation in a transaction, detects reconcile option changes, writes the inode key, commits, updates the VFS inode while the btree node lock still protects `ei_inode`, and wakes reconcile work if needed.
- VFS inodes are tracked in both a full `(subvol, inum)` `rhashtable` and an inum-only `rhltable`; the latter supports snapshot/open-inode checks.
- `bch2_inode_hash_find()` handles races with `I_FREEING`/`I_WILL_FREE` by waiting on the inode bit waitqueue, dropping btree locks when called from a transaction.
- `bch2_inode_hash_insert()` handles duplicate-cache races by discarding the newly allocated inode and returning the already-cached inode.
- Namespace mutations update btree metadata first, then refresh affected VFS inodes and dentry state. Casefolded negative dentries are intentionally not cached.
- Project quota changes are pre-transferred before updates and rolled back when the btree commit fails.
- Mount setup parses device lists, deduplicates already-mounted device sets, opens/starts the filesystem, configures the superblock, initializes root inode/dentry, and maps read-only recovery cases to user-visible errors carefully.

Important invariants:
- `ei_update_lock` serializes in-memory inode updates with btree inode writes; multi-inode operations use sorted locking via `bch2_lock_inodes()` to avoid deadlocks.
- VFS inode cache insertion occurs before transaction exit for newly created inodes to prevent another thread from importing and modifying the same on-disk inode first.
- Inodes in snapshot subvolumes are flagged with `EI_INODE_SNAPSHOT` and excluded from normal quota accounting paths.
- `bch2_evict_inode()` removes non-deleted inodes from VFS hashes before final pagecache teardown, but keeps deleting inodes visible until fsck/open-inode checks can observe them.
- Mount reconfiguration uses `state_lock` and filesystem read-only/read-write transitions, and synchronous conversion to read-only flushes the filesystem first.
- Address-space operations are installed for all VFS inodes; regular files receive bcachefs file ops, directories directory ops, symlinks page-backed link ops, and special files `init_special_inode()`.

Filesystem relevance:
- This file is the Linux VFS personality of bcachefs. It turns bcachefs transactional inode, dirent, quota, subvolume, snapshot, xattr, and journal machinery into normal Linux filesystem semantics.

Notable risks:
- Inode-cache races are delicate because bcachefs does not use `I_NEW` for normal lookup insertion; compatibility with VFS discard paths is handled explicitly.
- Several comments call out deadlock hazards around eviction-time btree reads and lookup/check repair commits.
- Freeze support relies on internal write references instead of full VFS internal-write freeze integration.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fs.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fs.h

Defines the bcachefs VFS inode wrapper and the public VFS-layer inode helpers used by namespace, I/O, ioctl, pagecache, quota, and lifecycle code.

Key declarations:
- `struct bch_inode_info` embeds `struct inode` and adds bcachefs identity, hash nodes, list membership, flags, update/quota/pagecache locks, quota reservation state, qid, devices needing nocow flush, cached unpacked inode, and delayed writeback work.
- Pagecache locking helpers expose two-state lock modes: add-pagecache users (`bch2_pagecache_add_*`) and block-pagecache users (`bch2_pagecache_block_*`).
- `bch2_lock_inodes()` / `bch2_unlock_inodes()` sort inode pointers and acquire requested update/pagecache locks in stable order.
- `inode_attr_changing()` / `inode_attrs_changing()` detect inherited inode option changes, especially for project quota inheritance.
- Public entry points include inode creation, lookup/import, inode writeback/update, quota transfer, setattr, unlink, subvolume inode eviction, fiemap, and VFS init/exit.

Core mechanics:
- `inode_inum()` returns the bcachefs `(subvol, inum)` identity cached in `ei_inum`.
- `to_bch_ei()` and `file_bch_inode()` provide container conversions from VFS inode/file to bcachefs inode wrapper.
- `bch2_set_projid()` is a small project-id helper over `bch2_fs_quota_transfer()`, updating `QTYP_PRJ`.
- `bch2_dirty_inode()` queues delayed VFS writeback work when the mount has a nonzero writeback timeout.

Important invariants:
- `EI_INODE_ERROR` means VFS and btree inode state may no longer be consistent after an error.
- `EI_INODE_SNAPSHOT` marks snapshot-subvolume inodes where quota accounting is skipped.
- `EI_INODE_HASHED` protects inode hash-table membership and is tested under the VFS inode lock.
- Multi-inode lock macros intentionally de-duplicate equal inode pointers after sorting.

Filesystem relevance:
- This header defines the state that lets bcachefs pair Linux VFS inode semantics with transactional btree inode metadata and per-folio allocation state.

Notable risks:
- `ei_devs_need_flush` tracks nocow flush needs coarsely by device mask; comments note that per-device flush sequence tracking would be more precise.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/io.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/io.c

Implements VFS-level file I/O helpers around fsync, truncate, fallocate, hole punching, collapse/insert range, reflink/remap, quota/disk accounting, nocow flushes, and `llseek(SEEK_DATA/SEEK_HOLE)`.

Key entry points:
- `bch2_inode_flush_nocow_writes_async()` and `bch2_fsync()` flush pagecache, inode metadata, journal sequence, and devices that received nocow writes.
- `bch2_write_inode_size()` writes size and selected time fields to the btree inode.
- `__bch2_i_sectors_acct()` / `bch2_i_sectors_acct()` update `i_blocks`, quota reservations, and quota accounting.
- `bch2_zero_pagecache_posteof()` and `bchfs_truncate()` implement size changes and post-EOF zeroing.
- `bch2_fallocate_dispatch()` dispatches normal preallocation, zero range, punch hole, insert range, and collapse range.
- `bch2_remap_file_range()` implements clone/dedupe-style remapping between files.
- `bch2_llseek()` implements regular seek plus btree/pagecache-aware `SEEK_DATA` and `SEEK_HOLE`.

Core mechanics:
- Nocow write flushing consumes `inode->ei_devs_need_flush`, submits `REQ_PREFLUSH` bios through `nocow_flush_bioset`, and holds per-device write refs until endio.
- `bch2_flush_inode()` reads the authoritative inode journal sequence from the btree, repairs impossible future sequence values, flushes the journal to that sequence, then flushes nocow devices.
- Truncation blocks concurrent pagecache additions, waits for DIO, reads the btree inode, handles journal error cases, truncates partial folios, updates VFS size, flushes straddling/extended ranges, calls btree truncate, adjusts `i_blocks`, and writes final attributes.
- Partial folio truncation reads existing data when needed, initializes `bch_folio` sector state, marks full filesystem-block sectors unallocated, zeroes the requested bytes, obtains a nofail disk reservation to avoid truncate `ENOSPC`, cleans writable mappings, and redirties the folio.
- Fallocate walks extent slots in the target subvolume, skips already-reserved data, clamps holes against dirty pagecache, reserves quota/disk space, installs extent reservations, marks pagecache sectors reserved, and updates block accounting.
- Remap validates flags/alignment/overlap, locks both files, blocks pagecache additions, waits for DIO, prepares the generic remap, invalidates destination pagecache, reserves quota for destination holes, updates source pagecache allocation state, calls `bch2_remap_range()`, updates destination `i_size`, and flushes when sync semantics require it.
- `SEEK_DATA` and `SEEK_HOLE` combine extent btree scans with pagecache state so dirty cached data not yet in the btree is visible to userspace.

Important invariants:
- Size-changing operations hold `i_rwsem` via VFS callers or explicitly lock the inode, wait for DIO, and use `bch2_pagecache_block` when invalidating or restructuring cached pages.
- `i_blocks` underflow is treated as a filesystem check error and clamped to prevent negative VFS state.
- Truncate may set `EI_INODE_ERROR` when btree truncate fails after VFS pagecache/size state changed.
- Fallocate and remap must release quota reservations on all error paths.
- Collapse/insert range require block-size alignment and invalidate/write back all affected pagecache before btree extent movement.

Filesystem relevance:
- This is the bcachefs VFS file-space mutation layer. It coordinates user-visible file size/range operations with extent btrees, quota accounting, pagecache state, journal durability, and copy-on-write/reflink semantics.

Notable risks:
- Comments note that partial-folio truncate currently cannot distinguish real data from zero-only content precisely.
- Pagecache invalidation can spin if another task repeatedly redirties a page.
- Remap aligns the btree operation beyond the requested byte length, then trims the reported byte count back to the user-requested range.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/io.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/io.h

Declares VFS I/O helpers and inline quota/pagecache support used by buffered I/O, direct I/O, fsync, truncate, fallocate, remap, and seek paths.

Key declarations:
- `struct nocow_flush` wraps a flush bio with closure and device ownership metadata.
- `struct folio_vec` and bio iteration helpers convert `bio_vec` segments into folio-relative segments.
- `struct quota_res` tracks reserved quota sectors for pending write/fallocate work.
- Quota helpers reserve and release `Q_SPC` preallocations, with snapshot inodes bypassing quota reservation.
- Public functions cover sector accounting, nocow flushes, size writes, fsync, post-EOF zeroing, truncate, fallocate, remap, and bcachefs `llseek`.

Core mechanics:
- `biovec_to_foliovec()` computes folio-relative offset/length even when a `bio_vec` page is part of a larger folio.
- `bio_for_each_folio()` iterates the current bio iterator by folio-sized subsegments.
- `bch2_quota_reservation_add()` takes `ei_quota_lock`, charges quota in preallocation or nocheck mode, updates `ei_quota_reserved`, and accumulates the local reservation.
- `bch2_quota_reservation_put()` reverses outstanding quota reservations under the inode quota lock.
- Fault-disabled mapping helpers wrap the filesystem `fdm_table` used by page-fault lock-order handling.

Important invariants:
- Quota reservation release asserts that the local reservation does not exceed `inode->ei_quota_reserved`.
- `bch2_i_sectors_acct()` serializes nonzero sector accounting through `ei_quota_lock`.
- Snapshot inodes do not take quota reservations.

Filesystem relevance:
- This header is the compact contract between the VFS I/O code and lower bcachefs allocation/quota/pagecache subsystems.

Notable risks:
- The no-quota build stubs make reservation calls no-ops, so code using them must still be correct without quota side effects.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/io.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/ioctl.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/ioctl.c

Implements bcachefs file ioctl handling for attribute reinheritance, label/version/shutdown ioctls, subvolume create/destroy/list/path queries, snapshot-tree queries, reflink option propagation, raw direct reads, and unpoisoning poisoned extents.

Key entry points:
- `bch2_fs_file_ioctl()` dispatches all file-level bcachefs and generic filesystem ioctls, falling back to `bch2_fs_ioctl()` for global bcachefs commands.
- `bch2_compat_fs_ioctl()` maps selected 32-bit compat commands to native handling.
- `bch2_ioc_reinherit_attrs()` reapplies inherited inode attributes from a directory to a named child and performs project quota transfer if needed.
- `bch2_ioc_getlabel()`, `bch2_ioc_setlabel()`, `bch2_ioc_getversion()`, and `bch2_ioc_goingdown()` implement generic filesystem label/version/shutdown controls.
- `bch2_ioctl_subvolume_create*()` and `bch2_ioctl_subvolume_destroy*()` create snapshots/subvolumes and remove subvolumes through VFS path lookup and bcachefs create/unlink transactions.
- `bch2_ioctl_subvolume_list()` and `bch2_ioctl_subvolume_to_path()` expose subvolume child listings and subvolume-root paths.
- `bch2_ioctl_snapshot_tree()` reports snapshot tree metadata and per-snapshot accounting.
- `bch2_ioc_set_reflink_p_may_update_opts()` and `bch2_ioc_propagate_reflink_p_opts()` update reflink option propagation metadata.
- `bch2_ioc_pread_raw()` performs privileged owner raw direct reads with optional poison-check suppression and returns structured error messages.
- `bch2_ioc_unpoison()` clears poisoned extent flags in regular extents and reflink targets.

Core mechanics:
- Subvolume creation validates flags, optionally resolves a source path for snapshots, syncs inodes before snapshot creation, performs VFS path creation and permission/security checks, and calls `__bch2_create()` under `snapshots.create_lock`.
- Subvolume destruction uses the VFS locked path-removal API, adjusts lock ordering around `mnt_want_write()`, revalidates the victim dentry, checks permissions, and calls `__bch2_unlink(..., deleting_snapshot=true)`.
- Subvolume listing iterates `BTREE_ID_subvolume_children`, checks that the caller can traverse from child root to parent via full VFS permission checks, converts inums to relative paths, and emits packed user records.
- Snapshot-tree query resolves tree id from argument or current file subvolume, requires `CAP_SYS_ADMIN` for arbitrary tree ids, flushes the btree write buffer, iterates snapshots in the tree, reads per-snapshot accounting, and copies bounded node records to userspace.
- Reflink option propagation walks extent keys, updates `KEY_TYPE_reflink_p` flags, then propagates options to underlying `reflink_v` records spanning front/back padding.
- Raw pread requires `O_DIRECT` and file ownership/capability, imports a userspace buffer, calls the direct I/O read path with a `bch_read_err_report`, and copies error count/message state back to userspace.
- Unpoisoning rebuilds extent keys with the poisoned flag cleared and commits updates across regular and reflink-backed ranges.

Important invariants:
- Label setting and shutdown require `CAP_SYS_ADMIN`; arbitrary snapshot-tree lookup and reflink feature enablement do too.
- Subvolume create/destroy reject cross-filesystem paths with `-EXDEV`.
- v2 subvolume ioctls copy structured error messages back through `bch2_copy_ioctl_err_msg()`.
- User buffer writes use explicit `copy_to_user_errcode()`, `put_user()`, padding zero-fill, and range-size checks.
- Permission-sensitive traversal deliberately unlocks the btree transaction before calling `inode_permission()` because ACL lookup may start its own transaction.

Filesystem relevance:
- This file is the user-control surface for bcachefs-specific VFS features: subvolumes, snapshots, reflink metadata maintenance, poison recovery, raw reads, labels, and controlled emergency shutdown.

Notable risks:
- Subvolume listing combines btree traversal with VFS permission checks and transaction relocking, making restart/error handling subtle.
- Some comments and strings contain typos such as "invalid flasg", but behavior is unaffected.
- Raw reads and unpoison operations intentionally expose low-level repair/diagnostic functionality and are guarded by ownership/capability checks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/ioctl.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/ioctl.h

Declares the bcachefs VFS ioctl entry points.

Key declarations:
- `bch2_fs_file_ioctl()` handles native file ioctls.
- `bch2_compat_fs_ioctl()` handles supported compat ioctls when `CONFIG_COMPAT` is enabled by callers.

Filesystem relevance:
- This header connects file and directory operation tables in `fs.c` to the ioctl implementation in `ioctl.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/pagecache.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/pagecache.c

Implements bcachefs pagecache/folio-private state: per-sector allocation/dirty/reservation tracking, disk/quota reservation acquisition, page-fault and mmap write handling, invalidation/release hooks, and pagecache-aware data/hole seeking.

Key entry points:
- `bch2_filemap_get_contig_folios_d()` gathers contiguous folios over a byte range, creating at most the first 1 MiB before switching off creation.
- `bch2_write_invalidate_inode_pages_range()` writes back and invalidates a mapping range, retrying on `-EBUSY`.
- `bch2_folio_set()` initializes folio sector state from extent btree slots.
- `bch2_bio_page_state_set()` stamps folio state from extents represented by completed bios.
- `bch2_mark_pagecache_unallocated()` and `bch2_mark_pagecache_reserved()` adjust cached folio allocation state after remap/fallocate/truncate-style operations.
- `bch2_get_folio_disk_reservation()`, `bch2_folio_reservation_get()`, and `bch2_folio_reservation_get_partial()` reserve disk/quota space for dirtying folio ranges.
- `bch2_set_folio_dirty()`, `bch2_set_folio_undirty()`, and `bch2_vfs_dirty_folio()` transition folio sectors through dirty/reserved states and update accounting.
- `bch2_page_fault()` and `bch2_page_mkwrite()` implement mmap fault/write fault coordination with pagecache locks and reservations.
- `bch2_invalidate_folio()` and `bch2_release_folio()` release bcachefs folio-private state.
- `bch2_seek_pagecache_data()`, `bch2_seek_pagecache_hole()`, and `bch2_clamp_data_hole()` expose pagecache data/hole state to seek and fallocate code.

Core mechanics:
- `struct bch_folio` is allocated as folio private data and contains a spinlock, write count, uptodate flag, and per-sector `struct bch_folio_sector` entries.
- Sector states form a small state machine: unallocated, reserved, dirty, dirty-reserved, and allocated. Helpers dirty, undirty, or reserve states without losing allocation information.
- `bch2_folio_set()` walks extent slots in the inode subvolume and fills each sector with replica count and allocation/reservation/unallocated state.
- Disk reservation needs are computed as desired replicas minus existing replicas minus already-reserved replicas.
- Dirtying a range moves disk reservation sectors into per-sector `replicas_reserved`, consumes quota reservation for newly unallocated sectors, updates `i_blocks`, and dirties the folio through `filemap_dirty_folio()`.
- `bch2_vfs_dirty_folio()` handles generic mm dirtying by nofail-reserving enough space for the in-size part of the folio.
- `bch2_page_fault()` coordinates with the faults-disabled mapping table to avoid pagecache lock-order inversions; on dropped locks it signals SIGBUS so the higher path can retry safely.
- `bch2_page_mkwrite()` starts a page fault, updates file time, locks the folio, validates mapping and size, initializes folio state, reserves space, marks the folio dirty, waits for stable writeback, queues delayed inode writeback, and returns `VM_FAULT_LOCKED`.
- Data/hole helpers inspect dirty/reserved per-sector state in pagecache so cached not-yet-written data participates in `SEEK_DATA`, `SEEK_HOLE`, and fallocate hole clamping.

Important invariants:
- Folio-private state creation requires the folio lock.
- Reservation and dirty transitions require `bch_folio->uptodate`.
- Full-folio invalidation/release clears dirty accounting, releases reservations, and detaches private state; partial invalidation leaves state intact.
- `bch2_release_folio()` refuses to release dirty or writeback folios.
- Pagecache hole/data searches can run nonblocking and return `-EAGAIN` if folio locks cannot be acquired.

Filesystem relevance:
- This file is the bridge between Linux folios and bcachefs extent allocation. It lets buffered writes, mmap writes, fallocate, remap, truncate, and seek reason about sub-folio allocation and dirty state at filesystem-sector granularity.

Notable risks:
- Comments acknowledge that generic mm dirtying may dirty more of a large folio than the exact modified byte range.
- Folios above `i_size` can legitimately be dirtied by mm/GUP/truncate races; writeback must clean up sector dirty bits later.
- `bch2_mark_pagecache_reserved()` updates `*start` before deriving the folio offset, a subtle area to inspect if reservation marking appears off by range.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/pagecache.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/pagecache.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/pagecache.h

Defines the bcachefs folio-private data structures, sector state enum, reservation wrapper, folio geometry helpers, and pagecache operation declarations.

Key declarations:
- `typedef DARRAY(struct folio *) folios` is used for dynamic batches of folio pointers.
- `folio_end_pos()`, `folio_sectors()`, `folio_sector()`, and `folio_end_sector()` convert folio geometry to byte and sector ranges.
- `enum bch_folio_sector_state` defines unallocated, reserved, dirty, dirty-reserved, and allocated states.
- `struct bch_folio_sector` stores fully allocated replica count, reserved replica count, and sector state.
- `struct bch_folio` stores the folio-private spinlock, write count, uptodate flag, and variable-length per-sector array.
- `struct bch2_folio_reservation` combines a disk reservation and quota reservation.
- Public declarations cover folio creation/release, state initialization, bio state stamping, pagecache marking, reservation get/put, dirty/undirty transitions, mmap faults, invalidation/release, and pagecache data/hole seeking.

Core mechanics:
- `BCH_WRITEPAGE_BUF_BYTES` computes the worst-case temporary per-folio sector-state snapshot size for `MAX_PAGECACHE_ORDER`.
- `folio_pos_to_s()` converts a file offset inside a folio to a bcachefs sector-state index and asserts the offset lies inside the folio.
- `bch2_folio_release()` requires a locked folio before detaching and freeing private state.
- `inode_nr_replicas()` derives desired data replicas from inode options or filesystem defaults.
- `bch2_folio_reservation_init()` zeroes a reservation wrapper and seeds desired disk replica count.

Important invariants:
- The per-sector state array has one entry per 512-byte sector in the folio.
- `bch2_folio(folio)` returns folio private data and callers generally require it to exist and be uptodate before accounting transitions.
- The comment explains use of `u64` end positions to avoid overflow at maximum supported mapping ranges.

Filesystem relevance:
- This header defines the state model that lets bcachefs track dirty and reserved file data independently of coarse Linux folio dirty bits.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/pagecache.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/types.h

Defines the per-filesystem VFS state container embedded in `struct bch_fs`.

Key fields:
- `inodes_list` and `inodes_lock` track all live bcachefs VFS inodes for subvolume eviction and lifecycle operations.
- `inodes_table` maps full `(subvol, inum)` identities to cached VFS inodes.
- `inodes_by_inum_table` maps inode numbers across subvolumes for snapshot/open-descendent checks.
- `writepage_bioset`, `dio_write_bioset`, `dio_read_bioset`, and `nocow_flush_bioset` back specialized bio allocations.
- `writepage_buf_pool` reserves memory for writepage folio-sector snapshots.
- `writeback_wq` runs delayed inode writeback work.

Filesystem relevance:
- This structure groups the shared VFS resources that are initialized during filesystem startup and torn down during VFS exit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/vfs/types.h -->