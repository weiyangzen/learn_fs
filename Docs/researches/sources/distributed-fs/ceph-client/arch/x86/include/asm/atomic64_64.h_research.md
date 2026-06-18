
# sources/distributed-fs/ceph-client/arch/x86/include/asm/atomic64_64.h

Purpose: native 64-bit x86 implementation of `atomic64_t` operations.

Important APIs and control flow: read/write use one-copy access; add/sub/inc/dec and bitwise updates use locked qword instructions. Conditional-return helpers use `GEN_*_RMWcc`; fetch and return helpers use `xadd`; cmpxchg, try-cmpxchg, and xchg delegate to generic x86 exchange primitives. Fetch-and/or/xor loop with `arch_atomic64_try_cmpxchg()`.

State, dependencies, and risks: state is caller-provided atomic64 storage. Dependencies include x86 lock semantics, cmpxchg, alternatives, and rmwcc. Risks include relying on implicit x86 ordering for generic atomic contracts, contention in cmpxchg bitwise loops, and misuse for non-atomic composite state. Test signals come from generic atomic tests, lockless data-structure stress, and sanitizer/litmus validation.
