# sources/distributed-fs/coda/coda-src/vol/cvnode.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vol/cvnode.cc` implements the Coda volume package's cached vnode layer. It manages in-memory vnode caches for small and large vnode classes, hash/LRU indexing, fid allocation, vnode allocation, vnode retrieval/locking, writeback to recoverable indexes, abort/flush behavior, and fid conversion helpers.

## Important APIs, Types, and Functions

Global state includes `VnodeClassInfo_Array[nVNODECLASSES]` and a 256-bucket `VnodeHashTable`. Public functions include `VolumeHashOffset`, `VInitVnodes`, `VAllocFid` overloads, `VAllocVnode` overloads, `VGetVnode`, `VPutVnode`, `VFlushVnode`, `VN_VN2Fid`, and `VN_VN2PFid`. Private helpers include `GrowVnLRUCache`, `VAllocVnodeCommon`, `moveHash`, and `StickOnLruChain`.

## Control Flow

Initialization creates circular LRU lists for each vnode class. Allocation first reserves fid bits and uniquifiers, grows RVM vnode arrays if needed, verifies no object already exists in RVM or VM, takes a vnode from the LRU tail, moves it to the target hash bucket, initializes disk and in-memory fields, removes it from LRU, and write-locks it. `VGetVnode` validates volume and lock mode, looks up the hash table, reads from the recoverable index on cache miss, validates magic/type/inconsistency/barren flags, removes the first user from LRU, obtains read or write lock, and bumps volume usage. `VPutVnode` writes dirty/deleted write-locked vnodes to the index, creates resolution logs for directories when enabled, updates volume timestamps, frees bitmap entries for fully deleted vnodes, returns the last user to LRU, and releases locks. `VFlushVnode` aborts a write by rereading the disk object or making the VM entry unreachable.

## State and Persistence Behavior

VM state consists of hash chains, circular LRU lists, lock state, user counts, cached vnode disk objects, dirty/delete flags, writer identity, directory handles, and cache checks. Persistent state is stored through `vindex` into recoverable vnode arrays and volume bitmaps/uniquifiers. `VAllocFid` advances transient and recoverable uniquifier counters and updates the volume header transactionally when extending beyond the RVM counter. `VPutVnode` is the normal path for persisting vnode changes; `VFlushVnode` is the rollback path.

## Dependencies and Integration Points

The file depends on LWP locks, RVM transactions, `vindex`, volume headers, recovery/log APIs (`CreateResLog`), vnode bitmap allocation/free helpers, volume online/writeability checks, directory handle cleanup, `VAddToVolumeUpdateList`, `VBumpVolumeUsage`, and global vnode cache sizing variables `large` and `small`. Server operation code obtains and releases objects through this layer.

## Risks and Edge Cases

Correctness relies on `nUsers`, LRU membership, hash membership, `cacheCheck`, and lock ownership staying synchronized. The cache dynamically grows if only one LRU entry remains, but memory pressure is not otherwise bounded. `VGetVnode` can return `EINCONS`, `EIO`, `VREADONLY`, `VOFFLINE`, `VSALVAGE`, or `EWOULDBLOCK` depending on state and lock mode. `VFlushVnode` has a subtle path that zeroes vnode identifiers before checking `IsEmpty`, which deserves scrutiny. Persistent magic mismatch forces volume offline/salvage.

## Test Signals

Test cache initialization and growth, hash distribution through `VolumeHashOffset`, fid range allocation and uniquifier extension, duplicate allocation detection, read/write/try-lock behavior, inconsistent and barren vnode rejection, dirty writeback, delete bitmap free, abort reread with `VFlushVnode`, resolution log creation for directories, and stress tests with concurrent vnode users.
