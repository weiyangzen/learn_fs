# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/membarrier.h

Purpose: implements the PowerPC architecture hook for membarrier behavior during address-space switches.

Important APIs/types/functions: `membarrier_arch_switch_mm(prev, next, tsk)` conditionally issues `smp_mb()` when switching into an mm that has private or global expedited membarrier state and a previous mm exists.

Control flow: context-switch code calls this hook after storing `rq->curr` and before returning to userspace. Most switches return early on SMP when no expedited membarrier state is set.

State and persistence: reads `next->membarrier_state`; no state is written.

Dependencies and integration points: relies on SMP, atomic membarrier state bits, scheduler context-switch ordering, and generic membarrier syscall semantics.

Risks: missing the barrier can violate userspace membarrier guarantees. Adding unnecessary barriers can hurt context-switch performance. The `prev` check depends on kernel/userspace switch ordering documented in the comment.

Test signals: membarrier selftests, stress context switching between processes with expedited registrations, and memory-order litmus tests on SMP PowerPC.
