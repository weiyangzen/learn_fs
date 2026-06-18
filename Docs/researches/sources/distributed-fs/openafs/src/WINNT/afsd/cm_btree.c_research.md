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
