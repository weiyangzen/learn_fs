# Research: subset-b-007818

This grouped report covers OpenAFS volume package files in `sources/distributed-fs/openafs/src/vol`. Each file section is bounded with reconciliation markers so the final per-file research documents can be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache.c -->
# sources/distributed-fs/openafs/src/vol/vg_cache.c

## Purpose

`vg_cache.c` implements the demand-attach file server volume-group cache. A volume group is keyed by its read-write parent volume id and contains the ids of the RW, RO, and backup children recorded in volume headers. The cache lets callers query membership by any member id without walking partition header files for every lookup.

The file is compiled only under `AFS_DEMAND_ATTACH_FS`. It owns the global `VVGCache_hash_table` and `VVGCache` instances declared in the implementation header, allocates the hash table during package init, tracks per-partition validity, and exposes locked and `_r` caller-lock-held entry add/delete/query/scan functions.

## Important APIs, Types, and Functions

Public APIs from this file include `VVGCache_PkgInit`, `VVGCache_PkgShutdown`, `VVGCache_entry_add`, `VVGCache_entry_add_r`, `VVGCache_entry_del`, `VVGCache_entry_del_r`, `VVGCache_query`, `VVGCache_query_r`, `VVGCache_scanStart`, `VVGCache_scanStart_r`, `VVGCache_scanWait`, and `VVGCache_scanWait_r`. Internal APIs exported for `vg_scan.c` include `_VVGC_flush_part`, `_VVGC_flush_part_r`, `_VVGC_state_change`, and `_VVGC_entry_purge_r`.

The core private object is `VVGCache_entry_t`, with `rw`, fixed `children[VOL_VG_MAX_VOLS]`, and `refcnt`. Each member id also has a `VVGCache_hash_entry_t` stored in `VVGCache_hash_table.hash_buckets[VVGC_HASH(volid)]`; the hash entry records `volid`, partition pointer, and shared `entry`. The RW id has a hash entry even when it is also a child; child hash entries are removed individually, and the shared cache entry is freed when its refcount drops to zero.

## Control Flow

`VVGCache_PkgInit` allocates one queue head per `VolumeHashTable.Size` bucket and initializes every partition state to `VVGC_PART_STATE_INVALID` with a condition variable. `VVGCache_PkgShutdown` frees the bucket array and destroys per-partition condition variables, but returns `EOPNOTSUPP`, so consumers should not treat it as a complete cleanup implementation.

`VVGCache_entry_add_r` first looks up parent and child ids. If both exist and point to the same entry, it is usually a no-op, except the parent-equals-child case still ensures the RW id is present in the child list. If only the child exists, the existing entry is re-rooted by changing `rw` and adding a parent hash entry. If neither exists, `_VVGC_entry_add` allocates a new entry and RW hash entry. Any newly associated child gets a hash entry and is appended to the fixed child vector by `_VVGC_entry_cl_add`, which also increments the entry refcount. When a partition is in `UPDATING`, a successful add removes the tuple from the scanner delete-list so a delete/recreate race does not wipe out the new mapping.

`VVGCache_entry_del_r` records deletes on the partition delete-list while a scan is active, then calls `_VVGC_entry_purge_r`. Purge looks up the child id, optionally verifies the supplied parent maps to the same entry, then calls `_VVGC_hash_entry_del`. That removes the child from the vector and decrements the shared entry refcount; non-RW hash entries are unlinked immediately. When the final reference is dropped, `_VVGC_entry_put` looks up and unlinks the RW hash entry and frees the shared entry.

`VVGCache_query_r` lazy-starts a partition scan if the partition cache is invalid, returning `EAGAIN` while the async scan is starting or running. Valid state performs a hash lookup by any member id and exports the RW id plus child vector into `VVGCache_query_t`.

## State, Persistence, and Concurrency

This is an in-memory cache of persistent `.vol` header parent/id relationships. It does not write volume metadata. Persistence is provided by volume header files scanned by `vg_scan.c`; this file only keeps derived state and invalidates/rebuilds per partition.

All `_r` functions expect `VOL_LOCK` to be held unless documented otherwise. Non-`_r` wrappers acquire and release `VOL_LOCK`. Per-partition condition variables wake waiters when `_VVGC_state_change` changes `INVALID`, `UPDATING`, or `VALID`. `_VVGC_lookup` refuses to return mappings for invalid partitions.

## Dependencies and Integration Points

The implementation depends on OpenAFS queue primitives (`rx_queue`), volume package globals (`VolumeHashTable`, `DiskPartitionList`, `VOL_LOCK`), partition paths, volume ids, and logging through `ViceLog`. It integrates with `vg_scan.c` for async scans and delete-list reconciliation. The public cache API is consumed by demand-attach volume management code that needs fast volume-group membership.

## Risks and Test Signals

Important risks are hash/list/refcount consistency, race behavior during `UPDATING`, fixed child-vector capacity, and error propagation. A notable wrapper defect is that `VVGCache_entry_add` initializes `code` but ignores the return value from `VVGCache_entry_add_r`, so non-locked callers will always see success. Tests should cover add idempotency, parent re-rooting, conflicting parent/child mappings, delete of RW versus non-RW ids, query-triggered scan `EAGAIN`, partition invalidation, and delete-list behavior during a simulated scan. Stress tests should use colliding hash buckets and full `VOL_VG_MAX_VOLS` groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache.h -->
# sources/distributed-fs/openafs/src/vol/vg_cache.h

## Purpose

`vg_cache.h` is the public interface for the demand-attach volume-group cache. It exposes operations for adding/removing parent-child volume id relationships, querying a volume group by member id, launching/waiting for partition scans, checking partition state, and initializing/shutting down the package.

## Important APIs and Types

The header includes `vg_cache_types.h` for `VVGCache_query_t` and `partition.h` for `struct DiskPartition64`. For every mutating and query operation it generally exports both a normal wrapper and an `_r` variant: `VVGCache_entry_add`/`VVGCache_entry_add_r`, `VVGCache_entry_del`/`VVGCache_entry_del_r`, `VVGCache_query`/`VVGCache_query_r`, and scan start/wait pairs. In OpenAFS naming, the `_r` suffix means the caller is expected to hold the volume package global lock.

`VVGCache_checkPartition_r` is declared here but not implemented in the inspected source set; this is either a stale declaration or implemented conditionally elsewhere in builds not present in this tree.

## Control Flow and State Contract

Callers initialize with `VVGCache_PkgInit`, then use add/delete to keep the cache synchronized with volume header lifecycle events. A query may return `EAGAIN` when a partition cache is invalid or currently being rebuilt; callers should wait with `VVGCache_scanWait` or retry after the async scanner completes. Passing `NULL` to `VVGCache_scanStart` asks the implementation to scan all partitions.

## Dependencies and Integration Points

This header sits between volume attach/volser code and the private implementation in `vg_cache.c`/`vg_scan.c`. It intentionally hides hash table entries, scan tables, and partition delete-lists. Consumers only see partition pointers, volume ids, and exported query results.

## Risks and Test Signals

The most important contract risk is lock discipline: mixing `_r` and non-`_r` calls incorrectly can deadlock or race with scanner updates. Header-level tests are compile/link oriented: ensure all declared functions have definitions for the target build configuration, ensure callers include the public header instead of `vg_cache_impl.h`, and verify DAFS-only consumers guard use with `AFS_DEMAND_ATTACH_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache_impl.h -->
# sources/distributed-fs/openafs/src/vol/vg_cache_impl.h

## Purpose

`vg_cache_impl.h` is the private cross-file interface for the volume-group cache implementation. It is shared by `vg_cache.c` and `vg_scan.c`, not intended for normal callers.

## Important APIs, Types, and Constants

The key constant is `VVGC_SCAN_TBL_LEN`, set to 4096, defining how many discovered volume headers a scanner thread batches before flushing into the global cache under `VOL_LOCK`. The header includes `vg_cache_impl_types.h`, declares the global `VVGCache_hash_table` and `VVGCache`, and exposes internal helpers used across implementation files: `_VVGC_flush_part`, `_VVGC_flush_part_r`, `_VVGC_scan_start`, `_VVGC_state_change`, `_VVGC_entry_purge_r`, `_VVGC_dlist_add_r`, and `_VVGC_dlist_del_r`.

`VVGC_HASH(volumeId)` maps a volume id to a hash bucket by masking with `VolumeHashTable.Mask`, so it depends on volume package hash-table sizing.

## Control Flow and State Contract

The header allows the scanner to transition a partition to `UPDATING`, flush existing entries, batch newly discovered mappings, and reconcile deletes that occur during the scan. It also lets the public delete path add to the scanner delete-list and purge global cache entries with shared logic.

## Dependencies and Integration Points

It depends on the private type definitions in `vg_cache_impl_types.h`, volume package hash globals, and the DAFS volume lock model. Including this header outside the implementation effectively opts into internal state and should be avoided.

## Risks and Test Signals

Because the hash macro is a simple mask, tests should use a `VolumeHashTable.Size`/`Mask` combination that matches package initialization. Cross-file tests should verify the scan table length and delete-list logic do not depend on implementation details hidden from public callers. Static checks should flag accidental inclusion of this private header by unrelated modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache_impl_types.h -->
# sources/distributed-fs/openafs/src/vol/vg_cache_impl_types.h

## Purpose

`vg_cache_impl_types.h` defines private data structures for the demand-attach volume-group cache. It deliberately errors out unless `__VOL_VG_CACHE_IMPL` is defined, protecting internal layout from external consumers.

## Important Types

`VVGCache_entry_t` represents one volume group: `rw` is the read-write parent id, `children` is a fixed vector of `VOL_VG_MAX_VOLS` member ids, and `refcnt` tracks child-vector memberships. `VVGCache_hash_table_t` owns a dynamically allocated array of queue heads. `VVGCache_hash_entry_t` is the per-member hash node, containing queue links, the member `volid`, the associated partition pointer, and the shared `VVGCache_entry_t`.

Scanner-only types include `VVGCache_scan_entry_t` for one discovered `(volid,parent)` tuple and `VVGCache_scan_table_t` for the thread-local batch with counters for discovered volumes and groups. `VVGCache_part_state_t` defines `VALID`, `INVALID`, and `UPDATING`. `VVGCache_dlist_entry_t` records a pending delete during a scan, and `VVGCache_part_t` stores each partition's state, condition variable, and temporary delete-list buckets. `VVGCache_t` is the global array of per-partition state for `VOLMAXPARTS + 1`.

## State and Persistence Behavior

These structures are in-memory only. Persistent truth is in OpenAFS volume headers and vnode/index files. The cache entry refcount is not a generic object reference count; it tracks how many children currently keep the group alive. The RW hash entry can exist separately from children so lookups by parent still resolve to the group, but the group is freed after all child vector entries have been removed.

## Dependencies and Integration Points

The file depends on `volume.h`, `rx_queue`, pthread condition variables via included types, and `VOL_VG_MAX_VOLS` from volume definitions. It is tightly integrated with `vg_cache.c` and `vg_scan.c`; layout changes require auditing queue scanning, allocation/free paths, and scanner dlist operations.

## Risks and Test Signals

Risks include fixed-size child arrays, ambiguous semantics of `refcnt`, and stale dlist buckets when scan start fails. Tests should assert queue nodes are initialized before use, dlist buckets are allocated only during `UPDATING`, condition variables are initialized for every partition in package init, and cache entries are freed exactly once after last child deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache_impl_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache_types.h -->
# sources/distributed-fs/openafs/src/vol/vg_cache_types.h

## Purpose

`vg_cache_types.h` defines the public data returned by volume-group cache queries. It is intentionally small and independent of private hash/scanner internals.

## Important Types

`VVGCache_query_t` contains `rw`, the read-write volume id for the group, and `children[VOL_VG_MAX_VOLS]`, the fixed vector of member volume ids. The implementation copies internal `VVGCache_entry_t` fields directly into this public structure.

## Control Flow and State

Callers pass a pointer to `VVGCache_query` or `VVGCache_query_r`; on success the buffer is filled with the RW id and child slots. Empty child slots are zero because the internal representation uses zero as the empty marker. There is no count field, so callers must scan the whole fixed array and ignore zero entries.

## Dependencies and Integration Points

The header includes `voldefs.h` for `VOL_VG_MAX_VOLS` and OpenAFS volume id types. It is included by `vg_cache.h` and should be the only volume-group cache type visible to external callers.

## Risks and Test Signals

The lack of an explicit child count is easy to misuse. Tests for callers should include sparse child vectors, zero-terminated assumptions, and groups at maximum capacity. ABI-sensitive consumers should be rebuilt when `VOL_VG_MAX_VOLS` changes because the public structure size changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_cache_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_scan.c -->
# sources/distributed-fs/openafs/src/vol/vg_scan.c

## Purpose

`vg_scan.c` implements the asynchronous partition scanner for the demand-attach volume-group cache. It rebuilds cache state from `.vol` header files and coordinates with concurrent cache deletes while the scan is running.

## Important APIs and Functions

The public-to-private entry point is `_VVGC_scan_start`, declared in `vg_cache_impl.h` and called by `VVGCache_scanStart_r`. The scanner thread runs `_VVGC_scanner_thread`, which calls `_VVGC_scan_partition`. Header walking callbacks are `_VVGC_RecordHeader`, which batches `hdr->id` and `hdr->parent`, and `_VVGC_UnlinkHeader`, which removes invalid volume header files found by `VWalkVolumeHeaders`.

Batching helpers are `_VVGC_scan_table_init`, `_VVGC_scan_table_add`, and `_VVGC_scan_table_flush`. Delete-list helpers are `_VVGC_dlist_lookup_r`, `_VVGC_flush_dlist`, `_VVGC_dlist_add_r`, and `_VVGC_dlist_del_r`.

## Control Flow

`_VVGC_scan_start` changes the partition state to `UPDATING`. If it was already `UPDATING`, it reports a race with `-3`. It allocates per-partition dlist hash buckets, initializes them, configures a detached pthread, and starts `_VVGC_scanner_thread`.

`_VVGC_scan_partition` initializes a local scan table, validates the partition path, flushes old cache entries for the partition under `VOL_LOCK`, opens the partition directory, and calls `VWalkVolumeHeaders`. Each valid header adds a tuple to the local table; if the table reaches `VVGC_SCAN_TBL_LEN`, it flushes to the global cache. A final flush occurs after the walk. On completion, the scanner flushes the delete-list, frees dlist buckets, and transitions the partition state to `VALID` or `INVALID`.

`_VVGC_scan_table_flush` acquires `VOL_LOCK`, skips any tuple present in the delete-list, calls `VVGCache_entry_add_r`, updates counters, and flushes the dlist opportunistically to keep it small. This avoids stale scan results resurrecting entries deleted during a long partition walk.

## State, Persistence, and Concurrency

The scanner reads persistent volume header files but only writes persistence when `_VVGC_UnlinkHeader` deletes illegitimate headers. All cache insertion and delete-list manipulation happens under `VOL_LOCK`, while directory walking and header scanning run without it. The dlist exists only for a partition in `UPDATING` state and is freed before the state transition broadcast.

## Dependencies and Integration Points

The file depends on partition walking (`VPartitionPath`, `VWalkVolumeHeaders`), volume disk headers, queue primitives, pthreads, the global volume lock, and cache internals from `vg_cache_impl.h`. It integrates with `vg_cache.c` add/delete/purge and state-change helpers.

## Risks and Test Signals

Race tests are essential: delete during scan, delete followed by recreate in a different group, duplicate headers, scan start races, pthread creation failure, and invalid partition paths. Error handling should be checked for dlist cleanup on scan-start failures. Scanner tests should also verify that invalid header unlink errors are logged but do not corrupt cache state, and that waiters on `VVGCache_scanWait_r` wake after final state change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vg_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/viceinode.h -->
# sources/distributed-fs/openafs/src/vol/viceinode.h

## Purpose

`viceinode.h` defines the parameter layout OpenAFS uses to encode fileserver inode metadata. It is a compact contract between the volume package, salvager/fsck-style tools, and platform-specific inode/namei implementations.

## Important Types and Constants

`struct InodeParams` describes ordinary vnode data inodes with `volumeId`, `vnodeNumber`, `vnodeUniquifier`, and `inodeDataVersion`. `struct SpecialInodeParams` describes volume special inodes with `volumeId`, `vnodeNumber` set to `INODESPECIAL`, parent id, and type; field order differs under `AFS_3DISPARES`.

`struct ViceInodeInfo` is the fsck output record: inode number, byte count, link count, and a union exposing raw parameters or the ordinary/special interpretations. `INODESPECIAL` is platform-dependent, and special inode type ids include `VI_VOLINFO`, `VI_SMALLINDEX`, `VI_LARGEINDEX`, `VI_ACL`, `VI_MOUNTTABLE`, and `VI_LINKTABLE`.

## State and Persistence Behavior

These structures describe persisted inode identity. Ordinary inodes are tied to a volume/vnode/unique/data-version tuple; special inodes represent the volume info file, vnode index files, ACL/mount/link tables, and other metadata. The values are interpreted by salvage, volume inspection, and inode-handle code rather than manipulated here.

## Dependencies and Integration Points

The header assumes OpenAFS typedefs such as `VolumeId`, `VnodeId`, `Unique`, `FileVersion`, `Inode`, `afs_fsize_t`, and `bit32` are already available through volume headers. It is included by volume cache and scanner code even when those files do not directly use the structs, because inode identity is part of volume package context.

## Risks and Test Signals

The largest risk is ABI and on-disk compatibility. Reordering special inode fields, changing `INODESPECIAL`, or changing special type numbering can break fsck/salvage interpretation. Tests should decode known fsck records for both ordinary and special inodes, including `AFS_3DISPARES` builds, and verify special type ids match `vutil.h` expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/viceinode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vnode.c -->
# sources/distributed-fs/openafs/src/vol/vnode.c

## Purpose

`vnode.c` implements the OpenAFS volume package vnode cache: allocation, lookup, load from vnode index files, writeback, lock/read-state conversion, LRU/hash/list membership, and volume detach cleanup. Vnodes are the per-file/per-directory/per-symlink metadata records stored in large and small vnode index files.

## Important APIs and Functions

Public APIs include `VInitVnodes`, `VGetVnode`, `VGetVnode_r`, `VPutVnode`, `VPutVnode_r`, `VVnodeWriteToRead`, `VVnodeWriteToRead_r`, `VAllocVnode`, `VAllocVnode_r`, `VGetFreeVnode_r`, `VLookupVnode`, and list/hash helpers declared in `vnode.h`. Internal helpers include `VInvalidateVnode_r`, `VnLoad`, `VnStore`, and `VInvalidateVnodesByVolume_r`. The file also exposes `VnodeClassInfo[nVNODECLASSES]` and a circular debug log through `VNLog`.

## Control Flow

`VInitVnodes` builds one cache pool per vnode class. It sets disk/resident sizes and magic numbers, allocates a contiguous array, initializes each `Vnode`, and threads them onto a circular LRU list.

`VGetVnode_r` validates the requested vnode number and volume state, checks writeability for write locks, updates volume usage/update state, then looks in the vnode hash. Cached vnodes get a reservation and, under DAFS, wait for exclusive or quiescent state. Uncached vnodes are taken from the LRU by `VGetFreeVnode_r`, attached to the volume, hashed early for DAFS, and loaded from the appropriate vnode index by `VnLoad`. Finally the vnode lock/read state is acquired and null/deleted cache entries are rejected.

`VAllocVnode_r` allocates a vnode slot for new files or a specific replication-supplied vnode/unique pair. It updates the uniquifier, allocates or grows the bitmap, obtains/reuses a cache vnode, checks that the disk slot is blank, initializes disk metadata, increments filecount, and leaves the vnode in exclusive state for the caller.

`VPutVnode_r` releases a read or write vnode. If write-locked and changed/deleted, it updates server modify time and volume update counters, writes the vnode index record with `VnStore`, and frees bitmap/filecount state after successful deletion. `VVnodeWriteToRead_r` performs the same writeback path but downgrades exclusive access to shared read access.

Volume teardown uses `VCloseVnodeFiles_r` and `VReleaseVnodeFiles_r` via `VInvalidateVnodesByVolume_r` to detach vnode cache entries from a volume, collect inode handles, then close/release handles outside `VOL_LOCK`.

## State, Persistence, and Concurrency

Persistent vnode state lives in large and small vnode index files. `VnLoad` reads `VnodeDiskObject` records by `vnodeIndexOffset`; `VnStore` writes them back. The code drops `VOL_LOCK` around latent inode-handle I/O. In DAFS, vnode states (`LOAD`, `ALLOC`, `EXCLUSIVE`, `READ`, `STORE`, `ONLINE`, etc.), volume exclusive states, reservations, and condition variables protect cache coherency while the lock is dropped. Non-DAFS uses vnode read/write locks but the source notes a race where two non-DAFS threads can load the same vnode into different cache objects.

Cache state is tracked by hash table membership, LRU membership, per-volume vnode queue membership, refcount, cacheCheck, inode handle pointer, changed/delete flags, and DAFS reader count/state.

## Dependencies and Integration Points

`vnode.c` depends on `ihandle` for index/data inode handles, `volume.h`/`volume_inline.h` for volume state and bitmaps, `vnode_inline.h` for DAFS state helpers, `partition.h`, `salvsync.h` for salvage requests, `opr/jhash` for vnode hash buckets, and OpenAFS lock primitives. It is central to file server vnode operations, volume attach/detach, salvager behavior, RW replication, and debugging protocols.

## Risks and Test Signals

High-risk areas include lock dropping during index I/O, bitmap/index consistency, vnode reuse from LRU, DAFS state transitions, writeback after delete, handle release during volume detach, and stale cacheCheck behavior. Tests should cover cache hits/misses, bad vnode magic, unallocated bitmap entries, index growth, uniquifier rollover, write-to-read conversion, deletion bitmap free ordering, volume offline/read-only rejection, salvage request paths, and forced concurrent get/alloc/put on the same vnode. Instrumentation should watch `VnodeClassInfo` gets/reads/writes and confirm no vnode remains simultaneously on LRU while referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vnode.h -->
# sources/distributed-fs/openafs/src/vol/vnode.h

## Purpose

`vnode.h` defines OpenAFS vnode on-disk and in-memory structures, vnode number/class conversion helpers, size constants, state flags, and public vnode package APIs. It is the main structural contract for volume metadata records.

## Important Types, Macros, and APIs

`ViceLock` stores advisory lock counters/timestamps with inline helpers to check and clear it. Vnode types are `vNull`, `vFile`, `vDirectory`, and `vSymlink`; vnode classes are `vLarge` for directories and `vSmall` for files/symlinks. Inline conversions map types and vnode ids to class, bitmap bit number, index offset, and vnode number.

`VnodeDiskObject` is the persisted vnode record. It stores type, cloned flag, mode bits, link count, 64-bit length split into low/high fields, uniquifier, data version, inode number split into low/high fields, user/server modify times, author/owner/group, parent vnode, magic number, and advisory lock. Small disk vnodes are 64 bytes; large disk vnodes are 256 bytes and use the extra space for directory ACL data via `VVnodeDiskACL`.

Under `AFS_DEMAND_ATTACH_FS`, `VnState` describes vnode cache state and `enum VnFlags` tracks hash/LRU/per-volume-list membership. `struct Vnode` is the in-memory cache object containing queue/hash/LRU links, changed/delete bits, id, volume pointer, refcount, cacheCheck, DAFS state or non-DAFS lock, writer owner, class pointer, inode handle, and disk object.

The header declares core operations implemented in `vnode.c`: init, get, put, allocate, write-to-read conversion, free-vnode retrieval, lookup, and list/hash manipulation.

## State and Persistence Behavior

The disk object layout is persistent and size-sensitive. Macros `VN_GET_LEN`, `VN_SET_LEN`, `VN_GET_INO`, and related disk variants preserve 64-bit fields on platforms that support 64-bit inode operations while keeping the old layout. `vnodeIndexOffset` accounts for an index header record at the start of each vnode index file.

## Dependencies and Integration Points

The header is used by file server, salvager, volume utilities, directory scanning, vol-info tools, and vnode cache implementation. It assumes OpenAFS core typedefs, lock definitions, ACL structures, and volume forward declarations.

## Risks and Test Signals

Any layout change risks on-disk compatibility. Tests should assert `CHECKSIZE_SMALLVNODE`, `SIZEOF_LARGEDISKVNODE`, vnode id/class round trips, ACL pointer placement, 64-bit inode/length macros, and DAFS state validity. API tests should verify callers obey lock ownership and do not access disk fields after a vnode has been put and possibly recycled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vnode_inline.h -->
# sources/distributed-fs/openafs/src/vol/vnode_inline.h

## Purpose

`vnode_inline.h` contains inline vnode cache helper routines, especially the demand-attach vnode state machine. It centralizes reservation, lock, state transition, wait, and read-count operations used by `vnode.c`.

## Important APIs and Functions

`VnCreateReservation_r` increments a vnode refcount and removes it from LRU when it becomes active. `VnCancelReservation_r` decrements the refcount, returns the vnode to LRU when it reaches zero, and optionally removes the vnode from the volume vnode list when `TrustVnodeCacheEntry` is false.

`VnLock` and `VnUnlock` abstract vnode locking. Under DAFS, they mostly set/clear the writer field because DAFS state transitions provide synchronization; under non-DAFS they acquire/release read/write locks, dropping `VOL_LOCK` when needed to avoid deadlock.

DAFS-only helpers include `VnChangeState_r`, `VnIsExclusiveState`, `VnIsErrorState`, `VnIsValidState`, `VnWaitStateChange_r`, `VnWaitExclusiveState_r`, `VnWaitQuiescent_r`, `VnBeginRead_r`, and `VnEndRead_r`.

## Control Flow and State

The normal DAFS read path waits until the vnode is not in an exclusive state, changes `ONLINE` to `READ` when the first reader starts, increments `nReaders`, and returns. The write path waits for quiescence and changes state to `EXCLUSIVE`. Store/load/allocation/release paths use exclusive states and broadcast on every state change. Ending the last reader broadcasts and returns the vnode to `ONLINE`.

## Dependencies and Integration Points

The header depends on `vnode.h`, OpenAFS `VOL_LOCK`/condition-variable primitives, pthread or LWP writer identity, and list helpers from `vnode.c`. It is included by vnode implementation and any internal code needing the state-machine helpers.

## Risks and Test Signals

The highest risk is incorrect lock-state pairing: forgetting `VnCancelReservation_r`, beginning reads from the wrong state, or failing to broadcast on state changes can stall DAFS. Tests should cover reader transitions, writer thread identity, LRU membership across reservation creation/cancellation, error-state detection, wait behavior under concurrent exclusive operations, and non-DAFS lock acquisition with and without `VOL_LOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vnode_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-bless.c -->
# sources/distributed-fs/openafs/src/vol/vol-bless.c

## Purpose

`vol-bless.c` is a small command-line utility for setting or clearing a volume's blessed bit. The blessed bit is stored in the volume disk data and affects whether the fileserver considers the volume usable after operations such as salvage or restore.

## Important APIs and Functions

`main` defines command syntax with `-id`, `-bless`, `-unbless`, and `-nofssync`. `handleit` parses options, initializes the volume package with `VInitVolumePackage2`, attaches the requested volume for update with `VAttachVolume(..., V_VOLUPD)`, changes `V_blessed(vp)`, writes the header with `VUpdateVolume`, and detaches with `VDetachVolume`.

`VolumeChanged` is defined as a global to satisfy lower-level physio expectations.

## Control Flow and State

The tool rejects simultaneous `-bless` and `-unbless`. With normal operation it runs as `volumeUtility` and may use FSSYNC to coordinate with a running fileserver. With `-nofssync`, it initializes as `salvager` and disables FSSYNC use. The only intended persistent mutation is the blessed flag in the attached volume header, committed through `VUpdateVolume`.

## Dependencies and Integration Points

The utility depends on OpenAFS command parsing (`afs/cmd.h`), rx/xdr and queue headers, vnode/volume package APIs, and the volume package's FSSYNC option handling. It integrates administratively with fileserver/salvager workflows.

## Risks and Test Signals

Risks are direct metadata mutation on the wrong volume, unsafe `-nofssync` use while a fileserver is active, and failure paths that exit after attach errors. Tests should cover argument validation, bless/unbless persistence, FSSYNC-enabled and no-FSSYNC initialization, failure to attach, failure to update, and idempotent repeated bless/unbless operations on a test volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-bless.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-info.c -->
# sources/distributed-fs/openafs/src/vol/vol-info.c

## Purpose

`vol-info.c` implements reusable volume inspection and scanning logic for OpenAFS volume utility commands. It can dump volume headers, inspect special files, scan vnode index files, print selected vnode fields as tabular columns, find paths, classify symlinks as mount points, scan ACLs, save inode contents, and accumulate size totals.

## Important APIs, Types, and Functions

Public functions declared in `vol-info.h` include `volinfo_Init`, `volinfo_Options`, `volinfo_AddOutputColumn`, `volinfo_ScanPartitions`, `volinfo_AddVnodeHandler`, and vnode handlers such as `volinfo_PrintVnode`, `volinfo_PrintVnodeDetails`, `volinfo_ScanAcl`, `volinfo_SaveInode`, and `volinfo_AddVnodeToSizeTotals`.

Internally, `struct VnodeDetails` packages a volume, vnode class, disk vnode pointer, vnode number, index offset, optional path, and union payload for mount/symlink/ACL output. `ColumnName` maps the `VOLSCAN_COLUMNS` macro list to numeric column ids. `VnodeScanLists` stores per-class callback lists.

Major helpers include `ReadHdr1`, `AttachVolume`, `DetachVolume`, `volinfo_ScanPartitions`, `HandleAllPart`, `HandlePart`, `HandleVolume`, `HandleHeaderFiles`, `HandleSpecialFile`, `HandleVnodes`, `LookupPath`, `ReadSymlinkTarget`, `PrintColumns`, and size-total print helpers.

## Control Flow

`volinfo_Init` enforces root on non-Windows, initializes directory handling, initializes empty vnode cache class info, and initializes scan callback lists. `volinfo_Options` creates defaults: dump info enabled, hostname set, space column delimiter, and directory magic checks enabled. Callers add output columns and vnode handlers, then call `volinfo_ScanPartitions`.

`volinfo_ScanPartitions` optionally initializes FSSYNC checkout, attaches partitions, resolves partition names or current partition, prints headings, and scans either all partitions, one partition, or one volume. `HandlePart` walks partition directory entries ending in `VHDREXT`. `HandleVolume` reads and validates the volume header file, optionally inspects special inodes, attaches a simplified `Volume` object from inode handles and disk data, prints header information, scans large and small vnode indexes if handlers are registered, prints size totals, and detaches.

`HandleVnodes` opens the class index, computes vnode count from index file size minus the header record, skips the header, reads disk vnode records, applies mode masks, fills `VnodeDetails`, and invokes every registered handler. Handlers print raw vnode lines, output structured columns, save inode data, scan ACLs, or accumulate sizes.

Path lookup uses the large vnode index and `afs_dir_InverseLookup` to climb parent directories from a child fid back to root. Symlink handling reads the target inode and recognizes AFS mount points when contents begin with `#` or `%` and end in `.`.

## State, Persistence, and Concurrency

Most operations are read-only inspections of volume headers, special inodes, vnode index files, and data inodes. Mutating behavior exists in `ReadHdr1` when `opt->fixHeader` repairs bad magic/version fields, and in `volinfo_SaveInode` when inode contents are copied to `TmpInode.*` files in the current directory. FSSYNC checkout can request fileserver coordination before reading volumes. Global state includes selected columns, callback queues, `DirIndexFd`, size totals, and initialization state, so this module is not designed for independent concurrent scans in the same process.

## Dependencies and Integration Points

The file depends on command/dir/ACL/prs headers, vnode and volume structures, partition attach, salvage directory helpers, daemon/FSSYNC inline protocols, inode handles, namei support, and OpenAFS stream wrappers. It provides shared implementation for utilities that need volume/vnode inspection without fully attaching through the fileserver path.

## Risks and Test Signals

Risks include stale global state across scans, path lookup failures on corrupt parent chains, static buffers in date/path/symlink functions, unchecked callback allocation in `volinfo_AddVnodeHandler`, root-only behavior, and accidental mutation via `fixHeader` or inode saving. Tests should cover scanning all/one partition/one volume, FSSYNC denial, bad header magic/version with and without repair, volume type filters, mode masks, symlink and mount parsing, ACL positive/negative entries, path reconstruction, namei output, size totals, and output column formatting with custom delimiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-info.h -->
# sources/distributed-fs/openafs/src/vol/vol-info.h

## Purpose

`vol-info.h` declares options, filters, output columns, and public helper APIs for OpenAFS volume inspection utilities implemented by `vol-info.c`.

## Important Types, Flags, and APIs

Scan-volume flags are `SCAN_RW`, `SCAN_RO`, and `SCAN_BK`. Vnode find flags are `FIND_FILE`, `FIND_DIR`, `FIND_MOUNT`, `FIND_SYMLINK`, and `FIND_ACL`.

`struct VolInfoOpt` is the caller-configurable scan state. It controls FSSYNC checkout, header/info/vnode dumping, inode numbers and times, file names, orphan reporting, size summaries, inode saving, header repair, hostname, column delimiter, headings, directory magic checks, mode masks, volume type filters, and vnode type filters.

`VOLSCAN_COLUMNS` is the canonical list of structured output columns. It is reused by `vol-info.c` to generate the column enum and name table, keeping CLI column names synchronized with switch handling.

Public APIs initialize the module/options, add vnode handlers, add output columns, scan partitions, and provide standard vnode handlers for size totals, saving inodes, raw/detail printing, and ACL scanning.

## Control Flow and Integration

A typical utility calls `volinfo_Init`, obtains defaults with `volinfo_Options`, modifies fields based on CLI options, registers output columns/handlers, and calls `volinfo_ScanPartitions`. `struct VnodeDetails` is forward-declared so callers can register callbacks without depending on its layout.

## State and Persistence Behavior

This header does not define persistence, but its options can enable persistent side effects in the implementation: `fixHeader` can rewrite bad special inode headers and `saveInodes` can create local copies of inode contents. All other flags primarily affect reads and output formatting.

## Risks and Test Signals

API risks include uninitialized option fields, unsupported column names, mode mask array overflow in callers, and handlers assuming `VnodeDetails` internals. Tests should verify default options, every `VOLSCAN_COLUMNS` value can be registered and printed, scan type filters combine correctly, find flags select expected handlers, and callback registration stays per vnode class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vol-info.h -->
