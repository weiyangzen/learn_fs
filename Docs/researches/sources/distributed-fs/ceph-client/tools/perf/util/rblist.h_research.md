# sources/distributed-fs/ceph-client/tools/perf/util/rblist.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rblist.h` declares the generic red-black-list wrapper used by perf code to build sorted unique collections with custom node payloads.

## Important APIs, Types, and Functions

`struct rblist` stores `struct rb_root_cached entries`, `nr_entries`, and callbacks `node_cmp`, `node_new`, and `node_delete`. Public APIs mirror the implementation: init, exit, delete, add, remove, find, find-or-create, and indexed entry lookup. Inline helpers are `rblist__empty` and `rblist__nr_entries`.

## Control Flow

The header has no runtime flow beyond inline count checks. Callers embed `struct rblist`, initialize callbacks, then use the implementation to maintain the tree.

## State and Persistence Behavior

State is in-memory and callback-owned. The wrapper tracks count and tree root but does not define payload layout.

## Dependencies and Integration Points

It includes Linux rbtree support and `<stdbool.h>`. The comments document the expected embedding pattern for node and list structs.

## Risks and Edge Cases

The API requires callback initialization before use. Inline helpers assume non-NULL `rblist`. Payload ownership and ordering are not enforced by the type system.

## Test Signals

Compile-time embedding tests and runtime coverage from `rblist.c` operations validate the contract.
