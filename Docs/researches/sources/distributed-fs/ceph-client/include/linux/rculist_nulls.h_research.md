# sources/distributed-fs/ceph-client/include/linux/rculist_nulls.h

Purpose: provides RCU helpers for nulls-terminated hash lists, where the end marker encodes bucket identity so lockless readers can detect races with node movement or table changes.

Important APIs and types: helpers expose first/next/pprev RCU pointers, delete with or without reinitialization, add head/tail, add fake node, replace with or without old-node initialization, and traverse through `hlist_nulls_for_each_entry_rcu()` or safe variant. Traversal includes a compiler barrier so restarted loops reread the first element.

Control flow: writers serialize updates, publish head/next changes with RCU assignment, and preserve nulls markers at list ends. Readers traverse under RCU until `is_a_nulls(pos)` is true; higher-level lookup code can inspect the marker to decide whether a restart is needed.

State and persistence: state is caller-owned nulls hlist nodes and heads in memory. Removed nodes remain valid until grace-period cleanup.

Dependencies and integration points: depends on `list_nulls.h` and RCU. It is commonly used by networking hash tables where entries can move between buckets during lockless lookup.

Risks and test signals: risks include wrong nulls marker after table changes, missing traversal barrier, early free, replacing unhashed nodes, tail insertion marker corruption, and lookup loops that fail to restart on marker mismatch. Test concurrent rehash/move/delete/lookup, marker mismatch restart logic, fake-node deletion, replace-init behavior, and lockdep RCU coverage.
