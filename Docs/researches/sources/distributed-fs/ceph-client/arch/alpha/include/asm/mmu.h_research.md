# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mmu.h

This header defines Alpha's MMU context type as `unsigned long mm_context_t[NR_CPUS]`: one ASN/context bitmap or value per CPU.

There is no control flow. State lives in each mm's per-CPU context array and is used by context switch, TLB, and icache-ASN flushing code. Dependencies include `NR_CPUS` availability from kernel configuration. Risks are array sizing for large CPU counts and assumptions in cacheflush/mmu_context code about per-CPU context invalidation. Tests are process context switching, TLB flushes, and SMP builds.
