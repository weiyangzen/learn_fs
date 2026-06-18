# subset-b-000843 research

Grouped source-tree-aligned research for SPARC headers under `sources/distributed-fs/ceph-client/arch/sparc/include/asm`. Each section is bounded for reconciliation into the mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pci.h

Purpose: SPARC PCI policy header defining platform PCI bus defaults and, on sparc64, IOMMU bypass and `/proc/bus/pci` mmap integration.

Important APIs/types/functions: functions/helpers `pci_domain_nr`, `pci_proc_domain`; macros/constants `___ASM_SPARC_PCI_H`, `pcibios_assign_all_busses`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `PCI_IRQ_NONE`, `PCI64_REQUIRED_MASK`, `PCI64_ADDR_BASE`, `HAVE_PCI_MMAP`, `arch_can_pci_mmap_io`, `HAVE_ARCH_PCI_GET_UNMAPPED_AREA`, `ARCH_GENERIC_PCI_MMAP_RESOURCE`, `get_pci_unmapped_area`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_PCI_H`, `CONFIG_SPARC64`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, PCI paths rather than through standalone functions.

State and persistence behavior: State is compile-time policy only; the runtime domain number is supplied by `pci_domain_nr()`, and framebuffer-style unmapped-area selection is delegated to `get_fb_unmapped_area`.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management, PCI; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: PCI probing, resource mmap tests, 64-bit DMA mask negotiation, and controller-domain enumeration are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pcic.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pcic.h

Purpose: JavaEngine 1 PCIC controller contract: MMIO register offsets, interrupt/status bits, the `linux_pcic` controller structure, and optional probe/IRQ/time hooks under `CONFIG_PCIC_PCI`.

Important APIs/types/functions: types `linux_pcic`; functions/helpers `pcic_present`, `pcic_probe`, `pci_time_init`, `sun4m_pci_init_IRQ`; macros/constants `__SPARC_PCIC_H`, `PCI_SPACE_SIZE`, `PCI_DIAGNOSTIC_0`, `PCI_SIZE_0`, `PCI_SIZE_1`, `PCI_SIZE_2`, `PCI_SIZE_3`, `PCI_SIZE_4`, `PCI_SIZE_5`, `PCI_PIO_CONTROL`, `PCI_DVMA_CONTROL`, `PCI_DVMA_CONTROL_INACTIVITY_REQ`, `PCI_DVMA_CONTROL_IOTLB_ENABLE`, `PCI_DVMA_CONTROL_IOTLB_DISABLE`, `PCI_DVMA_CONTROL_INACTIVITY_ACK`, `PCI_INTERRUPT_CONTROL`, `PCI_CPU_INTERRUPT_PENDING`, `PCI_DIAGNOSTIC_1`, plus 62 more.

Control flow: The file is driven by preprocessor gates such as `__SPARC_PCIC_H`, `__ASSEMBLER__`, `CONFIG_PCIC_PCI`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, SMP, timekeeping, PCI paths rather than through standalone functions.

State and persistence behavior: State lives in mapped PCIC registers, `struct resource` ranges, the embedded `linux_pbm_info`, and interrupt mapping arrays; disabled builds provide zero/no-op stubs.

Dependencies and integration points: Includes/dependencies: `linux/types.h`, `linux/smp.h`, `linux/pci.h`, `linux/ioport.h`, `asm/pbm.h`. Integration points include memory-management, TLB/MMU, SMP, timekeeping, PCI; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Exercise PCIC probe on JavaEngine/sun4m PCI, register resource reservation, IOTLB enable/disable, interrupt pending/clear paths, and timer IRQ setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pcic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pcr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pcr.h

Purpose: Performance Control Register abstraction for sparc64 performance counters and NMI overflow programming across Niagara-era PCR layouts.

Important APIs/types/functions: types `pcr_ops`; functions/helpers `deferred_pcr_work_irq`, `schedule_deferred_pcr_work`, `pcr_arch_init`; macros/constants `__PCR_H`, `PCR_PIC_PRIV`, `PCR_STRACE`, `PCR_UTRACE`, `PCR_N2_HTRACE`, `PCR_N2_TOE_OV0`, `PCR_N2_TOE_OV1`, `PCR_N2_MASK0`, `PCR_N2_MASK0_SHIFT`, `PCR_N2_SL0`, `PCR_N2_SL0_SHIFT`, `PCR_N2_OV0`, `PCR_N2_MASK1`, `PCR_N2_MASK1_SHIFT`, `PCR_N2_SL1`, `PCR_N2_SL1_SHIFT`, `PCR_N2_OV1`, `PCR_N4_OV`, plus 11 more.

Control flow: The file is driven by preprocessor gates such as `__PCR_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: The global `pcr_ops` vtable persists the selected CPU implementation; deferred PCR work reschedules counter handling out of constrained interrupt contexts.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: Perf-event PMU tests, NMI overflow delivery, deferred IRQ work, and N2/N4 event mask programming are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu.h

Purpose: selects `percpu_64.h` or `percpu_32.h` from `CONFIG_SPARC64` so generic kernel code can include one SPARC per-CPU entry point.

Important APIs/types/functions: macros/constants `___ASM_SPARC_PERCPU_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_PERCPU_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/percpu_64.h`, `asm/percpu_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu_32.h

Purpose: SPARC32-specific implementation header for `percpu_32.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `__ARCH_SPARC_PERCPU__`.

Control flow: The file is driven by preprocessor gates such as `__ARCH_SPARC_PERCPU__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm-generic/percpu.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build and runtime coverage on sparc32 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu_64.h

Purpose: sparc64 per-CPU addressing header binding the per-CPU base to global register `%g5` and, under SMP, to `trap_block[cpu].__per_cpu_base`.

Important APIs/types/functions: functions/helpers `asm`; macros/constants `__ARCH_SPARC64_PERCPU__`, `__per_cpu_offset`, `per_cpu_offset`, `__my_cpu_offset`.

Control flow: The file is driven by preprocessor gates such as `__ARCH_SPARC64_PERCPU__`, `BUILD_VDSO`, `CONFIG_SMP`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP, VDSO paths rather than through standalone functions.

State and persistence behavior: Persistent state is per-CPU trap-block storage plus the register-resident `__local_per_cpu_offset`; VDSO builds intentionally avoid the register declaration.

Dependencies and integration points: Includes/dependencies: `linux/compiler.h`, `asm/trap_block.h`, `asm-generic/percpu.h`. Integration points include SMP, VDSO; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Boot CPU bring-up, secondary CPU per-CPU variable access, VDSO builds, and context switch preservation of `%g5` are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/perf_event.h

Purpose: Perf helper that synthesizes a `pt_regs` snapshot for caller sampling by reading `%pstate`, `%asi`, `%pil`, `%i7`, and `%i6`.

Important APIs/types/functions: macros/constants `__ASM_SPARC_PERF_EVENT_H`, `perf_arch_fetch_caller_regs`.

Control flow: The file is driven by preprocessor gates such as `__ASM_SPARC_PERF_EVENT_H`, `CONFIG_PERF_EVENTS`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: No persistent state is owned; the macro mutates a caller-supplied `pt_regs` and encodes the current control registers into `tstate`.

Dependencies and integration points: Includes/dependencies: `asm/ptrace.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, configuration-specific build gaps. Test signals: Perf sampling backtraces, interrupt-context samples, and register-window frame-pointer validity are the practical tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc.h

Purpose: selects the 64-bit or 32-bit page-table allocation backend, preserving the common Linux `pgd_alloc`, `pmd_alloc_one`, and PTE allocation API names.

Important APIs/types/functions: macros/constants `___ASM_SPARC_PGALLOC_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_PGALLOC_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/pgalloc_64.h`, `asm/pgalloc_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc_32.h

Purpose: SPARC32 SRMMU page-table allocator interface using non-cacheable SRMMU table memory for PGD/PMD/PTE levels.

Important APIs/types/functions: types `page`; functions/helpers `srmmu_free_nocache`, `free_pgd_fast`, `pud_set`, `free_pmd_fast`, `pmd_set`, `pte_alloc_one`, `free_pte_fast`, `pte_free`; macros/constants `_SPARC_PGALLOC_H`, `pgd_free`, `pgd_alloc`, `pud_populate`, `pmd_free`, `__pmd_free_tlb`, `pmd_populate`, `pmd_populate_kernel`, `pte_free_kernel`, `__pte_free_tlb`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_PGALLOC_H`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: Page table state persists in nocache allocations from `srmmu_get_nocache`; freeing returns memory through `srmmu_free_nocache`, and `pud_set`/`pmd_set` encode SRMMU PTD physical pointers.

Dependencies and integration points: Includes/dependencies: `linux/kernel.h`, `linux/sched.h`, `linux/pgtable.h`, `asm/pgtsrmmu.h`, `asm/vaddrs.h`, `asm/page.h`. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions. Test signals: Fork/exit page-table allocation, TLB-gather freeing, nocache allocator exhaustion, and SRMMU page table alignment are test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc_64.h

Purpose: sparc64 page-table allocator using `pgtable_cache`, page-backed PTE allocations, deferred frees, and SMP-safe TLB table removal.

Important APIs/types/functions: types `mmu_gather`; functions/helpers `__p4d_populate`, `pgd_free`, `__pud_populate`, `pud_free`, `pmd_free`, `pte_alloc_one`, `pte_free_kernel`, `pte_free`, `pte_free_defer`, `pgtable_free`, `tlb_remove_table`, `pgtable_free_tlb`, `__tlb_remove_table`, `__pte_free_tlb`; macros/constants `_SPARC64_PGALLOC_H`, `p4d_populate`, `pud_populate`, `pte_free_defer`, `pmd_populate_kernel`, `pmd_populate`, `__pmd_free_tlb`, `__pud_free_tlb`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_PGALLOC_H`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, SMP paths rather than through standalone functions.

State and persistence behavior: State is split between slab-backed upper tables, page-backed PTE tables, and `mmu_gather` deferred-free entries with a low-bit tag identifying page tables.

Dependencies and integration points: Includes/dependencies: `linux/kernel.h`, `linux/sched.h`, `linux/mm.h`, `linux/slab.h`, `asm/spitfire.h`, `asm/cpudata.h`, `asm/cacheflush.h`, `asm/page.h`. Integration points include memory-management, TLB/MMU, SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: MM teardown under SMP, THP split/free, RCU/deferred PTE free, and pgtable cache lifetime should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable.h

Purpose: routes generic MM code to `pgtable_64.h` or `pgtable_32.h`, hiding the very different Spitfire/SRMMU page table encodings.

Important APIs/types/functions: macros/constants `___ASM_SPARC_PGTABLE_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_PGTABLE_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/pgtable_64.h`, `asm/pgtable_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable_32.h

Purpose: SPARC32 SRMMU page-table definition: address-space layout, PTE/PMD/PGD sizing, atomic PTE updates via `swap`, swap-entry encoding, IO-space PFN encoding, and SRMMU helper hooks.

Important APIs/types/functions: types `vm_area_struct`, `page`, `seq_file`; functions/helpers `load_mmu`, `calc_highpages`, `bootmem_init`, `paging_init`, `srmmu_swap`, `set_pte`, `srmmu_device_memory`, `pmd_pfn`, `__pmd_page`, `pmd_page_vaddr`, `pte_present`, `pte_none`, `__pte_clear`, `pte_clear`, `pmd_bad`, `pmd_present`, plus 33 more; macros/constants `_SPARC_PGTABLE_H`, `PMD_SHIFT`, `PMD_SIZE`, `PMD_MASK`, `PMD_ALIGN`, `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`, `PGDIR_ALIGN`, `pte_ERROR`, `pmd_ERROR`, `pgd_ERROR`, `PTRS_PER_PTE`, `PTRS_PER_PMD`, `PTRS_PER_PGD`, `USER_PTRS_PER_PGD`, `PTE_SIZE`, `PAGE_NONE`, plus 28 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_PGTABLE_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, locking paths rather than through standalone functions.

State and persistence behavior: Persistent state includes `phys_base`, `pfn_base`, `ptr_in_current_pgd`, SRMMU PTE bits, and page-table entries updated atomically so hardware ref/mod bits stay coherent.

Dependencies and integration points: Includes/dependencies: `linux/const.h`, `asm-generic/pgtable-nopud.h`, `linux/spinlock.h`, `linux/mm_types.h`, `asm/types.h`, `asm/pgtsrmmu.h`, `asm/vaddrs.h`, `asm/oplib.h`, `asm/cpu_type.h`. Integration points include memory-management, TLB/MMU, locking; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: Fault handling, swap PTE round trips, `io_remap_pfn_range`, cache-disabled mappings, and `ptep_set_access_flags` TLB flush behavior are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable_64.h

Purpose: sparc64 Spitfire/SUN4V page-table definition covering virtual layout, PTE bit encodings, huge pages, ADI tag save/restore, TLB batching, swap entries, IO PFNs, and fault-handler integration.

Important APIs/types/functions: types `seq_file`, `vm_area_struct`; functions/helpers `kern_addr_valid`, `mk_pte_io`, `pte_sz_bits`, `pfn_pte`, `pfn_pmd`, `pte_pfn`, `pte_modify`, `pmd_modify`, `pgprot_noncached`, `pte_dirty`, `pte_write`, `arch_make_huge_pte`, `__pte_default_huge_mask`, `pte_mkhuge`, `is_default_hugetlb_pte`, `is_hugetlb_pmd`, plus 70 more; macros/constants `_SPARC64_PGTABLE_H`, `TLBTEMP_BASE`, `TSBMAP_8K_BASE`, `TSBMAP_4M_BASE`, `MODULES_VADDR`, `MODULES_LEN`, `MODULES_END`, `LOW_OBP_ADDRESS`, `HI_OBP_ADDRESS`, `VMALLOC_START`, `VMEMMAP_BASE`, `PMD_SHIFT`, `PMD_SIZE`, `PMD_MASK`, `PMD_BITS`, `PUD_SHIFT`, `PUD_SIZE`, `PUD_MASK`, plus 143 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_PGTABLE_H`, `(MAX_PHYS_ADDRESS_BITS > PGDIR_SHIFT + PGDIR_BITS)`, `(PGDIR_SHIFT + PGDIR_BITS) != 53`, `(PMD_SHIFT != HPAGE_SHIFT)`, `__ASSEMBLER__`, `REAL_HPAGE_SHIFT != 22`, `CONFIG_TRANSPARENT_HUGEPAGE`, `defined(CONFIG_HUGETLB_PAGE) || defined(CONFIG_TRANSPARENT_HUGEPAGE)`, plus 2 more; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State persists in page tables, TSB/TLB batch queues, global patchable page-size/cache masks, ADI tag metadata, `VMALLOC_END`, and platform-selected SUN4U/SUN4V bit layouts.

Dependencies and integration points: Includes/dependencies: `asm-generic/pgtable-nop4d.h`, `linux/compiler.h`, `linux/const.h`, `asm/types.h`, `asm/spitfire.h`, `asm/asi.h`, `asm/adi.h`, `asm/page.h`, `asm/processor.h`, `linux/sched.h`, `asm/tlbflush.h`. Integration points include memory-management, TLB/MMU, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Boot on sun4u/sun4v, THP/hugetlb, ADI MCD mappings, swap migration, framebuffer mmap alignment, D-cache alias moves, and TLB batch flushing are critical tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtsrmmu.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtsrmmu.h

Purpose: SRMMU register and PTE-bit header for SPARC32, with inline assembly accessors for context-table pointer, context id, fault status/address, whole-TLB flush, and raw PTE reads.

Important APIs/types/functions: functions/helpers `srmmu_get_mmureg`, `srmmu_set_mmureg`, `srmmu_set_ctable_ptr`, `srmmu_set_context`, `srmmu_get_context`, `srmmu_get_fstatus`, `srmmu_get_faddr`, `srmmu_flush_whole_tlb`, `srmmu_get_pte`; macros/constants `_SPARC_PGTSRMMU_H`, `SRMMU_MAX_CONTEXTS`, `SRMMU_PTE_TABLE_SIZE`, `SRMMU_PMD_TABLE_SIZE`, `SRMMU_PGD_TABLE_SIZE`, `SRMMU_ET_MASK`, `SRMMU_ET_INVALID`, `SRMMU_ET_PTD`, `SRMMU_ET_PTE`, `SRMMU_ET_REPTE`, `SRMMU_CTX_PMASK`, `SRMMU_PTD_PMASK`, `SRMMU_PTE_PMASK`, `SRMMU_CACHE`, `SRMMU_DIRTY`, `SRMMU_REF`, `SRMMU_NOREAD`, `SRMMU_EXEC`, plus 24 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_PGTSRMMU_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: Architectural state is the SRMMU control/context registers, TLB contents, and fault registers addressed through alternate-space loads/stores.

Dependencies and integration points: Includes/dependencies: `asm/page.h`, `asm/thread_info.h`. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: SRMMU boot, context switch, page-fault decoding, TLB flush coverage, and CPU errata around ASI accesses should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtsrmmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pil.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pil.h

Purpose: Constant/ABI header for `pil.h` supplying numeric definitions consumed by low-level SPARC code.

Important APIs/types/functions: macros/constants `_SPARC64_PIL_H`, `PIL_SMP_CALL_FUNC`, `PIL_SMP_RECEIVE_SIGNAL`, `PIL_SMP_CAPTURE`, `PIL_DEVICE_IRQ`, `PIL_SMP_CALL_FUNC_SNGL`, `PIL_DEFERRED_PCR_WORK`, `PIL_KGDB_CAPTURE`, `PIL_NORMAL_MAX`, `PIL_NMI`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_PIL_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP paths rather than through standalone functions.

State and persistence behavior: State is external hardware or ABI state represented by constants; the header itself has no mutable storage.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Compile-time users plus boot/runtime paths that decode these constants are the main tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor.h

Purpose: combines VDSO processor helpers with the 32-bit or 64-bit task/CPU context header selected by `CONFIG_SPARC64`.

Important APIs/types/functions: macros/constants `___ASM_SPARC_PROCESSOR_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_PROCESSOR_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into VDSO, scheduler/task paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/vdso/processor.h`, `asm/processor_64.h`, `asm/processor_32.h`. Integration points include VDSO, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor_32.h

Purpose: SPARC32 task processor-state definition: user address bounds, thread FP/window state, `start_thread()`, kernel stack register access, math emulation hooks, and idle callback declaration.

Important APIs/types/functions: types `task_struct`, `fpq`, `thread_struct`; functions/helpers `start_thread`, `__get_wchan`, `do_mathemu`, `void`; macros/constants `__ASM_SPARC_PROCESSOR_H`, `TASK_SIZE`, `STACK_TOP`, `STACK_TOP_MAX`, `INIT_THREAD`, `task_pt_regs`, `KSTK_EIP`, `KSTK_ESP`.

Control flow: The file is driven by preprocessor gates such as `__ASM_SPARC_PROCESSOR_H`, `__KERNEL__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into scheduler/task paths rather than through standalone functions.

State and persistence behavior: State persists in `thread_struct`, saved register windows, FPU queue/status, `last_task_used_math`, and the initial user pt_regs window created by `start_thread`.

Dependencies and integration points: Includes/dependencies: `asm/psr.h`, `asm/ptrace.h`, `asm/head.h`, `asm/signal.h`, `asm/page.h`. Integration points include scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: Exec, fork, signal delivery, FP emulation, window spill/fill, and kernel stack unwinding are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor_64.h

Purpose: sparc64 task processor-state definition: 32/64-bit task size selection, stack tops, thread debug-lock data, `start_thread`/`start_thread32`, prefetch helpers, and math emulation hooks.

Important APIs/types/functions: types `thread_struct`, `task_struct`; functions/helpers `__get_wchan`, `prefetch`, `prefetchw`, `do_mathemu`; macros/constants `__ASM_SPARC64_PROCESSOR_H`, `VA_BITS`, `VPTE_SIZE`, `TASK_SIZE_OF`, `TASK_SIZE`, `STACK_TOP32`, `STACK_TOP64`, `STACK_TOP`, `STACK_TOP_MAX`, `INIT_THREAD`, `TSTATE_INITIAL_MM`, `start_thread`, `start_thread32`, `task_pt_regs`, `KSTK_EIP`, `KSTK_ESP`, `ARCH_HAS_PREFETCH`, `ARCH_HAS_PREFETCHW`, plus 1 more.

Control flow: The file is driven by preprocessor gates such as `__ASM_SPARC64_PROCESSOR_H`, `__ASSEMBLER__`, `__KERNEL__`, `CONFIG_DEBUG_SPINLOCK`, `CONFIG_SMP`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, locking, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is stored in `pt_regs`, thread-info window/FPU fields, utrap reference counts, FPRS/XFSR bits, and task flags such as `TIF_32BIT`.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`, `asm/pstate.h`, `asm/ptrace.h`, `asm/page.h`, `linux/types.h`, `asm/fpumacro.h`. Integration points include memory-management, SMP, locking, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: 64-bit and compat exec, utrap cleanup, FPU reset, user stack setup, mmap layout, and prefetch-enabled builds should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/processor_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/prom.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/prom.h

Purpose: OpenPROM/OpenFirmware device-tree integration header for SPARC, declaring property mutation, integer property lookup, PROM tree build, CPU mask population, IO unmap, and IRQ translation setup.

Important APIs/types/functions: types `of_irq_controller`, `device_node`, `resource`; functions/helpers `of_set_property`, `of_getintprop_default`, `of_find_in_proplist`, `prom_build_devicetree`, `of_populate_present_mask`, `of_fill_in_cpu_data`, `of_iounmap`, `irq_trans_init`; macros/constants `_SPARC_PROM_H`, `of_compat_cmp`, `of_prop_cmp`, `of_node_cmp`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_PROM_H`, `__KERNEL__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into locking paths rather than through standalone functions.

State and persistence behavior: Persistent state lives in OF device nodes/properties, present CPU masks, IRQ domains/controllers, and PROM-created resource mappings.

Dependencies and integration points: Includes/dependencies: `linux/of.h`, `linux/types.h`, `linux/of_pdt.h`, `linux/proc_fs.h`, `linux/mutex.h`, `linux/atomic.h`, `linux/irqdomain.h`, `linux/spinlock.h`. Integration points include locking; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Boot device-tree population, property update locking, CPU enumeration, PROM IO mapping teardown, and IRQ domain translation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/psr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/psr.h

Purpose: Kernel wrapper around SPARC PSR definitions with inline helpers to read/write `%psr` and read the floating-point status register.

Important APIs/types/functions: functions/helpers `get_psr`, `put_psr`, `get_fsr`; macros/constants `__LINUX_SPARC_PSR_H`.

Control flow: The file is driven by preprocessor gates such as `__LINUX_SPARC_PSR_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is architectural: PSR condition/supervisor/PIL/window bits and FSR contents; `put_psr` writes directly to CPU control state.

Dependencies and integration points: Includes/dependencies: `uapi/asm/psr.h`. Integration points include scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, ABI compatibility breaks. Test signals: Trap entry/return, interrupt enable/disable, context switching, and FPU exception handling are test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/psr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ptrace.h

Purpose: Architecture ptrace/register helper header for both sparc64 and sparc32, exposing syscall markers, user-mode tests, instruction/stack pointers, register snapshots, profiling PC lookup, and register offset accessors.

Important APIs/types/functions: types `global_reg_snapshot`, `global_pmu_snapshot`; functions/helpers `pt_regs_trap_type`, `pt_regs_is_syscall`, `pt_regs_clear_syscall`, `is_syscall_success`, `regs_return_value`, `profile_pc`, `regs_query_register_offset`, `regs_get_kernel_stack_nth`, `regs_get_register`, `kernel_stack_pointer`; macros/constants `__SPARC_PTRACE_H`, `arch_ptrace_stop_needed`, `arch_ptrace_stop`, `current_pt_regs`, `force_successful_syscall_return`, `user_mode`, `instruction_pointer`, `instruction_pointer_set`, `user_stack_pointer`, `profile_pc`, `MAX_REG_OFFSET`, `STACK_BIAS`, `GR_SNAP_TSTATE`, `GR_SNAP_TPC`, `GR_SNAP_TNPC`, `GR_SNAP_O7`, `GR_SNAP_I7`, `GR_SNAP_RPC`, plus 2 more.

Control flow: The file is driven by preprocessor gates such as `__SPARC_PTRACE_H`, `defined(__sparc__) && defined(__arch64__)`, `__ASSEMBLER__`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP, syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State is `pt_regs`, `thread_info` window-save counters, sparc64 global CPU snapshots, and syscall carry/noerror bits.

Dependencies and integration points: Includes/dependencies: `uapi/asm/ptrace.h`, `linux/compiler.h`, `linux/threads.h`, `asm/switch_to.h`. Integration points include SMP, syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps, ABI compatibility breaks. Test signals: PTRACE register access, syscall tracing/rollback, stack unwinding, SMP profiling, and user-window synchronization on ptrace stop should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/qrwlock.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/qrwlock.h

Purpose: Adapter header that enables generic queued rwlock types and operations for SPARC.

Important APIs/types/functions: macros/constants `_ASM_SPARC_QRWLOCK_H`.

Control flow: The file is driven by preprocessor gates such as `_ASM_SPARC_QRWLOCK_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: Runtime state is the generic lock word defined by `asm-generic`; this header only chooses the implementation.

Dependencies and integration points: Includes/dependencies: `asm-generic/qrwlock_types.h`, `asm-generic/qrwlock.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: SMP locking stress, lockdep, and allnoconfig/defconfig build coverage are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/qrwlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/qspinlock.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/qspinlock.h

Purpose: Adapter header that enables generic queued spinlock types and operations for SPARC.

Important APIs/types/functions: macros/constants `_ASM_SPARC_QSPINLOCK_H`.

Control flow: The file is driven by preprocessor gates such as `_ASM_SPARC_QSPINLOCK_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into locking paths rather than through standalone functions.

State and persistence behavior: Runtime state is the generic lock word defined by `asm-generic`; this header only chooses the implementation.

Dependencies and integration points: Includes/dependencies: `asm-generic/qspinlock_types.h`, `asm-generic/qspinlock.h`. Integration points include locking; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: SMP locking stress, lockdep, and allnoconfig/defconfig build coverage are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/qspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ross.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ross.h

Purpose: Ross/hyperSPARC CPU control and cache helper header defining ICR bits and inline ASI sequences for I-cache/D-cache/tag/cache-page operations.

Important APIs/types/functions: functions/helpers `get_ross_icr`, `put_ross_icr`, `hyper_flush_whole_icache`, `hyper_clear_all_tags`, `hyper_flush_unconditional_combined`, `hyper_flush_cache_user`, `hyper_flush_cache_page`; macros/constants `_SPARC_ROSS_H`, `HYPERSPARC_CWENABLE`, `HYPERSPARC_SBENABLE`, `HYPERSPARC_WBENABLE`, `HYPERSPARC_MIDMASK`, `HYPERSPARC_BMODE`, `HYPERSPARC_ACENABLE`, `HYPERSPARC_CSIZE`, `HYPERSPARC_MRFLCT`, `HYPERSPARC_CMODE`, `HYPERSPARC_CENABLE`, `HYPERSPARC_NFAULT`, `HYPERSPARC_MENABLE`, `HYPERSPARC_ICCR_FTD`, `HYPERSPARC_ICCR_ICE`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_ROSS_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is CPU cache-control/tag registers and cache contents; helpers invalidate or flush physical cache structures through alternate spaces.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`, `asm/page.h`. Integration points include memory-management, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: hyperSPARC boot, cache flush correctness, copy-on-write aliasing, and cache-control register programming are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ross.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sbi.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sbi.h

Purpose: Sun4d SBI bus interface header defining SBI register layout, device-id mapping, interrupt target bits, and helpers to acquire/release/configure SBI controller registers.

Important APIs/types/functions: types `sbi_regs`; functions/helpers `acquire_sbi`, `release_sbi`, `set_sbi_tid`, `get_sbi_ctl`, `set_sbi_ctl`; macros/constants `_SPARC_SBI_H`, `SBI_CID`, `SBI_CTL`, `SBI_STATUS`, `SBI_CFG0`, `SBI_CFG1`, `SBI_CFG2`, `SBI_CFG3`, `SBI_STB0`, `SBI_STB1`, `SBI_STB2`, `SBI_STB3`, `SBI_INTR_STATE`, `SBI_INTR_TID`, `SBI_INTR_DIAG`, `SBI_CFG_BURST_MASK`, `SBI2DEVID`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_SBI_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State is memory-mapped SBI registers and interrupt target/control fields, usually accessed through OBIO mappings.

Dependencies and integration points: Includes/dependencies: `asm/obio.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: sun4d interrupt routing, bus acquisition/release, CPU target programming, and register endian/offset checks are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/scratchpad.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/scratchpad.h

Purpose: Constant/ABI header for `scratchpad.h` supplying numeric definitions consumed by low-level SPARC code.

Important APIs/types/functions: macros/constants `_SPARC64_SCRATCHPAD_H`, `SCRATCHPAD_MMU_MISS`, `SCRATCHPAD_CPUID`, `SCRATCHPAD_UTSBREG1`, `SCRATCHPAD_UTSBREG2`, `SCRATCHPAD_UNUSED1`, `SCRATCHPAD_UNUSED2`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SCRATCHPAD_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State is external hardware or ABI state represented by constants; the header itself has no mutable storage.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: Compile-time users plus boot/runtime paths that decode these constants are the main tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/scratchpad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/seccomp.h

Purpose: SPARC architecture header `seccomp.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: macros/constants `_ASM_SECCOMP_H`, `__NR_seccomp_sigreturn_32`.

Control flow: The file is driven by preprocessor gates such as `_ASM_SECCOMP_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `linux/unistd.h`, `asm-generic/seccomp.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sections.h

Purpose: SPARC architecture header `sections.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: macros/constants `__SPARC_SECTIONS_H`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SECTIONS_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm-generic/sections.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/setup.h

Purpose: SPARC setup hook declarations shared by boot, console, floppy IRQ, device scan, unaligned/FPU load-store emulation, hypervisor console IRQ migration, and break handling.

Important APIs/types/functions: functions/helpers `con_is_present`, `sparc_floppy_request_irq`, `device_scan`, `safe_compute_effective_address`, `start_early_boot`, `handle_ldf_stq`, `handle_ld_nf`, `sunhv_migrate_hvcons_irq`, `sun_do_break`; macros/constants `_SPARC_SETUP_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_SETUP_H`, `CONFIG_SPARC32`, `CONFIG_SPARC64`, `CONFIG_SERIAL_SUNHV`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: This header owns no state but wires early boot and trap handlers into global setup state, IRQ descriptors, and CPU/hypervisor state.

Dependencies and integration points: Includes/dependencies: `linux/interrupt.h`, `uapi/asm/setup.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps, ABI compatibility breaks. Test signals: Boot on supported machines, console detection, floppy IRQ registration, unaligned instruction emulation, and break/NMI paths are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfafsr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfafsr.h

Purpose: Constant/ABI header for `sfafsr.h` supplying numeric definitions consumed by low-level SPARC code.

Important APIs/types/functions: macros/constants `_SPARC64_SFAFSR_H`, `SFAFSR_ME`, `SFAFSR_ME_SHIFT`, `SFAFSR_PRIV`, `SFAFSR_PRIV_SHIFT`, `SFAFSR_ISAP`, `SFAFSR_ISAP_SHIFT`, `SFAFSR_ETP`, `SFAFSR_ETP_SHIFT`, `SFAFSR_IVUE`, `SFAFSR_IVUE_SHIFT`, `SFAFSR_TO`, `SFAFSR_TO_SHIFT`, `SFAFSR_BERR`, `SFAFSR_BERR_SHIFT`, `SFAFSR_LDP`, `SFAFSR_LDP_SHIFT`, `SFAFSR_CP`, plus 33 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SFAFSR_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State is external hardware or ABI state represented by constants; the header itself has no mutable storage.

Dependencies and integration points: Includes/dependencies: `linux/const.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Compile-time users plus boot/runtime paths that decode these constants are the main tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfafsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine.h

Purpose: selects the soft-float machine description for SPARC32 or SPARC64.

Important APIs/types/functions: macros/constants `___ASM_SPARC_SFP_MACHINE_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_SFP_MACHINE_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/sfp-machine_64.h`, `asm/sfp-machine_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine_32.h

Purpose: SPARC32 soft-float machine description for Linux math emulation, defining word sizes, multiply/divide meat macros, NaN selection, rounding, exception bits, and fraction helpers.

Important APIs/types/functions: macros/constants `_SFP_MACHINE_H`, `_FP_W_TYPE_SIZE`, `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_I_TYPE`, `_FP_MUL_MEAT_S`, `_FP_MUL_MEAT_D`, `_FP_MUL_MEAT_Q`, `_FP_DIV_MEAT_S`, `_FP_DIV_MEAT_D`, `_FP_DIV_MEAT_Q`, `_FP_NANFRAC_S`, `_FP_NANFRAC_D`, `_FP_NANFRAC_Q`, `_FP_NANSIGN_S`, `_FP_NANSIGN_D`, `_FP_NANSIGN_Q`, `_FP_KEEPNANFRACP`, plus 17 more.

Control flow: The file is driven by preprocessor gates such as `_SFP_MACHINE_H`, `CONFIG_SMP`, `FP_ROUNDMODE`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP paths rather than through standalone functions.

State and persistence behavior: State is per-operation macro local state plus caller-provided exception accumulators; no kernel global state is introduced.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management, SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, configuration-specific build gaps. Test signals: Soft-float single/double/quad arithmetic, NaN propagation, rounding modes, and trap exception flag compatibility are test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine_64.h

Purpose: SPARC64 soft-float machine description optimized for 64-bit words, defining arithmetic meat macros, NaN payloads, rounding-mode access, exception bits, and quad helpers.

Important APIs/types/functions: macros/constants `_SFP_MACHINE_H`, `_FP_W_TYPE_SIZE`, `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_I_TYPE`, `_FP_MUL_MEAT_S`, `_FP_MUL_MEAT_D`, `_FP_MUL_MEAT_Q`, `_FP_DIV_MEAT_S`, `_FP_DIV_MEAT_D`, `_FP_DIV_MEAT_Q`, `_FP_NANFRAC_S`, `_FP_NANFRAC_D`, `_FP_NANFRAC_Q`, `_FP_NANSIGN_S`, `_FP_NANSIGN_D`, `_FP_NANSIGN_Q`, `_FP_KEEPNANFRACP`, plus 10 more.

Control flow: The file is driven by preprocessor gates such as `_SFP_MACHINE_H`, `FP_ROUNDMODE`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State is carried through soft-fp macro variables and FSR-derived rounding/exception values supplied by the math-emulation caller.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: 64-bit math emulation, quad precision operations, NaN/sign handling, and exception flag reporting should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sfp-machine_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam.h

Purpose: selects the shared-memory low-boundary alignment constants for the active SPARC ABI.

Important APIs/types/functions: macros/constants `___ASM_SPARC_SHMPARAM_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_SHMPARAM_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/shmparam_64.h`, `asm/shmparam_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam_32.h

Purpose: SPARC32-specific implementation header for `shmparam_32.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `_ASMSPARC_SHMPARAM_H`, `__ARCH_FORCE_SHMLBA`, `SHMLBA`.

Control flow: The file is driven by preprocessor gates such as `_ASMSPARC_SHMPARAM_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions. Test signals: Build and runtime coverage on sparc32 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam_64.h

Purpose: SPARC64-specific implementation header for `shmparam_64.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `_ASMSPARC64_SHMPARAM_H`, `__ARCH_FORCE_SHMLBA`, `SHMLBA`.

Control flow: The file is driven by preprocessor gates such as `_ASMSPARC64_SHMPARAM_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/spitfire.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions. Test signals: Build and runtime coverage on sparc64 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/shmparam_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sigcontext.h

Purpose: Kernel-visible SPARC signal-context layouts for 32-bit and 64-bit signal frames, including saved register windows, FPU state pointers, masks, and stack metadata.

Important APIs/types/functions: types `sigcontext32`, `sigcontext`; macros/constants `__SPARC_SIGCONTEXT_H`, `__SUNOS_MAXWIN`, `__SIGC_MAXWIN`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SIGCONTEXT_H`, `__ASSEMBLER__`, `CONFIG_SPARC64`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: This defines ABI-persistent user-frame state; changing field order or sizes breaks signal restore and compatibility.

Dependencies and integration points: Includes/dependencies: `asm/ptrace.h`, `uapi/asm/sigcontext.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps, ABI compatibility breaks. Test signals: Signal delivery/return, compat signal frames, alternate stacks, saved windows, and FPU state restore are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/signal.h

Purpose: SPARC architecture header `signal.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: macros/constants `__SPARC_SIGNAL_H`, `__ARCH_HAS_KA_RESTORER`, `__ARCH_HAS_SA_RESTORER`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SIGNAL_H`, `__ASSEMBLER__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `linux/personality.h`, `linux/types.h`, `uapi/asm/signal.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are ABI compatibility breaks. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp.h

Purpose: routes SMP callers to the 32-bit sun4m/sun4d IPI interface or the sparc64 CPU-poke/global-snapshot interface.

Important APIs/types/functions: macros/constants `___ASM_SPARC_SMP_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_SMP_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/smp_64.h`, `asm/smp_32.h`. Integration points include SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp_32.h

Purpose: SPARC32 SMP header for sun4m/sun4d CPU startup, cross-call/IPI message IDs, logical/physical CPU mapping, interrupt handlers, and `sparc32_ipi_ops`.

Important APIs/types/functions: types `seq_file`, `sparc32_ipi_ops`; functions/helpers `cpu_panic`, `sun4m_init_smp`, `sun4d_init_smp`, `smp_callin`, `smp_store_cpu_info`, `smp_resched_interrupt`, `smp_call_function_single_interrupt`, `smp_call_function_interrupt`, `smp_bogo`, `smp_info`, `xc0`, `xc1`, `xc2`, `xc3`, `xc4`, `arch_send_call_function_single_ipi`, plus 4 more; macros/constants `_SPARC_SMP_H`, `raw_smp_processor_id`, `MSG_CROSS_CALL`, `MBOX_STOPCPU`, `MBOX_IDLECPU`, `MBOX_IDLECPU2`, `MBOX_STOPCPU2`, `hard_smp_processor_id`, `smp_setup_cpu_possible_map`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_SMP_H`, `__ASSEMBLER__`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State persists in CPU maps, boot-time SMP ops, mailbox message bits, atomic CPU state, and per-CPU call-function state.

Dependencies and integration points: Includes/dependencies: `linux/threads.h`, `asm/head.h`, `linux/cpumask.h`, `asm/ptrace.h`, `asm/asi.h`, `linux/atomic.h`. Integration points include memory-management, SMP, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps. Test signals: Secondary CPU bring-up, IPI broadcast/single delivery, CPU panic/stop, `/proc/cpuinfo`, and hard CPU id mapping are tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp_64.h

Purpose: sparc64 SMP header exposing per-CPU id access, scheduler poke, cross-call IPI senders, sibling/core maps, CPU hotplug, global register/PMU snapshots, and tick synchronization.

Important APIs/types/functions: types `seq_file`; functions/helpers `smp_init_cpu_poke`, `scheduler_poke`, `arch_send_call_function_single_ipi`, `arch_send_call_function_ipi_mask`, `hard_smp_processor_id`, `smp_fill_in_sib_core_maps`, `cpu_play_dead`, `smp_fetch_global_regs`, `smp_fetch_global_pmu`, `smp_bogo`, `smp_info`, `smp_callin`, `cpu_panic`, `smp_synchronize_tick_client`, `smp_capture`, `smp_release`, plus 2 more; macros/constants `_SPARC64_SMP_H`, `raw_smp_processor_id`, `hard_smp_processor_id`, `smp_fill_in_sib_core_maps`, `smp_fetch_global_regs`, `smp_fetch_global_pmu`, `smp_init_cpu_poke`, `scheduler_poke`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SMP_H`, `__ASSEMBLER__`, `CONFIG_SMP`, `CONFIG_HOTPLUG_CPU`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State includes per-CPU `cpu_data`, trap-block CPU ids, global snapshot arrays, CPU sibling masks, and hotplug lifecycle state.

Dependencies and integration points: Includes/dependencies: `linux/threads.h`, `asm/asi.h`, `asm/starfire.h`, `asm/spitfire.h`, `linux/cpumask.h`, `linux/cache.h`, `linux/bitops.h`, `linux/atomic.h`, `asm/percpu.h`. Integration points include SMP, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps. Test signals: CPU hotplug, scheduler IPI latency, perf snapshot IPIs, sibling maps, tick sync, and suspend/death paths should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sparsemem.h

Purpose: Constant/ABI header for `sparsemem.h` supplying numeric definitions consumed by low-level SPARC code.

Important APIs/types/functions: macros/constants `_SPARC64_SPARSEMEM_H`, `SECTION_SIZE_BITS`, `MAX_PHYSMEM_BITS`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SPARSEMEM_H`, `__KERNEL__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State is external hardware or ABI state represented by constants; the header itself has no mutable storage.

Dependencies and integration points: Includes/dependencies: `asm/page.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Compile-time users plus boot/runtime paths that decode these constants are the main tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock.h

Purpose: selects either the 32-bit hand-written lock primitives or the sparc64 queued spin/rw lock implementation.

Important APIs/types/functions: macros/constants `___ASM_SPARC_SPINLOCK_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_SPINLOCK_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into locking paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/spinlock_64.h`, `asm/spinlock_32.h`. Integration points include locking; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_32.h

Purpose: SPARC32 spin/rwlock implementation using `ldstub`, interrupt masking around readers, and out-of-line rwlock slow paths.

Important APIs/types/functions: functions/helpers `arch_spin_lock`, `arch_spin_trylock`, `arch_spin_unlock`, `__arch_read_lock`, `__arch_read_unlock`, `arch_write_lock`, `arch_write_unlock`, `arch_write_trylock`, `__arch_read_trylock`; macros/constants `__SPARC_SPINLOCK_H`, `arch_spin_is_locked`, `arch_read_lock`, `arch_read_unlock`, `arch_read_trylock`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SPINLOCK_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, locking, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is the lock byte/word itself; rwlocks encode a writer byte plus a 24-bit reader counter and temporarily mask IRQs for reader operations.

Dependencies and integration points: Includes/dependencies: `asm/psr.h`, `asm/barrier.h`, `asm/processor.h`. Integration points include memory-management, locking, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Lockdep/debug-spinlock, IRQ-context readers, writer starvation, trylock behavior, and SMP stress tests are required signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_64.h

Purpose: SPARC64-specific implementation header for `spinlock_64.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `__SPARC64_SPINLOCK_H`.

Control flow: The file is driven by preprocessor gates such as `__SPARC64_SPINLOCK_H`, `__ASSEMBLER__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into locking, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/processor.h`, `asm/barrier.h`, `asm/qspinlock.h`, `asm/qrwlock.h`. Integration points include locking, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build and runtime coverage on sparc64 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_types.h

Purpose: SPARC architecture header `spinlock_types.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: macros/constants `__SPARC_SPINLOCK_TYPES_H`, `__ARCH_SPIN_LOCK_UNLOCKED`, `__ARCH_RW_LOCK_UNLOCKED`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SPINLOCK_TYPES_H`, `CONFIG_QUEUED_SPINLOCKS`, `CONFIG_QUEUED_RWLOCKS`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into locking paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm-generic/qspinlock_types.h`, `asm-generic/qrwlock_types.h`. Integration points include locking; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spitfire.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/spitfire.h

Purpose: sparc64 UltraSPARC/Spitfire/Cheetah/SUN4V MMU/cache register header with TLB tag/data accessors, cache flush helpers, chip IDs, LSU control bits, and D-cache alias flags.

Important APIs/types/functions: functions/helpers `cheetah_enable_pcache`, `spitfire_put_dcache_tag`, `spitfire_put_icache_tag`, `spitfire_get_dtlb_data`, `spitfire_get_dtlb_tag`, `spitfire_put_dtlb_data`, `spitfire_get_itlb_data`, `spitfire_get_itlb_tag`, `spitfire_put_itlb_data`, `spitfire_flush_dtlb_nucleus_page`, `spitfire_flush_itlb_nucleus_page`, `cheetah_flush_dtlb_all`, `cheetah_flush_itlb_all`, `cheetah_get_ldtlb_data`, `cheetah_get_litlb_data`, `cheetah_get_ldtlb_tag`, plus 9 more; macros/constants `_SPARC64_SPITFIRE_H`, `TSB_TAG_TARGET`, `TLB_SFSR`, `TSB_REG`, `TLB_TAG_ACCESS`, `VIRT_WATCHPOINT`, `PHYS_WATCHPOINT`, `TSB_EXTENSION_P`, `TSB_EXTENSION_S`, `TSB_EXTENSION_N`, `TLB_TAG_ACCESS_EXT`, `PRIMARY_CONTEXT`, `SECONDARY_CONTEXT`, `DMMU_SFAR`, `SPITFIRE_HIGHEST_LOCKED_TLBENT`, `CHEETAH_HIGHEST_LOCKED_TLBENT`, `L1DCACHE_SIZE`, `SUN4V_CHIP_INVALID`, plus 21 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SPITFIRE_H`, `CONFIG_SPARC64`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: State is architectural MMU/cache registers, TLB entries, CPU implementation ids, and global flags such as `tlb_type`/cache aliasing.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Boot patching across sun4u/sun4v, TLB dump/flush, cache enable/disable, LSU control, and Niagara chip detection are tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/spitfire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/stacktrace.h

Purpose: SPARC architecture header `stacktrace.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `stack_trace_flush`; macros/constants `_SPARC64_STACKTRACE_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_STACKTRACE_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/starfire.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/starfire.h

Purpose: SPARC architecture header `starfire.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `check_if_starfire`, `starfire_hookup`, `starfire_translate`; macros/constants `_SPARC64_STARFIRE_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_STARFIRE_H`, `__ASSEMBLER__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/starfire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/string.h

Purpose: SPARC architecture header `string.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `memcmp`, `strlen`, `strncmp`; macros/constants `___ASM_SPARC_STRING_H`, `__HAVE_ARCH_MEMMOVE`, `__HAVE_ARCH_MEMCPY`, `memcpy`, `__HAVE_ARCH_MEMSET`, `memset`, `__HAVE_ARCH_MEMSCAN`, `memscan`, `__HAVE_ARCH_MEMCMP`, `__HAVE_ARCH_STRLEN`, `__HAVE_ARCH_STRNCMP`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_STRING_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/string_64.h`, `asm/string_32.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/string_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/string_32.h

Purpose: SPARC32-specific implementation header for `string_32.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `__SPARC_STRING_H__`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_STRING_H__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/page.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build and runtime coverage on sparc32 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/string_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/string_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/string_64.h

Purpose: SPARC64-specific implementation header for `string_64.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `__SPARC64_STRING_H__`.

Control flow: The file is driven by preprocessor gates such as `__SPARC64_STRING_H__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build and runtime coverage on sparc64 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/string_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sunbpp.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sunbpp.h

Purpose: SPARC architecture header `sunbpp.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `bpp_regs`; macros/constants `_ASM_SPARC_SUNBPP_H`, `P_HCR_TEST`, `P_HCR_DSW`, `P_HCR_DDS`, `P_OCR_MEM_CLR`, `P_OCR_DATA_SRC`, `P_OCR_DS_DSEL`, `P_OCR_BUSY_DSEL`, `P_OCR_ACK_DSEL`, `P_OCR_EN_DIAG`, `P_OCR_BUSY_OP`, `P_OCR_ACK_OP`, `P_OCR_SRST`, `P_OCR_IDLE`, `P_OCR_V_ILCK`, `P_OCR_EN_VER`, `P_TCR_DIR`, `P_TCR_BUSY`, plus 27 more.

Control flow: The file is driven by preprocessor gates such as `_ASM_SPARC_SUNBPP_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/sunbpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/swift.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/swift.h

Purpose: SPARC architecture header `swift.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `swift_inv_insn_tag`, `swift_inv_data_tag`, `swift_flush_dcache`, `swift_flush_icache`, `swift_idflash_clear`, `swift_flush_page`, `swift_flush_segment`, `swift_flush_region`, `swift_flush_context`; macros/constants `_SPARC_SWIFT_H`, `SWIFT_ST`, `SWIFT_WP`, `SWIFT_BF`, `SWIFT_PMC`, `SWIFT_PE`, `SWIFT_PC`, `SWIFT_AP`, `SWIFT_AC`, `SWIFT_BM`, `SWIFT_RC`, `SWIFT_IE`, `SWIFT_DE`, `SWIFT_SA`, `SWIFT_NF`, `SWIFT_EN`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_SWIFT_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is inline assembly.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/swift.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to.h

Purpose: routes scheduler context-switch code to the 32-bit or 64-bit SPARC assembly contract.

Important APIs/types/functions: macros/constants `___ASM_SPARC_SWITCH_TO_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_SWITCH_TO_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/switch_to_64.h`, `asm/switch_to_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to_32.h

Purpose: SPARC32 context-switch macro contract, saving lazy FPU state when `TIF_USEDFPU` is set and calling low-level `__switch_to`.

Important APIs/types/functions: functions/helpers `fpsave`, `synchronize_user_stack`; macros/constants `__SPARC_SWITCH_TO_H`, `SWITCH_ENTER`, `SWITCH_DO_LAZY_FPU`, `prepare_arch_switch`, `switch_to`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SWITCH_TO_H`, `CONFIG_SMP`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State moves among `thread_struct` fields, `%psr`, register windows, saved FPU registers, and per-task kernel stack pointers.

Dependencies and integration points: Includes/dependencies: `asm/smp.h`. Integration points include memory-management, SMP, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, configuration-specific build gaps. Test signals: Scheduler stress, lazy FPU handoff, user-window synchronization, fork/exec switch paths, and SMP switching are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to_64.h

Purpose: sparc64 context-switch contract that flushes VIS state, calls `__switch_to`, and exposes user-window synchronization/fault-in helpers.

Important APIs/types/functions: types `pt_regs`; functions/helpers `synchronize_user_stack`, `fault_in_user_windows`; macros/constants `__SPARC64_SWITCH_TO_64_H`, `prepare_arch_switch`, `switch_to`.

Control flow: The file is driven by preprocessor gates such as `__SPARC64_SWITCH_TO_64_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State is in `thread_info`, FPRS/VIS/FPU state, register windows, and the returned previous task pointer.

Dependencies and integration points: Includes/dependencies: `asm/visasm.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes. Test signals: VIS/FPU context switching, ptrace/signal window synchronization, and scheduler switch correctness should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/switch_to_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/syscall.h

Purpose: Architecture syscall helper header implementing syscall number get/set, rollback, error/return handling, argument access, and audit architecture selection for sparc32/sparc64/compat.

Important APIs/types/functions: functions/helpers `syscall_get_nr`, `syscall_set_nr`, `syscall_rollback`, `syscall_has_error`, `syscall_set_error`, `syscall_clear_error`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`; macros/constants `__ASM_SPARC_SYSCALL_H`.

Control flow: The file is driven by preprocessor gates such as `__ASM_SPARC_SYSCALL_H`, `CONFIG_SPARC32`, `CONFIG_SPARC64`, `defined(CONFIG_SPARC64) && defined(CONFIG_COMPAT)`, `defined(CONFIG_SPARC64)`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State is entirely in `pt_regs` and thread flags such as sparc64 no-error; control flow toggles carry bits and writes `%i0`/syscall number slots.

Dependencies and integration points: Includes/dependencies: `uapi/linux/audit.h`, `linux/kernel.h`, `linux/compat.h`, `linux/sched.h`, `asm/ptrace.h`, `asm/thread_info.h`. Integration points include syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps, ABI compatibility breaks. Test signals: strace/seccomp/audit, syscall restart/rollback, compat argument layout, error injection, and return value tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/syscalls.h

Purpose: SPARC architecture header `syscalls.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `pt_regs`; functions/helpers `sparc_fork`, `sparc_vfork`, `sparc_clone`, `sparc_clone3`; macros/constants `_SPARC64_SYSCALLS_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SYSCALLS_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/termbits.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/termbits.h

Purpose: Constant/ABI header for `termbits.h` supplying numeric definitions consumed by low-level SPARC code.

Important APIs/types/functions: macros/constants `_SPARC_TERMBITS_H`, `VMIN`, `VTIME`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TERMBITS_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State is external hardware or ABI state represented by constants; the header itself has no mutable storage.

Dependencies and integration points: Includes/dependencies: `uapi/asm/termbits.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are ABI compatibility breaks. Test signals: Compile-time users plus boot/runtime paths that decode these constants are the main tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/termbits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info.h

Purpose: selects the low-level per-thread layout used by trap return, syscall, and scheduler assembly.

Important APIs/types/functions: macros/constants `___ASM_SPARC_THREAD_INFO_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_THREAD_INFO_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/thread_info_64.h`, `asm/thread_info_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info_32.h

Purpose: SPARC32 `thread_info` layout used by trap, scheduler, syscall, and window spill code, including register-window buffers, flags, counters, CPU id, and kernel saved state offsets.

Important APIs/types/functions: types `thread_info`; functions/helpers `asm`; macros/constants `_ASM_THREAD_INFO_H`, `NSWINS`, `INIT_THREAD_INFO`, `current_thread_info`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `TI_UWINMASK`, `TI_TASK`, `TI_FLAGS`, `TI_CPU`, `TI_PREEMPT`, `TI_SOFTIRQ`, `TI_HARDIRQ`, `TI_KSP`, `TI_KPC`, `TI_KPSR`, `TI_KWIM`, `TI_REG_WINDOW`, plus 20 more.

Control flow: The file is driven by preprocessor gates such as `_ASM_THREAD_INFO_H`, `__KERNEL__`, `__ASSEMBLER__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP, syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: This is persistent per-task low-level state at the base of the kernel stack; assembly depends on every `TI_*` offset and flag bit.

Dependencies and integration points: Includes/dependencies: `asm/ptrace.h`, `asm/page.h`. Integration points include SMP, syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, MMU/TLB encoding regressions. Test signals: Context switch, preemption counters, signal/window save, syscall work masks, and assembly-offset validation are test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info_64.h

Purpose: sparc64 `thread_info` layout with packed flag/status bytes, saved windows, FPU/VIS register storage, utraps, fault metadata, and assembly offsets.

Important APIs/types/functions: types `task_struct`, `thread_info`; functions/helpers `asm`; macros/constants `_ASM_THREAD_INFO_H`, `NSWINS`, `TI_FLAG_BYTE_FAULT_CODE`, `TI_FLAG_FAULT_CODE_SHIFT`, `TI_FLAG_BYTE_WSTATE`, `TI_FLAG_WSTATE_SHIFT`, `TI_FLAG_BYTE_NOERROR`, `TI_FLAG_BYTE_NOERROR_SHIFT`, `TI_FLAG_BYTE_FPDEPTH`, `TI_FLAG_FPDEPTH_SHIFT`, `TI_FLAG_BYTE_CWP`, `TI_FLAG_CWP_SHIFT`, `TI_FLAG_BYTE_WSAVED`, `TI_FLAG_WSAVED_SHIFT`, `TI_TASK`, `TI_FLAGS`, `TI_FAULT_CODE`, `TI_WSTATE`, plus 77 more.

Control flow: The file is driven by preprocessor gates such as `_ASM_THREAD_INFO_H`, `__KERNEL__`, `__ASSEMBLER__`, `PAGE_SHIFT == 13`, `BUILD_VDSO`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, syscall/ptrace, VDSO paths rather than through standalone functions.

State and persistence behavior: Per-task state persists in kernel stack/thread storage; high bytes of `flags` encode fault code, wstate, no-error, fpdepth, cwp, and wsaved for trap-return fast paths.

Dependencies and integration points: Includes/dependencies: `asm/page.h`, `asm/ptrace.h`, `asm/types.h`. Integration points include memory-management, TLB/MMU, syscall/ptrace, VDSO; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, MMU/TLB encoding regressions. Test signals: Trap return work masks, 32-bit compat flagging, FPU/VIS save/restore, MCD faults, utraps, and offset-generation checks are critical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer.h

Purpose: selects the 32-bit SBUS timer interface or the 64-bit tick/stick operations.

Important APIs/types/functions: macros/constants `___ASM_SPARC_TIMER_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_TIMER_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into timekeeping paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/timer_64.h`, `asm/timer_32.h`. Integration points include timekeeping; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer_32.h

Purpose: SPARC32 timer header for SBUS clock constants, timer counter extraction, timer interrupt declaration, and per-CPU clockevent registration.

Important APIs/types/functions: functions/helpers `timer_value`, `timer_interrupt`, `register_percpu_ce`; macros/constants `_SPARC_TIMER_H`, `SBUS_CLOCK_RATE`, `TIMER_VALUE_SHIFT`, `TIMER_VALUE_MASK`, `TIMER_LIMIT_BIT`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TIMER_H`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, timekeeping paths rather than through standalone functions.

State and persistence behavior: State is in hardware timer registers supplied to `timer_value()` and per-CPU clockevent devices registered by platform code.

Dependencies and integration points: Includes/dependencies: `linux/clocksource.h`, `linux/irqreturn.h`, `asm-generic/percpu.h`, `asm/cpu_type.h`. Integration points include memory-management, SMP, timekeeping; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Clocksource monotonicity, timer IRQ handling, sun4m/sun4d timer rate, and SMP per-CPU clockevents are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer_64.h

Purpose: sparc64 tick/stick timer header with tick compare bits, HyperSparc stick addresses, tick operation vector, patch descriptors, and inline `get_tick()`.

Important APIs/types/functions: types `sparc64_tick_ops`, `get_tick_patch`; functions/helpers `sparc64_get_clock_tick`, `setup_sparc64_timer`, `get_tick`; macros/constants `_SPARC64_TIMER_H`, `TICK_PRIV_BIT`, `TICKCMP_IRQ_BIT`, `HBIRD_STICKCMP_ADDR`, `HBIRD_STICK_ADDR`, `GET_TICK_NINSTR`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TIMER_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, timekeeping paths rather than through standalone functions.

State and persistence behavior: State is architectural `%tick`/`%stick`/compare registers and the selected `sparc64_tick_ops` implementation patched during timer setup.

Dependencies and integration points: Includes/dependencies: `uapi/asm/asi.h`, `linux/types.h`, `linux/init.h`. Integration points include memory-management, timekeeping; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, ABI compatibility breaks. Test signals: Clocksource reads, timer interrupt compare programming, sun4v/hummingbird variants, and instruction patching are tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex.h

Purpose: routes timekeeping callers to SPARC32 generic-timex constants or SPARC64 tick-cycle helpers.

Important APIs/types/functions: macros/constants `___ASM_SPARC_TIMEX_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_TIMEX_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/timex_64.h`, `asm/timex_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex_32.h

Purpose: SPARC32-specific implementation header for `timex_32.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `_ASMsparc_TIMEX_H`, `CLOCK_TICK_RATE`.

Control flow: The file is driven by preprocessor gates such as `_ASMsparc_TIMEX_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm-generic/timex.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build and runtime coverage on sparc32 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex_64.h

Purpose: SPARC64-specific implementation header for `timex_64.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `_ASMsparc64_TIMEX_H`, `CLOCK_TICK_RATE`, `get_cycles`, `ARCH_HAS_READ_CURRENT_TIMER`.

Control flow: The file is driven by preprocessor gates such as `_ASMsparc64_TIMEX_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into timekeeping paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/timer.h`. Integration points include timekeeping; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build and runtime coverage on sparc64 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/timex_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb.h

Purpose: selects generic 32-bit TLB gather behavior or the sparc64 batching hooks.

Important APIs/types/functions: macros/constants `___ASM_SPARC_TLB_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_TLB_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into TLB/MMU paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/tlb_64.h`, `asm/tlb_32.h`. Integration points include TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb_32.h

Purpose: SPARC32-specific implementation header for `tlb_32.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `_SPARC_TLB_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TLB_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into TLB/MMU paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm-generic/tlb.h`. Integration points include TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions. Test signals: Build and runtime coverage on sparc32 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb_64.h

Purpose: sparc64 TLB-gather integration that triggers pending TLB flush batches for `mmu_gather`, choosing SMP-aware or local flush paths.

Important APIs/types/functions: functions/helpers `smp_flush_tlb_pending`, `smp_flush_tlb_mm`, `__flush_tlb_pending`, `flush_tlb_pending`; macros/constants `_SPARC64_TLB_H`, `do_flush_tlb_mm`, `tlb_flush`, `tlb_needs_table_invalidate`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TLB_H`, `CONFIG_SMP`, `CONFIG_MMU_GATHER_RCU_TABLE_FREE`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, SMP paths rather than through standalone functions.

State and persistence behavior: State is pending per-mm TLB batch data and mm context; `tlb_flush` bridges generic MM teardown to sparc64 flush code.

Dependencies and integration points: Includes/dependencies: `linux/swap.h`, `linux/pagemap.h`, `asm/tlbflush.h`, `asm/mmu_context.h`, `asm-generic/tlb.h`. Integration points include memory-management, TLB/MMU, SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: munmap/exit under SMP, batched flush ordering, table invalidation, and lazy MMU mode interactions are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush.h

Purpose: selects the architecture TLB shootdown declarations for 32-bit SRMMU or 64-bit TSB/TLB code.

Important APIs/types/functions: macros/constants `___ASM_SPARC_TLBFLUSH_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_TLBFLUSH_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into TLB/MMU paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/tlbflush_64.h`, `asm/tlbflush_32.h`. Integration points include TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush_32.h

Purpose: SPARC32-specific implementation header for `tlbflush_32.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: functions/helpers `flush_tlb_kernel_range`; macros/constants `_SPARC_TLBFLUSH_H`, `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_range`, `flush_tlb_page`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TLBFLUSH_H`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/cachetlb_32.h`. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions. Test signals: Build and runtime coverage on sparc32 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush_64.h

Purpose: sparc64 TLB/TSB flush declarations and lazy batch structure, including per-CPU `tlb_batch`, kernel/user TSB flushes, page/range/mm flushes, and SMP shootdowns.

Important APIs/types/functions: types `tlb_batch`; functions/helpers `flush_tsb_kernel_range`, `flush_tsb_user`, `flush_tsb_user_page`, `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_range`, `flush_tlb_kernel_range`, `flush_tlb_pending`, `arch_enter_lazy_mmu_mode`, `arch_flush_lazy_mmu_mode`, `arch_leave_lazy_mmu_mode`, `__flush_tlb_all`, `__flush_tlb_page`, `__flush_tlb_kernel_range`, `global_flush_tlb_page`, `smp_flush_tlb_kernel_range`, plus 1 more; macros/constants `_SPARC64_TLBFLUSH_H`, `TLB_BATCH_NR`, `global_flush_tlb_page`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TLBFLUSH_H`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, SMP paths rather than through standalone functions.

State and persistence behavior: State persists in per-CPU `tlb_batch`, mm context IDs, TSB entries, and lazy MMU mode batching until `flush_tlb_pending`.

Dependencies and integration points: Includes/dependencies: `asm/mmu_context.h`. Integration points include memory-management, TLB/MMU, SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: TLB shootdown races, huge-page flushes, context recycle, kernel vmalloc flushes, and SMP page invalidation are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology.h

Purpose: routes topology users to the generic 32-bit topology defaults or sparc64 node/core maps.

Important APIs/types/functions: macros/constants `___ASM_SPARC_TOPOLOGY_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_TOPOLOGY_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/topology_64.h`, `asm/topology_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology_32.h

Purpose: SPARC32-specific implementation header for `topology_32.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: macros/constants `_ASM_SPARC_TOPOLOGY_H`.

Control flow: The file is driven by preprocessor gates such as `_ASM_SPARC_TOPOLOGY_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm-generic/topology.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build and runtime coverage on sparc32 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology_64.h

Purpose: SPARC64-specific implementation header for `topology_64.h` providing the architecture half of a common SPARC wrapper.

Important APIs/types/functions: types `pci_bus`; functions/helpers `cpu_to_node`, `pcibus_to_node`, `__node_distance`; macros/constants `_ASM_SPARC64_TOPOLOGY_H`, `cpumask_of_node`, `cpumask_of_pcibus`, `node_distance`, `topology_physical_package_id`, `topology_core_id`, `topology_core_cpumask`, `topology_core_cache_cpumask`, `topology_sibling_cpumask`.

Control flow: The file is driven by preprocessor gates such as `_ASM_SPARC64_TOPOLOGY_H`, `CONFIG_NUMA`, `CONFIG_PCI`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, PCI paths rather than through standalone functions.

State and persistence behavior: State effects are mostly architectural or per-task/per-CPU data exposed through macros and inline helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/mmzone.h`, `asm-generic/topology.h`, `asm/cpudata.h`. Integration points include memory-management, SMP, PCI; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Build and runtime coverage on sparc64 configurations, especially callers listed in dependencies, are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/topology_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/trap_block.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/trap_block.h

Purpose: sparc64 trap-block layout and assembly offsets for per-CPU trap-time data: current thread, PGD physical address, mondo queues, fault info, TSB huge-page data, IRQ worklist, and per-CPU base.

Important APIs/types/functions: types `thread_info`, `trap_per_cpu`, `cpuid_patch_entry`, `sun4v_1insn_patch_entry`, `sun4v_2insn_patch_entry`; functions/helpers `init_cur_cpu_trap`, `setup_tba`, `real_hard_smp_processor_id`; macros/constants `_SPARC_TRAP_BLOCK_H`, `TRAP_PER_CPU_THREAD`, `TRAP_PER_CPU_PGD_PADDR`, `TRAP_PER_CPU_CPU_MONDO_PA`, `TRAP_PER_CPU_DEV_MONDO_PA`, `TRAP_PER_CPU_RESUM_MONDO_PA`, `TRAP_PER_CPU_RESUM_KBUF_PA`, `TRAP_PER_CPU_NONRESUM_MONDO_PA`, `TRAP_PER_CPU_NONRESUM_KBUF_PA`, `TRAP_PER_CPU_FAULT_INFO`, `TRAP_PER_CPU_CPU_MONDO_BLOCK_PA`, `TRAP_PER_CPU_CPU_LIST_PA`, `TRAP_PER_CPU_TSB_HUGE`, `TRAP_PER_CPU_TSB_HUGE_TEMP`, `TRAP_PER_CPU_IRQ_WORKLIST_PA`, `TRAP_PER_CPU_CPU_MONDO_QMASK`, `TRAP_PER_CPU_DEV_MONDO_QMASK`, `TRAP_PER_CPU_RESUM_QMASK`, plus 9 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TRAP_BLOCK_H`, `__ASSEMBLER__`, `CONFIG_SMP`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into TLB/MMU, SMP, scheduler/task paths rather than through standalone functions.

State and persistence behavior: Persistent per-CPU state lives in `trap_block[NR_CPUS]`; assembly macros load CPU id, trap block base, PGD physical address, and IRQ work addresses directly.

Dependencies and integration points: Includes/dependencies: `linux/threads.h`, `asm/hypervisor.h`, `asm/asi.h`, `asm/scratchpad.h`. Integration points include TLB/MMU, SMP, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: CPU bring-up, hypervisor mondo queues, TLB miss handlers, per-CPU variable access, and offset stability tests are critical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/trap_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/traps.h

Purpose: SPARC architecture header `traps.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `tt_entry`; macros/constants `_SPARC_TRAPS_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TRAPS_H`, `__ASSEMBLER__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `uapi/asm/traps.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are ABI compatibility breaks. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tsb.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tsb.h

Purpose: sparc64 Translation Storage Buffer assembly macro header defining TSB entry format, lock/invalid tag bits, physical-load patch tables, kernel/user page-table walks, huge-page propagation, OBP lookup, and kernel TSB lookup.

Important APIs/types/functions: types `tsb_ldquad_phys_patch_entry`, `tsb_phys_patch_entry`; macros/constants `_SPARC64_TSB_H`, `TSB_TAG_LOCK_BIT`, `TSB_TAG_LOCK_HIGH`, `TSB_TAG_INVALID_BIT`, `TSB_TAG_INVALID_HIGH`, `TSB_LOAD_QUAD`, `TSB_LOAD_TAG_HIGH`, `TSB_LOAD_TAG`, `TSB_CAS_TAG_HIGH`, `TSB_CAS_TAG`, `TSB_STORE`, `TSB_LOCK_TAG`, `TSB_WRITE`, `KERN_PGTABLE_WALK`, `USER_PGTABLE_CHECK_PUD_HUGE`, `USER_PGTABLE_CHECK_PMD_HUGE`, `USER_PGTABLE_WALK_TL1`, `OBP_TRANS_LOOKUP`, plus 5 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TSB_H`, `__ASSEMBLER__`, `defined(CONFIG_HUGETLB_PAGE) || defined(CONFIG_TRANSPARENT_HUGEPAGE)`, `CONFIG_DEBUG_PAGEALLOC`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: State is TSB tag/PTE slots protected by tag lock bits, patch-section records for physical load variants, swapper TSBs, and PROM translation tables.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: TLB miss handler tests, TSB conflict/lock stress, huge-page misses, OBP mappings, sun4u/sun4v physical load patching, and DEBUG_PAGEALLOC variants are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tsb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tsunami.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tsunami.h

Purpose: SPARC architecture header `tsunami.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `tsunami_flush_icache`, `tsunami_flush_dcache`; macros/constants `_SPARC_TSUNAMI_H`, `TSUNAMI_SW`, `TSUNAMI_AV`, `TSUNAMI_DV`, `TSUNAMI_MV`, `TSUNAMI_PC`, `TSUNAMI_ITD`, `TSUNAMI_ALC`, `TSUNAMI_PE`, `TSUNAMI_RCMASK`, `TSUNAMI_IENAB`, `TSUNAMI_DENAB`, `TSUNAMI_NF`, `TSUNAMI_ME`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TSUNAMI_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is inline assembly.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/tsunami.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ttable.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ttable.h

Purpose: sparc64 trap-table macro library for boot vector, trap entry/return wrappers, syscall traps, IRQ/NMI traps, TSB miss vectors, spill/fill handlers, and kprobe/uprobe/kgdb trap selection.

Important APIs/types/functions: macros/constants `_SPARC64_TTABLE_H`, `BOOT_KERNEL`, `CLEAN_WINDOW`, `TRAP`, `TRAP_7INSNS`, `TRAP_SAVEFPU`, `TRAP_NOSAVE`, `TRAP_NOSAVE_7INSNS`, `TRAPTL1`, `TRAP_ARG`, `TRAPTL1_ARG`, `SYSCALL_TRAP`, `TRAP_UTRAP`, `LINUX_32BIT_SYSCALL_TRAP`, `LINUX_64BIT_SYSCALL_TRAP`, `GETCC_TRAP`, `SETCC_TRAP`, `BREAKPOINT_TRAP`, plus 56 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TTABLE_H`, `__ASSEMBLER__`, `CONFIG_COMPAT`, `CONFIG_TRACE_IRQFLAGS`, `CONFIG_KPROBES`, `CONFIG_UPROBES`, `CONFIG_KGDB`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State is architectural trap level/register-window state plus `thread_info` saved-window buffers; macros branch through `etrap`, `rtrap`, fixup labels, and optional tracing subsections.

Dependencies and integration points: Includes/dependencies: `asm/utrap.h`, `asm/pil.h`, `asm/thread_info.h`. Integration points include memory-management, syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Trap-table assembly build, syscall entry, IRQ/NMI levels, window spill/fill faults, compat 32-bit stack handling, and kprobe/uprobe/kgdb traps are required tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ttable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/turbosparc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/turbosparc.h

Purpose: SPARC architecture header `turbosparc.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `turbosparc_inv_insn_tag`, `turbosparc_inv_data_tag`, `turbosparc_flush_icache`, `turbosparc_flush_dcache`, `turbosparc_idflash_clear`, `turbosparc_set_ccreg`, `turbosparc_get_ccreg`; macros/constants `_SPARC_TURBOSPARC_H`, `TURBOSPARC_MMUENABLE`, `TURBOSPARC_NOFAULT`, `TURBOSPARC_ICSNOOP`, `TURBOSPARC_PSO`, `TURBOSPARC_DCENABLE`, `TURBOSPARC_ICENABLE`, `TURBOSPARC_BMODE`, `TURBOSPARC_PARITYODD`, `TURBOSPARC_PCENABLE`, `TURBOSPARC_SCENABLE`, `TURBOSPARC_uS2`, `TURBOSPARC_WTENABLE`, `TURBOSPARC_SNENABLE`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TURBOSPARC_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is inline assembly.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`, `asm/pgtsrmmu.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/turbosparc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess.h

Purpose: combines exception-table setup with the selected 32-bit/64-bit user-memory accessor implementation.

Important APIs/types/functions: functions/helpers `strncpy_from_user`; macros/constants `___ASM_SPARC_UACCESS_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_UACCESS_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into user-copy paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/extable.h`, `asm/uaccess_64.h`, `asm/uaccess_32.h`. Integration points include user-copy; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess_32.h

Purpose: SPARC32 user-memory accessor implementation with `get_user`/`put_user`, inline ASI load/store fixups, raw copy declarations, clear/string helpers, and range checking through generic `access_ok`.

Important APIs/types/functions: types `__large_struct`; functions/helpers `__volatile__`, `__copy_user`, `raw_copy_to_user`, `raw_copy_from_user`, `__clear_user`, `clear_user`, `strnlen_user`; macros/constants `_ASM_UACCESS_H`, `put_user`, `get_user`, `__put_user`, `__get_user`, `__m`, `__put_user_check`, `__put_user_nocheck`, `__put_user_asm`, `__get_user_check`, `__get_user_nocheck`, `__get_user_asm`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`.

Control flow: The file is driven by preprocessor gates such as `_ASM_UACCESS_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into user-copy, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is not persistent except caller memory; exception-table fixups convert data faults to `-EFAULT` and zero failed reads.

Dependencies and integration points: Includes/dependencies: `linux/compiler.h`, `linux/string.h`, `asm/processor.h`, `asm-generic/access_ok.h`. Integration points include user-copy, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Fault injection on bad user pointers, copy_to/from_user, clear_user, string length/from-user helpers, and size-specific accessors are tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess_64.h

Purpose: sparc64 user-memory accessor implementation using secondary ASI loads/stores, exception-table fixups, kernel nofault helpers, range checks, raw copy declarations, and effective-address decoding.

Important APIs/types/functions: types `__large_struct`, `pt_regs`; functions/helpers `__chk_range_not_ok`, `__retl_efault`, `__volatile__`, `raw_copy_from_user`, `raw_copy_to_user`, `raw_copy_in_user`, `__clear_user`, `strnlen_user`, `compute_effective_address`; macros/constants `_ASM_UACCESS_H`, `__range_not_ok`, `put_user`, `get_user`, `__put_user`, `__get_user`, `__m`, `__put_kernel_nofault`, `__put_kernel_asm`, `__put_user_nocheck`, `__put_user_asm`, `__get_kernel_nofault`, `__get_kernel_asm`, `__get_user_nocheck`, `__get_user_asm`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `clear_user`.

Control flow: The file is driven by preprocessor gates such as `_ASM_UACCESS_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, user-copy, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is caller/user memory plus exception-table control flow; user ASIs isolate user VM from kernel VM, and fixup paths return `-EFAULT`.

Dependencies and integration points: Includes/dependencies: `linux/compiler.h`, `linux/string.h`, `linux/mm_types.h`, `asm/asi.h`, `asm/spitfire.h`, `asm/pgtable.h`, `asm/processor.h`, `asm-generic/access_ok.h`. Integration points include memory-management, user-copy, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes. Test signals: Bad pointer fault tests, compat user copy, nofault kernel probes, raw_copy_in_user, clear_user, and unaligned effective-address handling are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/unistd.h

Purpose: SPARC architecture header `unistd.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: macros/constants `_SPARC_UNISTD_H`, `NR_syscalls`, `__NR_time`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_ALARM`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_SIGNAL`, `__ARCH_WANT_SYS_TIME32`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_WAITPID`, `__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_FADVISE64`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLDUMOUNT`, plus 11 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_UNISTD_H`, `__32bit_syscall_numbers__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `uapi/asm/unistd.h`. Integration points include syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are ABI compatibility breaks. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/upa.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/upa.h

Purpose: SPARC architecture header `upa.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `_upa_readb`, `_upa_readw`, `_upa_readl`, `_upa_readq`, `_upa_writeb`, `_upa_writew`, `_upa_writel`, `_upa_writeq`; macros/constants `_SPARC64_UPA_H`, `UPA_CONFIG_RESV`, `UPA_CONFIG_PCON`, `UPA_CONFIG_MID`, `UPA_CONFIG_PCAP`, `UPA_PORTID_FNP`, `UPA_PORTID_RESV`, `UPA_PORTID_ECCVALID`, `UPA_PORTID_ONEREAD`, `UPA_PORTID_PINTRDQ`, `UPA_PORTID_PREQDQ`, `UPA_PORTID_PREQRD`, `UPA_PORTID_UPACAP`, `UPA_PORTID_ID`, `upa_readb`, `upa_readw`, `upa_readl`, `upa_readq`, plus 4 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_UPA_H`, `defined(__KERNEL__) && !defined(__ASSEMBLER__)`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is inline assembly.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, configuration-specific build gaps. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/upa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/uprobes.h

Purpose: SPARC architecture header `uprobes.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `arch_uprobe`, `arch_uprobe_task`, `task_struct`, `notifier_block`; functions/helpers `arch_uprobe_analyze_insn`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `arch_uprobe_xol_was_trapped`, `arch_uprobe_exception_notify`, `arch_uprobe_abort_xol`; macros/constants `_ASM_UPROBES_H`, `MAX_UINSN_BYTES`, `UPROBE_XOL_SLOT_BYTES`, `UPROBE_SWBP_INSN_SIZE`, `UPROBE_SWBP_INSN`, `UPROBE_STP_INSN`, `ANNUL_BIT`.

Control flow: The file is driven by preprocessor gates such as `_ASM_UPROBES_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/user.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/user.h

Purpose: Constant/ABI header for `user.h` supplying numeric definitions consumed by low-level SPARC code.

Important APIs/types/functions: macros/constants `_SPARC_USER_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_USER_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State is external hardware or ABI state represented by constants; the header itself has no mutable storage.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Compile-time users plus boot/runtime paths that decode these constants are the main tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vaddrs.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vaddrs.h

Purpose: SPARC32 virtual-address layout header for SRMMU nocache area, fixed mappings, IO space, debugger/PROM ranges, and DVMA windows.

Important APIs/types/functions: macros/constants `_SPARC_VADDRS_H`, `SRMMU_MAXMEM`, `SRMMU_NOCACHE_VADDR`, `SRMMU_MIN_NOCACHE_PAGES`, `SRMMU_MAX_NOCACHE_PAGES`, `SRMMU_NOCACHE_ALCRATIO`, `FIXADDR_TOP`, `FIXADDR_SIZE`, `FIXADDR_START`, `__fix_to_virt`, `SUN4M_IOBASE_VADDR`, `IOBASE_VADDR`, `IOBASE_END`, `KADB_DEBUGGER_BEGVM`, `KADB_DEBUGGER_ENDVM`, `DEBUG_FIRSTVADDR`, `DEBUG_LASTVADDR`, `LINUX_OPPROM_BEGVM`, plus 3 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_VADDRS_H`, `__ASSEMBLER__`, `CONFIG_HIGHMEM`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State is compile-time virtual address partitioning consumed by MMU setup, IO mapping, and DVMA code; no runtime variables are declared here.

Dependencies and integration points: Includes/dependencies: `asm/head.h`, `asm/kmap_size.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Boot memory layout, nocache allocator bounds, IO/DVMA mapping, PROM/debugger overlap checks, and fixed-address translation tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vaddrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso.h

Purpose: SPARC architecture header `vdso.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `vdso_image`; macros/constants `_ASM_SPARC_VDSO_H`.

Control flow: The file is driven by preprocessor gates such as `_ASM_SPARC_VDSO_H`, `CONFIG_SPARC64`, `CONFIG_COMPAT`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into VDSO paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include VDSO; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/clocksource.h

Purpose: SPARC VDSO clocksource selector that advertises the architecture clock modes available to generic VDSO time code through `VDSO_ARCH_CLOCKMODES`, currently `VDSO_CLOCKMODE_NONE` and `VDSO_CLOCKMODE_ARCHTIMER`.

Important APIs/types/functions: macros/constants `__ASM_VDSO_CLOCKSOURCE_H`, `VDSO_ARCH_CLOCKMODES`.

Control flow: The file is declarative and is reached from generic VDSO clocksource/datapage code. There is no runtime branch in this header; the clock-mode list controls which VDSO counter paths can be selected by kernel VDSO data setup.

State and persistence behavior: It owns no mutable storage. Persistent state is the VDSO datapage clock-mode value written elsewhere; this header only constrains the valid architecture-specific values that user VDSO code may decode.

Dependencies and integration points: Includes/dependencies: none beyond VDSO clock-mode enum visibility from includers. Integration points include `vdso/datapage.h`, `vdso/gettimeofday.h`, and kernel VDSO clocksource setup.

Risks and test signals: Main risks are advertising a mode unsupported by `gettimeofday.h`, omitting a newly supported SPARC counter mode, or breaking generic VDSO builds through enum mismatch. Test signals include SPARC VDSO build coverage, clock_gettime fallback versus VDSO mode selection, and boot tests where the datapage selects `ARCHTIMER` or disables VDSO counter reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/gettimeofday.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/gettimeofday.h

Purpose: SPARC VDSO time accessor implementation: reads tick/stick counters, exposes `__arch_get_hw_counter()`, shifts cycles to nanoseconds, and provides inline syscall fallbacks for `clock_gettime`, `clock_gettime32`, and `gettimeofday`.

Important APIs/types/functions: functions/helpers `vread_tick`, `vread_tick_stick`, `vdso_shift_ns`, `__arch_get_hw_counter`, `clock_gettime_fallback`, `clock_gettime32_fallback`, `gettimeofday_fallback`; macros/constants `_ASM_SPARC_VDSO_GETTIMEOFDAY_H`, `SYSCALL_STRING`, `SYSCALL_CLOBBERS`, `__arch_get_vdso_u_time_data`.

Control flow: VDSO callers enter `__arch_get_hw_counter()`, which dispatches on `vd->clock_mode` and reads either `%tick` or `%asr24` stick on sparc64, returning `U64_MAX` for unsupported modes. Fallback helpers issue SPARC trap instructions (`ta 0x10` on 64-bit, `ta 0x6d` on 32-bit) with syscall numbers and ABI-specific register constraints.

State and persistence behavior: Runtime state is external: the VDSO datapage supplies clock mode, mask, multiplier, shift, and cycle base, while hardware tick/stick registers supply counters. The header mutates no kernel state, but its inline assembly defines user-visible syscall ABI behavior when VDSO fast paths cannot answer.

Dependencies and integration points: Includes/dependencies: `uapi/linux/time.h`, `uapi/linux/unistd.h`, `vdso/align.h`, `vdso/clocksource.h`, `vdso/datapage.h`, `vdso/page.h`, and `linux/types.h`. Integration points include generic VDSO time code, SPARC timer setup, syscall tables, and 32-bit compat time ABI.

Risks and test signals: Main risks are wrong trap number/register clobbers, incorrect tick/stick mode selection, stale 32-bit time fallback ABI, and counter wrap/shift errors. Test signals include VDSO `clock_gettime`/`gettimeofday` correctness against syscalls, sparc32 and sparc64 builds, unsupported clock-mode fallback, monotonicity under counter wrap, and compat `clock_gettime32` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/processor.h

Purpose: SPARC VDSO processor helper header defining `cpu_relax()` in a form usable from user-mapped VDSO code and kernel-side builds.

Important APIs/types/functions: macros/constants `_ASM_SPARC_VDSO_PROCESSOR_H`, `cpu_relax`.

Control flow: The header selects one of three compile-time definitions: sparc64 emits a memory-barrier annotated `rd %ccr, %g0`, VDSO builds on non-64-bit emit an empty compiler barrier, and kernel non-VDSO builds can use `barrier()`. There is no runtime state machine.

State and persistence behavior: It owns no persistent state. Its only effect is a scheduling/spin-wait hint and compiler ordering point for loops that may run in VDSO or kernel context.

Dependencies and integration points: Includes/dependencies: `linux/compiler.h`. Integration points include generic VDSO processor hooks and any VDSO spin/read retry loop that needs an architecture `cpu_relax()` without pulling in full kernel processor state.

Risks and test signals: Main risks are using privileged instructions in VDSO, missing compiler barriers in retry loops, or accidentally depending on kernel-only headers. Test signals include VDSO compilation for 32-bit and 64-bit SPARC, disassembly checks for sparc64 relax instruction, and VDSO time retry-loop stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/vsyscall.h

Purpose: SPARC VDSO vsyscall glue that includes generic VDSO vsyscall support and declares the architecture VDSO mapping size with `__VDSO_PAGES`.

Important APIs/types/functions: macros/constants `_ASM_SPARC_VDSO_VSYSCALL_H`, `__VDSO_PAGES`.

Control flow: The file is declarative; generic VDSO build/runtime code consumes `__VDSO_PAGES` while syscall fallback logic lives in `vdso/gettimeofday.h` and the generic include.

State and persistence behavior: It owns no mutable state. The page-count constant becomes part of the persistent VDSO image/mapping contract used when the kernel maps VDSO pages into user processes.

Dependencies and integration points: Includes/dependencies: `asm-generic/vdso/vsyscall.h`. Integration points include VDSO image layout, process `mmap`/exec setup, and generic VDSO symbol handling.

Risks and test signals: Main risks are an incorrect VDSO page count causing truncated or overlarge mappings, mismatch with `vdso_image`, and build drift from generic VDSO APIs. Test signals include VDSO image size checks, exec-time VDSO mapping tests, symbol resolution from user space, and sparc32/sparc64 VDSO builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/video.h

Purpose: SPARC architecture header `video.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `device`; functions/helpers `pgprot_framebuffer`, `video_is_primary_device`, `fb_memcpy_fromio`, `fb_memcpy_toio`, `fb_memset_io`; macros/constants `_SPARC_VIDEO_H_`, `pgprot_framebuffer`, `video_is_primary_device`, `fb_memcpy_fromio`, `fb_memcpy_toio`, `fb_memset`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_VIDEO_H_`, `CONFIG_SPARC32`, `CONFIG_VIDEO`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `linux/io.h`, `linux/types.h`, `asm/page.h`, `asm-generic/video.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/viking.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/viking.h

Purpose: Viking/MXCC CPU header defining control bits, cache/tag constants, and inline ASI helpers for I/D cache flush, branch prediction, MXCC parity, and hardware probe support.

Important APIs/types/functions: functions/helpers `viking_flush_icache`, `viking_flush_dcache`, `viking_unlock_icache`, `viking_unlock_dcache`, `viking_set_bpreg`, `viking_get_bpreg`, `viking_get_dcache_ptag`, `viking_mxcc_turn_off_parity`, `viking_hwprobe`; macros/constants `_SPARC_VIKING_H`, `VIKING_MMUENABLE`, `VIKING_NOFAULT`, `VIKING_PSO`, `VIKING_DCENABLE`, `VIKING_ICENABLE`, `VIKING_SBENABLE`, `VIKING_MMODE`, `VIKING_PCENABLE`, `VIKING_BMODE`, `VIKING_SPENABLE`, `VIKING_ACENABLE`, `VIKING_TCENABLE`, `VIKING_DPENABLE`, `VIKING_ACTION_MIX`, `VIKING_PTAG_VALID`, `VIKING_PTAG_DIRTY`, `VIKING_PTAG_SHARED`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_VIKING_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is Viking control/cache/tag/MXCC registers and cache contents manipulated through ASI operations.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`, `asm/mxcc.h`, `asm/pgtable.h`, `asm/pgtsrmmu.h`. Integration points include memory-management, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: Viking boot, cache flush correctness, MXCC parity behavior, hardware probe identification, and SRMMU mapping interactions should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/viking.h -->
