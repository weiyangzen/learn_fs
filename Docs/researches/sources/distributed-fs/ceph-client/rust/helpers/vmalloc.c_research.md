# sources/distributed-fs/ceph-client/rust/helpers/vmalloc.c

## Purpose
Exposes aligned vmalloc realloc for Rust virtual-memory allocators.

## APIs, Types, and Functions
`rust_helper_vrealloc_node_align()` wraps `vrealloc_node_align()`.

## Control Flow, State, and Persistence
State is vmalloc allocation ownership; no helper-local state.

## Dependencies and Integration
Depends on `linux/vmalloc.h` and Rust `Vmalloc` allocator implementation.

## Risks and Test Signals
Risks include alignment/size mismatches, pointer loss on failure, NUMA behavior assumptions, and page-iterator safety. Test signals are Rust allocator KUnit alignment tests and large allocation growth/shrink cases.
