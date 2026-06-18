# sources/distributed-fs/ceph-client/kernel/bpf/range_tree.h

Purpose: declares the BPF arena range-tree structure and operations for setting, clearing, checking, finding, initializing, and destroying contiguous ranges. The source was read as a complete 21-line file.

Important APIs/types: `struct range_tree` with `it_root` and `range_size_root`; functions `range_tree_init`, `range_tree_destroy`, `range_tree_clear`, `range_tree_set`, `is_range_tree_set`, and `range_tree_find`.

Control flow: no executable flow is defined in the header. It exposes the API contract implemented by `range_tree.c`.

State and persistence: callers embed or allocate `struct range_tree`; its roots persist until `range_tree_destroy`. Range nodes are private to the implementation.

Dependencies/integration: requires rb-tree types from included kernel headers through users/implementation. It is a private BPF kernel header for BPF arena allocation logic.

Risks and edge cases: callers must provide synchronization and valid range bounds because the API does not encode locking or maximum size. `range_tree_find` returns signed `s64`, using negative errno values for failure.

Test signals: compile coverage of BPF arena users and runtime tests for all range-tree API functions.
