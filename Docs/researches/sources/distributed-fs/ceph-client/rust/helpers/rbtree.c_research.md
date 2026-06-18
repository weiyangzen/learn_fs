# sources/distributed-fs/ceph-client/rust/helpers/rbtree.c

## Purpose
Exposes selected red-black tree operations to Rust intrusive tree code.

## APIs, Types, and Functions
Exports `rb_link_node`, `rb_first`, and `rb_last` wrappers.

## Control Flow, State, and Persistence
Mutates or reads caller-owned rb-tree nodes and roots; no local state.

## Dependencies and Integration
Depends on `linux/rbtree.h` and Rust rbtree abstractions.

## Risks and Test Signals
Risks include incorrect parent/link pointers, missing rebalancing outside this helper, and lifetime aliasing of intrusive nodes. Test signals are insertion/removal/order tests with debug assertions.
