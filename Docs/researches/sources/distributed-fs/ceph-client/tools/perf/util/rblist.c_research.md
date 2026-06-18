# sources/distributed-fs/ceph-client/tools/perf/util/rblist.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rblist.c` implements a generic cached red-black-tree list wrapper with caller-provided node comparison, allocation, and deletion callbacks.

## Important APIs, Types, and Functions

Public functions are `rblist__init`, `rblist__exit`, `rblist__delete`, `rblist__add_node`, `rblist__remove_node`, `rblist__find`, `rblist__findnew`, and `rblist__entry`. The shared implementation for lookup and optional creation is `__rblist__findnew`.

## Control Flow

Add and find-new walk the cached RB tree from the root, compare each existing node with the candidate entry, choose left or right branches, and reject duplicates. Creation calls the user `node_new` callback, links the node with `rb_link_node`, inserts/rebalances with `rb_insert_color_cached`, and increments `nr_entries`. Removal erases from the cached tree, decrements count, and invokes the user delete callback. Exit walks from the cached first node, removes every entry, and leaves no nodes behind. Indexed lookup iterates in sorted order until the requested ordinal.

## State and Persistence Behavior

All state is in-memory in `struct rblist`: cached RB root and entry count. The wrapper owns tree membership but delegates node payload allocation/deletion to callbacks. There is no persistence or synchronization.

## Dependencies and Integration Points

It depends on Linux rbtree primitives and the callback contract in `rblist.h`. Many perf subsystems use this pattern for sorted unique containers.

## Risks and Edge Cases

Correct ordering depends entirely on a consistent `node_cmp`. If `node_new` or `node_delete` have side effects, tree operations inherit those risks. No NULL callback checks are performed. `rblist__entry` is O(n), not indexed-tree optimized. The container is not thread-safe.

## Test Signals

Unit tests should cover insert ordering, duplicate rejection with `-EEXIST`, allocation failure with `-ENOMEM`, find vs findnew behavior, leftmost cache correctness, entry count updates, removal callbacks, full exit/delete cleanup, and indexed iteration.
