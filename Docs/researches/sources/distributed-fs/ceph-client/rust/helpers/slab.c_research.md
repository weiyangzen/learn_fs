# sources/distributed-fs/ceph-client/rust/helpers/slab.c

## Purpose
Exposes aligned realloc helpers for slab and kvmalloc-backed Rust allocators.

## APIs, Types, and Functions
Exports `rust_helper_krealloc_node_align()` and `rust_helper_kvrealloc_node_align()` with `__must_check` and realloc-size annotations.

## Control Flow, State, and Persistence
State is heap allocation ownership transferred through returned pointers; no local helper state.

## Dependencies and Integration
Depends on `linux/slab.h` and Rust `Kmalloc`/`KVmalloc` allocator implementations.

## Risks and Test Signals
Risks include old-layout mismatches, losing the original pointer on allocation failure, alignment mistakes, and NUMA node misuse. Test signals are Rust allocator KUnit tests for alignment, growth/shrink, failure, and zero-size free.
