# Group Research: group_506_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_aadffac3e0d9

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/illumos/illumos-gate`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specvnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specvnops.c

Special-device vnode operations for illumos `specfs`, mediating character/block device access through snodes, common snodes, real backing vnodes, STREAMS state, device-policy checks, and VM/page-cache interfaces.

Key responsibilities:
- Defines `spec_vnodeops_template` for special-file VOPs: open, close, read, write, ioctl, getattr/setattr/access/create, fsync, inactive, fid, seek, locks, realvp, getpage/putpage, map/addmap/delmap, poll, dump, pageio, ACL, and pathconf.
- Maintains common-snode open/reference serialization using `spec_lockcsp()`, `SN_HOLD`, `SN_RELE`, `SLOCKED`, `SWANT`, and `SCLOSING`.
- Computes and caches device size in `spec_size()`, using driver properties such as `Size`, `size`, `Nblocks`, `nblocks`, `blksize`, and `device-blksize`, with `UNKNOWN_SIZE` for unavailable block-device sizes.
- Handles device opens in `spec_open()`, including devinfo association, `VFS_NODEVICES`, fencing, policy checks, STREAMS vs non-STREAMS dispatch, clone opens, open/close exclusion, device contracts, offset-capability flags, and EINTR behavior for drivers that opt in.
- Handles last-close semantics in `spec_close()`, including file lock/share cleanup, size invalidation, clone devinfo reassociation, and actual `device_close()` only when common-snode open/mapping references reach zero.
- Implements character and block device I/O: STREAMS read/write via `strread`/`strwrite`, character devices via `cdev_read`/`cdev_write`, and block devices via segmap/VPM data copy against the common vnode.
- Implements block-device VM operations: `spec_getpage()`, `spec_getapage()`, `spec_putpage()`, `spec_putapage()`, and `spec_startio()` use page clustering, read-ahead, page zeroing past device size, `pageio_setup()`, and `bdev_strategy()`.
- Implements device mmap support through `spec_map()`, `spec_char_map()`, and `spec_segmap()`, choosing old `mmap`, `devmap_setup`, driver `segmap`, or `segvn` mappings for block devices.
- Forwards attributes, ACLs, pathconf, fid, access, and setattr operations to `s_realvp` where available; otherwise fabricates special-file metadata from the snode.

Dependencies:
- Uses kernel device switch and DDI interfaces: `dev_open`, `device_close`, `cdev_*`, `bdev_*`, `devopsp`, `devnamesp`, `e_ddi_hold_devi_by_dev`, and `spec_assoc_vp_with_devi`.
- Uses STREAMS internals: `stropen`, `strread`, `strwrite`, `strioctl`, `strpoll`, `strctty`, stream head fields, and clone/qassociate handling.
- Uses VM/page infrastructure: `segmap`, `vpm`, `segvn`, `segdev`, `page_*`, `pvn_*`, `pageio_*`, `hat`, and vnode page-cache helpers.
- Depends on snode state from `sys/fs/snode.h` and global specfs state such as `stable_lock`, `snode_cache`, `spec_vfs`, and device fencing flags.

Concurrency and locking:
- Common-snode serialization is central; open, close, addmap, and delmap coordinate through `spec_lockcsp()` and `s_lock`.
- `spec_inactive()` removes snodes under `stable_lock`, drops vnode references carefully, updates real vnode times, releases devinfo/device-policy holds, and frees the snode.
- Mapping count `s_mapcnt` participates in close decisions; final `delmap` may close the device if open count is zero.

Notable risks:
- Open/close and clone handling is highly stateful; incorrect `s_count`, `s_mapcnt`, `SNEEDCLOSE`, or `SDIPSET` transitions can leak device references or close active devices.
- Size caching deliberately avoids calling driver property callbacks before attach/open to avoid driver panics; changing this can expose latent driver bugs.
- Block-device I/O depends on correct EOF/device-size clipping and page zeroing; errors here can expose stale memory or corrupt cached pages.
- Fencing policy is asymmetric by design: configuration/detection paths fail, but unconfiguration and some I/O paths are allowed through.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specvnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/swapfs/swap_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/swapfs/swap_subr.c

Swapfs initialization and shared support code for memory-backed swap vnodes, async putpage request queues, and dynamic recalculation of swapfs reserve thresholds.

Key responsibilities:
- Defines global swapfs reserve tunables/state: `swapfs_desfree`, `swapfs_minfree`, and `swapfs_reserve`.
- Initializes swapfs in `swapinit()`: mutexes, vnode table, reserve thresholds, memory-configuration callbacks, async request pool, VFS ops, and vnode ops.
- Creates per-identifier swap vnodes lazily in `swapfs_getvp()`, setting `VISSWAP` and `VISSWAPFS`.
- Implements `swap_sync()` to push pages from all swap vnodes on `SYNC_ALL`.
- Manages async request queues used by `swap_vnops.c`: pending list and free list through `sw_getreq`, `sw_putreq`, `sw_putbackreq`, `sw_getfree`, and `sw_putfree`.
- Recalculates reserve values in response to memory hotplug through `swap_mem_config_post_add`, `swap_mem_config_pre_del`, and `swap_mem_config_post_del`.

Dependencies:
- Uses `swap_vnodeops_template` from `swap_vnops.c`.
- Uses VM memory accounting globals such as `physmem`, `availrmem`, and `segspt_minfree`.
- Uses physical-memory configuration callback API `kphysm_setup_func_register`.
- Uses async request structures from swapnode/swap headers.

Concurrency and locking:
- `swapfs_lock` protects the vnode table, vnode count, and async request lists.
- Memory-delete callbacks use `swapfs_pending_delete` with atomic updates before recalculating viable thresholds.
- Async request insertion holds the vnode, and free-list return releases it.

Notable risks:
- `swapfs_recalc()` refuses memory-delete operations that would leave swapfs thresholds unsafe, returning `EBUSY`.
- `swapfs_getvp()` assumes `vidx` is within `MAX_SWAP_VNODES`; callers must enforce bounds.
- Async request pool size is tied to `klustsize / PAGESIZE * 2`; pressure behavior depends on that small fixed pool.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/swapfs/swap_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/swapfs/swap_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/swapfs/swap_vnops.c

Swapfs vnode operations for anonymous-memory backing objects, page fault fill, pageout writeback to physical swap slots, large-page support, and page disposal.

Key responsibilities:
- Defines `swap_vnodeops_template` with inactive, getpage, putpage, dispose, and error stubs for unsupported VOPs.
- Implements `swap_getpage()` as a `pvn_getpages()` wrapper around `swap_getapage()`.
- Implements `swap_getapage()` to find/create swapfs pages, optionally force SEGKP pages non-relocatable, read from physical swap backing when present, free physical backing after successful read-in, or zero-fill when no backing exists.
- Implements `swap_getconpage()` for large-page anonymous memory paths using a caller-provided preallocated page, with relocation/size negotiation through `pszc` and `nreloc`.
- Implements `swap_putpage()` to scan vnode page ranges, optionally enqueue async pageout requests, and call `swap_putapage()` for dirty pages.
- Implements `swap_putapage()` to assign physical swap backing via `swap_newphysname()`, cluster adjacent pending async pageout requests when possible, and issue `VOP_PAGEIO()` to the physical swap vnode.
- Implements `swap_dispose()` to route final page disposal to the physical backing vnode when one exists, otherwise to generic `fs_dispose()`.

Dependencies:
- Depends on anonymous/swap metadata helpers: `swap_getphysname`, `swap_newphysname`, `swap_phys_free`, `swap_anon`, and `AH_MUTEX`.
- Uses `sw_getreq`, `sw_putreq`, `sw_putbackreq`, `sw_getfree`, and `sw_putfree` from `swap_subr.c`.
- Uses VM page interfaces: `page_lookup`, `page_create_va`, `page_lookup_create`, `page_relocate_cage`, `pvn_getpages`, `pvn_vplist_dirty`, `pvn_getdirty`, and `pvn_write_done`.
- Uses `segkp` and kernel cage checks for non-relocatable kernel pages.

Concurrency and locking:
- Page locks and page I/O locks drive correctness; functions assert or adjust exclusive/shared page locks as needed.
- Anonymous hash mutexes protect updates that clear `an_pvp/an_poff` after swap-in.
- Async clustering consumes pending requests opportunistically and returns or requeues requests on lookup, dirtiness, allocation, or contiguity failures.

Notable risks:
- `swap_getapage()` frees physical swap backing after reading a page back into memory, marking the page modified; this is central to swap slot lifecycle.
- Async clustering assumes contiguous physical swap slots and same physical vnode; failed clustering must restore page state and requeue correctly.
- `B_FORCE` is stripped in `swap_putpage()` so locked pages are not invalidated.
- `swap_getconpage()` returns special negative values for large-page size negotiation, so callers must distinguish them from normal errno paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/swapfs/swap_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_dir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_dir.c

Tmpfs directory-entry implementation: hashed lookup, directory list maintenance, create/link/rename/delete semantics, `.`/`..` initialization, and tmpnode creation helpers.

Key responsibilities:
- Maintains a global directory-entry hash table keyed by parent tmpnode and name, with 8192 buckets and 64 mutexes.
- Provides `tmpfs_hash_init`, `tmpfs_hash_in`, `tmpfs_hash_out`, `tmpfs_hash_change`, and `tmpfs_hash_lookup`.
- Implements `tdirlookup()` with execute permission checks and tmpnode holds on success.
- Implements `tdirenter()` for create, mkdir, link, and rename, including slash rejection, detached-directory handling, permission checks, link-count adjustment, and cleanup on partial failures.
- Implements `tdirdelete()` for remove, rename unlink, and rmdir, including sticky-directory checks, hash/list removal, ctime/mtime updates, link decrement, and directory truncation on rmdir.
- Initializes directories in `tdirinit()` by creating `.` and `..` entries, setting list offsets, link counts, and timestamps.
- Removes every entry in a directory via `tdirtrunc()`, with special xattr-directory link-count rules.
- Prevents directory rename cycles with `tdircheckpath()`.
- Replaces existing rename targets through `tdirrename()`, enforcing same-filesystem, type compatibility, empty-directory and mountpoint checks.
- Rewrites `..` on cross-directory renames via `tdirfixdotdot()`.
- Allocates and inserts directory entries in `tdiraddentry()`, using stable synthetic offsets and a roving slot pointer.
- Creates tmpnodes in `tdirmaketnode()`, including type, rdev, uid/gid inheritance, setgid handling, and initial directory setup.

Dependencies:
- Uses tmpnode and tmount structures from `sys/fs/tmpnode.h` and `sys/fs/tmp.h`.
- Uses permission helpers from `tmp_subr.c`, tmpnode allocation from `tmp_tnode.c`, and VFS/vnode event helpers.
- Uses vnode mount locks to prevent renaming/removing mounted directories.

Concurrency and locking:
- Directory mutation requires the target directory `tn_rwlock` held as writer.
- Link/rename may need the source tmpnode lock while already holding the target directory lock.
- Rename deadlock avoidance uses `rw_tryenter()`, drops/reacquires the target directory lock around `delay()`, and exposes tunables `tmpfs_rename_backoff_delay`, `tmpfs_rename_backoff_tries`, and `tmpfs_rename_loops`.
- Hash buckets have separate mutexes; `tmpfs_hash_change()` updates the tmpnode pointer under the appropriate hash mutex.

Notable risks:
- Link counts are deliberately adjusted before some operations and unwound on errors; mistakes can leak or prematurely free tmpnodes.
- Xattr directories have nonstandard link-count rules, especially for implicit `..` references.
- Synthetic directory offsets are not byte offsets; readdir users depend on their stability across removals.
- Rename replacement of directories must coordinate mountpoint locks, emptiness, `..` rewrites, and destination vnode events.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_subr.c

Small tmpfs support routines for access checks, sticky-directory remove policy, kernel-memory accounting, and mount-option parsing.

Key responsibilities:
- Implements `tmp_taccess()` using tmpnode owner/group/mode bits and `secpolicy_vnode_access2()`.
- Implements `tmp_sticky_remove_access()` for sticky directories: removal is allowed for directory owner, entry owner, privileged callers, or writable regular-file entries.
- Implements `tmp_memalloc()` and `tmp_memfree()` with global `tmp_kmemspace` accounting and `tmpfs_maxkmem` enforcement.
- Parses tmpfs size strings in `tmp_convnum()`, supporting bytes, cascading `k/m/g` suffixes, and a single `%` suffix relative to zone swap cap or total available swap.
- Parses root mode mount option strings in `tmp_convmode()` as octal values limited to `07777`.

Dependencies:
- Uses tmpfs globals from `tmp_vfsops.c`: `tmpfs_maxkmem`, `tmp_kmemspace`, and `tmpfs_minfree`.
- Uses zone swap controls, anoninfo accounting, DDI string parsers, policy helpers, and kernel allocator APIs.

Concurrency and locking:
- `tmp_kmemspace` is adjusted atomically on alloc/free.
- The one-per-second over-limit warning in `tmp_memalloc()` uses a static timestamp without a lock, acceptable only as throttled diagnostic state.

Notable risks:
- `musthave` allocations bypass `tmpfs_maxkmem`; callers must keep them subordinate to earlier successful normal allocations.
- `%` size parsing uses pages for intermediate cap calculation to avoid byte overflow.
- Cascading suffix handling is intentional compatibility behavior, not a typo.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_tnode.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_tnode.c

Tmpfs tmpnode lifecycle and file storage accounting: swap reservation, anon-map growth, tmpnode initialization, and truncation.

Key responsibilities:
- Reserves backing swap/memory for tmpfs file growth in `tmp_resv()`, enforcing per-mount `tm_anonmax`, system free-space policy, and zone reservations.
- Releases reservations in `tmp_unresv()` during truncation.
- Grows a regular file's anonymous-slot array in `tmpnode_growmap()`, initially allocating at least `TMP_INIT_SZ` slots.
- Initializes tmpnodes and backing vnodes in `tmpnode_init()`, setting mode, type, uid/gid, fsid, nodeid, generation, timestamps, vnode ops, mount linkage, and global mount tmpnode list membership.
- Truncates tmpnodes in `tmpnode_trunc()`, handling growth, shrink, partial-page zeroing, anon-page freeing, anon array release at size zero, symlink constraints, and directory truncation.

Dependencies:
- Uses anon subsystem calls: `anon_checkspace`, `anon_try_resv_zone`, `anon_unresv_zone`, `anon_create`, `anon_grow`, `anon_pages`, `anon_free`, and `anon_release`.
- Uses VM/vnode helpers such as `pvn_vpzero`, `vn_has_cached_data`, `vn_alloc`, `vn_setops`, and `vn_exists`.
- Uses tmpfs directory helper `tdirtrunc()` and vnode ops `tmp_vnodeops`.

Concurrency and locking:
- `tmp_resv()`, `tmp_unresv()`, `tmpnode_growmap()`, and `tmpnode_trunc()` assert the appropriate tmpnode rwlocks, especially `tn_rwlock` and `tn_contents`.
- Mount-wide tmpnode list and `tm_anonmem` accounting are protected by `tm_contents`.
- `tmpnode_trunc()` temporarily drops `tn_contents` while zeroing a partial final page to avoid VM re-entry deadlocks.

Notable risks:
- Reservation size is page-rounded and intended to track file size, including holes grown by truncate.
- Shrink updates `tn_size` before zeroing partial pages so concurrent faults do not instantiate pages beyond the new EOF.
- `tmpnode_init()` uses a pointer-derived 32-bit node id; generation numbers are used to disambiguate reuse in fids.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_tnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_vfsops.c

Tmpfs VFS operations and module glue: mount/remount/unmount, root lookup, statvfs, fid-to-vnode lookup, global limits, and module lifecycle.

Key responsibilities:
- Defines tmpfs module linkage and `vfsdef_t`, with mount options `xattr`, `noxattr`, `size`, and `mode`.
- Registers VFS and vnode operations in `tmpfsinit()`, initializes directory hashing, tmpfs resource limits, unique device major/minor state, and tmpfs globals.
- Handles `_init`, `_fini`, and `_info` module entry points.
- Implements `tmp_mount()` with mount permission checks, mountpoint busy checks, read-only rejection, size/mode parsing, remount size updates, tmount allocation, unique device selection, root tmpnode creation, mountpoint attribute inheritance, and root directory initialization.
- Implements `tmp_unmount()` with forced-unmount rejection, busy checks, tmpnode hold scanning, directory-entry truncation pass, node-release pass, xattr cleanup, mount-path/free-space assertions, mutex destruction, and tmount free.
- Implements `tmp_root()` by holding and returning the root vnode.
- Implements `tmp_statvfs()` from system/zone swap availability, per-mount anon use/limit, tmpfs kernel-memory headroom, device id, mount path, and flags.
- Implements `tmp_vget()` by scanning the tmpnode list for matching fid inode/generation, holding the vnode if still linked, and restoring `VISSWAP` for sticky non-directory swap-like files.

Dependencies:
- Uses tmpnode, tmp directory, and tmp option parsing helpers from other tmpfs files.
- Uses anon accounting, zone swap caps, vfs option helpers, pathname APIs, vnode lifecycle helpers, and kernel module/VFS registration APIs.

Concurrency and locking:
- `tmpfs_minor_lock` serializes unique tmpfs minor allocation.
- `tm_contents` protects mount-wide tmpnode list and anon accounting.
- `tmp_unmount()` holds tmpnodes while checking for busy references and releases them in a controlled reverse traversal.
- Root tmpnode initialization takes the root `tn_rwlock` while setting `VROOT`, inherited attributes, list pointers, and directory entries.

Notable risks:
- Remount only updates `tm_anonmax`; lowering below current usage is allowed and makes the filesystem full until usage drops.
- `tmp_statvfs()` must report zone-aware capacity when non-global zones or swap caps are involved.
- Unmount relies on `tmp_inactive()` eventually removing nodes held by pageout or anon slots; it waits and retries when the tail node remains.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_vnops.c

Tmpfs vnode operations for regular file I/O, directory namespace operations, extended attributes, VM paging, mmap, truncation, locking, fids, and pathconf.

Key responsibilities:
- Defines `tmp_vnodeops_template` covering open/close/read/write/ioctl/getattr/setattr/access/lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink/fsync/inactive/fid/rwlock/rwunlock/seek/space/getpage/putpage/map/addmap/delmap/pathconf/vnevent.
- Denies swap activation on tmpfs files in `tmp_open()` when `VISSWAP` is set.
- Implements regular-file writes in `wrtmp()`: mandatory lock checks, file-size/resource limits, swap reservation, anon slot allocation, segmap/VPM data copy, zeroing for partial new pages, size update/rollback, setuid/setgid clearing, and timestamp updates.
- Implements regular-file reads in `rdtmp()`: mandatory lock checks, EOF clipping, segmap/VPM copy, and access-time updates.
- Implements attributes and permissions through `tmp_getattr()`, `tmp_setattr()`, and `tmp_access()`, including root ownership refresh from covered vnode, policy checks, and truncate-on-size changes.
- Implements namespace VOPs on top of `tmp_dir.c`: lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, and readlink.
- Implements xattr-directory lookup/creation for `LOOKUP_XATTR`, with mode derivation and hidden xattr tmpnode setup.
- Wraps special-device tmpfs nodes with `specvp()` on lookup/create when needed.
- Implements `tmp_inactive()` to free unlinked tmpnodes, truncate remaining file data, remove xattr directories, unlink from mount list, destroy locks, free vnode, and free tmpnode memory.
- Implements VM fill/writeback via `tmp_getpage()`, `tmp_getapage()`, `tmp_putpage()`, and `tmp_putapage()`, using anon slots and physical swap backing only when pages must be paged out.
- Implements mmap through `tmp_map()` with `segvn_create`, while `tmp_addmap()` and `tmp_delmap()` are no-ops.
- Implements `F_FREESP` through `tmp_space()` and `tmp_freesp()`, with mandatory lock checks and `tmpnode_trunc()`.
- Implements fids (`tmp_fid()`), seek bounds, rwlock wrappers, and pathconf values for xattrs, system attributes, and timestamp resolution.

Dependencies:
- Uses tmpfs directory helpers (`tdirlookup`, `tdirenter`, `tdirdelete`, `tdirinit`, `tdirtrunc`) and tmpnode helpers (`tmp_resv`, `tmpnode_growmap`, `tmpnode_trunc`, `tmpnode_init`).
- Uses anon/swap helpers `anon_get_ptr`, `anon_set_ptr`, `anon_alloc`, `non_anon`, `swap_getphysname`, and `swap_newphysname`.
- Uses VM helpers `segmap`, `vpm`, `pvn_getpages`, `pvn_write_kluster`, `VOP_PAGEIO`, and page-cache lookup/writeback routines.
- Uses vnode event notification helpers for create/remove/link/rename/rmdir/truncate.

Concurrency and locking:
- Higher layers call `tmp_rwlock()`/`tmp_rwunlock()` around read/write-style operations; internal paths use `tn_rwlock` and `tn_contents`.
- Read/write drop `tn_contents` around segmap/VPM copying to avoid deadlocks when page faults re-enter tmpfs.
- `tmp_getpage()` upgrades `tn_contents` from reader to writer when it must instantiate anon slots for holes.
- `tmp_putpage()` avoids blocking pageout on `tn_contents`; pageout uses `rw_tryenter()` and returns `ENOMEM` if it cannot acquire the lock.
- `tmp_rename()` serializes mount-wide renames through `tm_renamelck`.

Notable risks:
- Tmpfs reserves swap for file growth before pages necessarily exist; holes are materialized later during getpage/write paths.
- `tmp_putpage()` normally does no I/O except pageout/free, invalidate, or explicit dontneed paths.
- `tmp_inactive()` has a retry loop because pages or anon slots can keep a vnode discoverable after link count reaches zero.
- Xattr directories are lazily created by lookup and have special restrictions on contained object types and link counts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_alloc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_alloc.c

UDF allocation and inode lifecycle support: bitmap/space-table block allocation, block freeing, inode allocation/freeing, truncate-space entry point, and metadata allocation cache.

Key responsibilities:
- Implements `ud_alloc_space()` to allocate blocks from a requested partition, optionally from the metadata cache, dispatching to bitmap or space-table allocation and updating free-block counters.
- Implements bitmap allocation in `ud_alloc_space_bmap()`, including proximity allocation, last-allocation scanning, cluster alignment while not fragmented, fallback to fragmented scanning, less-is-ok partial allocation, bitmap marking, and delayed writes.
- Implements `ud_check_free_and_mark_used()`, `ud_check_free()`, `ud_mark_used()`, and `ud_mark_free()` for bitmap manipulation.
- Implements space-table allocation in `ud_alloc_space_stbl()` for short and long allocation descriptors, using exact fit, first larger fit, or largest partial extent when `less_is_ok` is set.
- Implements `ud_free_space()` dispatching to bitmap or space-table free paths and marking the filesystem bad if free fails.
- Implements bitmap freeing in `ud_free_space_bmap()`, choosing freed-space bitmap if present or unallocated bitmap otherwise, marking blocks free, and updating free counters only when freeing directly to unallocated space.
- Implements space-table freeing in `ud_free_space_stbl()`, merging with adjacent short/long descriptor extents where possible or appending a new descriptor if space remains.
- Implements `ud_ialloc()` to allocate a file-entry block, initialize UDF file entry fields, permissions, uid/gid, times, implementation id, unique id, device extended attributes, ICB tag file type/flags, write the tag, update file/dir counters, and instantiate an inode via `ud_iget()`.
- Implements `ud_ifree()` to trash the on-disk file entry, free its ICB block, and decrement file/dir counters.
- Implements `ud_freesp()` for `F_FREESP`-style truncation to EOF, including mandatory lock checks and ordered inode locking before `ud_itrunc()`.
- Implements metadata block cache helpers `ud_alloc_from_cache()` and `ud_release_cache()` using cluster allocation and per-partition `udp_cache`.

Dependencies:
- Uses UDF volume/inode structures from `sys/fs/udf_volume.h` and `sys/fs/udf_inode.h`.
- Uses endian conversion macros such as `SWAP_16`, `SWAP_32`, and `SWAP_64`.
- Uses UDF helpers including `ud_bread`, `ud_xlate_to_daddr`, `ud_make_tag`, `ud_update_regid`, `ud_make_dev_spec_ear`, `ud_utime2dtime`, `ud_iget`, and `ud_itrunc`.
- Uses vnode/file-lock policy helpers for truncation and creation permission behavior.

Concurrency and locking:
- Filesystem-wide counters and allocation-cache state are protected by `udf_vfsp->udf_lock`.
- Bitmap buffers are modified then written with `bdwrite()`, while inode blocks use `BWRITE`/`BWRITE2`.
- `ud_freesp()` follows inode lock ordering by dropping `i_contents`, taking `i_rwlock` writer, then `i_contents` writer before truncation.
- `ud_alloc_from_cache()` releases `udf_lock` before recursively calling `ud_alloc_space()` to refill the cache.

Notable risks:
- Bitmap routines account for `HDR_BLKS` offset, so caller-visible partition block numbers differ from bitmap bit positions.
- Space-table descriptor compression loops copy one element beyond the logical last descriptor while removing an entry; this is longstanding C-style table compaction and relies on buffer slack.
- `ud_alloc_space_stbl()` declares `error` without initializing it before some success paths, but success paths jump to `end` where `if (!error)` is evaluated; this is a suspicious correctness risk in the source as read.
- `ud_release_cache()` frees cached blocks as a contiguous range starting at `udp_cache[0]`; this assumes the cache contents correspond to a contiguous cluster in ascending order.
- `ud_freesp()` explicitly notes a bug: unused bytes in the last retained block are not cleared, so a resulting hole may not read as zeroes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_alloc.c -->