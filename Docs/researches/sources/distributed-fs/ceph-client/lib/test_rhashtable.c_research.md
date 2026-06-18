# sources/distributed-fs/ceph-client/lib/test_rhashtable.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_rhashtable.c` is a self-test and stress test for resizable hash tables and rhlist tables. It validates insertion, lookup, deletion, max-size enforcement, duplicate-list insertion, concurrent access, and random add/delete rhlist behavior. The source was read as a complete 815-line file.

## Important APIs, Types, and Functions

Module parameters include `parm_entries`, `runs`, `max_size`, `shrinking`, `size`, `tcount`, and `enomem_retry`. Types are `struct test_obj_val`, `struct test_obj`, `struct test_obj_rhl`, and `struct thread_data`. Key functions include `my_hashfn`, `my_cmpfn`, `insert_retry`, `test_rht_lookup`, `test_bucket_stats`, `test_rhashtable`, `test_rhltable`, `test_rhashtable_max`, `print_ht`, `test_insert_dup`, `test_insert_duplicates_run`, `thread_lookup_test`, `threadfunc`, and `test_rht_init`.

## Control Flow

On load, `test_rht_init` clamps entry count, configures `test_rht_params`, allocates object arrays, then runs the basic rhashtable insertion/lookup/deletion test `runs` times. It separately checks that exceeding `max_size` fails with `-E2BIG`, tests duplicate rhlist insertion through fast and slow paths, and if `tcount` is nonzero, starts synchronized worker threads. Each worker inserts per-thread keys, validates lookups, removes entries in decreasing stride patterns, and revalidates after each phase. Finally it runs a smaller rhltable add/delete and random operation test.

## State and Persistence Behavior

The global `ht` and `rhlt` tables are initialized and destroyed per test phase. Object arrays are `vzalloc`ed and freed. Worker synchronization uses `startup_count` and `startup_wait`. There is no persistent state after module initialization completes.

## Dependencies and Integration Points

Direct dependencies include jhash, kthreads, RCU, rhashtable/rhltable, random, vmalloc, wait queues, and slab. Integration points are `rhashtable_init`, `rhashtable_insert_fast`, `rhashtable_insert_slow`, `rhashtable_lookup_fast`, `rhashtable_remove_fast`, `rhashtable_walk_*`, `rhashtable_destroy`, `rhltable_init`, `rhltable_insert`, `rhltable_lookup`, `rhltable_remove`, `rhltable_destroy`, `rhl_for_each_entry_rcu`, and RCU read-side traversal.

## Risks and Edge Cases

Large defaults can be expensive; comments note `rhltable_remove` can otherwise take minutes, so the rhltable phase uses `entries / 16`. Memory pressure can produce `-ENOMEM`; optional `enomem_retry` converts those into retry loops. The test stresses resize races and duplicate keys, but several warnings do not always propagate into a final failure code, so logs matter. Thread names contain a typo (`rhashtable_thrad`) but behavior is unaffected.

## Test Signals

Signals include per-run duration, traversal count matching `nelems` and expected entries, successful max-size rejection, duplicate insertion count matching, no worker thread errors, and final rhltable return `0`. Init returns `-EINVAL` for core basic-test failures, but some later WARN-based diagnostics require log inspection.
