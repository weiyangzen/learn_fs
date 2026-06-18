# Group Research: group_1289_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_chfs_chfs_erase_c_sour_721b7939c2ef

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All 17 listed CHFS source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_erase.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_erase.c

Purpose: Implements logical eraseblock remapping for CHFS.

Key entry point:
- `chfs_remap_leb`: chooses an erase-pending block, frees its node-reference blocks, calls EBH unmap/map, resets accounting, and returns the block to `chm_free_queue`.

Important behavior:
- Requires mountfields and size locks, and asserts write-buffer lock is not held.
- If no block is directly erasable, it may promote one from `chm_erasable_pending_wbuf_queue` after flushing pending write-buffer data.
- Resets dirty, unchecked, used, free, and wasted counters through shared size-change helpers.
- Returns `ENOSPC` if nothing can be erased.

Dependencies:
- Uses EBH mapping APIs, node-ref freeing from allocation code, and queue/accounting helpers from CHFS core.

Research notes:
- Comments still flag erase/remap policy as needing design work.
- Error paths after `chfs_unmap_leb`/`chfs_map_leb` do not restore the removed block to a queue in this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_erase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_gc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_gc.c

Purpose: Implements CHFS garbage collection: wake policy, background thread lifecycle, unchecked inode validation, eraseblock selection, and live-node relocation.

Key entry points:
- `chfs_gc_trigger`, `chfs_gc_thread_start`, `chfs_gc_thread_stop`, `chfs_gc_thread_should_wake`.
- `chfs_gcollect_pass`: main GC pass.
- `find_gc_block`: chooses erase-pending, very-dirty, dirty, or clean blocks with weighted randomness.
- `chfs_gcollect_pristine`, `chfs_gcollect_live`, `chfs_gcollect_vnode`, `chfs_gcollect_dirent`, `chfs_gcollect_deletion_dirent`, `chfs_gcollect_dnode`.

Important behavior:
- GC first drains `chm_unchecked_size` by checking vnode caches with `chfs_check` and `chfs_read_inode_internal`.
- Avoids collecting `chm_nextblock`; selected block becomes `chm_gcblock`.
- Rewrites live vnode metadata, dirents, deletion dirents, and data nodes using GC allocation.
- Copies pristine nodes after header/node CRC validation.
- Fully dirty/wasted GC blocks move to `chm_erase_pending_queue` and are remapped.

Dependencies:
- Tightly coupled to vnode-cache states, read-inode fragment construction, write paths, node-list operations, and erase remapping.

Research notes:
- `chfs_gc_release_inode` is a stub.
- Several paths sleep/retry on concurrent read/check states.
- GC panics if it cannot make space in a critical condition.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_inode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_inode.h

Purpose: Defines CHFS in-memory inode state and compatibility constants/macros.

Key definitions:
- `CHFS_ROOTINO` is inode 2.
- `enum chtype`: CHFS file types aligned with NetBSD vnode type conversion.
- `CHTTOVT`, `VTTOCHT`, `IFTOCHT`: type conversion macros.
- `struct chfs_inode`: embeds `genfs_node`, locks, UFS/CHFS mount pointers, vnode pointer, vnode cache, directory list, fragment tree, metadata, flags, rdev, and symlink target.
- `VTOI`, `ITOV`: vnode/inode conversion macros.

Important behavior:
- Tracks append-log `version`, logical `size`, write-progress `write_size`, timestamps, mode, ownership, and update flags.
- Uses UFS-style compatibility constants for permissions and file types.

Dependencies:
- Kernel vnode, stat, UFS mount, and genfs APIs.

Research notes:
- Comments note UFS dependencies and duplicated constants should be removed.
- `ctime` is commented as creation time but used like change time in update paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_malloc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_malloc.c

Purpose: Provides CHFS allocation wrappers and global pool caches for core in-memory and flash-format objects.

Key entry points:
- `chfs_alloc_pool_caches`, `chfs_destroy_pool_caches`.
- `chfs_vnode_cache_alloc/free`.
- `chfs_alloc_refblock`, `chfs_free_refblock`, `chfs_alloc_node_ref`, `chfs_free_node_refs`.
- Alloc/free helpers for dirents, full dnodes, flash vnode/dirent/data nodes, node fragments, temporary dnodes, and temporary dnode info.

Important behavior:
- Node refs are allocated in blocks of `REFS_BLOCK_LEN + 1`; the final slot is a link sentinel to the next refblock.
- `chfs_alloc_node_ref` appends physical node refs per eraseblock and initializes `nref_lnr`.
- Vnode-cache allocation initializes `v`, `dirents`, and `dnode` as sentinel self-pointers.
- Dirents are variable-size `kmem` allocations with trailing name storage.

Dependencies:
- NetBSD `pool_cache` and `kmem`.
- Used by scan, vnode cache, read-inode, write, GC, and nodeops.

Research notes:
- Most allocations use sleeping/waiting allocation semantics.
- `chfs_free_node_refs` walks sentinel-linked refblocks and frees each block.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_nodeops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_nodeops.c

Purpose: Implements node-reference list manipulation, obsolete marking, eraseblock accounting transitions, eraseblock closing, and write-space reservation.

Key entry points:
- `chfs_update_eb_dirty`, `chfs_add_node_to_list`, `chfs_remove_node_from_list`, `chfs_remove_and_obsolete`.
- `chfs_add_fd_to_inode`, `chfs_add_vnode_ref_to_vc`.
- `chfs_nref_next`, `chfs_nref_len`.
- `chfs_mark_node_obsolete`, `chfs_close_eraseblock`.
- `chfs_reserve_space_normal`, `chfs_reserve_space_gc`, `chfs_reserve_space`.

Important behavior:
- Vnode-cache node lists are sorted by logical eraseblock and offset.
- Obsolete marking converts used/unchecked bytes to dirty bytes and may move eraseblocks between clean, dirty, very-dirty, erase-pending, and pending-wbuf queues.
- If a block becomes fully obsolete, it may be queued for erase and immediately remapped.
- Reservation paths trigger GC/remap to maintain free-block reserves.
- Closing an eraseblock appends a terminal node ref and dirties remaining free space.

Dependencies:
- Central dependency for scan, write, unlink, GC, truncate, and fragment cleanup.

Research notes:
- Queue removal during obsolete marking is explicitly marked ugly because the current queue is not tracked.
- Reservation policy has TODOs around free-block thresholds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_nodeops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_pool.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_pool.c

Purpose: Implements per-mount CHFS pool wrappers and fixed-size string pools.

Key entry points:
- `chfs_pool_init`, `chfs_pool_destroy`.
- `chfs_pool_page_alloc`, `chfs_pool_page_free`.
- `chfs_str_pool_init`, `chfs_str_pool_destroy`, `chfs_str_pool_get`, `chfs_str_pool_put`.

Important behavior:
- Pool names include the object purpose and mount pointer.
- Custom pool allocator accounts pages through `chm_pages_used` and refuses allocations at `CHFS_PAGES_MAX(chmp)`.
- String pools bucket allocations at 16, 32, 64, 128, 256, 512, and 1024 bytes.
- String get/put asserts `len <= 1024`.

Dependencies:
- NetBSD `pool`, `pool_allocator`, and atomics.
- Public declarations are in `chfs_pool.h`.

Research notes:
- `chfs_pool_page_alloc` calls `pool_get(pp, flags | PR_WAITOK)` from within allocator hooks, which is unusual and depends on local allocator assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_pool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_pool.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_pool.h

Purpose: Declares CHFS pool wrapper types and APIs.

Key definitions:
- `struct chfs_pool`: embeds NetBSD `struct pool`, owning `chfs_mount`, and name buffer.
- `struct chfs_str_pool`: groups fixed-size pools from 16 to 1024 bytes.
- `CHFS_POOL_GET`, `CHFS_POOL_PUT`: cast-based convenience wrappers around `pool_get`/`pool_put`.

Declared APIs:
- `chfs_pool_init`, `chfs_pool_destroy`.
- `chfs_str_pool_init`, `chfs_str_pool_destroy`.
- `chfs_str_pool_get`, `chfs_str_pool_put`.

Dependencies:
- Kernel-only declarations requiring broader CHFS mount definitions.

Research notes:
- `struct pool` is intentionally first in `struct chfs_pool`, enabling cast-based use.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_pool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_readinode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_readinode.c

Purpose: Reconstructs in-memory inode data from flash node refs, validates unchecked data nodes, builds file fragment trees, truncates fragments, and serves block reads.

Key entry points:
- Temporary-node helpers: `chfs_check_td_data`, `chfs_check_td_node`, `chfs_add_tmp_dnode_to_tree`.
- Fragment helpers: `new_fragment`, `chfs_add_frag_to_fragtree`, `chfs_remove_frags_of_node`, `chfs_kill_fragtree`, `chfs_truncate_fragtree`, `chfs_obsolete_node_frag`.
- Inode/data entry points: `chfs_get_data_nodes`, `chfs_build_fragtree`, `chfs_read_inode`, `chfs_read_inode_internal`, `chfs_read_data`.

Important behavior:
- Scan marks data nodes unchecked; this file validates only surviving temporary data-node versions before promoting bytes from unchecked to used.
- Uses temporary rb-trees to resolve overlapping data nodes by offset/version.
- Final fragment rb-tree can contain hole fragments with `node == NULL`.
- Obsoletes old full data nodes only when all fragments referencing them disappear.
- `chfs_read_data` validates header, magic, node CRC, and data CRC before copying data into a buffer.

Dependencies:
- Uses vnode-cache node lists, node obsolete/list helpers, EBH read API, CRC helpers, and NetBSD buffer/page sizing.

Research notes:
- Error cleanup has FIXME comments around partially built fragment trees.
- Some compare callbacks subtract 64-bit offsets into signed int return values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_readinode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_scan.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_scan.c

Purpose: Scans eraseblocks at mount/build time, validates flash node headers, creates vnode-cache records, builds initial node-ref chains, and classifies eraseblocks.

Key entry points:
- `chfs_scan_make_vnode_cache`.
- `chfs_scan_check_node_hdr`, `chfs_scan_check_vnode`, `chfs_scan_check_dirent_node`, `chfs_scan_check_data_node`.
- `chfs_add_fd_to_list`, `chfs_scan_mark_dirent_obsolete`.
- `chfs_scan_classify_cheb`, `chfs_scan_eraseblock`.

Important behavior:
- Recognizes free space by repeated `0xff` header-sized reads until `MAX_READ_FREE`.
- Bad magic/CRC advances by 4 bytes and dirties scanned bytes.
- Vnode nodes keep only newest version in the vnode cache.
- Dirents are ordered/replaced by hash/name/version in the parent scan list.
- Data nodes are not fully data-CRC checked during scan; they are linked with `CHFS_UNCHECKED_NODE_MASK` for later GC/read-inode validation.
- Padding nodes are allocated as obsolete node refs and counted dirty.

Dependencies:
- Uses EBH reads, CRC helpers, vnode-cache hash functions, node-list operations, and eraseblock accounting.

Research notes:
- Mount-time scan is responsible for initial free/used/dirty/unchecked accounting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_scan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_subr.c

Purpose: Provides supporting vnode/filesystem routines for memory limits, directory lookup/fill, size changes, flag changes, and timestamp updates.

Key entry points:
- `chfs_mem_info`: computes available/total memory page estimate.
- `chfs_dir_lookup`: linear directory entry lookup excluding physical `.`/`..`.
- `chfs_filldir`: emits NetBSD `struct dirent` records.
- `chfs_chsize`: grows/truncates vnode size and fragment tree.
- `chfs_chflags`: validates and updates file flags.
- `chfs_itimes`, `chfs_update`: update inode timestamps and iflags.

Important behavior:
- `chfs_chsize` rejects directory truncation, handles read-only mounts, zeroes truncated ranges, drops obsolete fragments, and updates UVM/vnode/inode size.
- `chfs_chflags` uses kauth/genfs authorization and handles user/system flag separation.
- Timestamps are stored as seconds and convert `IN_*` flags into accessed/modified state.

Dependencies:
- NetBSD VFS, UVM, kauth, genfs, dirent, and CHFS fragment helpers.

Research notes:
- `chfs_update` is lightweight and does not itself write flash metadata; callers write vnode nodes separately.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vfsops.c

Purpose: Implements CHFS VFS integration: mount/unmount, vnode loading, statvfs, module lifecycle, and VFS operation registration.

Key entry points:
- `chfs_mount`, `chfs_mountfs`, `chfs_unmount`, `chfs_root`.
- `chfs_loadvnode`, `chfs_vget`.
- `chfs_statvfs`, `chfs_init`, `chfs_reinit`, `chfs_done`, `chfs_modcmd`.

Important behavior:
- Mount verifies a block device backed by the flash cdev major, opens EBH, allocates CHFS/UFS mount structs, initializes locks, queues, write buffer, vnode-cache hash, eraseblock array, accounting, and trigger levels.
- Calls `chfs_build_filesystem`, creates root vnode, starts GC, and marks device mounted.
- Vnode loading allocates `struct chfs_inode`, attaches genfs ops, reads flash vnode metadata, builds dirents/fragments depending on type, and initializes spec/fifo operations.
- Unmount stops GC, flushes pending wbuf data, frees node refs/vnode cache, closes EBH, destroys locks, and closes device.

Dependencies:
- NetBSD VFS module layer, UFS compatibility APIs, genfs, specfs, EBH flash layer, CHFS scan/build and GC.

Research notes:
- `chfs_sync`, file-handle conversion, snapshot, and mount updates are mostly unsupported/stubs.
- The mount structure is still bridged through `struct ufsmount`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnode.c

Purpose: Provides vnode/inode construction helpers, flash metadata loading, directory-entry loading, new inode creation, and size accounting helpers.

Key entry points:
- `chfs_vnode_lookup`: scans mounted vnodes for an inode number.
- `chfs_readvnode`: reads flash vnode metadata into `struct chfs_inode`.
- `chfs_readdirent`: reads a flash dirent and adds it to an inode.
- `chfs_makeinode`: creates a new vnode/inode, writes vnode metadata and parent dirent.
- `chfs_set_vnode_size`.
- `chfs_change_size_free/dirty/unchecked/used/wasted`.

Important behavior:
- Root inode is treated as in-memory metadata.
- `chfs_makeinode` allocates a new vnode number, initializes vnode cache, sets ownership/mode/type, writes child and parent vnode records, writes dirent, and inserts it into the parent’s dirent list.
- Size-change helpers update both mount-wide and per-eraseblock counters with assertions.

Dependencies:
- NetBSD vnode iterator/cache APIs, UFS mount bridge, kauth, CHFS write paths, vnode-cache helpers, and accounting locks.

Research notes:
- Parent link count is incremented for all new inodes in `chfs_makeinode`, which is notable for non-directory creation behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnode_cache.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnode_cache.c

Purpose: Implements the CHFS vnode-cache hash table.

Key entry points:
- `chfs_vnocache_hash_init`.
- `chfs_vnode_cache_get`.
- `chfs_vnode_cache_add`.
- `chfs_vnode_cache_remove`.
- `chfs_vnocache_hash_destroy`.

Important behavior:
- Hash table has `VNODECACHE_SIZE` buckets.
- Each bucket is sorted by vnode number, allowing lookup/removal by increasing `vno`.
- `chfs_vnode_cache_add` assigns a new vnode number when `new->vno` is zero.
- Remove frees the cache unless its state is `VNO_STATE_READING` or `VNO_STATE_CLEARING`.
- Destroy walks every bucket and frees all cache objects.

Dependencies:
- Requires `chm_lock_vnocache` for get/add/remove operations.
- Allocation/freeing delegated to `chfs_malloc.c`.

Research notes:
- This cache is the central mount-time and runtime index for flash node refs by inode number.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnode_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnops.c

Purpose: Implements CHFS vnode operations for regular files, directories, symlinks, special devices, and FIFOs.

Key entry points:
- Namespace ops: `chfs_lookup`, `chfs_create`, `chfs_mknod`, `chfs_remove`, `chfs_link`, `chfs_rename`, `chfs_mkdir`, `chfs_rmdir`, `chfs_symlink`.
- File ops: `chfs_open`, `chfs_close`, `chfs_access`, `chfs_getattr`, `chfs_setattr`, `chfs_read`, `chfs_write`, `chfs_fsync`.
- Directory/symlink ops: `chfs_readdir`, `chfs_readlink`.
- Lifecycle/I/O ops: `chfs_inactive`, `chfs_reclaim`, `chfs_strategy`, `chfs_bmap`.
- Vnodeop vectors: `chfs_vnodeop_entries`, `chfs_specop_entries`, `chfs_fifoop_entries`.

Important behavior:
- Lookup uses name cache, handles `.`/`..`, enforces permissions, and loads children via `VFS_VGET`.
- Create/mkdir/mknod/symlink use `chfs_makeinode`; device nodes and short symlinks store payload as CHFS data nodes.
- Read/write are adapted from FFS/genfs/UBC flows; regular reads use UBC, strategy reads call `chfs_read_data`, and strategy writes append CHFS data nodes.
- Writes update vnode size, clear suid/sgid when required, flush pages for sync writes, then append a new flash vnode metadata node.
- Remove/rmdir call `chfs_do_unlink`; link and rename are implemented as append-log dirent/vnode updates.
- Reclaim clears fragment trees and in-memory dirents, resets vnode-cache state, purges name cache, and releases inode storage.

Dependencies:
- Heavy use of NetBSD VFS, genfs, UBC, UFS helper routines, kauth, CHFS write/read/fragment helpers, and vnode-cache state.

Research notes:
- Rename is simple link-new/unlink-old logic and has limited error recovery.
- `chfs_advlock` returns success without real locking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_wbuf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_wbuf.c

Purpose: Implements CHFS flash write buffering, page-aligned flushing, direct large writes, and explicit padding nodes.

Key entry points:
- `chfs_flush_wbuf`: internal flush with optional padding.
- `chfs_fill_wbuf`: internal copy into write buffer.
- `chfs_write_wbuf`: public buffered write path for append-log nodes.
- `chfs_flush_pending_wbuf`: forces pending buffer flush with padding.

Important behavior:
- Write buffer size is the flash page size.
- Enforces contiguous writes; non-contiguous writes panic.
- If flushing with padding, writes a `CHFS_NODETYPE_PADDING` node, allocates an obsolete node ref, and moves bytes from free to wasted.
- Full pages can be written directly when residual data exceeds the write-buffer page size.
- `chfs_write_wbuf` owns `chm_lock_wbuf` internally but expects mountfields and size locks held.

Dependencies:
- Uses EBH/flash write API, node-ref allocation, CRC helpers, and eraseblock accounting.

Research notes:
- `chfs_flush_pending_wbuf` assumes mountfields lock and acquires size plus write-buffer locks.
- Comment misspells “pending” in the function header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_wbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_write.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_write.c

Purpose: Serializes CHFS vnode metadata, directory entries, and data nodes to flash, and implements logical link/unlink operations.

Key entry points:
- `chfs_write_flash_vnode`.
- `chfs_write_flash_dirent`.
- `chfs_write_flash_dnode`.
- `chfs_do_link`.
- `chfs_do_unlink`.

Important behavior:
- Vnode metadata writes skip root, bump vnode-cache version, reserve space, allocate a node ref, write via `chfs_write_wbuf`, account bytes, and replace old vnode refs.
- Dirent writes serialize parent inode number, child inode number or zero for deletion, version, type, name CRC, and padded name bytes.
- Data-node writes serialize page/block payload, compute data/node CRCs, append the node, update `write_size`, replace old node refs/frags if needed, and insert into vnode-cache data list.
- Link writes updated inode metadata and a new dirent.
- Unlink flushes buffers, kills fragments, decrements links, writes deletion dirent, obsoletes old dirent/data/vnode refs, and updates parent link count.

Dependencies:
- Relies on reservation/remap/GC in nodeops, write buffer, vnode-cache list helpers, fragment helpers, and timestamp updates.

Research notes:
- Several error paths have TODO comments for recovery policy.
- Some flash fields are assigned without explicit endian conversion in dirent serialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/debug.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/debug.h

Purpose: Defines CHFS debug/error logging prefixes, debug macros, and a lightweight assertion helper.

Key definitions:
- Prefix constants for error, warning, notice, debug, EBH debug, and GC debug messages.
- `unlikely(x)` wraps `__builtin_expect`.
- `debug_msg(pref, fmt, ...)` prints prefix, function name, and formatted message.
- `chfs_assert(expr)` prints a failed assertion message without panicking.
- `chfs_err`, `chfs_warn`, `chfs_noti`, `dbg`, `dbg2`, `dbg_ebh`, `dbg_gc`.

Important behavior:
- Error, warning, and notice messages always print through `debug_msg`.
- General debug output is compiled out unless `DBG_MSG` is defined.
- GC debug output is compiled out unless `DBG_MSG_GC` is defined.

Dependencies:
- Uses kernel `printf` and compiler variadic macro support.

Research notes:
- The `DBG_MSG` branch for `dbg2` appears malformed: `CHFS_DBG2_PREFIX(fmt, ...` is missing the expected comma/parenthesis structure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/debug.h -->