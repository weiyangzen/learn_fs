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
