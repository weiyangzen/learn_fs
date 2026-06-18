# Group Research: group_322_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_fuse_fuse_vnops_c_s_65e3745c3e98

Scope checked against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_vnops.c

This file implements DragonFlyBSD vnode operations for the in-kernel FUSE filesystem bridge. It translates VOP calls into FUSE protocol IPC requests, maintains cached vnode/node state, and integrates FUSE regular-file I/O with DragonFly’s buffer cache, VM pager, namecache, kqueue, locking, and vnode lifecycle.

Main responsibilities:
- Attribute translation and caching via `fuse_set_attr()`, mapping FUSE `struct fuse_attr` into DragonFly `struct vattr`.
- Permission and metadata operations: `access`, `getattr`, `setattr`, `pathconf`.
- File-handle lifecycle: `open`, `close`, `fsync`, `inactive`, `reclaim`, and `fuse_release()`.
- Namecache-backed namespace operations: lookup/resolve, link, create, mknod, unlink, mkdir, rmdir, rename, symlink, readlink, and readdir.
- Regular file read/write through buffer-cache blocks, with VM shortcut reads and size-extension/truncation handling.
- Strategy I/O queuing to a FUSE helper thread so sensitive kernel contexts, including pageout, do not block directly on userland FUSE IPC.
- kqueue filter support for read/write/vnode notifications.
- VM pager glue through generic vnode getpages/putpages.

Key implementation details:
- Most operations first check `fuse_test_dead()` and `fuse_test_nosys()` to gracefully handle dead mounts or unsupported FUSE opcodes.
- `fuse_vop_open()` lazily obtains a FUSE file handle if the node lacks one, using `FUSE_OPENDIR` for directories and `FUSE_OPEN` otherwise. `O_CREAT` is stripped when reopening an already-created vnode.
- `fuse_vop_close()` does not immediately release the FUSE handle. It requests vnode finalization when clean, because the vnode may still be active through directory state, mmap, or other references.
- `fuse_vop_fsync()` flushes DragonFly dirty buffers first, clears `sizeoverride`, may finalize closed vnodes, then sends `FUSE_FSYNC` or `FUSE_FSYNCDIR`.
- `fuse_vop_getattr()` refreshes attributes only when `fnp->attrgood` is clear, otherwise it serves cached attributes. Root ENOTCONN has a fallback minimal attribute response.
- `fuse_vop_setattr()` builds a `FUSE_SETATTR` request from DragonFly `vattr` changes, including size, uid/gid, mode, and timestamps. Unsupported flags return `EOPNOTSUPP`.
- Lookup uses `FUSE_LOOKUP`, creates/locates a `fuse_node`, sets the namecache vnode, and tracks `nlookup` except for `"."`, `".."`, and root-style cases.
- Create-like namespace operations consume `fuse_entry_out`, validate vnode type, allocate a node, cache returned attributes, update namecache, and emit knotes.
- Remove and rename attempt to release unopened target handles early to avoid `.fuse_hidden*` behavior, though comments note that simple `v_opencount` does not fully account for mmap/file pointer cases.
- `fuse_vop_readdir()` requests a large directory buffer and converts FUSE directory entries into DragonFly dirents using `vop_write_dirent()`.
- `fuse_vop_read()` uses `vop_helper_read_shortcut()` first, then falls back to buffer-cache block reads through `cluster_readx()` or `bread_kvabio()`.
- `fuse_vop_write()` enforces max file size and process file-size limits, extends the file through `fuse_reg_resize()`, manages partial/full block overwrite behavior, writes via buffer cache, updates dirty/modified flags, and clears setuid/setgid when required.
- `fuse_vop_strategy()` queues reads/writes on `fmp->bioq`; `fuse_io_thread()` drains the queue and `fuse_io_execute()` performs actual `FUSE_READ`/`FUSE_WRITE` IPC.
- `fuse_bmap()` presents file storage as contiguous to support clustering even though actual backing I/O is RPC-based.
- `fuse_reg_resize()` updates in-memory size, marks `sizeoverride`, and uses `nvtruncbuf()`/`nvextendbuf()` for VM/buffer object resizing.

Important dependencies:
- FUSE core types and helpers from `fuse.h`, including IPC allocation/fill/tx/put helpers.
- DragonFly VFS/namecache APIs: `cache_setvp`, `cache_unlink`, `cache_rename`, vnode finalization, vnode dirty state, and VOP helpers.
- Buffer cache and clustering APIs: `getblk`, `bread_kvabio`, `cluster_readx`, `cluster_write`, `vn_cache_strategy`.
- VM pager APIs: generic vnode pager getpages/putpages and object cleaning.
- kqueue/knote APIs for event delivery.

Notable risks and edge cases:
- Several unsupported or partially-used FUSE protocol fields are explicitly left unused.
- `FUSE_FORGET` paths are disabled because comments state sshfs fails when they are issued.
- Directory reading requests all entries at once with a fixed large buffer; the comment flags this as a limitation.
- Rename/remove cleanup relies on `v_opencount`, with comments warning this misses mmap and file-pointer subtleties.
- Strategy write error handling maps FUSE write failures to `EINVAL` on the buffer rather than preserving the exact FUSE error.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/Makefile

This is the kernel module makefile for DragonFlyBSD HAMMER. It declares `KMOD= hammer` and lists the C source files compiled into the HAMMER filesystem module.

Included subsystems:
- VFS and vnode operations: `hammer_vfsops.c`, `hammer_vnops.c`.
- Core object/inode/cursor/B-Tree code: `hammer_inode.c`, `hammer_object.c`, `hammer_cursor.c`, `hammer_btree.c`.
- On-disk and I/O machinery: `hammer_ondisk.c`, `hammer_io.c`, `hammer_blockmap.c`, `hammer_undo.c`, `hammer_redo.c`.
- Transactions, recovery, and flushing: `hammer_transaction.c`, `hammer_recover.c`, `hammer_flusher.c`.
- Admin/reorganization features: ioctl, reblock, rebalance, mirror, pseudofs, prune, volume, dedup.
- Kernel trace option header: `opt_ktr.h`.

The file ends by including DragonFly’s standard kernel-module build rules through `<bsd.kmod.mk>`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer.h

This is HAMMER’s central internal kernel header. It defines the in-memory structures, flags, helper inlines, global tunables/statistics, and cross-module function prototypes used by the HAMMER filesystem implementation. On-disk formats are delegated to `hammer_disk.h`, while this file models runtime state and internal APIs.

Major data structures:
- `hammer_transaction`: transaction state, TID, timestamp fields, sync-lock refs, flags, and root volume.
- `hammer_lock`: HAMMER’s custom ref/lock structure with reference flags, exclusive lock bits, owner tracking, and inline state tests.
- `hammer_pseudofs_inmem`: in-memory pseudo-filesystem metadata and locking.
- `hammer_objid_cache`: directory-local object-id allocation cache for locality.
- `hammer_node_cache`: cached B-Tree node search-start association.
- `hammer_flush_group`: chunked inode flush grouping to avoid exhausting the UNDO FIFO during large syncs.
- `hammer_inode`: core in-memory inode object, including RB-tree linkage, vnode pointer, pseudofs pointer, inode data cache, record tree, flush/sync copies, dirty flags, REDO tracking, and B-Tree node caches.
- `hammer_record`: unsynchronized in-memory record representation for directory entries, inode records, delete records, bulk data, and general metadata records.
- `hammer_io`: common header embedded in volumes and buffers for lock state, dirty/running state, buffer-cache association, modify refs, I/O callbacks, and flush/reclaim coordination.
- `hammer_volume`: in-memory wrapper around on-disk volume header and device vnode.
- `hammer_buffer`: in-memory wrapper for on-disk buffers and associated node list.
- `hammer_node`: in-memory wrapper for on-disk B-Tree nodes, including node lock, backing buffer, cursor list, cache list, and CRC/state flags.
- `hammer_node_lock`: recursive node-lock tree used by split/rebalance-style operations.
- `hammer_reserve`: blockmap big-block reservation used by direct write and delayed reuse protection.
- `hammer_undo`: recent undo history entry for avoiding duplicate undo records.
- `hammer_flusher`: master flusher state, sequencing, ready/run lists, transaction, and finalization lock.
- `hammer_mount`: full per-mount runtime state, including RB roots for inodes, volumes, nodes, buffers, undo/reservation trees, blockmaps, flusher, dirty-space counters, volume map, TID state, export state, locks, tokens, and statistics.

Important flags and constants:
- Transaction flags include new-inode and CRC-domain behavior.
- Inode flags cover dirty data, reserved resources, on-disk state, deletion state, read-only snapshot state, flush/reflush state, atime/mtime changes, REDO/RDIRTY state, truncation, and reclaim.
- Record flags distinguish allocated data, RB-tree membership, frontend/backend deletion, committed state, backend interlocks, waiters, delete conversion, and REDO.
- I/O types distinguish volume, metadata buffer, undo buffer, data buffer, and dummy buffer.
- Mount flags track critical errors, flush recovery, and REDO recovery state.
- Checkspace slop constants define reservation conservatism for reblock, mirror, write, create, remove, and emergency paths.

Important inline helpers:
- Lock/reference state checks for `hammer_lock`.
- `hammer_checkspace()` wrapper around `_hammer_checkspace()`.
- Convenience wrappers for lock acquisition, mem-record waits, and no-undo modifications.
- B-Tree node modification helpers, including full-node undo fallback and CRC scheduling through `HAMMER_NODE_NEEDSCRC`.
- `hammer_btree_extract_leaf()` and `hammer_btree_extract_data()` wrappers.
- `hammer_blockmap_lookup()`, which can skip verification when zone verification is disabled and direct-map to zone 2.
- Volume-number bitmap add/delete/test helpers.
- Buffer-to-HAMMER-IO attach/peek helpers.
- Directory localization helper for directory-local inode placement.

Function prototype coverage:
- VFS/vnode entry points and vnode acquisition.
- Inode lookup, creation, syncing, reclaim, unload, and dirtying.
- Volume and buffer installation, lookup, unload, reference/release, and sync/deletion.
- HAMMER object and record operations.
- Cursor navigation, lock upgrade/downgrade, recovery, and cursor mutation notifications.
- B-Tree lookup, iteration, insertion, deletion, propagation, node locking, parent lookup, and diagnostics.
- Block allocation, data allocation, blockmap reserve/finalize/free/dedup/checkspace.
- UNDO/REDO generation and recovery.
- Transaction start/finish and TID allocation.
- Directory entry and bulk-data operations.
- Pseudofs operations and ioctl handlers.
- Low-level I/O operations, direct read/write paths, interlocks, flushing, and error clearing.
- Administrative ioctls: reblock, rebalance, prune, mirror, pseudofs, volume add/delete/list, dedup.
- Flusher and recovery entry points.
- Block-size helpers and fsid conversion.

Architectural role:
- This header is the connective tissue for HAMMER’s kernel implementation. It exposes almost every internal subsystem boundary, so changes here affect the whole filesystem.
- It separates on-disk formats from in-memory synchronization, caching, and transactional behavior.
- The code assumes careful coordination between `fs_token`, `io_token`, HAMMER locks, buffer modify refs, cursor locks, and flusher sequencing.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_blockmap.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_blockmap.c

This file implements HAMMER’s blockmap allocation, reservation, free, dedup accounting, lookup verification, and space-checking logic. The blockmap maps logical HAMMER zone offsets through layered free-space metadata to physical zone-2 storage and coordinates crash-safe reuse of big-blocks.

Core structures used:
- Per-mount blockmaps from `hmp->blockmap[]`.
- Freemap layer1 entries, which point to layer2 blocks and track free big-block counts.
- Freemap layer2 entries, one per big-block, tracking owning zone, append offset, free bytes, and CRC.
- `hammer_reserve` RB tree keyed by zone-2 big-block base offset.
- Delay list reservations used to prevent unsafe reuse before flusher cycles complete.

Main functions:
- `hammer_blockmap_alloc()`: backend allocation from a zone.
- `hammer_blockmap_reserve()`: frontend reservation without committing metadata, mainly for direct-write paths.
- `hammer_blockmap_reserve_complete()`: reference release and possible buffer invalidation for reserved big-blocks.
- `hammer_reserve_clrdelay()`: removes delayed reservations when their flush point is reached.
- `hammer_blockmap_free()`: frees allocated space and may reset entirely-free big-blocks.
- `hammer_blockmap_dedup()`: adjusts accounting for deduplicated references, allowing `bytes_free` to become negative.
- `hammer_blockmap_finalize()`: commits a previously reserved range into the blockmap.
- `hammer_blockmap_getfree()`: reports approximate free bytes in a big-block for reblocker use.
- `hammer_blockmap_lookup_verify()`: validates layer1/layer2 metadata and returns translated zone-2 offset.
- `_hammer_checkspace()`: computes reserved/dirty/slop pressure against copied free-big-block statistics.
- `hammer_check_volume()` and `hammer_skip_volume()`: handle unavailable volume ranges and volume wrapping.

Allocation behavior:
- Request sizes are aligned with `HAMMER_DATA_DOALIGN`.
- Allocations are constrained not to cross buffer boundaries, and large allocations must not cross big-block boundaries.
- Optional hints are honored only while they stay in the hinted big-block and requested zone.
- The allocator skips full layer1 ranges, unavailable volume ranges, layer2 entries owned by another zone, entries whose append offset is past the candidate offset, and big-blocks reserved by other zones.
- Metadata updates are protected by `hmp->blkmap_lock`, but layer reads and CRC checks occur before lock acquisition and are revalidated around races.
- When a layer2 big-block is first claimed, layer1 free count and root-volume free-big-block statistics are decremented.
- `blockmap->next_offset` is advanced when no usable external hint was supplied.

Reservation behavior:
- `hammer_blockmap_reserve()` reserves address space and advances the zone’s `next_offset` without updating layer1/layer2 ownership/free-byte metadata.
- Reservations prevent other zones or allocation paths from using the same big-block range before finalization.
- If a reserved big-block is entirely free at layer2, the reservation records `HAMMER_RESF_LAYER2FREE`, enabling later invalidation/deletion of stale buffers.
- `hammer_blockmap_finalize()` assigns layer2 ownership if needed, decrements free bytes, clears layer2-free reservation state, and raises `append_off` to cover the finalized range.

Free/reuse safety:
- `hammer_blockmap_free()` increments layer2 free bytes. When the entire big-block becomes free, it installs a delayed reservation before resetting layer2 zone and append state.
- Delayed reservations avoid crash-recovery hazards where an old UNDO/REDO state could resurrect a block already reused and overwritten.
- `hammer_blockmap_reserve_complete()` can delete related HAMMER buffers for a fully-free reserved big-block, but if buffer deletion conflicts it requeues the reservation on the delay list.

CRC and corruption handling:
- Layer1 and layer2 CRCs are tested on read. If an initial test fails, the blockmap lock is acquired and the test is retried before panic.
- Layer1/layer2 CRCs are regenerated after metadata modifications.
- Lookup verification asserts zone consistency and handles the special case where layer2 is unassigned but a matching reservation exists.

Space accounting:
- `_hammer_checkspace()` estimates pressure from reserved inodes, reserved records, reserved data bytes, delayed reservations, dirty buffer limits, and caller-provided slop.
- Free space is checked against `hmp->copy_stat_freebigblocks`, a mount-level copy of root-volume free-big-block state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_blockmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_btree.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_btree.c

This file implements HAMMER’s modified B+Tree search, iteration, insertion, deletion, splitting, removal, mirror-TID propagation, child locking, comparison, and debug printing. The tree stores records only in leaves while internal nodes carry boundary elements that allow cursors to begin searches from cached interior positions instead of always starting at the root.

Core model:
- Internal nodes contain left/right boundary information and subtree pointers.
- Leaf nodes contain record elements only.
- Internal node `count` excludes the right boundary; leaf node `count` is the number of records.
- Searches can start from arbitrary cursor positions and move up/down until the key falls inside current bounds.
- Insertions split full nodes top-down while descending.
- Deletions remove leaf records and may recursively remove empty nodes, but avoid creating empty internal nodes.
- Historical as-of lookup is integrated into the key-search logic through `create_tid` and `delete_tid`.

Traversal and lookup:
- `hammer_btree_lookup()` searches for `cursor->key_beg`, with special handling for `HAMMER_CURSOR_ASOF`.
- `btree_search()` is the core search engine. It moves upward until bounds cover the key, then descends through internal nodes using boundary comparisons and binary-assisted scans.
- `hammer_btree_first()` and `hammer_btree_last()` position cursors for forward or reverse range iteration.
- `hammer_btree_iterate()` advances forward through leaves, moving up/down internal nodes as needed, observing `key_end`, inclusive/exclusive end behavior, ASOF visibility, and mirror-filter skipping.
- `hammer_btree_iterate_reverse()` mirrors forward iteration for reverse scans, especially pruning, without mirror filtering.
- `hammer_btree_search_node()` uses a coarse binary search shortcut before linear checks.

Historical record handling:
- `hammer_btree_cmp()` compares localization, object id, record type, key, and create TID, returning magnitude values that indicate which field differed.
- A create TID of zero sorts as positive infinity.
- `hammer_btree_chkts()` determines whether a record is visible at an as-of TID.
- `btree_search()` can set `HAMMER_CURSOR_CREATE_CHECK` and `cursor->create_check` when an as-of lookup might have descended too far right due to create-TID boundary placement. `hammer_btree_lookup()` retries with the adjusted create TID.

Extraction:
- `hammer_btree_extract()` records the current leaf element in the cursor and optionally reads associated data through `hammer_bread_ext()`.
- Data CRC is verified with `hammer_crc_test_leaf()`.
- CRC failure can return `EDOM` for less-critical mirror-domain transactions or `EIO` otherwise.
- Bulk data buffers can be marked non-metadata to avoid inappropriate metadata treatment.

Insertion:
- `hammer_btree_insert()` requires a cursor previously positioned by an insert-mode lookup returning `ENOENT`.
- It upgrades the cursor node, shifts leaf elements, inserts the new leaf, updates count and cursor tracking, and updates node mirror TID aggregation.
- It returns a propagation hint through `doprop` when the inserted record’s create/delete TID raises the node mirror TID.

Deletion:
- `hammer_btree_delete()` upgrades the cursor, removes the current leaf element, updates cursor tracking, and calls `btree_remove()` if the leaf becomes empty.
- Empty leaf removal may recurse upward. If deadlock prevents full cleanup, empty leaves can remain for later cleanup.
- Deletion tracks optionally how many B-Tree nodes were deleted.

Splitting:
- `btree_split_internal()` splits a full internal node, promotes a separator into the parent, fixes child parent pointers, and creates a new root if splitting the filesystem root.
- `btree_split_leaf()` splits a full leaf, creates a separator between adjacent leaf keys using `hammer_make_separator()`, inserts it into the parent, and creates a new root if needed.
- Split points are normally near half, but append-like insertion at the end uses a three-quarter split heuristic unless the node has been marked nonlinear.
- Splits carefully adjust cursor node/index, parent index, and left/right bounds.

Node removal:
- `btree_remove()` handles deletion of empty leaves or one-element internal nodes.
- Removing the root converts it into an empty leaf.
- For parent count greater than one, it removes the parent’s subtree pointer, preserves mirror TID coverage, updates cursor tracking, deletes the node, and moves the cursor upward.
- For parent count one, it uses `hammer_cursor_up_locked()` and recursive removal, with deadlock-aware fallback.

Mirror support:
- `hammer_btree_do_propagation()` propagates a leaf/node mirror TID upward after modifications, using a pushed cursor so the original cursor can be temporarily unlocked and restored.
- `hammer_btree_mirror_propagate()` updates parent internal elements and node aggregate mirror TIDs until no higher propagation is needed.
- `hammer_cursor_mirror_filter()` computes skipped key ranges when mirroring can skip entire subtrees whose aggregate mirror TID is older than the requested mirror TID.

Recursive child locking and rebalance support:
- `hammer_btree_lock_children()` exclusively locks child subtrees to protect cursor consistency during split/rebalance operations.
- It prefetches children before taking exclusive locks to avoid blocking on I/O while holding locks.
- `hammer_btree_lcache_init()` and `hammer_btree_lcache_free()` preallocate node-lock/cache structures and node copies for deep rebalance operations.
- `hammer_btree_lock_copy()` snapshots locked nodes in memory.
- `hammer_btree_sync_copy()` writes modified copies back to real nodes and deletes nodes marked deleted.
- `hammer_btree_unlock_children()` releases recursive locks and returns cached structures.

Parent/child helpers:
- `hammer_btree_get_parent()` loads and locks a node’s parent, then finds the parent element pointing to the child.
- `btree_set_parent_of_child()` updates a moved child’s parent pointer when internal elements move during splits.
- `btree_node_is_full()` checks type-specific node capacity.

Debug support:
- `hammer_print_btree_node()` and `hammer_print_btree_elm()` dump node and element state.
- Inline debug helpers print cursor, element, parent, key, and comparison information when B-Tree debugging is enabled.

Important invariants:
- Internal elements must have nonzero subtree offsets.
- Leaf elements must be record elements.
- Cursor bounds must contain the selected node and insertion key after splits.
- Empty internal nodes are not allowed.
- Root splitting updates `vol0_btree_root`.
- Modifications use HAMMER node modification helpers so undo/CRC/dirty tracking is preserved.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_btree.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_btree.h

This header defines HAMMER’s on-disk B-Tree element and node structures, localization constants, element type constants, capacity constants, and small helper predicates. It documents HAMMER’s modified B+Tree design: records live only in leaves, while internal nodes include built-in left/right boundary information.

Key structures:
- `hammer_base_elm`: common key and type prefix for all B-Tree elements. Sort priority is localization, object id, record type, key, and create TID. It also stores delete TID, object type, element type, and localization.
- `hammer_btree_internal_elm`: base element plus mirror TID and subtree offset.
- `hammer_btree_leaf_elm`: base element plus create/delete timestamps, data offset, data length, and data CRC.
- `hammer_btree_elm`: union overlay for base, internal, and leaf element views.
- `hammer_node_ondisk`: 4 KB on-disk node containing CRC, parent pointer, count, node type, mirror TID aggregator, reserved fields, and 63 element slots.

Localization:
- Lower 16 bits encode localization type, including inode and misc.
- Upper 16 bits encode pseudo-filesystem id.
- Helper macros convert between localization and PFS id.
- The root inode uses the default localization.

Element and node constants:
- B-Tree element/node types include internal, leaf, record, deleted, and none.
- Leaf nodes hold 63 elements.
- Internal nodes logically hold one fewer element because the final physical element is a right boundary.
- `HAMMER_BTREE_CRCSIZE` excludes the CRC field itself.

Inline helpers:
- `hammer_is_internal_node_elm()` identifies internal-node child references.
- `hammer_is_leaf_node_elm()` identifies leaf record elements.
- `hammer_node_max_elements()` returns type-specific node capacity.
- `hammer_elm_btype()` maps element type to printable characters, including fallbacks for none and unknown types.

Architectural role:
- This header is included through HAMMER disk/internal headers and underpins all B-Tree search, update, CRC, mirror, and cursor logic.
- It is an on-disk ABI definition; layout changes affect filesystem compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_crc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_crc.h

This header centralizes HAMMER CRC calculation, setting, and testing for blockmaps, freemap layers, volume headers, FIFO heads, B-Tree nodes, B-Tree leaf data, and mirror record heads. It supports compatibility across HAMMER volume versions that use different CRC algorithms.

CRC version behavior:
- For volume versions up to 6, CRCs use `crc32`.
- For volume version 7 and later, CRCs use `iscsi_crc32`.
- Test functions first check the current-version CRC and, for version 7 or newer, also accept a version-6 CRC. This supports upgraded filesystems whose existing metadata has not yet been rewritten with the newer algorithm.
- Newly created or rewritten metadata uses the mounted filesystem’s current version.

Covered structures:
- Blockmap entries: `hammer_crc_get/set/test_blockmap`.
- Freemap layer1 entries: `hammer_crc_get/set/test_layer1`.
- Freemap layer2 entries: `hammer_crc_get/set/test_layer2`.
- Volume headers: `hammer_crc_get/set/test_volume`, combining two CRC ranges around the stored CRC field.
- FIFO heads: `hammer_crc_get/set/test_fifo_head`, excluding the CRC field.
- B-Tree nodes: `hammer_crc_get/set/test_btree`, excluding the first CRC field.
- B-Tree leaf data: `hammer_crc_get/set/test_leaf`.
- Mirror record heads: `hammer_crc_get/set/test_mrec_head`, always using `crc32`.

Leaf-data special cases:
- Zero-length data returns CRC zero.
- Inode record data CRC excludes atime and mtime fields by using `HAMMER_INODE_CRCSIZE`, allowing those timestamp fields to be updated in place.
- Kernel invariant checks assert inode data length matches `struct hammer_inode_data` when appropriate.

Userspace/kernel split:
- When not compiling in kernel mode, the file declares CRC function prototypes because userspace cannot include the kernel `systm.h` declarations.

Architectural role:
- This header lets blockmap, B-Tree, I/O, recovery, mirroring, and userspace tooling share consistent integrity rules.
- The compatibility fallback is important for online upgrades and gradual metadata/data CRC modernization through reblocking.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_crc.h -->