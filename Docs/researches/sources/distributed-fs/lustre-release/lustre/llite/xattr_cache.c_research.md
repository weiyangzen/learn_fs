<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr_cache.c -->
# sources/distributed-fs/lustre-release/lustre/llite/xattr_cache.c

## Purpose
`xattr_cache.c` implements an inode-local client cache for MDT xattrs. It fetches whole xattr sets under an LDLM xattr lock, stores name/value pairs in a protected list, serves get/list operations, preserves encryption context across cache emptying, and invalidates the cache on lock cancellation or explicit destroy.

## Important APIs, Types, And Functions
The cache entry type is `struct ll_xattr_entry`. Public functions are `ll_xattr_init()`, `ll_xattr_fini()`, `ll_xattr_cache_destroy()`, `ll_xattr_cache_empty()`, `ll_xattr_cache_get()`, and `ll_xattr_cache_insert()`. Internal helpers include `ll_xattr_find_get_lock()`, `ll_xattr_cache_refill()`, `ll_xattr_cache_add()`, `ll_xattr_cache_del()`, and `ll_xattr_cache_list()`.

## Control Flow
`ll_xattr_cache_get()` takes a read lock and refills if the full cache is needed and not filled. Refill serializes enqueue with `lli_xattrs_enq_lock`, tries to match an existing `MDS_INODELOCK_XATTR` PR lock, otherwise enqueues an intent that requests names, values, and lengths. It validates reply capsules, initializes the cache if needed, filters ACL access, security labels, and `trusted.som`, adds the rest, marks `LLIF_XATTR_CACHE_FILLED`, attaches lock data, and drops the intent lock. Reads then copy a single value, list names, or synthesize virtual `trusted.projid`.

## State And Persistence
State lives in `ll_inode_info::lli_xattrs`, protected by `lli_xattrs_list_rwsem`, with flags `LLIF_XATTR_CACHE` and `LLIF_XATTR_CACHE_FILLED`. `xattr_kmem` backs entry objects, while names and values are separately allocated. Lock state is held by LDLM and tied back to the inode through `ll_set_lock_data()`.

## Dependencies And Integration Points
The file depends on llite inode flags/locks, MDC intent locks, request capsules (`RMF_EADATA`, `RMF_EAVALS`, `RMF_EAVALS_LENS`), LDLM xattr inodebits locks, operation statistics, encryption xattr naming, project IDs, and failpoints for pause/ENOMEM.

## Risks And Edge Cases
There is no atomic match-or-enqueue API, so refill uses an explicit enqueue mutex to avoid duplicate fetches. Protocol validation must catch broken name NULs and value lengths. Duplicate encryption contexts are ignored because they are immutable. `-ERANGE` during refill is converted to `-EAGAIN` so callers can fall back to direct getxattr.

## Test Signals
Cover cache hit/miss/refill, parallel refill races, lock match versus enqueue, cancellation/error paths, list buffer sizing, virtual project ID reads, encryption context insert/preserve, cache empty/destroy, malformed server replies, and failpoints for pause and allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr_cache.c -->
