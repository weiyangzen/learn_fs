<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/assoc_array.c -->
# sources/distributed-fs/ceph-client/lib/assoc_array.c

## Purpose
Implements the generic RCU-friendly associative array used for key-indexed object collections. It provides lockless read-side find/iterate support while writers precompute edit scripts and publish updates atomically.

## APIs, Types, and Functions
Exports `assoc_array_iterate()`, `assoc_array_find()`, `assoc_array_destroy()`, `assoc_array_insert()`, `assoc_array_insert_set_object()`, `assoc_array_delete()`, `assoc_array_clear()`, `assoc_array_apply_edit()`, `assoc_array_cancel_edit()`, and `assoc_array_gc()`. Internal types include `assoc_array_walk_result`, `assoc_array_walk_status`, deletion collapse context, and metadata nodes/shortcuts from `assoc_array_priv.h`.

## Control Flow, State, and Persistence
Readers walk the root pointer through nodes and shortcuts using key chunks supplied by caller ops. `assoc_array_find()` lands at a terminal node and compares leaves. Iteration performs a two-pass node traversal: leaves first, then metadata, so concurrent reshapes do not miss objects, though duplicates are possible. Inserts walk to an empty tree, terminal node, or wrong shortcut, allocate needed nodes/shortcuts ahead of time, and return an edit script. Deletes clear a leaf and may collapse small subtrees. `assoc_array_apply_edit()` publishes leaf, parent-slot, back-pointer, and root changes with write barriers, adjusts leaf counts up the ancestry, and defers cleanup through RCU. GC duplicates the tree while filtering leaves through a callback, compresses sparse nodes, and swaps in the new root. State persists in caller-owned `struct assoc_array`, metadata allocations, leaf counts, and RCU-delayed destruction.

## Dependencies and Integration
Depends on `linux/assoc_array_priv.h`, RCU, slab allocation, pointer tagging helpers, and caller-provided `struct assoc_array_ops` for key extraction/comparison, object retention, and object freeing. Used by keyrings and other kernel indexes needing concurrent reads.

## Risks and Test Signals
Risks include incorrect caller locking around edit construction/application, RCU misuse by readers, pointer-tagging alignment assumptions, tree corruption from parent/back-pointer mistakes, leaf-count drift, duplicate iteration surprises, and allocation failure during complex splits. This snapshot also contains duplicated source text in cleanup logic, a source-integrity signal to verify with compilation. Test signals include insert/find/delete/replace, shortcut split cases with long common prefixes, full-node splits, GC retention and discard paths, concurrent RCU readers under writer updates, cancellation after allocation failure, KASAN/RCU stall detection, and keyring regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/assoc_array.c -->
