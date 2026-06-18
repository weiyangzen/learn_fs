# sources/distributed-fs/ceph-client/rust/kernel/alloc/allocator.rs

## Purpose
Implements the concrete Rust kernel allocators backed by `kmalloc`, `vmalloc`, and `kvmalloc`, plus a page iterator export for vmalloc allocations.

## APIs, Types, and Functions
Defines zero-sized allocator marker types `Kmalloc`, `Vmalloc`, and `KVmalloc`. `ReallocFunc` wraps C aligned realloc helpers (`krealloc_node_align`, `vrealloc_node_align`, `kvrealloc_node_align`) and centralizes pointer/size handling. `Kmalloc::aligned_layout()` pads layouts so slab alignment satisfies Rust layout requirements. `Vmalloc::to_page()` converts a vmalloc pointer to a borrowed page. Unsafe `Allocator` impls provide `MIN_ALIGN` and delegate `realloc()` to the selected C helper. The `rust_allocator` KUnit module tests alignment for all three allocators.

## Control Flow, State, and Persistence
Allocation control flow normalizes zero-size requests to aligned dangling pointers, turns zero-size reallocation into free semantics, and preserves old allocations on failure according to C realloc helper behavior. Persistent state is heap memory owned by callers; no allocator instance state exists because the marker types are ZSTs.

## Dependencies and Integration
Depends on Rust allocation traits, generated bindings for aligned realloc helpers and alignment constants, `page::BorrowedPage`, and C helpers from `slab.c`/`vmalloc.c`. It integrates with `Box`, `Vec`, and page iteration.

## Risks and Test Signals
Risks include old-layout mismatches, incorrect padding for kmalloc alignment, assuming vmalloc memory is physically contiguous, pointer validity in `to_page()`, and C helper behavior changes. Test signals are KUnit `test_alignment`, allocation failure injection, large `KVmalloc` fallback cases, page iterator tests, and zero-sized/growth/shrink coverage.
