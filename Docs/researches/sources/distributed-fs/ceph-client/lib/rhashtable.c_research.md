## sources/distributed-fs/ceph-client/lib/rhashtable.c

Purpose: generic resizable, concurrent hash table implementation supporting RCU lookups, per-bucket locking, async resizing, nested bucket allocation fallback, rhlist duplicate-key mode, and walkers.

Important APIs/functions: public exports include `rhashtable_init_noprof()`, `rhltable_init_noprof()`, `rhashtable_insert_slow()`, walker APIs (`rhashtable_walk_enter/exit/start_check/next/peek/stop`), `rhashtable_free_and_destroy()`, `rhashtable_destroy()`, and nested bucket helpers. Internal resize functions include `rhashtable_rehash_alloc()`, `rhashtable_rehash_attach()`, `rhashtable_rehash_table()`, and deferred workers.

Control flow: initialization validates hash/key callbacks, chooses size, allocates a bucket table, seeds hash salt, and initializes work items. Insert scans the current or future table, locks a bucket, checks duplicates/elasticity, inserts with RCU pointer updates, increments element count, and schedules rehash when load grows. Resize attaches a future table, migrates chains bucket by bucket, publishes the new table with RCU, tracks walkers, and frees old tables after grace period. Iterators preserve table/slot/skip state and report `-EAGAIN` across resizes.

State and persistence: `struct rhashtable` owns table pointers, params, counters, lock/mutex, work/irq_work, and optional rhlist mode. Bucket tables hold random salts, bucket heads, future table links, walkers, and optional nested tables.

Dependencies/integration: uses RCU, atomics, jhash/random, workqueues, irq_work, vmalloc/slab, lockdep, and nulls lists.

Risks/test signals: resize concurrency, nested allocation, walker relinking, and teardown ordering are high-risk. Comments document lock-order and teardown fixes. Users usually validate through subsystem tests exercising insert/delete/lookup under RCU.
