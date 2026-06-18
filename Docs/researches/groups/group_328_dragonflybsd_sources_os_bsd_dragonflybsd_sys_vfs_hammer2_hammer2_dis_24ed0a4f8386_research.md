# Group Research: group_328_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer2_hammer2_dis_24ed0a4f8386

Scope: `Docs/research_subset_a.md`, DragonFlyBSD HAMMER2 VFS sources. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_disk.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_disk.h

## Purpose
Defines HAMMER2's on-disk media ABI: allocation geometry, freemap layout, block references, inode records, PFS identity fields, volume headers, checksum/compression encodings, and the union used to interpret 64KB media buffers.

## Major Definitions
- Allocation geometry: minimum allocation is 1KB (`HAMMER2_ALLOC_MIN`, radix 10), current maximum is 64KB (`HAMMER2_ALLOC_MAX`, radix 16), logical buffer size is 16KB, physical buffer size is 64KB, and allocation/freemap segment size is 4MB.
- Indirect topology: blockrefs are 128 bytes, arranged in fully associative sets of 4 in embedded inode blocksets, with indirect blocks supporting 4KB to 64KB payloads.
- Offset encoding: `hammer2_off_t` stores a 64-byte-aligned physical offset in the high bits and the allocation-size radix in the low 6 bits; radix 0 is a special no-data value.
- Freemap geometry: reserved 4MB area per 1GB region, eight rotating freemap copies, levels from 1GB leaves through 4EB nodes, and a level-6 blockset in the volume header for 16EB reach.
- Freemap bitmap model: 4MB `hammer2_bmap_data` entries use 8 x 64-bit words, two bits per 16KB region, with `00` free, `10` possibly free, and `11` allocated.
- DMSG/cluster configuration: `hammer2_volconf` and `dmsg_lnk_hammer2_volconf` describe copy targets, PFS cluster IDs, priorities, labels, and remote paths.
- Core media objects: `hammer2_blockref`, `hammer2_blockset`, `hammer2_bmap_data`, `hammer2_inode_meta`, `hammer2_inode_data`, `hammer2_volume_data`, and `hammer2_media_data`.

## On-Disk Structures
- `hammer2_blockref` is the core recursive pointer. It carries object type, check/compression methods, copy ID, key range, mirror/modify/update tids, physical data offset, embedded directory entry or aggregate stats, and a 64-byte check area.
- `hammer2_inode_data` is exactly 1024 bytes: 256 bytes of metadata, 256 bytes of filename storage, and 512 bytes of direct data or an embedded blockset.
- `hammer2_volume_data` is exactly 64KB. It contains magic/version fields, boot/aux ranges, volume sizing, allocator counters, mirror/freemap tids, copy-existence bitmap, CRC sectors, super-root blockset, freemap blockset, volume logical offsets, and 256 copyinfo records.
- `hammer2_media_data` overlays the same 64KB physical buffer as volume data, inode data, blockset, indirect blockref array, freemap bitmap array, or raw bytes.

## Filesystem Semantics Captured Here
- HAMMER2 is COW; any modification propagates check code and mirror tid upward through the blockref tree.
- Directory entries and inodes share the blockref topology. Small file data can live directly inside the inode, making tiny files directory-local.
- PFS roots are directories under the super-root and are identified by both cluster ID (`pfs_clid`) and filesystem ID (`pfs_fsid`).
- PFS type encodings support cache, slave, soft-slave, soft-master, master, super-root, dummy, and transition states.
- Volume headers exist in four 2GB-spaced copies; the mount code can choose a consistent synchronization point after a crash.

## Important Invariants
- Many structures are packed and size-sensitive; comments repeatedly note exact 128-byte, 1024-byte, and 64KB requirements.
- The freemap assumes `HAMMER2_SET_COUNT == 4`, enforced by preprocessor checks.
- `HAMMER2_VOLUME_ALIGN` and `HAMMER2_ZONE_SEG` must align to the 4MB freemap level-0 size.
- Host byte order is the normal media format; reversed-endian compatibility would require explicit access adjustment.
- Volume versions before multi-volume support imply a single root volume; version 2 supports up to 64 volumes.

## Interactions
- Used by nearly every HAMMER2 implementation file for media layout and constants.
- `hammer2_freemap.c` consumes the freemap geometry and bitmap definitions.
- `hammer2_flush.c` updates blockref checks, mirror tids, and volume-header CRCs.
- `hammer2_inode.c` mirrors `hammer2_inode_meta` into in-memory inodes.
- `hammer2_ioctl.c` exposes PFS, inode, volume, and remote-copy fields to userland.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_flush.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_flush.c

## Purpose
Implements HAMMER2 transaction accounting and recursive COW flush propagation. It converts modified chain state into updated media blockrefs, manages parent block-table updates, flushes freemap and topology roots, and coordinates volume-header synchronization.

## Transaction Handling
- `hammer2_trans_init()` increments per-PFS transaction state and serializes flush transactions against other flushes. Buffer-cache transactions are allowed through to avoid deadlocks.
- `hammer2_trans_sub()` allocates a new cluster-level modify tid (`modify_tid`) for sequenced XOPs inside a transaction.
- `hammer2_trans_setflags()` and `hammer2_trans_clearflags()` modify transaction state atomically and wake waiters when `HAMMER2_TRANS_WAITING` clears.
- `hammer2_trans_done()` decrements the transaction count, clears flags supplied by the caller, and wakes waiters when a flush completes or pending flushes can proceed.
- `hammer2_trans_newinum()` atomically allocates inode numbers.
- `hammer2_trans_assert_strategy()` is currently permissive; historical assertions disallowing strategy during flush are disabled.

## Flush Algorithm
- `hammer2_flush()` prepares a `hammer2_flush_info` context, references the parent and target chain, and repeatedly invokes `hammer2_flush_core()` until parent movement no longer requires retry.
- `hammer2_flush_core()` is the main recursive state machine:
  - Returns quickly if no flush-relevant chain flags are present.
  - Stops at mounted PFS boundaries unless `HAMMER2_FLUSH_ALL` is requested, while preserving parent `ONFLUSH` if work remains below.
  - Optionally stops at inode boundaries for `HAMMER2_FLUSH_INODE_STOP`.
  - Recurses down on `ONFLUSH` or `DESTROY`, then performs bottom-up work.
  - Locks parent then child in the required order before modifying parent block tables.
  - Clears `MODIFIED`, updates checksums/statistics, handles destroyed chains, and processes `UPDATE`.
- `hammer2_flush_recurse()` is the RB-tree child scanner. It references children before dropping the parent spinlock, handles parent movement races, propagates destroy state, and skips hidden PFS-root inode-index entries during non-filesystem-sync flushes.

## Media-Specific Flush Behavior
- `HAMMER2_BREF_TYPE_FREEMAP`: updates `voldata.freemap_tid`, asserts vchain is modified, and bumps `voldata.mirror_tid` so topology and freemap recovery remain distinguishable.
- `HAMMER2_BREF_TYPE_VOLUME`: locks fchain, updates `voldata.mirror_tid`, computes sector and full-header iCRCs, copies `voldata` to `volsync`, and marks `HAMMER2_CHAIN_VOLUMESYNC`.
- `DATA`: assumes data has already been written through file buffer-cache paths.
- `INDIRECT`, `FREEMAP_NODE`, `FREEMAP_LEAF`, non-inline `DIRENT`, and `INODE`: recompute chain checks; PFS-root inodes also copy `pmp->inode_tid` into media.
- Destroyed modified chains have dedup candidacy deleted and have disabled code for DIO invalidation.

## Parent Block-Table Updates
- `UPDATE` with no parent is simply cleared.
- Non-FSSYNC inode flushes with `HAMMER2_FLUSH_INODE_STOP` intentionally avoid updating the parent block table, preserving dependency ordering across crashes.
- Destroyed parents skip real block-table rewrites and only carry forward the child's modify tid.
- Indirect blocks receive maintenance for deletion/collapse before parent updates.
- Parent modification errors, including ENOSPC, are accumulated but do not abort recursive flushing; the child `UPDATE` flag is restored.
- Parent blockref arrays are selected from inode embedded blocksets, indirect/freemap-node arrays, volume super-root blockset, or freemap array depending on parent type.

## Backend Flush XOP
- `hammer2_xop_inode_flush()` flushes a single inode chain for a cluster element, optionally with inode-stop, filesystem-sync, and volume-header flags.
- For PFS roots, it can flush the super-root, fchain, vchain, device buffers, and then a rotated volume header.
- Device buffers are fsynced before writing `volsync` to the selected volume-header slot.
- The volume header write is preceded by a device `BUF_CMD_FLUSH` for ordering.

## Concurrency and Failure Notes
- Uses atomic chain flags, chain refs/holds, chain locks, spinlocks for child RB scans, and transaction wait channels.
- Parent-child races are explicitly detected as `LOST CHILD` cases and retried or skipped.
- Recursion depth above 60 panics rather than deferring; the surrounding comments describe deferral support, but current code uses a hard panic.
- Flush errors are cumulative in `info.error`, but later buffer writeback errors may occur after the flush call returns.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_flush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_freemap.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_freemap.c

## Purpose
Implements HAMMER2 media allocation and freemap recovery adjustment. It allocates normal data/metadata from bitmap leaves, reserves freemap blocks algorithmically in rotating reserved zones, initializes new freemap leaves, and marks recovered allocations after mount-time repair.

## Allocation State
- `hammer2_fiterate` tracks the preferred allocation offset, next scan offset, loop count, and whether relaxed class allocation has been entered.
- Allocation heuristics are indexed by blockref type and device block radix so different object classes can maintain locality.
- `hmp->freemap_relaxed` allows allocation from any class once stricter class matching has exhausted space.

## Freemap Block Reservation
- `hammer2_freemap_reserve()` handles freemap node/leaf storage. These blocks are not allocated from the freemap; they are placed in reserved 4MB zones at deterministic offsets.
- Existing freemap blocks rotate through eight copies, using the current data offset to choose the next reserved slot.
- The reserved slot depends on freemap level: level 1 leaf, levels 2-5 node, and the corresponding 64KB block inside the reserved segment.

## Normal Allocation
- `hammer2_freemap_alloc()` validates power-of-two allocation sizes, obtains an `mtid`, handles zero-byte allocation by clearing `data_off`, and delegates freemap-node/leaf allocation to the reserve path.
- Normal allocations must be 1KB through 64KB.
- It locks `hmp->fchain`, initializes iteration from the heuristic offset, repeatedly calls `hammer2_freemap_try_alloc()` while it returns EAGAIN, stores the new heuristic offset, and releases fchain.

## Leaf Lookup and Creation
- `hammer2_freemap_try_alloc()` looks up the level-1 freemap leaf covering the next candidate offset.
- If no leaf exists, it creates one through `hammer2_chain_create()`, modifies it, zeros its data, initializes `bigmask` and `avail`, and calls `hammer2_freemap_init()`.
- Existing leaves are skipped early if their `bigmask` says the requested radix cannot fit.
- Allocation scans the 256 level-0 entries in locality order, first forward from the start index and then backward.
- A bmap is considered usable if it has bitmap-granular availability or has a partial linear region for sub-16KB allocations.
- Class matching prefers empty or matching `(type << 8) | HAMMER2_PBUFRADIX` entries unless relaxed mode is active.
- On success, the target blockref receives `key | radix`, and data block allocations register dedup bits while the freemap leaf is still locked.
- On ENOSPC, `hammer2_freemap_iterate()` advances by 1GB leaves, wraps, and eventually switches to relaxed mode before returning real ENOSPC.

## Bitmap Allocation
- `hammer2_bmap_alloc()` allocates within a 4MB `hammer2_bmap_data`.
- Sub-16KB allocations can use the `linear` byte cursor inside an already allocated 16KB bitmap chunk.
- Larger allocations or block-aligned small allocations search the bitmap for clear two-bit groups; data blocks can use the low bits of the logical key to preserve sequential on-disk layout.
- It opportunistically calls `hammer2_io_newnz()` on a containing 64KB physical buffer if the whole physical buffer is newly unused, avoiding read-before-write.
- Availability and `allocator_free` are updated at bitmap granularity, not fine allocation granularity, because bulkfree cannot reconstruct sub-16KB allocation state.

## Freemap Initialization
- `hammer2_freemap_init()` marks unavailable portions of a new 1GB leaf as allocated:
  - Static allocations made by `newfs_hammer2`.
  - Reserved zone segment at the base of each applicable zone.
  - Trailing space past end-of-volume.
- Usable 4MB entries start with full availability; unavailable ones get all bitmap bits set, `avail = 0`, and `linear = HAMMER2_SEGSIZE`.

## Recovery Adjustment
- `hammer2_freemap_adjust()` is currently asserted for `HAMMER2_FREEMAP_DORECOVER`.
- It marks referenced blocks allocated during recovery when freemap updates may not have reached stable media before a crash.
- Static `newfs_hammer2` allocations are ignored because they predate dynamic freemap management.
- Missing leaves are created and initialized during recovery.
- The function sets bitmap bits to allocated, updates class if needed, reduces bmap availability and volume `allocator_free` at 16KB granularity, resets the linear allocator after modifications, sets `bigmask = -1`, and clears relaxed mode.
- Disabled code documents older may-free/real-free handling but notes availability accounting and state `10` semantics no longer match that implementation.

## Bulkfree Context
- The file ends with documentation for three-stage freemap validation:
  - Stage 1: allocated to possibly-free.
  - Stage 2: topology scan returns live blocks to allocated.
  - Stage 3: vetted possibly-free blocks become free.
- The implementation in this file does not include the bulkfree pass itself; it provides allocation and recovery primitives consumed by other HAMMER2 code.

## Important Constraints
- Reserved zones must never be dynamically allocated; successful normal allocation asserts the result is beyond `allocator_beg`, inside `total_size`, and past the zone reserved segment.
- Allocation hints are permissive. Clearing `bigmask` requires a full relaxed scan from the beginning; otherwise the allocator avoids making restrictive assumptions.
- Sub-16KB allocations cause deliberate internal accounting loss after unmount/reboot because only the 16KB bitmap state persists.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_freemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_inode.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_inode.c

## Purpose
Implements HAMMER2 in-memory inode lifecycle, locking, dependency grouping for sync, vnode association, inode creation, directory-entry creation, cluster repointing, unlink finalization, and synchronization of frontend inode state into backend chains.

## Inode Hashing and References
- `hammer2_inum_hash_init()` initializes per-PFS inode hash bucket spinlocks.
- `inumhash()` maps inode numbers to hash buckets.
- `hammer2_inode_lookup()` returns referenced in-memory inodes by inode number, except for super-root PFS contexts where duplicate inums prevent indexing.
- `hammer2_inode_ref()` increments refs and has optional debug tracing.
- `hammer2_inode_drop()` handles last-reference teardown: removes the inode from the hash, decrements PFS counts, clears cluster references via `hammer2_inode_repoint(ip, NULL)`, and frees the object.

## Locking and Sync Dependencies
- `hammer2_inode_lock()` supports shared and exclusive locks. Exclusive locks enforce SYNCQ semantics: if the inode is already staged for sync, it is moved to the front of the sync queue and the caller sleeps until safe.
- `hammer2_inode_lock4()` locks two to four inodes together, builds or merges dependency groups, and waits if any locked inode is on SYNCQ.
- `hammer2_inode_unlock()` wakes waiters marked by `HAMMER2_INODE_SYNCQ_WAKEUP` and drops the reference acquired by lock.
- Temporary release/restore and shared-to-exclusive upgrade/downgrade helpers wrap the inode mutex.
- `hammer2_inode_setdepend_locked()` is the core dependency merger. It handles SIDEQ, SYNCQ, PASS2, self-dependencies, dependency queue merging, and transaction rescan signaling.
- `hammer2_inode_depend()` groups two locked inodes so metadata dependencies such as directory entry and nlink updates are flushed together.
- `hammer2_inode_delayed_sideq()` places dirty inodes on the side queue lazily.

## Chain Access and Cluster Repointing
- `hammer2_inode_chain()` selects and locks a chain at a cluster index.
- `hammer2_inode_chain_and_parent()` obtains child and parent in lock order, retrying if the relationship changes.
- `hammer2_inode_repoint()` replaces all chains in an inode's embedded cluster, drops cached data chains, updates focus and flags, and drops old chain refs after releasing the spinlock.
- `hammer2_inode_repoint_one()` updates one cluster element, used by synchronization threads for piecemeal cluster updates.
- `hammer2_inode_data_count()` and `hammer2_inode_inode_count()` report maximum aggregate stats across cluster chains.

## Vnode Integration
- `hammer2_igetv()` returns an exclusively locked vnode for an inode, reusing an existing vnode when possible while dropping the inode lock around `vget()` to avoid reclaim deadlocks.
- It allocates new vnodes with type-specific setup:
  - Directories become `VDIR`.
  - Regular files and symlinks use VKVABIO and VMIO initialized to logical buffer size.
  - Character/block devices use spec ops and aliases.
  - FIFOs use fifo ops.
  - Sockets become `VSOCK`.
- The PFS root vnode is marked `VROOT`.

## Inode Creation
- `hammer2_inode_get()` returns an existing or new in-memory inode synchronized to an XOP cluster. It handles insertion races into the inode hash and can create super-root/PFS-style unindexed inodes.
- `hammer2_inode_create_pfs()` creates a PFS inode under the super-root inside a flush transaction. It computes a directory hash key, scans for collision-free low hash bits, builds metadata, creates the media chain through XOPs, and returns the locked inode.
- `hammer2_inode_create_normal()` creates regular inodes in memory and detached backend chains during a normal transaction. It sets metadata from parent/vattr/credentials, handles device numbers and uid/gid inheritance, enables direct data for regular files and symlinks, and marks the inode `HAMMER2_INODE_CREATING` for later insertion.
- `hammer2_dirent_create()` creates a directory entry under a locked directory, resolving name-hash collisions and issuing a mkdirent XOP.

## Unlink and Deletion
- `hammer2_inode_unlink_finisher()` decrements `nlinks`, marks zero-link inodes as unlinked, queues vnode recycling when possible, and queues no-vnode inodes for deletion.
- `hammer2_inode_vprecycle()` aggressively finalizes a vnode after unlink to allow reclaim of zero-link inodes.
- `hammer2_inode_chain_des()` turns `HAMMER2_INODE_DELETING` into a backend destroy XOP and clears both deleting and unlinked flags.

## Inode Sync
- `hammer2_inode_modify()` marks in-memory metadata dirty, marks an associated vnode dirty, and queues the inode unless `NOSIDEQ` is set.
- `hammer2_inode_chain_sync()` pushes in-memory metadata and resize state to backend chains. It clears direct-data mode when size exceeds embedded capacity and starts an fsync XOP.
- `hammer2_inode_chain_ins()` inserts newly created detached inode chains into the media topology during sync.
- `hammer2_inode_chain_flush()` clears `DIRTYDATA`, starts the inode flush XOP, waits for all cluster elements, and treats ENOENT as success.

## Concurrency and Edge Cases
- The code intentionally separates inode locks from chain locks to avoid confusing multi-holder inode state and chain lifecycle.
- SYNCQ/PASS2 logic is designed to prevent crash-inconsistent splits between related inode updates.
- Super-root PFS contexts are special because inode number uniqueness is not guaranteed.
- `hammer2_inode_get()` temporarily unholds XOP clusters to avoid deadlocks against vnode recycling.
- Creation APIs distinguish PFS creation, which inserts directly into the super-root during a flush transaction, from normal inode creation, which defers media topology insertion.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_io.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_io.c

## Purpose
Provides HAMMER2's device I/O abstraction (`hammer2_io_t`) over DragonFly buffer-cache buffers. It maps smaller logical allocations into 64KB physical buffers, handles read/new/write lifecycle, tracks dirty state, caches DIO objects in a hash table, and records dedup-validity bits.

## DIO Hashing and Allocation
- `hammer2_io_hash_init()` initializes per-device DIO hash spinlocks.
- `hammer2_io_alloc()` maps a `data_off|radix` to a 64KB physical base, looks for an existing DIO, or creates one when requested.
- It validates that the logical allocation fits within one 64KB physical buffer and resolves the backing volume/device via `hammer2_get_volume()`.
- DIO refs use low bits as a reference count plus high state flags such as GOOD, INPROG, WAITING, DIRTY, and FLUSH.
- Reusing a free DIO decrements `hmp->iofree_count`; creating a new one increments global DIO count.

## Buffer Acquisition
- `_hammer2_io_getblk()` handles read, new-zeroed, new-nonzero, and quick-read operations.
- If a DIO is already GOOD, it returns immediately after optional zeroing/dirty marking.
- Otherwise it atomically owns `INPROG`, waits on concurrent owners as needed, and performs `getblk()`, `breadnx()`, or `cluster_readx()` depending on operation and clustering settings.
- Metadata and data reads use separate tunables (`hammer2_cluster_meta_read`, `hammer2_cluster_data_read`), and data buffers are tagged `B_NOTMETA`.
- New allocations can avoid reads when logical allocation exactly matches the physical DIO; partial-new operations read first and then zero/dirty the requested range.
- Buffers are synchronized for KVA access with `bkvasync()` and associated with the kernel process via `BUF_KERNPROC()`.

## Buffer Release and Writeback
- `_hammer2_io_putblk()` decrements references. On the last reference, it clears GOOD/DIRTY, marks INPROG, detaches the buffer, and then releases or schedules writeback.
- Dirty DIOs normally use delayed write (`bdwrite`) to accumulate writes and avoid chain-lock-driven write/read churn.
- If `HAMMER2_DIO_FLUSH` is set, dirty DIOs use clustered write or async write depending on write clustering tunables.
- Clean buffers are released by `bqrelse()` unless error/invalidation flags require `brelse()`.
- DIO objects remain cached after buffer release; `iofree_count` drives cleanup pressure.
- `_hammer2_io_bawrite()`, `_hammer2_io_bdwrite()`, and `_hammer2_io_bwrite()` set dirty/flush flags then drop the DIO.

## Public Helpers
- `hammer2_io_new()` creates a zeroed DIO range.
- `hammer2_io_newnz()` creates a DIO range without zeroing the target data.
- `_hammer2_io_bread()` reads a DIO range.
- `_hammer2_io_getquick()` returns a DIO only if already cached.
- `hammer2_io_data()` returns a pointer to the logical range within the physical buffer.
- `hammer2_io_setdirty()` marks an already-held DIO dirty.
- `hammer2_io_bkvasync()` synchronizes a held buffer for KVA access.
- `_hammer2_io_ref()` adds a reference to an already-owned DIO.
- `hammer2_io_inval()` is currently a no-op placeholder for destroyed metadata invalidation.

## Dedup Tracking
- `hammer2_io_dedup_set()` creates/references a DIO without needing a buffer and marks dedup allocation bits while clearing validation bits.
- `hammer2_io_dedup_delete()` clears allocation and validation bits for data blocks when allocations are destroyed or bulkfree invalidates candidates.
- `hammer2_io_dedup_assert()` asserts no dedup allocation bits are set for a range, useful for transitions to free.
- Dedup operations are synchronized with freemap allocation/free state through the DIO object rather than the buffer cache buffer.

## Cleanup
- `hammer2_io_hash_cleanup()` scans hash buckets, ages inactive DIOs via `act` and `ticks`, removes free non-INPROG DIOs, and frees them outside locks.
- `hammer2_io_hash_cleanup_all()` destroys every DIO for a media device during teardown and asserts no buffer or live ref remains.

## Important Constraints
- `pbase` must be nonzero and the logical extent must not cross a 64KB physical buffer.
- Last-drop handling must coordinate with concurrent getters through INPROG/WAITING bits.
- Dirty accounting is updated only if the buffer was not already delayed-write.
- Cached DIOs can persist after their buffers are released, preserving dedup state and enabling cheaper reuse.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_iocom.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_iocom.c

## Purpose
Integrates HAMMER2 with DragonFly's kernel DMSG/KDMSG communication layer. It initializes link communication, reconnects a mount to a file descriptor, advertises local PFS spans, receives remote spans, and transmits volume-copy configuration messages.

## I/O Communication Setup
- `hammer2_iocom_init()` initializes `hmp->iocom` with automatic LNK_CONN and automatic receive-side LNK_SPAN handling, but not automatic transmit-side spans because HAMMER2 advertises multiple PFSs itself.
- `hammer2_iocom_uninit()` tears down KDMSG state if message memory exists.
- `hammer2_cluster_reconnect()` installs a new communications file pointer, initializes automatic LNK_CONN fields, sets peer type to HAMMER2, restricts peer mask to HAMMER2 peers, assigns a host/mount label, and starts autoinitiation.

## Message Receive Handling
- `hammer2_rcvdmsg()` currently supports debug shell message scaffolding:
  - `DMSG_DBG_SHELL` receives `NOSUPP`.
  - `DMSG_DBG_SHELL | DMSGF_REPLY` prints auxiliary debug data.
  - Other transaction-creating messages receive `NOSUPP`; one-way and link-error messages are ignored to avoid reply loops.

## Automatic Link Handling
- `hammer2_autodmsg()` is called after KDMSG automatic LNK processing.
- On LNK_CONN replies to HAMMER2's auto-CONN, it:
  - Locks voldata.
  - Sends `DMSG_LNK_HAMMER2_VOLCONF` updates for nonempty copyinfo slots.
  - Unlocks voldata.
  - Calls `hammer2_update_spans()` to advertise local PFSs.
- On received LNK_SPAN create messages, it accepts only HAMMER2 peer type and protocol version 1, terminates the peer label string, optionally logs debug info, and replies with success.
- On LNK_SPAN delete messages, it relies on KDMSG automatic delete replies and optionally logs debug output.

## Span Advertisement
- `hammer2_update_spans()` locks the media-local super-root inode, scans its child chains, and for each inode creates a `DMSG_LNK_SPAN | DMSGF_CREATE` message.
- It fills span peer ID from PFS cluster ID, PFS ID from PFS filesystem ID, PFS type from inode metadata, peer type HAMMER2, protocol version 1, and peer label from the PFS filename.
- Reply handling for transmitted spans is `hammer2_lnk_span_reply()`, which replies to remote delete requests if the local transaction is not already deleting.

## Volume Configuration Updates
- `hammer2_volconf_update()` sends one `DMSG_LNK_HAMMER2_VOLCONF` message over the open connection transaction when `conn_state` exists.
- The message carries the selected copyinfo slot, media fsid, and index.
- The code notes missing interlocking against connection state termination.

## Current Limitations
- Remote PFS support is mostly connection and advertisement plumbing in this file; object-level remote PFS operations are described in comments but not implemented here.
- Unsupported DMSGs are deliberately rejected.
- Several peer-type and client-mode filters are disabled behind `#if 0`.
- `hammer2_update_spans()` has a loop hazard: if a non-inode chain is encountered, the `continue` path does not advance to the next chain in the visible code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_iocom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ioctl.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ioctl.c

## Purpose
Implements HAMMER2 ioctl dispatch and userland control operations for version queries, remote copy configuration, PFS scanning/creation/deletion/snapshotting, inode parameter access, bulkfree, emergency mode, destructive repair operations, growfs, and volume listing.

## Dispatch and Permissions
- `hammer2_ioctl()` begins with `caps_priv_check(cred, SYSCAP_NOVFS_IOCTL)` and selectively bypasses that result for non-privileged queries.
- Non-root allowed paths include version get, inode get, bulkfree scan in current code path, debug dump, and unsupported seek-hole/data handling depending on case logic.
- Mutating commands generally run only if the privilege check succeeded.
- `FIOSEEKDATA` and `FIOSEEKHOLE` return `EOPNOTSUPP`; disabled code references `vn_bmap_seekhole()`.

## Basic and Remote Operations
- `hammer2_ioctl_version_get()` returns media volume version from the first PFS device, or -1 if unavailable.
- `hammer2_ioctl_recluster()` takes a file descriptor, locates the PFS root cluster focus or sole chain, and reconnects the underlying device's KDMSG iocom.
- `hammer2_ioctl_remote_scan()` copies a selected `voldata.copyinfo` entry and computes the next occupied copyid.
- `hammer2_ioctl_remote_add()` allocates or uses a copyid, writes a copyinfo record into the volume header, marks voldata modified, and sends a volconf update.
- `hammer2_ioctl_remote_del()` deletes by copyid or by path search, clears the copyid field, and sends a volconf update.
- `hammer2_ioctl_remote_rep()` currently only locks/modifies voldata; replacement data is not copied into `copyinfo` in the visible implementation.
- Socket get/set are placeholders; get returns `EOPNOTSUPP`, set only validates copyid and locks/unlocks voldata.

## PFS Query Operations
- `hammer2_ioctl_pfs_get()` scans PFS entries under the media super-root, or returns the current file descriptor's mounted PFS when `name_key == -1`.
- It returns name key, PFS type/subtype, cluster ID, filesystem ID, name, and next key for iteration.
- `hammer2_ioctl_pfs_lookup()` hashes a supplied name, scans its collision range under the super-root, tests dirent names, and returns PFS identity fields.

## PFS Mutation
- `hammer2_ioctl_pfs_create()` validates name, checks for duplicates, starts a super-root flush transaction, creates a PFS inode, sets PFS metadata and default compression/check algorithms, disables compression for a PFS named `boot`, syncs/flushes the super-root inode, and allocates a local PFS association.
- `hammer2_ioctl_pfs_delete()` locates the PFS in the global PFS list for the target media, rejects mounted PFSs, deallocates the PFS cluster element, then permanently unlinks the PFS from the device super-root with force flags.
- `hammer2_ioctl_pfs_snapshot()` optionally syncs the source filesystem, sets `pfs_lsnap_tid`, creates a PFS inode under the super-root, assigns snapshot metadata and new UUIDs, copies the source root blockset from cached PFS root blocksets, flushes it, allocates a local PFS association, and seeds the snapshot inode allocator.

## Inode Ioctls
- `hammer2_ioctl_inode_get()` locks the inode shared, returns aggregate data/inode counts and the metadata portion of the inode.
- `hammer2_ioctl_inode_set()` starts a transaction, locks the inode, and conditionally updates check algorithm, compression algorithm, inode quota, data quota, and copy count before sideq transaction completion.

## Debug and Emergency Controls
- `hammer2_ioctl_debug_dump()` dumps each cluster chain through `hammer2_dump_chain()` with a high count limit.
- `hammer2_ioctl_emerg_mode()` toggles emergency flags on the PFS and all device mounts in its cluster, with console warnings.

## Bulkfree
- `hammer2_ioctl_bulkfree_scan()` serializes through `hmp->bflock`, syncs all mounted PFSs sharing the media, and chooses a snapshot topology unless ENOSPC forces live topology.
- Snapshot bulkfree runs outside a transaction; live bulkfree enters a flush transaction.
- It freezes the bulkfree thread, runs `hammer2_bulkfree_pass()`, unfreezes, drops the snapshot/live chain, converts HAMMER2 errors to errno, and releases the lock.
- As written, the dispatcher passes `NULL` for `HAMMER2IOC_BULKFREE_ASYNC`, but the function returns `EINVAL` on NULL data, so the async path is not actually asynchronous here.

## Destructive Repair
- `hammer2_ioctl_destroy()` rejects read-only PFSs.
- `HAMMER2_DELETE_FILE` force-unlinks a named directory entry under the fd directory with permanent/force/ignore-inode flags.
- `HAMMER2_DELETE_INUM` deletes a bad inode by inode number via the PFS root and `hammer2_delete_desc`.

## Growfs and Volumes
- `hammer2_ioctl_growfs()` supports only single-volume filesystems. It discovers device size from disklabel or vnode attributes, aligns to `HAMMER2_VOLUME_ALIGN`, rejects shrink and >2^63-1 sizes, clears newly exposed backup volume-header blocks, updates volume and allocator size/free counters in voldata and runtime structures, completes a flush transaction, and immediately syncs the filesystem.
- `hammer2_ioctl_volume_list()` copies out volume id, path, offset, and size for each volume up to caller capacity, then returns volume version and PFS name.

## Concurrency and Risk Notes
- Many operations lock `voldata` rather than chain topology to avoid deadlock with volume-chain locks.
- PFS deletion uses global `hammer2_mntlk` to coordinate with mount state.
- Snapshot creation serializes with `hmp->bulklk`.
- Remote replacement and socket operations are skeletal.
- Several control operations are marked with comments indicating incomplete clustering support, especially snapshots and growfs on multi-volume filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ioctl.c -->