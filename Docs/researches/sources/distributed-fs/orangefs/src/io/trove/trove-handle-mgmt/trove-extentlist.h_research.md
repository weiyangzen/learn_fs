## sources/distributed-fs/orangefs/src/io/trove/trove-handle-mgmt/trove-extentlist.h

Purpose: Declares the AVL-backed extent-list data structures and operations used by Trove handle ledgers to represent free handle ranges.

Important APIs and types: `struct TROVE_handle_extent` is an inclusive `[first,last]` range plus an unused-looking backing-store `index`. `struct TROVE_handle_extentlist` records allocation size, extent/handle counts, timestamp, an `extents` array, and an AVL root. Macros `AVLDATUM`, `AVLKEY_TYPE`, `AVLKEY`, and `AVLALTKEY` specialize `avltree.h` so ranges are keyed by `first` and can also be searched by `last`. Public functions cover initialization/free, merge, allocation, range allocation, peek, explicit removal, debug display/count/stats, cutoff detection, delayed reuse, timeout setting, and extent insertion.

Control flow: The header has no runtime logic, but it defines the invariants expected by `trove-extentlist.c`: extents are non-overlapping inclusive ranges, AVL primary keys are range starts, and alternate keys are range ends. Callers are expected to initialize a list before use and serialize mutations externally.

State and persistence: The declared list contains both an AVL index and a backing array intended for historical or future persistent storage. Current implementation code uses the AVL tree as live state and leaves most array growth logic disabled. `EXTENTLIST_PURGATORY_DEFAULT` sets the default seconds before recently freed handles can return to the free pool.

Dependencies and integration points: Pulls in `pvfs2-internal.h`, `trove.h`, `trove-internal.h`, `sys/time.h`, and `avltree.h`. It is included by both `trove-extentlist.c` and `trove-ledger.c`, and indirectly by the higher-level handle manager.

Risks: The public struct exposes internal fields, so callers could mutate AVL/count/timestamp state outside the implementation. The alternate-key AVL search relies on non-overlap and adjacency invariants that are not enforced by the type system. Count fields are signed 64-bit while handle quantities are conceptually unsigned. The backing array fields can mislead maintainers because current persistence support is disabled.

Test signals: Compile tests should verify AVL macro compatibility. Behavioral tests should assert that every public function preserves non-overlap, inclusive boundaries, count fields, and timestamp expectations.
