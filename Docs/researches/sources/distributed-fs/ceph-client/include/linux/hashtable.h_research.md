<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hashtable.h -->
# sources/distributed-fs/ceph-client/include/linux/hashtable.h

Purpose: This header implements statically sized kernel hash tables using arrays of `hlist_head` buckets.

Important APIs/types/functions: Definition macros include `DEFINE_HASHTABLE()`, `DEFINE_READ_MOSTLY_HASHTABLE()`, and `DECLARE_HASHTABLE()`. Sizing macros are `HASH_SIZE()` and `HASH_BITS()`. `hash_min()` selects `hash_32()` for small keys or `hash_long()` otherwise. Helpers include `hash_init()`, `hash_add()`, `hash_add_rcu()`, `hash_hashed()`, `hash_empty()`, `hash_del()`, `hash_del_rcu()`, and iteration macros for all buckets, RCU, safe removal, possible matching bucket, possible RCU/notrace, and possible safe removal.

Control flow, state, and persistence: A table is an in-place bucket array owned by the caller. Objects embed `hlist_node` members and are inserted into bucket heads based on the hashed key. The macros do not compare keys; callers must compare object keys inside `hash_for_each_possible*` loops. RCU variants rely on caller-side RCU read-side locking and deferred freeing.

Dependencies/integration: It depends on list/hlist, kernel array helpers, `hash.h`, and RCU list primitives.

Risks and test signals: `HASH_BITS()` only works on actual arrays, not pointers, so `hash_init()` and macros require compile-time arrays. Missing key comparison after bucket iteration causes false matches. Tests should cover table init, add/delete, empty state, safe deletion while iterating, RCU insertion/deletion under readers, bucket distribution, and pointer-vs-array misuse caught at build time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hashtable.h -->
