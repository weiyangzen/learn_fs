<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/layout.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/layout.rs

## Purpose
This file provides `ArrayLayout<T>`, a small checked wrapper for array allocation layouts used by kernel allocator-backed containers.

## Important APIs, Types, and Functions
`LayoutError` marks invalid layout construction. `ArrayLayout<T>` stores an element count and enforces the invariant `len * size_of::<T>() <= isize::MAX`. It exposes `empty`, checked `new`, unsafe `new_unchecked`, `len`, `is_empty`, and `size`, and converts into `core::alloc::Layout`.

## Control Flow and State
`new` multiplies the requested length by element size with `checked_mul` and rejects overflow or sizes above `isize::MAX`. `new_unchecked` bypasses validation for callers that have already established the invariant. Conversion to `Layout` calls `Layout::array::<T>` and unwraps unchecked because `ArrayLayout`'s invariant should make failure impossible.

## State and Persistence Behavior
`ArrayLayout` is copyable and stores only the logical element count plus phantom type identity. It persists no allocation itself; it describes allocation size and alignment for other allocators and containers.

## Dependencies and Integration Points
The type depends only on `core::alloc::Layout` and `PhantomData`. It is used by `kvec.rs` to record vector capacity and to pass exact old/new layouts into allocator `realloc`/`free` calls.

## Risks
Incorrect use of `new_unchecked` can poison allocator calls with layouts exceeding pointer offset limits. Because `From<ArrayLayout<T>> for Layout` unwraps unchecked, invariant violations would become undefined behavior. ZST behavior requires care because `size()` is zero regardless of length.

## Test Signals
Doc examples validate normal construction and two failure modes: multiplication overflow and byte sizes above `isize::MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/layout.rs -->
