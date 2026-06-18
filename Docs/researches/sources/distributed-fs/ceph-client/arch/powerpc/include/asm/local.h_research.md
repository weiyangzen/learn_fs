# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/local.h

Purpose: implements PowerPC Book3S 64-bit `local_t` per-CPU arithmetic using PMU-aware local interrupt masking, and falls back to `asm-generic/local.h` elsewhere.

Important APIs/types/functions: defines `local_t`, `LOCAL_INIT`, `local_read`, `local_set`, add/sub/inc/dec return and test macros, `local_cmpxchg`, `local_try_cmpxchg`, `local_xchg`, `local_add_unless`, `local_inc_not_zero`, and raw `__local_*` helpers.

Control flow: update helpers save PMU/local IRQ state with `powerpc_local_irq_pmu_save`, modify the local counter, and restore state. Compare/exchange variants perform the compare while interrupts are masked.

State and persistence: mutates caller-owned `local_t.v`; no global state. The guarantee is local-CPU atomicity, not inter-CPU atomicity.

Dependencies and integration points: depends on percpu, atomic, irqflags, and `asm/hw_irq.h`; used by per-CPU counters where full atomics are unnecessary.

Risks: callers must not use `local_t` for cross-CPU synchronization. The raw `__local_dec(l)` macro increments rather than decrements in this source, so consumers should avoid raw helpers unless they know the local convention and tests cover it.

Test signals: compile Book3S 64 and generic fallback configs, run per-CPU counter tests, lockdep/irq tracing around PMU interrupt masking, and inspect raw helper users.
