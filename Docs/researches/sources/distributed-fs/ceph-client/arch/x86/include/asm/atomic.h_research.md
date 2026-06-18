
# sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic.h

Purpose: x86 `atomic_t` implementation and dispatcher to 32-bit or 64-bit `atomic64_t` implementations.

Important APIs and control flow: `arch_atomic_read()`/`set()` use one-copy read/write primitives. Arithmetic operations emit locked `addl`, `subl`, `incl`, `decl`, or use `GEN_*_RMWcc` for flag-returning variants. Return/fetch operations use `xadd`; compare/exchange uses `arch_cmpxchg` and `arch_try_cmpxchg`; bitwise fetch operations loop on try-cmpxchg. The file then includes `atomic64_32.h` or `atomic64_64.h`.

State, dependencies, and risks: state is caller-owned atomic storage. Dependencies include x86 lock prefix handling, cmpxchg, rmwcc, and barrier semantics. Risks are memory-ordering expectations, integer overflow semantics, and livelock under high contention for cmpxchg loops. Test signals include LKDTM/atomic litmus tests, refcount users, lockless data-structure tests, and architecture build matrices.
