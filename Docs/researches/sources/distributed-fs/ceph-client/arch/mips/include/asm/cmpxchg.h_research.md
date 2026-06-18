<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cmpxchg.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cmpxchg.h

**Purpose:** Implements MIPS `xchg`, `cmpxchg`, and `cmpxchg64` primitives.

**Important APIs/types/functions:** `__arch_xchg`, `arch_xchg`, `__cmpxchg`, `arch_cmpxchg_local`, `arch_cmpxchg`, and 64-bit variants. Small 1/2-byte operations are delegated to out-of-line helpers; bad sizes call compile-time error stubs.

**Control flow:** LL/SC loops implement 4/8-byte exchanges when available; fallback disables IRQs locally. 32-bit SMP `cmpxchg64` uses `lld/scd`, disables interrupts to protect 64-bit register halves, and requires CPU 64-bit capability.

**State, dependencies, integration:** Core synchronization primitive for locks, atomics, and reference updates. Depends on barriers, CPU features, asm constraints, and Loongson workarounds.

**Risks and test signals:** Size handling, memory ordering, and 32-bit `cmpxchg64` register splitting are high-risk. Test all operand sizes, SMP stress, no-LLSC fallback, unsupported `cmpxchg64` build errors, and Loongson workaround codegen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cmpxchg.h -->
