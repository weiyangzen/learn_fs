
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg.h

Purpose: generic x86 exchange, compare-exchange, try-compare-exchange, and xadd primitives for 1/2/4/8-byte operands.

Important APIs and control flow: size selector macros map qword support out on 32-bit. `__xchg_op()` emits `xchg` or `xadd` per operand size and reports wrong sizes through compile-time/link errors. `__raw_cmpxchg()` and `__raw_try_cmpxchg()` emit lockable cmpxchg variants and update the expected-value pointer on failure. Public macros include `arch_xchg`, `arch_cmpxchg`, sync/local variants, `arch_try_cmpxchg`, and `xadd`.

State, dependencies, and risks: state is caller-owned memory and expected-value variables. Dependencies include lock-prefix alternatives, cpufeatures, and 32/64-bit cmpxchg extension headers. Risks include unsupported operand sizes, accidental local variants in SMP-shared state, qword use on 32-bit without the right helper, and inline-asm constraint bugs. Test signals include atomic tests, cmpxchg64/128 build coverage, and lockless algorithms.
