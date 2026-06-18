# sources/distributed-fs/ceph-client/rust/helpers/atomic_ext.c

## Purpose
Adds Rust helper wrappers for small integer and pointer atomic-like operations not covered by the generated `atomic_t` helpers.

## APIs, Types, and Functions
Macro families generate `read`, `set`, `read_acquire`, `set_release`, `xchg` variants, and `try_cmpxchg` variants for `s8`, `s16`, and `const void *` pointer storage.

## Control Flow, State, and Persistence
Control flow is simple macro-expanded delegation to `READ_ONCE`, `WRITE_ONCE`, `smp_load_acquire`, `smp_store_release`, `xchg*`, and `try_cmpxchg*`. State is only the caller-provided memory location.

## Dependencies and Integration
Depends on `asm/barrier.h`, `asm/rwonce.h`, `linux/atomic.h`, and architecture support for byte/halfword/pointer exchange operations on Rust-supported architectures.

## Risks and Test Signals
Risks include unsupported atomic RMW width on a new Rust architecture, pointer constness mismatches, and callers assuming full `atomic_t` semantics for plain storage. Test signals are cross-architecture builds and Rust tests for memory-ordering-sensitive pointer/state machines.
