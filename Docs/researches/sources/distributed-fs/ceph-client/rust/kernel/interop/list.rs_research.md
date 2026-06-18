# sources/distributed-fs/ceph-client/rust/kernel/interop/list.rs

## Purpose
`interop/list.rs` provides Rust read/iteration wrappers for C `struct list_head` intrusive circular lists. It is intended for direct C interop, not as a native Rust list.

## Important APIs, Types, and Functions
`CListHead` wraps a `list_head` sentinel or node, with `from_raw`, `as_raw`, `next`, `is_linked`, and `new`. `CList<T, OFFSET>` views a sentinel as a typed list. `CListIter` yields `&T` by subtracting the embedded list offset. The exported `clist_create!` macro verifies the field path has type `list_head`, computes `offset_of!`, and calls `CList::from_raw`.

## Control Flow
Creation either initializes a standalone empty `list_head` with `INIT_LIST_HEAD` or casts an existing raw sentinel. Iteration starts from `head.next()`, stops when it returns to the sentinel, and converts each node to its containing item using the constant offset.

## State and Persistence
The wrapper does not own list items. It borrows a C-managed list for the lifetime of the returned reference. `CListHead::new` owns only a sentinel head used by other C APIs.

## Dependencies and Integration Points
The module depends on C `list_head`, `INIT_LIST_HEAD`, `Opaque`, pin-init, and `offset_of!`. `gpu/buddy.rs` uses it to iterate C `gpu_buddy_block` lists.

## Risks
Safety depends on the list not being concurrently modified during iteration and on `OFFSET` matching the real embedded field. `is_linked` treats an empty sentinel as not linked, which is correct for sentinel emptiness but not a full membership proof for arbitrary nodes. Wrong transparent wrapper layout can produce invalid references.

## Test Signals
Doctests and integration tests should cover empty and non-empty lists, field-offset validation, iteration order, fused iterator behavior, initialized sentinel creation, and C-owned item wrapper layout assumptions.
