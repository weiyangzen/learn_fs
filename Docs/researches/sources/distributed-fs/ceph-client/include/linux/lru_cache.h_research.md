<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lru_cache.h -->
# sources/distributed-fs/ceph-client/include/linux/lru_cache.h

## Purpose
This header declares the DRBD-originated LRU cache framework for tracking a bounded active set of labeled objects and pending label changes. It is designed for activity logs and persistent write-intent style metadata.

## Important APIs, Types, and Functions
`struct lc_element` contains hash collision linkage, list membership, refcount, index, current label, and pending new label. `struct lru_cache` holds `lru`, `free`, `in_use`, and `to_be_changed` lists, a kmem cache, element metadata, hash slots, element array, stats, flags, and pending-change limits. APIs include `lc_create`, `lc_reset`, `lc_destroy`, `lc_del`, `lc_get_cumulative`, `lc_try_get`, `lc_find`, `lc_get`, `lc_put`, `lc_committed`, `lc_seq_printf_stats`, `lc_seq_dump_details`, `lc_try_lock_for_transaction`, `lc_try_lock`, `lc_unlock`, `lc_is_used`, and `lc_element_by_index`.

## Control Flow
Lookups map labels to elements through hash slots. `lc_get` may hit an active element, reuse an LRU/free element, or mark pending changes for transaction commit. `lc_put` drops references and moves unused elements toward LRU. Transaction locks stop active-set changes while metadata is committed.

## State and Persistence Behavior
Runtime state tracks active labels, refcounts, LRU order, free entries, dirty/locked/starving flags, and pending changes. The cache itself does not write persistence, but its pending-change model exists so callers can persist activity-log transactions.

## Dependencies and Integration Points
It depends on lists, slab caches, bit operations, strings, and seq files. Integration is with DRBD-like replication metadata, resync tracking, and diagnostic seq output.

## Risks and Test Signals
Risks include missing external serialization, transaction lock misuse, starvation when the active set is too small, lost pending changes, and incorrect label/index persistence by callers. Test signals include DRBD activity-log tests, crash-recovery simulations, seq stats, starvation counters, and lock/dirty flag assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lru_cache.h -->
