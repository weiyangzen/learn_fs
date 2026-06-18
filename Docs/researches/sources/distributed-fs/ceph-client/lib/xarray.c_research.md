# sources/distributed-fs/ceph-client/lib/xarray.c

## Purpose
Implements Linux XArray: an RCU-readable, lock-protected indexed pointer store with radix-tree nodes, marks, allocation tracking, retry entries, value entries, sibling entries, optional multi-index entries, and iteration helpers.

## APIs and control flow
Advanced exports include `xas_load`, `xas_nomem`, `xas_create_range`, `xas_store`, mark operations, multi-index split helpers, `xas_pause`, `xas_find`, `xas_find_marked`, and conflict search. Public wrappers include `xa_load`, `xa_store`, `__xa_store`, `xa_erase`, `__xa_erase`, `__xa_cmpxchg`, `__xa_insert`, `xa_store_range`, `xa_get_order`, `__xa_alloc`, `__xa_alloc_cyclic`, mark get/set/clear, `xa_find`, `xa_find_after`, `xa_extract`, `xa_delete_node`, and `xa_destroy`. Lookups start at `xas_start`, descend through nodes, and return leaf/internal/bounds/error states. Stores expand/create nodes, replace slots, update counts and marks, free detached subtrees with retry entries for RCU walkers, and shrink empty roots.

## State, dependencies, and integration
State persists in caller-owned `struct xarray` and slab-allocated `xa_node`s. Readers use RCU; writers use the xarray lock variant encoded in flags. Marks aggregate from leaves to root flags, and allocation mode uses `XA_FREE_MARK`, `XA_ZERO_ENTRY`, and cyclic wrap flags. Dependencies include bitmap helpers, RCU, slab/LRU allocation, `linux/xarray.h`, and radix-tree internals.

## Risks and test signals
Risks center on RCU lifetime, mark propagation, retry entries, sibling/multi-index invariants, lock rules, and allocation retry behavior that may drop locks. Tests should cover node expand/shrink, stores/erases, marks, allocation/cyclic allocation, range stores, split helpers, RCU retry behavior, extraction, and debug `XA_NODE_BUG_ON` paths.
