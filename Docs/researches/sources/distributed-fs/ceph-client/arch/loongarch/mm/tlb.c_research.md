<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/tlb.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/tlb.c

### Purpose
`tlb.c` implements LoongArch local TLB flush/update primitives and installs TLB exception handlers and hardware page-walker configuration.

### Important APIs, Types, And Functions
Public functions are `local_flush_tlb_all()`, `local_flush_tlb_user()`, `local_flush_tlb_kernel()`, `local_flush_tlb_mm()`, `local_flush_tlb_range()`, `local_flush_tlb_kernel_range()`, `local_flush_tlb_page()`, `local_flush_tlb_one()`, `__update_tlb()`, and `tlb_init()`. Internal helpers include `__update_hugetlb()`, `setup_ptwalker()`, `output_pgtable_bits_defines()`, and `setup_tlb_handler()`.

### Control Flow
Flush helpers choose between ASID context drop and targeted `invtlb` operations based on ASID validity and range size. `__update_tlb()` inserts paired PTEs for a faulting address unless hardware PTW is active, with a special hugepage path. `setup_ptwalker()` programs CSR page-walk controls and PGD roots. CPU 0 copies/refills vector handlers into exception slots; secondary CPUs may allocate per-CPU exception-handler pages under NUMA. `tlb_init()` sets page sizes and invokes setup.

### State, Persistence, And Dependencies
State includes CPU CSR registers, ASIDs, `mm_cpumask`, TLB entries, exception vector memory, optional `pcpu_handlers`, and page-table bits. Dependencies include LoongArch CSR/TLB instructions, `current_cpu_data.tlbsize`, generic MMU context, exception tables, NUMA allocation, and handlers from `tlbex.S`.

### Integration Points
Generic `flush_tlb_*` paths call these primitives. `fault.c` and `tlbex.S` share TLB update/fault behavior. Suspend/resume restores exception vectors and flushes TLBs.

### Risks
Range-size heuristics must match hardware TLB organization. Paired PTE handling rounds to two-page boundaries and can be wrong if PTE alignment assumptions change. Per-CPU handler allocation must avoid using unavailable memory during CPU bring-up.

### Test Signals
Run TLB shootdown, context-switch ASID stress, hugepage faults, vmalloc/module mappings, CPU hotplug/NUMA boot, and hardware PTW versus software refill configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/tlb.c -->
