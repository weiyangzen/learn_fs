## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputhreads.h

Purpose: defines topology helpers for mapping logical CPUs to hardware threads, cores, subcores, and TLB-sharing siblings.

Important APIs/types/functions: exports `threads_per_core`, `threads_per_subcore`, `threads_shift`, `threads_core_mask`, `cpu_nr_cores()`, `cpu_core_index_of_thread()`, `cpu_first_thread_of_core()`, sibling helpers, `get_tensr()`, `book3e_start_thread()`, `book3e_stop_thread()`, and `INVALID_THREAD_HWID`.

Control flow: helpers use power-of-two thread layout arithmetic. POWER9 big-core TLB sharing adjusts first/last sibling and step values when `CPU_FTR_ARCH_300` and eight threads per core are present. `get_tensr()` reads `SPRN_TENSR` on BookE SMT systems.

State and persistence: reads topology globals established during CPU discovery. No persistent state is modified by the inline helpers.

Dependencies and integration: depends on cpumasks and CPU feature tests. Used by SMP bring-up, IPI routing, TLB shootdown, CPU hotplug, BookE thread control, and scheduler/topology code.

Risks and test signals: the arithmetic assumes power-of-two thread counts and uniform numbering. Wrong sibling masks can send IPIs or TLB invalidations to the wrong CPUs. Test signals include SMT boot on Book3S/BookE, TLB shootdown stress, CPU hotplug, scheduler topology validation, and POWER9 big-core tests.
