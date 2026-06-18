# sources/distributed-fs/ceph-client/include/linux/rhashtable.h

Purpose: this header provides the main inline implementation and API for Linux's resizable, scalable, RCU-friendly concurrent hash table and duplicate-key hash-list table.

Important APIs/types/functions: key internals include `struct bucket_table`, nulls markers, hash helpers (`rht_key_get_hash`, `rht_key_hashfn`, `rht_head_hashfn`), growth/shrink predicates, bucket lock helpers, traversal macros, lookup helpers, insertion helpers, removal/replacement helpers, walkers, and destroy APIs. Public operations include `rhashtable_lookup()`, `rhashtable_lookup_fast()`, `rhashtable_insert_fast()`, lookup-and-insert variants, `rhashtable_remove_fast()`, `rhashtable_replace_fast()`, `rhltable_lookup/insert/remove`, walker enter/start/next/stop/exit, and free/destroy.

Control flow: lookups RCU-dereference the current bucket table, compute a bucket, walk nulls-terminated chains, and restart on `future_tbl` during resize. Inserts take a per-bucket bit spinlock, check duplicate keys unless plain insert without key, insert at head, increment element count, and queue deferred resize if load exceeds thresholds; high chain elasticity or active resize falls back to slow path. Removal locks the old and possibly future table buckets until the object is found, unlinks it, decrements count, and schedules shrink if allowed. Replacement verifies old/new hash equality before swapping under bucket lock.

State and persistence: bucket tables persist size, hash seed, walker list, future table pointer, lockdep map, and bucket pointers whose low bit is used as lock state. Table state persists through `struct rhashtable` from `rhashtable-types.h`, including deferred work and atomic element count. Object lifetime remains caller-owned and RCU-sensitive.

Dependencies and integration points: depends on RCU, workqueues, irq_work, jhash, list_nulls, bit spinlocks, lockdep, and allocation hooks. It is widely used by networking, filesystems, and kernel lookup caches requiring concurrent resize.

Risks: callers must honor RCU/object lifetime rules, supply correct params, and avoid using fast lookup when objects can disappear after RCU unlock. Elasticity protects against hash-flood attacks unless disabled. The bucket pointer lock-bit trick is subtle and relies on pointer alignment. Test signals include rhashtable selftests, concurrent insert/remove/lookup under KCSAN/lockdep, resize growth/shrink, duplicate-key rhltable tests, hash collision/elasticity tests, and RCU stall/leak detection during destroy.
