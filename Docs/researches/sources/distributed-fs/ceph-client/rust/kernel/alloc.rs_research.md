# sources/distributed-fs/ceph-client/rust/kernel/alloc.rs

## Purpose
Defines the public Rust kernel allocation module surface: allocator traits, allocation flags, NUMA node identifiers, allocation errors, and re-exports of box/vector types.

## APIs, Types, and Functions
Exports modules `allocator`, `kbox`, `kvec`, and `layout`; re-exports `Box`, `KBox`, `VBox`, `KVBox`, `Vec`, `KVec`, `VVec`, and `KVVec`. `AllocError` represents allocation failure. `Flags` wraps GFP bits and implements `BitOr`, `BitAnd`, `Not`, and `contains()`. `flags` exposes GFP constants and modifiers. `NumaNode::new()` validates node ids, while `NumaNode::NO_NODE` represents no preference. The unsafe `Allocator` trait defines `MIN_ALIGN`, `alloc()`, unsafe `realloc()`, and unsafe `free()`. `dangling_from_layout()` provides aligned dangling pointers for zero-sized allocations.

## Control Flow, State, and Persistence
Control flow centers on `Allocator::alloc()` delegating to `realloc(None, ...)` and `free()` delegating to `realloc(Some, zero-sized layout, ...)`. Persistent state is not held by this module, but trait implementers return allocations that remain valid until freed or reallocated. NUMA and GFP flags are passed through to the underlying kernel allocator.

## Dependencies and Integration
Depends on generated bindings for GFP constants and NUMA limits, Rust `Layout`/`NonNull`, and concrete implementations in `allocator.rs`. It is the foundation for all heap-owning Rust kernel containers.

## Risks and Test Signals
Risks include unsafe implementers violating allocation/lifetime guarantees, zero-sized allocation pointer misuse, GFP flags used in invalid contexts, and NUMA id validation drifting from kernel constants. Test signals are Rust allocator KUnit tests, fallible allocation paths, zero-sized types, alignment stress, and build coverage with different NUMA settings.
