<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intlist.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intlist.h

## Purpose

`intlist.h` declares the integer rblist wrapper and iteration helpers used by perf utility code.

## Important APIs, Types, and Functions

`struct int_node` embeds an rb node, an unsigned long key `i`, and a `priv` pointer. `struct intlist` wraps `struct rblist`. The header declares create/delete/add/remove/find/findnew/entry functions and inline helpers for membership, emptiness, count, first/next, and safe/unsafe iteration macros.

## Control Flow

Inline iteration starts at `rb_first_cached()` and follows `rb_next()`. The safe macro stores the next pointer before each loop body so callers may remove the current node.

## State and Persistence Behavior

The header defines in-memory tree layout only. `priv` lifetime is not managed by intlist.

## Dependencies and Integration Points

It includes Linux rb-tree and perf `rblist.h`, and is consumed by filters such as pid lists in KVM/stat code.

## Risks and Edge Cases

`intlist__for_each_entry_safe` initializes `n` from `intlist__next(pos)` even when `pos` is NULL; the inline next handles NULL, so this is safe but worth preserving. Callers must not free `priv` implicitly through `intlist__delete()`.

## Test Signals

Compile tests should cover macro use in empty and non-empty lists. Runtime tests should remove nodes during safe iteration and confirm sorted traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intlist.h -->
