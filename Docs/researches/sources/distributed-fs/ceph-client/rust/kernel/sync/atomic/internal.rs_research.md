## sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/internal.rs

Purpose: provides the sealed low-level implementation layer that maps Rust atomic representations onto concrete kernel C atomic helper functions.

Important APIs/types/functions: `AtomicImpl` marks supported representation types (`i8`, `i16`, `*const c_void`, `i32`, `i64`) and their arithmetic `Delta`. `AtomicRepr<T>` wraps `UnsafeCell<T>`. Macro families declare and implement `AtomicBasicOps`, `AtomicExchangeOps`, and `AtomicArithmeticOps` for the relevant representation-to-C-helper mappings.

Control flow: `declare_and_impl_atomic_methods!` expands a type map into trait declarations and implementations. Generated methods cast `AtomicRepr::as_ptr()` to the C helper's expected pointer type, then call helpers like `atomic_read`, `atomic64_xchg`, `atomic_i8_read_acquire`, or `atomic_ptr_try_cmpxchg_relaxed`.

State/persistence: state is the underlying `UnsafeCell` memory. The module owns no global state.

Dependencies/integration: depends on generated bindings, paste macros, `UnsafeCell`, `c_void`, and architecture config. It includes a static assertion that current i8/i16/pointer helpers require `CONFIG_ARCH_SUPPORTS_ATOMIC_RMW`.

Risks: macro-generated safety comments are generic, so invocation-site requirements must remain accurate. Byte/halfword/pointer atomicity currently assumes native atomic RMW support. Arithmetic ops are intentionally limited to `i32` and `i64` representations.

Test signals: indirect KUnit coverage through public atomic tests. Build coverage across architectures is especially important because helper availability and config assertions are architecture-sensitive.
