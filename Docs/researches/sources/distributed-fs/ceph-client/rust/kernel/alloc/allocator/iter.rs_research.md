# sources/distributed-fs/ceph-client/rust/kernel/alloc/allocator/iter.rs

## Purpose
Implements iteration over the pages backing a `Vmalloc` allocation.

## APIs, Types, and Functions
`VmallocPageIter<'a>` stores a non-null page-aligned buffer pointer, byte size, current page index, and lifetime marker. It implements `Iterator<Item = page::BorrowedPage<'a>>`, `size_hint()`, unsafe constructor `new()`, `size()`, and `page_count()`.

## Control Flow, State, and Persistence
`next()` computes `index * PAGE_SIZE` with overflow checking, stops when the offset reaches the allocation size, advances the index, derives a pointer into the allocation, and converts it to a borrowed page via `Vmalloc::to_page()`. Persistent state is the iterator index and borrowed lifetime tied to the backing allocation; it does not own the allocation.

## Dependencies and Integration
Depends on `Vmalloc::to_page()`, `crate::page::PAGE_SIZE`, `BorrowedPage`, `NonNull`, and Rust iterator conventions. It integrates with `AsPageIter` for `VBox<T>`.

## Risks and Test Signals
Risks include unsafe constructor misuse with non-vmalloc or non-page-aligned pointers, backing allocation freed while iterating, overflow for enormous sizes, and last partial page handling. Test signals are iteration over zero, one, partial, and multi-page `VBox` allocations and page-fill operations through returned borrowed pages.
