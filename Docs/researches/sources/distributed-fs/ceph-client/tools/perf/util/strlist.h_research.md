# sources/distributed-fs/ceph-client/tools/perf/util/strlist.h

## Purpose

`strlist.h` declares the ordered string-list API backed by `rblist`.

## Important APIs, Types, and Functions

`struct str_node` stores an rbtree node and string pointer. `struct strlist` wraps `struct rblist` plus a `file_only` flag. `struct strlist_config` controls dirname substitution and filename-only behavior. The header declares create/delete/add/load/remove/find/index functions and inline helpers for membership, emptiness, count, first/next, and iteration macros.

## Control Flow and Data Flow

Consumers create a list from an optional comma-separated string, add or load entries, query by string or index, iterate in sorted order, remove entries, and delete the list.

## State and Persistence Behavior

The list owns inserted nodes and strings. Iteration is over rbtree order, not insertion order. `file_only` affects parsing at creation time.

## Dependencies and Integration Points

It depends on Linux rbtree, bool support, and `rblist.h`. It is used by perf option filters and elision helpers.

## Risks and Edge Cases

The safe-iteration macro computes `strlist__next(pos)` even when `pos` is NULL for empty lists, but the inline handles NULL. Callers must respect that returned `str_node->s` is owned by the list.

## Test Signals

Compile coverage and strlist parser/iteration/removal tests validate the header contract.
