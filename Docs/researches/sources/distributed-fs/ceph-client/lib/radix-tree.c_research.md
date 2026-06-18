# sources/distributed-fs/ceph-client/lib/radix-tree.c

## Purpose
Implements the legacy radix tree and IDR backing library, now sharing concepts and entries with xarray while preserving exported radix-tree APIs.

## APIs, Control Flow, and State
Exports node preload, insert, lookup, replace, tag, iteration, gang lookup, delete, IDR preload/free-slot/destroy helpers, and initialization. Global state includes `radix_tree_node_cachep` and per-CPU `radix_tree_preloads`. Nodes are allocated from slab or a preloaded per-CPU pool for nonblocking inserts; freeing is RCU-delayed and clears slots/tags before slab return. Insert calls `__radix_tree_create()`, extends tree height as needed, allocates missing nodes, and inserts into an empty slot. Lookup descends through internal entries and retries on `RADIX_TREE_RETRY`. Tags propagate upward to root flags and support tagged iteration. Delete clears tags or marks IDR slots free, replaces slots with NULL, shrinks single-child roots, and frees empty nodes. IDR free-slot discovery uses the `IDR_FREE` tag to find or create free indices up to a max.

## Dependencies, Integration, Risks, and Tests
Depends on bitmap/bitops, RCU, percpu/local locks, slab, CPU hotplug, xarray entry encoding, IDR definitions, and `lib/radix-tree.h`. Risks include RCU lifetime misuse by callers, tag propagation bugs, preloading lock misuse, internal/value entry accounting errors, IDR NULL semantics, CPU hotplug preload leaks, and iteration under concurrent mutation. Test signals include radix-tree and IDR selftests, xarray tests, RCU stress, CPU hotplug tests, gang lookup/tag iteration checks, and KASAN/KCSAN coverage.
