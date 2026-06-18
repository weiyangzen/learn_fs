# sources/distributed-fs/ceph-client/rust/helpers/atomic.c

## Purpose
Generated Rust helper translation unit for Linux `atomic_t` and `atomic64_t` operations, exposing C inline/macro atomic APIs as callable Rust FFI symbols.

## APIs, Types, and Functions
Defines many `rust_helper_atomic_*` and `rust_helper_atomic64_*` wrappers for read/set, add/sub/inc/dec, return and fetch forms, relaxed/acquire/release variants, xchg/cmpxchg/try_cmpxchg, add/sub unless, inc/dec predicates, and bitwise and/or/xor/andnot operations where supported.

## Control Flow, State, and Persistence
Each helper directly delegates to the corresponding kernel atomic primitive and persists no state beyond modifying the pointed atomic object. Ordering semantics are inherited exactly from the wrapped primitive, so control flow is a single call-return boundary.

## Dependencies and Integration
Depends on `linux/atomic.h` and the generator `scripts/atomic/gen-rust-atomic-helpers.sh`; it is included by `helpers.c` and bindgen-generated into Rust helper declarations.

## Risks and Test Signals
Risks include generator drift from C atomic API changes, incorrect memory-order wrapper selection, architecture-specific atomic availability, and Rust callers passing invalid pointers or wrong lifetime assumptions. Test signals are regenerated diff checks, Rust atomic abstraction tests, KCSAN/lock-free stress, and architecture builds covering both 32-bit and 64-bit atomics.
