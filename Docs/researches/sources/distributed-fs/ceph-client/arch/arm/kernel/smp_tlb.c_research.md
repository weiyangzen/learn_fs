# sources/distributed-fs/ceph-client/arch/arm/kernel/smp_tlb.c

Purpose: provides SMP-aware TLB and branch predictor flush operations, broadcasting flushes to relevant CPUs and applying Cortex-A15/Brahma-B15 erratum 798181 workarounds.

Important APIs/types/functions: `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_kernel_page`, `flush_tlb_range`, `flush_tlb_kernel_range`, `flush_bp_all`, and optional `erratum_a15_798181_init`. IPI helpers call local flush functions.

Control flow: each flush checks `tlb_ops_need_broadcast`; broadcast paths call `on_each_cpu` or `on_each_cpu_mask` with local IPI helpers, while non-broadcast paths use local flushes. User-address page/range flushes temporarily enable uaccess where required. Erratum handling may issue extra local invalidation and synchronous DMB broadcasts to affected CPUs or mm masks.

State and persistence: optional global function pointer `erratum_a15_798181_handler` encodes selected workaround level.

Dependencies and integration: MM/TLB core, SMP call functions, uaccess PAN helpers, CPU ID/revision registers, `mm_cpumask`, and setup-time erratum init.

Risks: missing a CPU in mask leaves stale translations; over-broadcast hurts performance; erratum detection must match CPU revision. Test signals include mmap/munmap stress on SMP, kernel mapping changes, A15 erratum platforms, and branch predictor flush users.
