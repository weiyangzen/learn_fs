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
