<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hash.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/hash.h research

Purpose: defines the generic batman-adv hashtable abstraction and inline add/remove operations used by feature modules that need RCU hlist buckets plus per-bucket spinlocks.

Important APIs and types: callback typedefs define key comparison, bucket selection, and optional free callback shape. `struct batadv_hashtable` contains the bucket table, lock array, size, and atomic generation. External functions allocate, destroy, and set lock classes. Inline `batadv_hash_add()` checks for duplicates under the selected bucket lock, inserts with `hlist_add_head_rcu()`, and increments generation. Inline `batadv_hash_remove()` selects a bucket, deletes the first matching node with `hlist_del_rcu()`, increments generation, and returns the removed node pointer.

Control flow and state behavior: callers provide both key data and the hlist node being inserted or removed. Compare callbacks receive existing nodes and key data; choose callbacks must be deterministic and return an index less than `size`. The table does not own object memory; removed nodes must be converted back to containing objects and released by the caller.

Dependencies and integration: includes `main.h`, atomic, hlist/rculist, spinlock, and lockdep. Generation is used by netlink dump code to mark consistency while iterating under bucket locks.

Risks: `batadv_hash_remove()` assumes a non-NULL hash and valid size, unlike `batadv_hash_add()` which checks NULL. Callers must not pass stack data nodes for inserted objects. Duplicate detection depends entirely on compare correctness. RCU deletion requires caller-managed grace-period safe freeing.

Test signals: duplicate insert returns 1, null add returns -1, remove missing returns NULL, generation increments exactly on successful insert/remove, lockdep catches nested table locking, and RCU readers can find/ref objects safely during concurrent delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hash.h -->
