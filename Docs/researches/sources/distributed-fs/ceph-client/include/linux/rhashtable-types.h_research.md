# sources/distributed-fs/ceph-client/include/linux/rhashtable-types.h

Purpose: this header provides the foundational type definitions for Linux's resizable concurrent hash table without pulling in the full inline implementation.

Important APIs/types/functions: it defines `struct rhash_head`, `struct rhlist_head`, `struct rhashtable_compare_arg`, callback typedefs `rht_hashfn_t`, `rht_obj_hashfn_t`, and `rht_obj_cmpfn_t`, construction parameters `struct rhashtable_params`, table handles `struct rhashtable` and `struct rhltable`, walker state `struct rhashtable_walker`, iterator state `struct rhashtable_iter`, and init APIs `rhashtable_init()`/`rhltable_init()` wrapping `_noprof` with allocation profiling hooks.

Control flow: users embed `rhash_head` or `rhlist_head` in objects, fill params describing key/head offsets and hash/compare functions, initialize a table, then use full `rhashtable.h` helpers for lookup/mutation/walk. `rhltable` supports duplicate-key lists.

State and persistence: `struct rhashtable` persists current bucket table pointer, key length, maximum elements, params, duplicate-list mode, deferred resize work, IRQ work, mutex, walker lock, element count, and optional allocation tag. Iterators persist traversal position and walker registration.

Dependencies and integration points: depends on atomics, workqueue/irq-work types, mutexes, allocation profiling, and the full rhashtable implementation. It is included by structures that need to embed hash heads without all helpers.

Risks: offsets and key lengths must match object layout exactly. Iterator state has RCU/walker lifetime constraints enforced by full APIs. Test signals include init parameter validation, duplicate-key rhltable behavior, allocation profiling builds, and compile coverage for headers embedding `rhash_head`.
