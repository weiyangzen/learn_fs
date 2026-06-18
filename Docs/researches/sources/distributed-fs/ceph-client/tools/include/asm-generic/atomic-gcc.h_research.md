# sources/distributed-fs/ceph-client/tools/include/asm-generic/atomic-gcc.h

## Purpose

This tools header supplies generic GCC-based atomic operations for architectures without a tools-specific atomic implementation.

## APIs, State, and Dependencies

It defines `ATOMIC_INIT`, `atomic_read`, `atomic_set`, `atomic_inc`, `atomic_dec_and_test`, `cmpxchg`, `atomic_cmpxchg`, `test_and_set_bit`, and `test_and_clear_bit`. The implementation uses `READ_ONCE`, GCC `__sync_*` builtins, and bit helpers `BIT_MASK` and `BIT_WORD`. It assumes `atomic_t` has a `counter` field supplied by included Linux types. No runtime state is stored in the header; operations mutate caller-provided atomic variables and bitmaps.

## Risks and Test Signals

Correctness depends on GCC builtin semantics and on matching the kernel-style `atomic_t` layout. `atomic_set` is a plain store rather than `WRITE_ONCE`, unlike `atomic_read`, so users needing strict compiler access semantics should check call sites. Tests are compile coverage on non-x86 tool builds and concurrency smoke tests for atomic counters and bit operations.
