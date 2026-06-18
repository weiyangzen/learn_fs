<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec.rs

## Purpose
This file implements the kernel Rust `Vec<T, A>` abstraction: a growable contiguous array whose backing storage is allocated by a kernel allocator implementing `Allocator`. It provides allocator-specific aliases `KVec<T>`, `VVec<T>`, and `KVVec<T>`, plus the exported `kvec!` macro for convenient construction with `GFP_KERNEL`.

## Important APIs, Types, and Functions
The central type is `Vec<T, A: Allocator>`, storing `ptr: NonNull<T>`, `layout: ArrayLayout<T>`, `len`, and allocator phantom state. Public APIs include `new`, `with_capacity`, `capacity`, `len`, `is_empty`, `as_slice`, `as_mut_slice`, raw pointer accessors, `spare_capacity_mut`, `reserve`, `push`, `push_within_capacity`, `insert_within_capacity`, `pop`, `remove`, `truncate`, `clear`, `drain_all`, `retain`, `into_raw_parts`, and unsafe `from_raw_parts`. Clone-oriented APIs include `extend_with`, `extend_from_slice`, `from_elem`, and `resize`. `Vec<T, KVmalloc>::shrink_to` is a temporary allocator-specific shrinking path. Trait integrations include `Drop`, `Default`, `Debug`, `Deref`, `DerefMut`, `Borrow`, `BorrowMut`, `Index`, `IndexMut`, slice equality implementations, reference iteration, owning `IntoIter`, and `AsPageIter` for `VVec<T>`.

## Control Flow and State
Growth flows through `reserve`: if spare capacity is insufficient, it doubles capacity or uses the requested minimum, validates via `ArrayLayout`, and calls `A::realloc`. Element insertion writes into spare `MaybeUninit<T>` and then uses unsafe `inc_len` only after initialization. Removal and truncation use `dec_len` to transfer ownership of initialized tail ranges before reading or dropping them. `IntoIter` takes raw parts, advances a cursor with each `next`, and frees the original buffer in `Drop`; its `collect` path can move remaining elements to the start of the buffer and attempt a shrink. `DrainAll` sets vector length to zero immediately, then owns the former elements until iteration or drop.

## State and Persistence Behavior
The vector owns initialized elements in `[0, len)` and uninitialized allocation in `[len, capacity)`. Non-ZST vectors persist heap allocation until `Drop`, explicit raw-part handoff, or `KVVec::shrink_to(0)` for an empty vector. ZST vectors use a dangling pointer and report `usize::MAX` capacity without allocation. Raw-part APIs deliberately allow allocation ownership to leave the type, so reconstruction must use the same allocator type and exact layout constraints.

## Dependencies and Integration Points
This code depends on `Allocator`, `Kmalloc`, `Vmalloc`, `KVmalloc`, `ArrayLayout`, `Flags`, `NumaNode`, kernel `Box`, page iteration helpers, and low-level pointer/slice primitives. It integrates with Rust-for-Linux allocation conventions rather than `std::vec::Vec`, and with vmalloc pages through `AsPageIter` for page-oriented kernel operations.

## Risks
Most risk is around unsafe invariants: length must increase only after initialization, raw parts must match allocator/layout, `ptr::copy` ranges must be valid under insert/remove/retain, and `IntoIter::collect` must not double-drop moved elements. `KVVec::shrink_to` is especially sensitive because it distinguishes kmalloc versus vmalloc storage with `is_vmalloc_addr`, frees pages only when beneficial, and manually copies live elements. Allocation failure paths must leave the original vector intact.

## Test Signals
The file includes KUnit tests for `retain` over all boolean predicates up to length nine, and for `KVVec::shrink_to` preserving data, shrinking empty vectors to zero capacity, no-op behavior when the minimum exceeds current capacity, and respecting minimum capacity. Doc examples cover core push, resize, raw-parts, iteration, and page-iteration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec.rs -->
