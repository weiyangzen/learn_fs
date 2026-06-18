## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cmpxchg.h

Purpose: implements PowerPC architecture exchange and compare-exchange primitives for 8, 16, 32, and on PPC64, 64-bit operands. It backs the generic Linux `xchg`, `cmpxchg`, and `cmpxchg64` APIs with PowerPC load-reserve/store-conditional instruction sequences.

Important APIs/types/functions: `arch_xchg_local`, `arch_xchg_relaxed`, `arch_cmpxchg`, `arch_cmpxchg_local`, `arch_cmpxchg_relaxed`, `arch_cmpxchg_acquire`, and PPC64 `arch_cmpxchg64*` macros wrap `__xchg_*` and `__cmpxchg_*` helpers. `XCHG_GEN` and `CMPXCHG_GEN` synthesize byte/halfword fallback implementations when `CONFIG_PPC_HAS_LBARX_LHARX` is absent.

Control flow: each primitive loops around `lbarx/lharx/lwarx/ldarx` and `stbcx./sthcx./stwcx./stdcx.` until the conditional store succeeds. Compare-exchange first compares the reserved value with `old`, exits without storing on mismatch, and applies entry/exit or acquire barriers according to the exported variant. Small-width fallbacks align to a 32-bit word, compute endian-sensitive bit offsets, mask the target lane, and update the containing word atomically.

State and persistence: no persistent state is owned by the header; it mutates caller memory atomically and relies on reservation granule semantics. Memory-ordering state is expressed through `PPC_ATOMIC_ENTRY_BARRIER`, `PPC_ATOMIC_EXIT_BARRIER`, `PPC_ACQUIRE_BARRIER`, memory clobbers, and local/relaxed variants.

Dependencies and integration: depends on `asm/synch.h`, `linux/bug.h`, PowerPC endian layout, and generic cmpxchg-local fallback for 32-bit `cmpxchg64_local`. It is a foundational dependency for locking, atomics, reference counts, scheduler state, and concurrent driver code.

Risks and test signals: barrier placement, clobbers, type sizes, and byte-lane masking are correctness-critical. Wrong fallback bit offsets corrupt adjacent bytes on big- or little-endian builds. Test signals include PowerPC allmodconfig builds, LKMM litmus tests, lock/RCU stress, KCSAN, atomic selftests, boot on CPUs with and without byte/halfword reserve instructions, and 32-bit `cmpxchg64_local` users.
