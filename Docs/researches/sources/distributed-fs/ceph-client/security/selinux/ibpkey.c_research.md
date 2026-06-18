## sources/distributed-fs/ceph-client/security/selinux/ibpkey.c

### Purpose
`ibpkey.c` implements SELinux's fast cache from Infiniband subnet prefix plus P_Key number to a policy SID. P_Key labels are policy-managed, but per-operation lookups need a bounded RCU-friendly cache similar to SELinux netif/netnode/netport caches.

### Important APIs, types, and functions
The exported APIs are `sel_ib_pkey_sid(u64 subnet_prefix, u16 pkey_num, u32 *sid)`, `sel_ib_pkey_flush()`, and `sel_ib_pkey_init()`. Internal types are `struct sel_ib_pkey_bkt`, which tracks a bucket list and size, and `struct sel_ib_pkey`, which embeds `struct pkey_security_struct`, a list node, and an RCU head. Helper functions include `sel_ib_pkey_hashfn`, `sel_ib_pkey_find`, `sel_ib_pkey_insert`, and `sel_ib_pkey_sid_slow`.

### Control flow
The fast path takes `rcu_read_lock()`, searches the bucket selected by the P_Key number, and returns the cached SID on hit. On miss, the slow path takes `sel_ib_pkey_lock`, repeats the lookup to avoid duplicate inserts, asks the security server through `security_ib_pkey_sid()`, and inserts a newly allocated cache entry if allocation succeeds. Bucket growth is bounded by `SEL_PKEY_HASH_BKT_LIMIT`; inserting at a full bucket evicts the tail with `list_del_rcu()` and `kfree_rcu()`.

### State and persistence
The cache is in-memory only: a static 256-bucket hash table plus one spinlock. Policy remains authoritative, and cache state is flushed by `sel_ib_pkey_flush()` on policy reset through `hooks.c`'s AVC callback. Allocation failure after a successful policy lookup does not fail the access path; the SID is returned but not cached.

### Dependencies and integration points
This file depends on Linux RCU/list/spinlock primitives, `initcalls.h`, `ibpkey.h`, `objsec.h`, and the security server function `security_ib_pkey_sid()`. It is consumed by `selinux_ib_pkey_access()` in `hooks.c`, which audits and checks `INFINIBAND_PKEY__ACCESS` against the returned P_Key SID.

### Risks
The hash function only uses the P_Key number, so many subnets with the same P_Key can collide. The bounded bucket eviction policy is simple FIFO-by-tail and can churn under adversarial or very large P_Key sets. Correctness depends on policy reset flushing the cache; stale entries would otherwise carry old SID decisions.

### Test signals
Exercise cache hit/miss behavior with repeated P_Key access, policy reload flushing, failure handling with allocation pressure, and multi-subnet same-P_Key collisions. Build coverage requires `CONFIG_SECURITY_INFINIBAND`.
