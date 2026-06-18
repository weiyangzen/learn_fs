
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg_64.h

Purpose: x86-64 64-bit and 128-bit compare-exchange support.

Important APIs and control flow: qword macros validate `sizeof(*ptr) == 8` and delegate to generic cmpxchg/try-cmpxchg. `union __u128_halves` splits 128-bit values for `cmpxchg16b`; `arch_cmpxchg128`, local variants, and try variants emit locked or local `cmpxchg16b` and return old values or success flags. `system_has_cmpxchg128()` checks `X86_FEATURE_CX16`.

State, dependencies, and risks: state is qword or 16-byte memory, usually lockless shared objects. Dependencies include CX16 support, alignment expectations, and compiler support for `u128`. Risks include using cmpxchg128 on unsupported hardware, insufficient alignment, and local variants on shared data. Test signals are 128-bit cmpxchg build tests, lockless algorithms using double-word CAS, and CPU feature fallback tests.
