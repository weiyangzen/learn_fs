## sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/predefine.rs

Purpose: supplies built-in `AtomicType` and `AtomicAdd` implementations for primitive bool, integer, pointer, and pointer-sized types, plus KUnit coverage for the public atomic API.

Important APIs/types/functions: implementations cover `bool`, `i8`, `i16`, raw pointers, `i32`, `i64`, `isize`, `usize`, `u32`, and `u64`. `isize_atomic_repr` selects `i32` or `i64` based on kernel/test pointer width. `static_assert!` checks size/alignment compatibility. KUnit tests use `for_each_type!` to exercise many primitive widths.

Control flow: unsigned and pointer-sized types map onto signed atomic representations with casts for arithmetic deltas. Pointer types map to `*const c_void`. Tests construct atomics, call operations, and assert results.

State/persistence: no production state; test module creates stack-local atomics.

Dependencies/integration: depends on `AtomicType`, `AtomicAdd`, `Atomic`, ordering markers, `static_assert!`, `c_void`, and KUnit macro support.

Risks: transmutability assumptions for unsigned-to-signed representations are core to correctness. Pointer atomic support is for pointer values only; dereferencing remains the caller's unsafe responsibility. `bool` is represented as `i8`, while `AtomicFlag` may use a wider representation elsewhere for RMW efficiency.

Test signals: KUnit tests cover basic, acquire/release, xchg, cmpxchg, arithmetic, bool, pointer, and flag behavior, providing the strongest test coverage in this subset.
