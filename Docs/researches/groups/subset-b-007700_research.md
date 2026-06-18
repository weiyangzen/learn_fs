# subset-b-007700 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_btree.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_btree.c

## Purpose
`cm_btree.c` implements the Windows cache manager's optional in-memory B+ tree directory index under `USE_BPLUS`. It provides generic B+ tree primitives over normalized file-name keys and then adapts them to AFS directory lookup, create/delete, emptiness checks, directory tree construction from `cm_ApplyDir`, enumeration snapshots, and bulk status prefetch for enumerated entries.

## Important APIs, types, and functions
The core tree entry points are `initBtree`, `freeBtree`, `insert`, `delete`, and the implemented lookup function `bplus_Lookup`. `cm_BPlusCompareNormalizedKeys` is the key comparator: normal ordering is case-insensitive via `cm_NormStrCmpI`, while `EXACT_MATCH` adds a case-sensitive normalized comparison after a case-insensitive match.

The directory-facing APIs are `cm_BPlusDirLookup`, `cm_BPlusDirLookupOriginalName`, `cm_BPlusDirCreateEntry`, `cm_BPlusDirDeleteEntry`, `cm_BPlusDirIsEmpty`, `cm_BPlusDirBuildTree`, `cm_BPlusDirFoo`, `cm_BPlusDirEnumerate`, `cm_BPlusDirNextEnumEntry`, `cm_BPlusDirPeekNextEnumEntry`, `cm_BPlusDirFreeEnumeration`, `cm_BPlusDirEnumBulkStat`, and `cm_BPlusDirEnumBulkStatOne`. Statistics are exported through counters such as `bplus_lookup_hits`, `bplus_lookup_misses`, `bplus_create_entry`, `bplus_build_tree`, and dump helpers `cm_BPlusDumpStats` and `cm_MemDumpBPlusStats`.

Internally, `getDataNode`, `getFreeNode`, `putFreeNode`, and `cleanupNodePool` manage pooled `Node` objects. Tree operations use `descendToLeaf`, `getSlot`, `findKey`, `bestMatch`, `descendSplit`, `insertEntry`, `placeEntry`, `split`, `makeNewRoot`, `descendBalance`, `removeEntry`, `merge`, `shift`, and `collapseRoot`. Transient operation key/data are stored in Windows TLS slots allocated by `cm_InitBPlusDir`.

## Control flow
Initialization allocates TLS indexes with `TlsAlloc`; `initBtree` allocates a `Tree`, creates an initial free node pool, takes one node as the first leaf/root, marks it `isLEAF | isROOT | FEWEST`, and installs the comparator.

Lookup normalizes the requested client name, stores it in TLS with `setfunkey`, descends from root with `descendToLeaf`, and then resolves duplicate data nodes hanging from the matching leaf entry. Directory lookup returns an exact match first; one inexact case-fold match returns `CM_ERROR_INEXACT_MATCH`; multiple inexact matches return `CM_ERROR_AMBIGUOUS_FILENAME`; no leaf returns `ENOENT`.

Insertion descends recursively to a leaf. Duplicate normalized keys are represented as a linked list of data nodes unless the tree has `TREE_FLAG_UNIQUE_KEYS`. When a full node is encountered, `setsplitpath` marks the first full node on the insertion path; `split` creates a sibling, `insertEntry` redistributes entries, and `makeNewRoot` installs a new root if the old root split.

Deletion also descends recursively, but passes immediate siblings, sibling anchors, and parent context into `descendBalance`. For duplicate data chains it deletes only an exact match; if other data nodes remain, the leaf key stays. If a leaf entry is removed, rebalancing either collapses the root, merges minimum-sized neighbors, or shifts entries from a larger neighbor, updating anchor keys.

Directory build creates a B+ tree for `scp->dirBplus` and invokes `cm_ApplyDir`; `cm_BPlusDirFoo` converts server directory entries to normalized/client/fs names and inserts long-name and optional generated 8.3 short-name entries. Enumeration first counts non-shortform matching entries, allocates a snapshot array, then copies client names, FIDs, optional generated short names, request flags, data version, and references to the directory scache and user.

Bulk stat walks an enumeration and uses cached callbacks where possible. Otherwise it batches FIDs into `cm_bulkStat_t`, always includes the directory FID to help preserve directory callbacks, maps RPC errors through `cm_MapRPCError`, and falls back to individual `cm_SyncOp` status fetches if the file server rejects bulk status.

## State and persistence behavior
The B+ tree is in-memory state hanging from `cm_scache_t.dirBplus`. It represents `cm_scache_t.dirDataVersion`, not persistent on-disk directory contents. Directory operations reject stale trees by comparing the operation data version to `dirDataVersion`; some structural lookup failures set `dirDataVersion` to bad/zero to force rebuild.

Nodes own duplicated normalized keys plus duplicated client and fileserver names in data values. `putFreeNode` and `cleanupNodePool` free those allocations and recycle/reset nodes. The free pool expands dynamically if insertion consumes the initial pool.

Concurrency is external: directory operations assert `scp->dirlock` read or write ownership. The tree has no internal lock. `Tree.branch.split/merge` is per-tree mutable state and relies on the caller's write lock during mutation. TLS only carries the current operation key/data; it is not durable tree state.

Statistics are process-global counters/timers. `bplus_free_tree` is declared and dumped but this implementation does not increment it in `freeBtree`.

## Dependencies and integration points
This file depends on Windows APIs (`TlsAlloc`, `TlsGetValue`, `QueryPerformanceCounter`), OpenAFS cache manager types (`cm_scache_t`, `cm_user_t`, `cm_req_t`, `cm_dirOp_t`, `cm_fid_t`), directory scanning (`cm_ApplyDir`), name conversion/normalization helpers (`cm_ClientStringToNormStringAlloc`, `cm_FsStringToNormStringAlloc`, `cm_NormalizeStringAlloc`, `cm_NormStrDup`, `cm_ClientStrDup`, `cm_FsStrDup`), 8.3 short-name helpers (`cm_Is8Dot3`, `cm_Gen8Dot3NameIntW`), scache/user lifetime helpers, bulk status RPCs, logging, and lock assertions.

The integration boundary is `cm_dir.c` and vnode operations that keep `dirBplus`, `dirDataVersion`, and `dirlock` coherent. Scache reset and recycle code frees trees through `freeBtree`. Directory enumeration consumers use the snapshot and release it with `cm_BPlusDirFreeEnumeration`.

## Risks and edge cases
The header declares `Nptr lookup(Tree *, keyT)`, but this file implements and callers use `bplus_Lookup`; that declaration mismatch is a compile/interface risk if strict prototypes are enabled.

TLS allocations for per-thread `keyT` and `dataT` storage are allocated lazily and not freed here. This may be acceptable for process-lifetime cache manager threads, but it is a leak risk in dynamic thread churn or shutdown analysis.

Exact-match deletion depends on normalized case-sensitive comparison. Ambiguous case-fold matches intentionally block destructive operations, but any inconsistency between generated short names and normalized long names can leave one side of the paired long/short entries behind.

Several invalid tree ordering paths log and may poison `dirDataVersion`; tests should exercise malformed ordering and duplicate chains because `findKey`/`bestMatch` have special sentinel values (`BTLOWER`, `BTUPPER`, `BTERROR`) with leaf-specific constraints.

In `cm_BPlusDirEnumBulkStat`, the assignment to `bs_flagsp[bsp->counter]` after `i = bsp->counter++` appears to use the batch counter as an enumeration index (`enump->entry[i].flags`) instead of the source enumeration index. That is a high-value review target because error/status flags could be written to the wrong entry.

Enumeration snapshots retain scache and user references and duplicate names. Failure cleanup releases partial entries, but any caller that forgets `cm_BPlusDirFreeEnumeration` leaks those references and names.

## Test signals
Useful tests include case-insensitive lookup with exact, single-inexact, and ambiguous names; long-name create/delete with `cm_shortNames` enabled; deleting by short name and by long name; duplicate normalized names with exact deletion of one data node; tree split/merge/root-collapse under many insertions and deletions; `cm_BPlusDirIsEmpty` with only `.` and `..`; stale `dirDataVersion` rejection; enumeration masks; enumeration free after partial failure; bulk-stat fallback from `CM_ERROR_BULKSTAT_FAILURE`; and debug validation with `findAllBtreeValues`/`btreetest.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_btree.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_btree.h

## Purpose
`cm_btree.h` defines the B+ tree data model, accessor macros, directory data payloads, directory enumeration structures, public B+ tree functions, and cache-manager directory APIs used by the Windows AFS client when `USE_BPLUS` is enabled.

## Important APIs, types, and macros
The primary structural types are `keyT`, `dataT`, `Entry`, `Inner`, `Leaf`, `Data`, `Node`, and `Tree`. `keyT` stores a normalized name. `dataT` stores a `cm_fid_t`, a `shortform` marker, the client-visible name, and the fileserver/original name. `Node` is a tagged union: internal/leaf nodes use entry arrays and child/next pointers, while data nodes carry one key/value and a duplicate-chain `next` pointer.

`Tree` stores root, first leaf, fanout/minfanout, height, all-node and free-node pools, split/merge path state, a `KeyCmp` comparator, and a debug message buffer. `TREE_FLAG_UNIQUE_KEYS` optionally disables duplicate data chains.

Flag constants include `isLEAF`, `isROOT`, `isDATA`, `isFULL`, `FEWEST`, and `BTREE_MAGIC`. Search sentinel values are `BTERROR`, `BTUPPER`, and `BTLOWER`. Fanout is capped by `MAX_FANOUT` of 9.

Public declarations include `initBtree`, `freeBtree`, `insert`, `delete`, `lookup`, directory lookup/create/delete/build/is-empty APIs, stats dump APIs, enumeration APIs, and `cm_InitBPlusDir`. The implemented C file uses `bplus_Lookup` rather than the declared `lookup`.

The macro layer abstracts direct union access: key/node access (`getkey`, `getnode`, `setkey`, `setnode`), flags (`setflag`, `clrflag`, `isleaf`, `isdata`, `isroot`, `isfull`, `isfew`), entry counts, child and leaf-next pointers, free/all-node lists, split/merge paths, comparator invocation, and node numbering. Under `DEBUG_BTREE`, some flag tests call validation helpers instead of raw bit checks.

`cm_direnum_entry_t` and `cm_direnum_t` define enumeration snapshots, including per-entry name, FID, generated short name, status flags, error code, owning directory scache/user, snapshot data version, request flags, count, next index, and whether status should be fetched.

## Control flow and contracts
Callers create a tree with `initBtree(poolsz, fan, keyCmp)`, mutate it with `insert` and `delete` while holding the directory write lock, and perform lookups/enumeration while holding at least the directory read lock. Tree balancing state in `Tree.branch` is intentionally mutable and protected by the caller's locking discipline.

Directory API contracts are encoded in the prototypes: lookup/original-name/is-empty require a `cm_dirOp_t`; create/delete require a writable directory operation; build requires a `cm_scache_t`, user, and request. Enumeration is a snapshot allocation followed by `Next`/`Peek` and eventual `FreeEnumeration`.

## State and persistence behavior
All state defined here is in-memory. The tree mirrors a directory version and stores duplicated string payloads owned by the tree. The header exposes extern counters `bplus_free_tree`, `bplus_dv_error`, and `bplus_free_time` for process-wide statistics.

Macros such as `clearflags` reset both flags and magic, and `isnode` rejects `isDATA` nodes even when they carry the same magic. Free nodes are represented through the same `nextNode` union slot used by leaf chaining.

## Dependencies and integration points
This header relies on types supplied by `afsd.h` and related cache-manager headers, including `normchar_t`, `clientchar_t`, `fschar_t`, `cm_fid_t`, `cm_dirOp_t`, `cm_scache_t`, `cm_user_t`, and `cm_req_t`. It also references `cm_NormStrDup` inside macros, so source files including this header need the string helper declarations available.

Consumers include `cm_btree.c`, directory code that manages `cm_scache_t.dirBplus`, tests under `src/WINNT/afsd/test/btreetest.c`, and any code that uses `cm_BPlusDirEnumerate` snapshots.

## Risks and edge cases
The public lookup prototype is stale relative to the implementation symbol `bplus_Lookup`; this is a direct interface risk.

The macros perform allocation (`setkey`, entry moves) and direct frees in the C implementation's helper macros. Misusing them outside the intended tree algorithms can leak or double-free keys.

`setfanout(B, v)` and `setminfanout(B, v)` store `v - 1`, so code must pass logical fanout values and not already-adjusted internal values. `getminfanout` varies by root/non-root and leaf/internal status, making off-by-one errors likely in new balancing code.

Because `Node.X` is a union, using node macros on data nodes or data macros on tree nodes corrupts state. `isnode` and `isdata` checks need to gate such access in new code.

`cm_direnum_t` uses a flexible-array-style `entry[1]`; allocation must use `cm_BPlusEnumAlloc`-style sizing for counts greater than one.

## Test signals
Header-level validation should build with strict prototypes to catch the `lookup`/`bplus_Lookup` mismatch, compile both `DEBUG_BTREE` and non-debug variants, exercise max fanout clamping, verify `cm_direnum_t` allocation sizing for zero/one/many entries, and run tree mutation tests under memory checking to catch macro-owned string lifetime mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_buf.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_buf.c

## Purpose
`cm_buf.c` implements the Windows cache manager buffer package. It maintains fixed-size cache buffers keyed by AFS FID and file offset, LRU/free queues, dirty-buffer writeback, memory-mapped cache initialization, redirector-held extents, buffer reservation, validation/debug dumps, and checksum helpers. It is the local page cache layer used by directory, vnode, SMB/raw/direct I/O, dcache, and scache synchronization code.

## Important APIs, globals, and functions
Global state includes `buf_globalLock`, `buf_rdrReleaseExtentsLock`, `buf_logp`, `cm_buf_opsp`, and the process-wide `cm_data` cache fields such as buffer counts, hash tables, all/free/dirty/redirector lists, mapped header/data addresses, and counters.

Lifecycle and reference APIs are `buf_Init`, `buf_Shutdown`, `buf_Hold`, `buf_HoldLocked`, `buf_Release`, and `buf_ReleaseLocked`. Lookup/allocation APIs are `buf_FindLocked`, `buf_Find`, `buf_FindAllLocked`, `buf_FindAll`, `buf_GetNewLocked`, `buf_Get`, and `buf_Recycle`.

Dirty/writeback APIs are `buf_SetDirty`, `buf_CleanLocked`, `buf_Clean`, `buf_CleanWait`, `buf_Sync`, `buf_CleanAndReset`, `buf_CleanVnode`, `buf_FlushCleanPages`, `buf_DirtyBuffersExist`, and `buf_Truncate`. Version/invalidation helpers are `buf_InvalidateBuffers` and `buf_ForceDataVersion`.

Capacity and validation APIs are `buf_SetNBuffers`, `buf_AddBuffers`, `buf_ReserveBuffers`, `buf_TryReserveBuffers`, `buf_UnreserveBuffers`, `buf_ValidateBuffers`, `buf_ValidateBufQueues`, `cm_DumpBufHashTable`, and `buf_ForceTrace`.

Redirector integration APIs are `buf_RDRShakeAnExtentFree`, `buf_RDRShakeFileExtentsFree`, `buf_RDRShakeSomeExtentsFree`, `buf_RDRBuffersExist`, `buf_ClearRDRFlag`, `buf_InsertToRedirQueue`, `buf_RemoveFromRedirQueue`, and `buf_MoveToHeadOfRedirQueue`. Checksum helpers are `buf_ComputeCheckSum`, `buf_ValidateCheckSum`, and `buf_HexCheckSum`.

## Control flow
`buf_Init` installs the operation callback table, initializes locks once, and either builds a new mapped buffer pool or reinitializes volatile fields from an existing mapped cache. For a new cache it sizes hash tables, initializes `cm_buf_t` headers and data pointers, adds every buffer to the free/LRU list, and starts a detached incremental sync thread. Existing-cache initialization resets wait/user/error state and cleans up redirector-held extents that survived restart.

`buf_Get` page-aligns the requested offset, tries to find an existing buffer, and otherwise calls `buf_GetNewLocked`. New buffers are removed from the LRU queue, hashed by FID/offset and by FID-only chain, locked, and optionally read through `cm_buf_opsp->Readp`. Short reads are zero-padded and zero-byte reads mark EOF.

`buf_GetNewLocked` scans the LRU tail for a recyclable zero-ref clean buffer. It skips buffers with references, buffers in the same valid chunk as the requester, buffers with active read/write flags, and buffers held by the redirector. Dirty candidates are held, cleaned outside the global lock, then rechecked because another thread may have created the requested buffer. If no buffer is usable and the redirector is initialized, it requests extent releases before sleeping and retrying.

`buf_SetDirty` merges dirty byte ranges within a buffer, records the last writer user, clears EOF, and, for non-redirector writes, adds the buffer to the dirty list with a hold. `buf_IncrSyncer` wakes periodically and calls `buf_Sync`, which walks the dirty list, asks the redirector to return held extents as needed, and invokes `buf_CleanLocked` for online or unknown volumes.

`buf_CleanLocked` resolves or creates the matching scache when needed, obtains callbacks/status through `cm_SyncOp`, calls the configured `Writep` callback over the dirty subrange, and clears dirty state or records `CM_BUF_ERROR` for fatal errors. Transient server/network failures leave dirty data in place unless the request forbids retries.

File-level operations walk the FID-only hash chain. `buf_CleanVnode` returns redirector extents, cleans all dirty buffers for a vnode, and propagates fatal errors. `buf_FlushCleanPages` stabilizes the object before flushing dirty pages and recycles clean pages when refcount permits. `buf_Truncate` zeroes partial tail data or invalidates whole pages past EOF and notifies the redirector when needed.

Redirector queue operations move buffers between the normal LRU/free list and global/per-scache redirector queues. Shake functions batch `AFSFileExtentCB` records and call `RDR_RequestExtentRelease` with per-file or global pressure. `buf_ClearRDRFlag` forcibly removes redirector ownership and releases the associated holds.

## State and persistence behavior
Buffer headers and data live in the mapped cache area described by `cm_data.bufHeaderBaseAddress`, `cm_data.bufDataBaseAddress`, and `cm_data.bufEndOfData`. The buffer cache cannot be resized after creation because the virtual/persistent mapped file contains complex fixed-layout structures.

`cm_buf_t` identity is `(fid, offset)` while hashed; `dataVersion` records the file version represented by the buffer or `CM_BUF_VERSION_BAD` when unknown/invalid. Dirty state is tracked by `CM_BUF_DIRTY`, `dirty_offset`, `dirty_length`, `dirtyCounter`, `error`, and `userp`. Queue membership is tracked separately in `qFlags` (`QINHASH`, `QINLRU`, `QINDL`, `QREDIR`).

The dirty list holds an extra buffer reference until `buf_Sync` removes the clean buffer from the dirty list. Redirector-held buffers are removed from the LRU list, put on redirector queues, counted separately, and also held until returned/cleared.

Some volatile state is reset on existing-cache initialization: user pointer, wait counters, waiting flag, error, redirector queue membership, release timestamps, and bad data version for unrecovered redirector extents.

## Dependencies and integration points
The implementation depends on Windows APIs, pthreads, OpenAFS lock and queue primitives, `cm_data`, `cm_scache_t`, `cm_user_t`, `cm_req_t`, FID helpers, volume lookup/status, scache lookup/status synchronization, server priority updates, event logging, redirector APIs (`RDR_RequestExtentRelease`, `RDR_InvalidateObject`), `cm_buf_ops_t` callbacks for file data read/write/stabilize/unstabilize, optional `DISKCACHE95`, and MD5 from hcrypto.

Major consumers are `cm_dcache.c`, `cm_direct.c`, `cm_dir.c`, `cm_vnodeops.c`, `rawops.c`, SMB/SMB3 handlers, scache synchronization, and redirector code. Those consumers are responsible for setting `CM_BUF_READING`, `CM_BUF_WRITING`, and `cmFlags` consistently around asynchronous fetch/store/write paths.

## Risks and edge cases
The locking hierarchy is strict: reservations, I/O flags, buffer mutex, then `buf_globalLock`. Some recycling paths intentionally grab a buffer mutex while holding the global lock only when refcount is zero; changing that assumption can deadlock.

`buf_RDRBuffersExist` sets a local `found` flag when it sees a redirector-held buffer but returns `0` unconditionally. That appears to defeat its advertised existence test.

`buf_CleanLocked` does not itself set `CM_BUF_WRITING`; lower-level write paths and scache sync code coordinate `CM_BUF_CMSTORING`/`CM_BUF_CMWRITING` and `CM_BUF_WRITING`. New writers must preserve the wait/wakeup contract or `buf_WaitIO` callers can sleep incorrectly.

Dirty writeback clears dirty data on fatal errors to avoid endless retries, records `CM_BUF_ERROR`, and marks the data version bad. This protects liveness but can discard local dirty data after server-side fatal errors; callers need to surface the stored error.

`buf_GetNewLocked` can spin/sleep indefinitely under heavy pinning, redirector retention, or repeated dirty-clean failures. The redirector release path uses `CM_REQ_NORETRY` to return `CM_ERROR_WOULDBLOCK`, but normal paths retry.

The all-buffer and file-hash walkers hold and release buffers while traversing mutable chains. Any change to hash/list mutation must preserve the hold-next-before-release-current pattern.

## Test signals
High-value tests include buffer get/find race where another thread creates the page, LRU recycle after clean zero-ref release, dirty range coalescing, dirty-list hold/release accounting, fatal write error handling, retryable write error preservation, truncate whole and partial page behavior, `buf_FlushCleanPages` stabilization, scache recycle with valid buffers, redirector insert/remove/move queue accounting, extent shake `CM_ERROR_RETRY` and `CM_REQ_NORETRY` behavior, checksum validation, persistent-cache restart cleanup of redirector state, and validation failures from deliberately corrupted queue/hash pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_buf.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_buf.h

## Purpose
`cm_buf.h` declares the Windows cache manager buffer abstraction: fixed-size cache pages, hash macros, queue and I/O flags, callback operations supplied by the data-cache layer, global lock/log symbols, buffer lifecycle APIs, dirty/writeback APIs, redirector extent APIs, validation/debug helpers, and checksum helpers.

## Important APIs, types, and macros
`cm_buf_t` is the central buffer header. It contains global queue links, queue/hash flags, magic, all/hash/file-hash/dirty links, a per-buffer mutex, refcount, dirty counter, FID/offset identity, mapped data pointer, local I/O flags/error, last writer user, cache-manager data version and cmFlags, sync wait counters, dirty byte range, optional disk-cache pointer, debug scache pointer, redirector queue/timestamps, and an MD5 checksum buffer.

`cm_buf_ops_t` is the callback table used by `cm_buf.c`: `Writep`, `Readp`, `Stabilizep`, and `Unstabilizep`. `CM_BUF_WRITE_SCP_LOCKED` is the write flag exported for callback coordination.

Hash macros are `BUF_HASH(fidp, offsetp)` for FID+offset and `BUF_FILEHASH(fidp)` for FID-only chains. Cache type constants are `CM_BUF_CACHETYPE_FILE` and `CM_BUF_CACHETYPE_VIRTUAL`; `CM_BUF_BLOCKSIZE` follows `CM_CONFIGDEFAULT_BLOCKSIZE`.

`cmFlags` describe scache-level activity (`CM_BUF_CMFETCHING`, `CM_BUF_CMSTORING`, `CM_BUF_CMFULLYFETCHED`, `CM_BUF_CMWRITING`). `qFlags` describe global queue membership (`CM_BUF_QINHASH`, `CM_BUF_QINLRU`, `CM_BUF_QINDL`, `CM_BUF_QREDIR`). `flags` describe buffer-local I/O/data state (`CM_BUF_READING`, `CM_BUF_WRITING`, `CM_BUF_DIRTY`, `CM_BUF_ERROR`, `CM_BUF_WAITING`, `CM_BUF_EOF`).

The public API covers initialization/shutdown, reference management, I/O waits, lookup, allocation, cleaning, dirty marking, reservation, truncation, vnode flush/clean/invalidate/version forcing, diagnostics, existence checks, redirector extent release/queue manipulation, and checksum computation/validation.

## Control flow and contracts
Callers initialize the package with `buf_Init(newFile, ops, nbuffers)` before using any buffer APIs. Buffers returned from `buf_Get` are held but unlocked; callers release with `buf_Release`. Functions with `Locked` in the name assume the caller already holds `buf_globalLock` or the buffer mutex as documented by the C file.

`buf_SetDirty` requires a locked, referenced buffer and a non-null user. `buf_Clean` and `buf_CleanLocked` push dirty bytes through the configured `Writep`. `buf_WaitIO` waits on `CM_BUF_READING`/`CM_BUF_WRITING` and uses buffer wait counters plus scache wakeups.

Redirector APIs treat `CM_BUF_QREDIR` as ownership by the Windows redirector; those buffers are not ordinary LRU candidates until the redirector releases or the cache manager shakes/clears the extent.

## State and persistence behavior
The header makes the split between persistent cache identity/data and volatile synchronization explicit. The buffer's FID, offset, data pointer, data version, dirty range, and flags are the meaningful page state. Reference counts, wait counters, queue membership, and redirector timestamps are runtime coordination state guarded by `buf_globalLock`, the buffer mutex, or `scp->mx`/redirector locks as noted in comments.

`CM_BUF_VERSION_BAD` marks unknown or invalid cached data. `dirtyCounter` is bumped on dirty-to-clean/error transitions and can be used by other layers to detect changes.

## Dependencies and integration points
The header includes `osi.h` and `opr/jhash.h` and relies on cache-manager definitions from surrounding OpenAFS headers for `cm_fid_t`, `cm_scache_t`, `cm_user_t`, and `cm_req_t`. It exposes `buf_globalLock` and `buf_logp` for modules that must coordinate directly with the buffer package. It integrates with redirector code through `AFSFileExtentCB`-driven release functions implemented in the C file, and with scache/dcache code through `cmFlags` and `cm_buf_ops_t`.

## Risks and edge cases
Refcount APIs have debug macro rewrites under `DEBUG_REFCOUNT`; mixed compilation units must include this header consistently.

The hash macros assume `cm_data.buf_hashSize` is a power of two because they mask with `hashSize - 1`. Initialization must preserve that invariant.

Queue membership flags are not interchangeable with buffer-local I/O flags. Bugs that clear `CM_BUF_QREDIR` without removing redirector queue links, or clear `CM_BUF_DIRTY` without dirty-list cleanup, lead to leaked holds and corrupted lists.

The `redirq_to_cm_buf_t` container macro depends on `offsetof(cm_buf_t, redirq)` and must only be used with valid `redirq` queue nodes.

`buf_SetNBuffers` is declared as if resizing is supported, but the implementation only accepts no-op same-size values or rejects shrinking/growing after cache creation.

## Test signals
Header/API tests should compile with and without `DEBUG_REFCOUNT`, validate the hash macros against initialized power-of-two hash sizes, verify all exported functions have matching definitions, exercise qFlag/flag transitions through public APIs, and include redirector queue container conversions under queue validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_buf.h -->
