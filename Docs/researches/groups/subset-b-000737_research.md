# subset-b-000737 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pci/bridge.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/pci/bridge.h

### Purpose
`bridge.h` is the SGI SN/IP27 Bridge/XBridge PCI-GIO-to-Xtalk ASIC contract. It maps the Bridge register file with `struct bridge_regs`, defines ATE, PIO, DMA, interrupt, response-buffer, reset, device-window, and error bit layouts, and carries the per-controller state shape used by PCI host bridge code.

### Important APIs, Types, And Functions
Key types are `struct bridge_regs`, `struct bridge_err_cmdword`, and `struct bridge_controller`. Important macros include `mkate`, `BRIDGE_INTERNAL_ATES`, the `BRIDGE_*` register offsets, ISR/IMR/IRR error groups, `BRIDGE_DEV_*` device-window attributes, PCI/GIO/Xtalk alias ranges, DMA range tests such as `IS_PCI32_MAPPED`, `BRIDGE_CONTROLLER(bus)`, and raw register helpers `bridge_read`, `bridge_write`, `bridge_set`, and `bridge_clr`.

### Control Flow
This header has no standalone runtime loop. Drivers include it, cast mapped Bridge MMIO to `struct bridge_regs`, then program register fields using raw reads/writes. PCI enumeration uses the Type 0/Type 1 config windows, DMA setup uses ATE/direct-map constants, interrupt setup writes destination and mask registers, and error handlers decode ISR/error command words into fatal, dumpable, or clearable groups.

### State, Persistence, Dependencies, And Integration
State lives in Bridge hardware registers, SSRAM/ATE RAM, PCI configuration space, IRQ domains, and `struct bridge_controller` instances attached to `pci_bus->sysdata`; nothing is filesystem-persistent. Dependencies include `linux/types.h`, `linux/pci.h`, Xtalk widget definitions, SGI SN `nasid_t`, raw I/O accessors, resources, and IRQ domains. The header integrates SGI Xtalk fabric, PCI core, GIO compatibility, DMA mapping, and interrupt routing; Ceph depends on it only indirectly through a working MIPS kernel platform.

### Risks
The register struct and offset macros must remain byte-exact; padding mistakes corrupt MMIO. Raw read-modify-write helpers are not locked and can race with IRQ or concurrent device setup. DMA address range macros assume Bridge address decoding and `PHYS_RAMBASE` semantics. Fatal-error masks are platform-policy sensitive, and misclassified errors can either panic unnecessarily or hide bus corruption.

### Test Signals
Build SGI SN/IP27 PCI configurations, compare `offsetof(struct bridge_regs, field)` with the `BRIDGE_*` constants, boot with PCI devices behind Bridge, exercise config cycles, DMA mapping, interrupts, and induced PCI/Xtalk errors, and run sparse/build warnings for pointer/address-width mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pci/bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/perf_event.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/perf_event.h

### Purpose
`perf_event.h` is intentionally empty except for its include guard. It satisfies the generic `linux/perf_event.h` expectation that every architecture provide an `asm/perf_event.h` include point.

### Important APIs, Types, And Functions
There are no exported functions, types, or feature macros beyond `__MIPS_PERF_EVENT_H__`.

### Control Flow
There is no runtime control flow. Inclusion succeeds and leaves generic perf code to use other MIPS PMU support paths.

### State, Persistence, Dependencies, And Integration
No state or persistence exists here. Integration is purely include-time: generic perf headers can include this file on MIPS without conditional special cases.

### Risks
The risk is accidental addition of stale architecture declarations or removal of the file, either of which can break generic perf include contracts.

### Test Signals
Compile MIPS kernels with `CONFIG_PERF_EVENTS` and representative PMU options; include-order failures are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgalloc.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgalloc.h

### Purpose
`pgalloc.h` supplies MIPS page-table allocation and population hooks for the generic MM subsystem. It creates PMD/PUD/P4D population helpers, declares table initializers, and connects page-table memory to TLB freeing.

### Important APIs, Types, And Functions
Important exports are `pmd_populate_kernel`, `pmd_populate`, `pud_populate`, `pgd_init`, `pgd_alloc`, `pmd_alloc_one`, `pud_alloc_one`, `p4d_populate`, and free macros `__pte_free_tlb`, `__pmd_free_tlb`, and `__pud_free_tlb`. It also advertises `__HAVE_ARCH_PMD_ALLOC_ONE` and `__HAVE_ARCH_PUD_ALLOC_ONE`.

### Control Flow
Generic MM calls allocation helpers when a page-table level is needed. MIPS allocates a `ptdesc`, runs the appropriate constructor, initializes invalid entries with `pmd_init` or `pud_init`, and returns the table pointer. Population helpers install child-table addresses into parent entries through architecture setters.

### State, Persistence, Dependencies, And Integration
State is kernel page-table memory, `struct ptdesc` metadata, and per-`mm_struct` accounting; freed tables are deferred through MMU gather/TLB removal. Dependencies include highmem, generic MM, scheduler accounting, `asm-generic/pgalloc.h`, MIPS table setter macros, and folded-level definitions from `pgtable-32.h` or `pgtable-64.h`.

### Risks
Allocation order and folded-level preprocessor branches must match page-table geometry. Missing constructors or wrong GFP flags can break accounting, and freeing the wrong virtual-to-ptdesc address can corrupt page-table lifetime under concurrent TLB teardown.

### Test Signals
Cross-build 32-bit, 64-bit, folded, and huge-page configurations; boot with fork/exec/mmap stress, highmem, memory pressure, and TLB shootdown tests; run page-table debug options when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-32.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-32.h

### Purpose
`pgtable-32.h` defines 32-bit MIPS page-table geometry, folded generic levels, virtual ranges, invalid table handling, PFN/PTE conversion, and swap-PTE encoding. It covers normal 32-bit physical addresses, 36-bit physical address extensions, XPA, R3K TLBs, highmem, and huge-TLB tradeoffs.

### Important APIs, Types, And Functions
Important declarations and macros include `temp_tlb_entry`, `add_temporary_entry`, `PGDIR_SHIFT`, `PGD_TABLE_ORDER`, `PTRS_PER_PGD`, `PTRS_PER_PTE`, `USER_PTRS_PER_PGD`, `VMALLOC_START`, `VMALLOC_END`, `invalid_pte_table`, `pmd_none`, `pmd_bad`, `pmd_present`, `pmd_clear`, `pte_pfn`, `pfn_pte`, `pfn_pmd`, `pte_page`, `__swp_type`, `__swp_offset`, `__swp_entry`, and `_PAGE_SWP_EXCLUSIVE`.

### Control Flow
The generic MM layer evaluates this header at compile time to pick table sizes and folds PUD/PMD levels. Runtime helpers validate or clear PMD entries by comparing against `invalid_pte_table`, create PTEs from PFNs using the active physical-address model, and encode swap entries into non-present PTE bit ranges.

### State, Persistence, Dependencies, And Integration
State is in page-table pages, temporary boot TLB entries, invalid table sentinels, and swap PTE values. Dependencies include `addrspace.h`, `page.h`, cache/fixmap definitions, highmem when configured, and generic no-PMD folding. Integration points are early TLB setup, vmalloc layout, highmem PKMAP placement, swap, huge pages, and generic fault handling.

### Risks
Bit layouts differ sharply across R3K, XPA, 36-bit, and normal builds. Any overlap between swap type/offset/exclusive bits and hardware-valid/global/present bits can corrupt swap or create valid bogus mappings. `PGDIR_SHIFT` changes for huge-page support can silently mis-size page tables if config guards drift.

### Test Signals
Build representative 32-bit MIPS configs with and without highmem, XPA, 36-bit physical addressing, R3K TLB, and huge TLB. Boot mmap/swap/vmalloc/highmem workloads, run hugepage tests where supported, and check early boot paths that call `add_temporary_entry`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-64.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-64.h

### Purpose
`pgtable-64.h` defines 64-bit MIPS page-table geometry across two-, three-, and four-level layouts. It calculates PGD/PUD/PMD shifts and orders for page sizes from 4 KiB through 64 KiB, defines vmalloc/module ranges, invalid table sentinels, folded/non-folded table types, PFN conversion, and swap-PTE encoding.

### Important APIs, Types, And Functions
Key exports include `PGDIR_SHIFT`, `PMD_SHIFT`, `PUD_SHIFT`, `PTRS_PER_*`, `USER_PTRS_PER_PGD`, `VMALLOC_START`, `VMALLOC_END`, `MODULES_VADDR`, `invalid_pte_table`, `invalid_pmd_table`, `invalid_pud_table`, `p4d_none`, `p4d_bad`, `p4d_present`, `p4d_clear`, `p4d_pgtable`, `set_p4d`, `pmd_none`, `pmd_bad`, `pmd_present`, `pmd_clear`, `pud_none`, `pud_bad`, `pud_present`, `pud_clear`, `pud_pgtable`, `pte_pfn`, `pfn_pte`, `pfn_pmd`, `mk_swap_pte`, and swap conversion macros.

### Control Flow
Compile-time branches select generic folded-level headers and compute table shape from `CONFIG_PGTABLE_LEVELS`, page size, and 48-bit virtual-address support. Runtime inline helpers compare entries against invalid sentinel tables, clear levels back to sentinels, and derive child-table or page addresses for generic MM walkers.

### State, Persistence, Dependencies, And Integration
State lives in page-table pages, invalid table arrays, TLB-visible PTE/PMD values, and swap entries. Dependencies include `linux/compiler.h`, `linux/linkage.h`, MIPS address-space/page/cache/fixmap headers, and generic no-level wrappers. Integration covers vmalloc, module loading in 32-bit-compatible segments, THP/hugetlb PMDs via `pgtable.h`, and generic MM page-table walking.

### Risks
The matrix of page sizes, VA bits, and folded levels is easy to desynchronize from generic MM expectations. `VMALLOC_END` depends on `cpu_vmbits` and table fanout; mistakes can expose unmapped holes or collide with fixmap/module space. Swap bit allocation must avoid hardware and soft-dirty/exclusive bits.

### Test Signals
Cross-build 64-bit MIPS with 4K/16K/64K pages, 2/3/4-level tables, and `CONFIG_MIPS_VA_BITS_48`; run vmalloc, module load, swap, fork/mmap, and hugepage/THP tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-bits.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-bits.h

### Purpose
`pgtable-bits.h` defines the bit-level MIPS PTE ABI: software present/write/accessed/modified/special/soft-dirty flags, hardware EntryLo valid/dirty/global/cache flags, optional RIXI no-read/no-exec bits, PFN shifts, cache attribute encodings, and conversion to TLB EntryLo.

### Important APIs, Types, And Functions
The central type is `enum pgtable_bits`, whose layout changes by XPA, 36-bit MIPS32, R3K, or R4K-style TLB. Important macros are `_PAGE_PRESENT`, `_PAGE_WRITE`, `_PAGE_ACCESSED`, `_PAGE_MODIFIED`, `_PAGE_HUGE`, `_PAGE_SPECIAL`, `_PAGE_SOFT_DIRTY`, `_PAGE_NO_EXEC`, `_PAGE_NO_READ`, `_PAGE_GLOBAL`, `_PAGE_VALID`, `_PAGE_DIRTY`, `_CACHE_*`, `PFN_PTE_SHIFT`, `_PFN_MASK`, `__READABLE`, `__WRITEABLE`, and `_PAGE_CHG_MASK`. `pte_to_entrylo` is the key inline function.

### Control Flow
Most behavior is compile-time bit selection. When a PTE is written to the TLB, `pte_to_entrylo` shifts away software-only bits and, on RIXI-capable CPUs, rotates the no-read/no-exec bits into the hardware position expected by EntryLo.

### State, Persistence, Dependencies, And Integration
State is encoded in page-table words and later in CP0 EntryLo registers; there is no persistent storage. Dependencies are `CONFIG_*` CPU/MM options, `cpu_has_rixi`, `PAGE_SHIFT`, and cache-mode definitions. Integration is central to `pgtable.h`, TLB refill handlers, cacheability setup, soft-dirty tracking, special PTEs, huge pages, and memory-protection enforcement.

### Risks
Bit overlap is the main risk: a misplaced enum value can turn a software bit into a hardware permission or cache attribute. RIXI runtime handling depends on assembly fast paths matching this C helper. Cache mode defaults affect DMA coherency and memory ordering.

### Test Signals
Build and boot R3K, R4K, RIXI, XPA, 36-bit, soft-dirty, special-PTE, and hugepage configs. Run mprotect, exec/no-exec, read-inhibit, dirty/accessed-bit, soft-dirty, DMA cacheability, and TLB refill stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable.h

### Purpose
`pgtable.h` is the main MIPS page-table API used by generic Linux MM. It combines the 32-bit or 64-bit geometry with bit definitions, defines kernel/user page protections, PTE/PMD mutation helpers, hardware table-walker control, cache/TLB update hooks, hugepage/THP support, noncached/write-combine protections, and GUP/vmalloc aliasing policy.

### Important APIs, Types, And Functions
Important exports include `PAGE_SHARED`, `PAGE_KERNEL`, `PAGE_KERNEL_NC`, `PAGE_KERNEL_UNCACHED`, `_page_cachable_default`, `__update_cache`, `ZERO_PAGE`, `pagetable_init`, `pmd_phys`, `pmd_pfn`, `pmd_page`, `htw_stop`, `htw_start`, `pte_none`, `pte_present`, `pte_no_exec`, `set_pte`, `pte_clear`, `set_ptes`, `pte_write`, `pte_dirty`, `pte_young`, `pte_wrprotect`, `pte_mkclean`, `pte_mkold`, `pte_mkwrite_novma`, `pte_mkdirty`, `pte_mkyoung`, `pte_modify`, swap-exclusive helpers, `pgprot_noncached`, `pgprot_writecombine`, `ptep_set_access_flags`, `__update_tlb`, `update_mmu_cache_range`, THP `pmd_*` helpers, `fixup_bigphys_addr`, and `gup_fast_permitted`.

### Control Flow
Fault handling and mmap paths call PTE mutators that preserve MIPS buddy/global semantics and update software valid/dirty/accessed bits. `set_ptes` checks whether cache updates are needed before installing a range. TLB update hooks feed the hardware TLB after faults. `htw_stop`/`htw_start` disable and re-enable the hardware table walker around destructive PTE clears.

### State, Persistence, Dependencies, And Integration
State includes page-table entries, zero-page coloring, hardware walker sequence counters in CPU data, CP0 PWCTL, cache state, TLB entries, and VMA/MM metadata. Dependencies include generic MM types, `pgtable-32.h` or `pgtable-64.h`, `cmpxchg`, I/O/cache/cpu-feature headers, and TLB/cache implementation functions. Integration points are all generic MM operations, hugepage/THP, swap, soft-dirty, cache aliasing, GUP-fast, and device memory remapping.

### Risks
The global-bit buddy rule is MIPS-specific and can create stale global translations if mishandled. Missing memory barriers in split 64-bit PTE writes can expose half-written entries. Cache update decisions affect VIPT alias correctness. Hardware-table-walker sequencing must be balanced or page walks can run on transient invalid entries.

### Test Signals
Run cross-architecture MIPS MM build matrices plus runtime fork/exec/mmap, COW, mprotect, swap, soft-dirty, hugepage/THP, aliasing-cache, GUP, and device-mmap tests. Fault-injection around TLB/cache update paths is especially useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pm-cps.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/pm-cps.h

### Purpose
`pm-cps.h` defines the public CPS power-management states and entry/support checks for MIPS systems with CM/CPC coherence and power control.

### Important APIs, Types, And Functions
The file exports `coupled_coherence`, `enum cps_pm_state` with `CPS_PM_NC_WAIT`, `CPS_PM_CLOCK_GATED`, `CPS_PM_POWER_GATED`, and `CPS_PM_STATE_COUNT`, plus `cps_pm_support_state` and `cps_pm_enter_state`.

### Control Flow
Callers first test whether a state is supported, then enter it. If `coupled_coherence` is true, all VP(E)s in a core must coordinate because CM/CPC only handles coherence/power at core granularity.

### State, Persistence, Dependencies, And Integration
State is CPU/core power and coherence state, not persisted storage. Dependencies are CPU feature macros such as MIPSr6, MT, and VP support. Integration is with cpuidle/suspend paths, coherent processing system code, and low-level CPC/CM drivers.

### Risks
Incorrect coupled-entry coordination can leave sibling VPEs incoherent or powered unexpectedly. Platform state support must reflect real hardware wiring, not just CPU capability bits.

### Test Signals
Build with MIPS MT and MIPSr6 variants; exercise cpuidle/suspend states on multi-VPE hardware, validate wakeup, interrupt delivery, cache coherency, and failure returns from unsupported states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pm-cps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pm.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/pm.h

### Purpose
`pm.h` provides MIPS suspend/resume assembly macros and the minimal static CPU-state structure needed for suspend-to-RAM, especially when EVA segment registers must be restored before normal memory access is safe.

### Important APIs, Types, And Functions
Assembler macros include `SUSPEND_SAVE_REGS`, `RESUME_RESTORE_REGS_RETURN`, `LA_STATIC_SUSPEND`, `SUSPEND_SAVE_STATIC`, `RESUME_RESTORE_STATIC`, `SUSPEND_CACHE_FLUSH`, `SUSPEND_SAVE`, and `RESUME_RESTORE_RETURN`. The C-visible type is `struct mips_static_suspend_state`.

### Control Flow
Suspend assembly saves callee-preserved GPRs and CP0 status to a `pt_regs`-sized stack frame, stores early-restore state in `mips_static_suspend_state`, flushes caches to RAM, and later resumes by restoring EVA segment registers if present, reloading the stack pointer, restoring registers, and returning.

### State, Persistence, Dependencies, And Integration
State is volatile CPU register context, CP0 segment configuration, stack frame contents, and flushed cachelines in RAM. Dependencies include assembly offsets, MIPS register definitions, `regdef.h`, hazard macros, and `__flush_cache_all`. Integration is with platform suspend code and low-level resume entry points.

### Risks
The macros are context-sensitive assembly: wrong offsets, missing hazards after EVA register writes, or unflushed cache state can make resume fail before diagnostics are available. The saved static structure must be reachable under early segment mappings.

### Test Signals
Build both C and assembler users with and without `CONFIG_EVA`; run suspend-to-RAM/resume loops, verify CP0 status/segment restoration, and test with cache-disabled or memory-remapped resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/prefetch.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/prefetch.h

### Purpose
`prefetch.h` defines MIPS prefetch hint numbers and assembler convenience macros for optional `pref` instructions, while documenting CPU-specific limitations and errata.

### Important APIs, Types, And Functions
Hint macros include `Pref_Load`, `Pref_Store`, `Pref_LoadStreamed`, `Pref_StoreStreamed`, `Pref_LoadRetained`, `Pref_StoreRetained`, `Pref_WriteBackInvalidate`, and `Pref_PrepareForStore`. Assembler macros include `__pref`, `pref_load`, `pref_store`, `pref_load_streamed`, `pref_store_streamed`, `pref_load_retained`, `pref_store_retained`, `pref_wback_inv`, and `pref_prepare_for_store`.

### Control Flow
Assembler code expands a prefetch macro. If `CONFIG_CPU_HAS_PREFETCH` is enabled it emits `pref`; otherwise it emits nothing.

### State, Persistence, Dependencies, And Integration
The only state affected is CPU cache/prefetch behavior. There is no persistence. Integration is with hand-written MIPS assembly and performance-sensitive memory paths.

### Risks
Some MIPS CPUs implement hints as no-ops or have broken hints; enabling the wrong hint can waste cycles or trigger errata. These macros intentionally do not validate target CPU errata at each call site.

### Test Signals
Cross-build assembler users with and without prefetch support; benchmark copy/checksum/cache-sensitive paths on affected CPUs; run errata-sensitive platforms with prefetch disabled/enabled as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/prefetch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/processor.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/processor.h

### Purpose
`processor.h` defines the MIPS processor and per-thread execution-state contract: task address limits, stack placement, FPU/MSA/DSP/watch/COP2 saved state, thread initialization, stack/register helpers, return-address handling, prefetch C intrinsics, and FP-mode prctl hooks.

### Important APIs, Types, And Functions
Key macros include `TASK_SIZE`, `TASK_SIZE32`, `TASK_SIZE64`, `STACK_TOP_MAX`, `TASK_UNMAPPED_BASE`, `VDSO_RANDOMIZE_SIZE`, `NUM_FPU_REGS`, `FPU_REG_WIDTH`, `FPR_IDX`, `INIT_THREAD`, `task_pt_regs`, `KSTK_EIP`, `KSTK_ESP`, `return_address`, `ARCH_HAS_PREFETCH`, `GET_FP_MODE`, and `SET_FP_MODE`. Key types include `union fpureg`, `struct mips_fpu_struct`, `struct mips_dsp_state`, `union mips_watch_reg_state`, Octeon COP2/CVMSEG state, and `struct thread_struct`. Externs include `arch_dup_task_struct`, `mips_stack_top`, `start_thread`, `__get_wchan`, `mips_get_process_fp_mode`, `mips_set_process_fp_mode`, and `show_registers`.

### Control Flow
Scheduler and fork/exec paths initialize and copy `thread_struct`; exception and ptrace paths read saved task registers through `task_pt_regs`; FP-mode prctls dispatch through the defined getter/setter; optional prefetch macros compile to GCC builtins when supported.

### State, Persistence, Dependencies, And Integration
State is per-task CPU context, FPU/MSA/DSP/watch registers, Octeon COP2 state, bad address/error/trap metadata, and ABI pointers. Dependencies include CPU/cache/thread headers, `mipsregs`, `dsemul`, `prefetch`, VDSO processor definitions, and task/thread flags. Integration is central to scheduler context switching, signal/ptrace, coredumps, FPU emulation, prctl, and VDSO stack layout.

### Risks
`struct thread_struct` layout is coupled to assembly offsets. Address-limit constants are ABI-visible and affect mmap, stack, and VDSO placement. Endianness-sensitive FPR indexing and optional MSA width must match save/restore code. Octeon COP2 alignment is strict.

### Test Signals
Cross-build 32/64-bit, O32/N32/N64, MSA, DSP, Octeon, and FP-affinity configs. Run fork/exec, signal, ptrace, coredump, FP/MSA/DSP context-switch, prctl FP-mode, and stack unwinding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/prom.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/prom.h

### Purpose
`prom.h` declares MIPS firmware/device-tree setup hooks and machine-name accessors. It supports Open Firmware/device-tree boot when `CONFIG_USE_OF` is enabled and provides no-op initialization otherwise.

### Important APIs, Types, And Functions
Exports include `device_tree_init`, forward `struct boot_param_header`, `__dt_setup_arch`, `__dt_register_buses`, `mips_get_machine_name`, and `mips_set_machine_name`.

### Control Flow
Early boot calls `device_tree_init` and architecture setup to consume the boot parameter header and register buses. Non-OF builds compile `device_tree_init` to an empty inline, leaving platform-specific boot paths to supply machine data.

### State, Persistence, Dependencies, And Integration
State includes the boot firmware's DT blob, registered platform buses, and an in-kernel machine-name string. Dependencies under OF include bug, I/O, type, and bootinfo headers. Integration is early architecture setup, platform device enumeration, and user-visible machine identity.

### Risks
DT pointers are early-boot memory and must remain valid until unflattened. Bus registration names must match platform driver expectations. Non-OF builds can silently skip DT setup, so call sites must not assume devices appear.

### Test Signals
Boot OF and non-OF MIPS configs, verify `/proc/device-tree` or platform devices, check machine name reporting, and build both branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ptrace.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/ptrace.h

### Purpose
`ptrace.h` defines MIPS saved exception/syscall register layout and helper APIs used by ptrace, kprobes, stack unwinding, profiling, syscall tracing, and die/oops handling.

### Important APIs, Types, And Functions
The key type is `struct pt_regs`, including saved syscall args for 32-bit, GPRs, CP0 status/cause/EPC/bad address, HI/LO, optional SmartMIPS ACX, and optional Octeon MTM/MTP registers. Helpers include `kernel_stack_pointer`, `instruction_pointer_set`, `regs_query_register_offset`, `regs_get_register`, `regs_within_kernel_stack`, `regs_get_kernel_stack_nth`, `ptrace_getregs`, `ptrace_setregs`, FP/watch ptrace APIs, `user_mode`, `is_syscall_success`, `regs_return_value`, `instruction_pointer`, `exception_ip`, `syscall_trace_enter`, `syscall_trace_leave`, `die`, `die_if_kernel`, `current_pt_regs`, and user-stack pointer accessors.

### Control Flow
Exception and syscall entry code saves registers into `pt_regs`. Ptrace and tracing code reads or writes that frame. Return-value helpers interpret MIPS syscall convention (`regs[7]` as error indicator). Fatal paths call `die_if_kernel` when a trap occurred outside user mode.

### State, Persistence, Dependencies, And Integration
State is the current exception frame on the kernel stack and optional architecture register blocks. Dependencies include compiler/linkage/types, ISA dependencies, page/thread info, and UAPI ptrace definitions. Integration is with `arch/mips/kernel/ptrace.c`, syscall tracing, signal delivery, stack dump, perf/profile PC collection, and seccomp/audit paths.

### Risks
The struct layout is coupled to assembly and `regoffset_table`; adding a register without updating offset users breaks ptrace. `current_pt_regs` depends on kernel-stack geometry. Error-return interpretation must stay aligned with syscall entry/exit code.

### Test Signals
Run ptrace register get/set tests across ABI variants, syscall tracing/seccomp tests, stack dump/oops tests, kprobes/perf sampling, and Octeon/SmartMIPS builds when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/r4k-timer.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/r4k-timer.h

### Purpose
`r4k-timer.h` declares or stubs synchronization of MIPS R4K CP0 count timers across CPUs.

### Important APIs, Types, And Functions
The single API is `synchronise_count_slave(int cpu)`, declared externally under `CONFIG_SYNC_R4K` and otherwise defined as an empty inline.

### Control Flow
SMP timer bring-up calls `synchronise_count_slave` for secondary CPUs. On configurations that do not require synchronization, the call compiles away.

### State, Persistence, Dependencies, And Integration
State is CP0 Count/Compare timing state and per-CPU timer skew; there is no persistence. Integration is with SMP CPU bring-up, clockevents, and scheduler tick correctness.

### Risks
Wrongly disabling synchronization can produce skewed timer interrupts. Calling synchronization too late or without matching master-side code can make secondary CPU timekeeping unstable.

### Test Signals
Boot SMP R4K-style systems with `CONFIG_SYNC_R4K`, compare per-CPU clockevent skew, run timer migration and scheduler tick tests, and build the stub branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/r4k-timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/r4kcache.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/r4kcache.h

### Purpose
`r4kcache.h` implements inline MIPS R4K-style cache operations and generated blast helpers for I-cache, D-cache, S-cache, user pages, address ranges, and Loongson node-aware secondary-cache flushing.

### Important APIs, Types, And Functions
Important declarations are `r5k_sc_init`, `rm7k_sc_init`, `mips_sc_init`, `r4k_blast_dcache`, and `r4k_blast_icache`. Important macros/functions include `INDEX_BASE`, `_cache_op`, `cache_op`, line flush/invalidate helpers, `protected_cache_op`, `protected_flush_icache_line`, `protected_writeback_dcache_line`, `protected_writeback_scache_line`, `invalidate_tcache_page`, `cache_unroll`, and generated `blast_*cache*`, `blast_*cache*_page`, `blast_*cache*_page_indexed`, `blast_*cache*_range`, protected range helpers, user-page helpers, and Loongson node helpers.

### Control Flow
Callers invoke inline helpers that emit `cache` or EVA `cachee` instructions. Protected variants wrap the instruction with exception-table fixups and return `-EFAULT` on invalid user addresses. Blast helpers iterate over ways/indices or line ranges, unrolling 32 cache operations per inner chunk.

### State, Persistence, Dependencies, And Integration
State is CPU cache contents/tags, current CPU cache geometry, exception-table fixups, and optional node address bases. Dependencies include cache op encodings, CPU feature/type detection, MIPS assembly helpers, EVA support, MM zones, and unroll macros. Integration is with cache flush implementations, DMA/I-cache coherency, signal trampolines, user copy, secondary cache initialization, and Loongson NUMA cache handling.

### Risks
Inline assembly constraints and ISA level must match target CPU. Wrong line size or way geometry can leave stale cachelines. Protected variants rely on exact exception-table relocation. Some CPUs need special operations, such as Loongson2 I-cache invalidation and R10000 writeback/invalidate behavior.

### Test Signals
Cross-build EVA/non-EVA, Loongson, R5K/RM7K, secondary-cache, and NUMA configs. Run I-cache coherency tests after code modification, DMA cache maintenance tests, user-address protected flush fault tests, and boot cache init diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/r4kcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/reboot.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/reboot.h

### Purpose
`reboot.h` exposes machine-specific reboot and halt hooks for MIPS platform code.

### Important APIs, Types, And Functions
The exported state is two function pointers: `_machine_restart(char *command)` and `_machine_halt(void)`.

### Control Flow
Generic reboot/halt paths call the installed platform hook. Platform setup assigns these pointers during boot.

### State, Persistence, Dependencies, And Integration
State is the currently installed reboot/halt implementation pointer; there is no persistent storage. Integration is with `kernel/reboot.c`-style generic shutdown paths and platform firmware or board reset drivers.

### Risks
Null or incorrectly installed hooks can hang shutdown. The restart command string lifetime and platform firmware expectations must match the implementation.

### Test Signals
Boot each MIPS platform config and exercise `reboot`, `halt`, and panic-restart paths; verify hook installation during platform init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/reboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/reg.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/reg.h

### Purpose
`reg.h` is a thin architecture include wrapper that re-exports UAPI MIPS register definitions to kernel code.

### Important APIs, Types, And Functions
It directly includes `<uapi/asm/reg.h>` and defines no local API.

### Control Flow
There is no runtime flow; consumers receive UAPI register constants through this include.

### State, Persistence, Dependencies, And Integration
No state exists here. Integration is between kernel-internal users and the userspace-visible register ABI definitions.

### Risks
Because it is ABI glue, replacing or removing the include can break ptrace/core/regset consumers expecting the UAPI definitions.

### Test Signals
Build ptrace, core dump, and register-set users; run ABI tests that include both UAPI and kernel MIPS register constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/regdef.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/regdef.h

### Purpose
`regdef.h` defines symbolic MIPS general-purpose register numbers and assembler register aliases for ABI32, NABI32, and ABI64 code.

### Important APIs, Types, And Functions
Numeric macros include `GPR_ZERO`, `GPR_AT`, `GPR_V0`, argument registers, temporaries, saved registers, `GPR_GP`, `GPR_SP`, `GPR_FP`, and `GPR_RA`. Under `__ASSEMBLER__`, it defines names such as `zero`, `AT`, `v0`, `a0`, `t0`, `s0`, `gp`, `sp`, `fp`, `s8`, and `ra`, with ABI-dependent argument/temporary mappings.

### Control Flow
There is no runtime flow. Assembly files expand these aliases when assembled for the selected `_MIPS_SIM`.

### State, Persistence, Dependencies, And Integration
No runtime state exists. Dependency is `asm/sgidefs.h` for ABI selection. Integration is broad across hand-written MIPS assembly, low-level entry code, suspend macros, and firmware call glue.

### Risks
ABI-specific alias differences are subtle: N32/N64 have more argument registers and different temporary naming than O32. A wrong alias can corrupt calling convention state in assembly.

### Test Signals
Assemble O32, N32, and N64 kernel/firmware assembly users; inspect generated code for argument/saved register use; run syscall, exception, and suspend/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/regdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/rtlx.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/rtlx.h

### Purpose
`rtlx.h` declares the MIPS RTLX communication channel interface used between Linux and another VPE/SP in MIPS MT/APRP environments.

### Important APIs, Types, And Functions
Constants include `RTLX_MODULE_NAME`, `LX_NODE_BASE`, `MIPS_CPU_RTLX_IRQ`, `RTLX_VERSION`, `RTLX_ID`, `RTLX_BUFFER_SIZE`, `RTLX_CHANNELS`, and standard channel IDs. APIs include `rtlx_starting`, `rtlx_stopping`, `rtlx_open`, `rtlx_release`, `rtlx_read`, `rtlx_write`, read/write poll helpers, module init/exit, and `_interrupt_sp`. Types/state include `enum rtlx_state`, `struct chan_waitqueues`, `struct rtlx_channel`, global `channel_wqs`, `rtlx_notify`, `rtlx_fops`, `aprp_hook`, and `struct rtlx_info *rtlx`.

### Control Flow
VPE lifecycle notifications start/stop RTLX, userspace device operations open channels and perform buffered reads/writes, poll helpers expose readiness, and `_interrupt_sp` is the low-level interrupt bridge to the service processor side.

### State, Persistence, Dependencies, And Integration
State is shared memory rings (`rt_buffer`/`lx_buffer` with read/write indices), channel state, wait queues, mutexes, and atomic open guards. Dependencies include IRQ and VPE notification infrastructure plus file operations. Integration is with character devices, poll/select, MIPS MT VPE management, and APRP hooks.

### Risks
Ring indices are shared with another execution context; ordering, cache coherency, and wakeups must be correct. Channel open serialization and sleeping behavior must avoid deadlocks. Buffer IDs and version constants must match the remote side.

### Test Signals
Build MIPS MT/APRP configs, run open/read/write/poll tests across all channels, start/stop remote VPEs, stress concurrent opens, and verify interrupt-driven wakeups and buffer wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/rtlx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/seccomp.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/seccomp.h

### Purpose
`seccomp.h` supplies MIPS architecture-specific seccomp mode 1 syscall allowlists for compat tasks and then includes the generic seccomp definitions.

### Important APIs, Types, And Functions
The main helper is `get_compat_mode1_syscalls`, enabled under `CONFIG_COMPAT`, returning O32 or N32 negative-terminated syscall arrays. It defines `get_compat_mode1_syscalls` for generic seccomp and includes `asm-generic/seccomp.h`.

### Control Flow
When compat seccomp mode 1 is evaluated, the helper chooses O32 if `CONFIG_MIPS32_O32` and `TIF_32BIT_REGS` are active, chooses N32 if enabled, and otherwise triggers `BUG()`.

### State, Persistence, Dependencies, And Integration
State is the current thread ABI flag and static syscall arrays; there is no persistence. Dependencies include `linux/unistd.h`, thread flags through included context, and generic seccomp. Integration is syscall filtering for compat MIPS ABIs.

### Risks
Syscall numbers must match ABI tables. The `BUG()` fallback is harsh if ABI detection is wrong. Missing updates when syscall numbering changes can make strict seccomp allow or deny the wrong calls.

### Test Signals
Run strict seccomp tests for O32 and N32 compat tasks, verify allowed `read`, `write`, `_exit`, and `sigreturn` numbers, and build non-compat and compat configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/setup.h

### Purpose
`setup.h` declares MIPS early setup hooks for PROM output, early printk, exception/vector installation, per-CPU trap setup, cache/TLB initialization, relocation, and hardware capability globals.

### Important APIs, Types, And Functions
Exports include `prom_putchar`, `setup_early_printk`, optional `setup_8250_early_printk_port`, `set_handler`, `set_uncached_handler`, `vi_handler_t`, `set_vi_handler`, `set_except_vector`, globals `ebase` and `hwrena`, `per_cpu_trap_init`, `cpu_cache_init`, `tlb_init`, optional `relocate_kernel`, and `plat_post_relocation`.

### Control Flow
Early boot configures console output, installs exception handlers/vectored interrupt handlers, initializes per-CPU traps, cache, and TLB, and optionally relocates the kernel before platform post-relocation callbacks.

### State, Persistence, Dependencies, And Integration
State is exception-vector memory, EBase, HWREna, early console port setup, cache/TLB state, and relocated kernel address state. Dependencies include init/types headers and UAPI setup constants. Integration is with boot code, trap handlers, early printk, CPU bring-up, and relocatable kernel support.

### Risks
Handlers are copied into low-level exception memory; wrong offsets or lengths can brick early boot. Early 8250 setup is a no-op unless configured. Relocation callbacks must run before references to old addresses become invalid.

### Test Signals
Build early printk and relocatable variants, boot with exceptions and interrupts enabled, verify early console output, run TLB/cache init smoke tests, and exercise secondary CPU trap init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/gio.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/gio.h

### Purpose
`sgi/gio.h` documents and defines SGI GIO bus address ranges and board-ID bit extraction for Indigo/Indy/Indigo2-era expansion devices.

### Important APIs, Types, And Functions
Macros include `GIO_ID`, `GIO_32BIT_ID`, `GIO_REV`, `GIO_64BIT_IFACE`, `GIO_ROM_PRESENT`, `GIO_VENDOR_CODE`, and slot base addresses `GIO_SLOT_GFX_BASE`, `GIO_SLOT_EXP0_BASE`, and `GIO_SLOT_EXP1_BASE`.

### Control Flow
There is no executable flow. GIO probing code reads a slot ID value and uses the macros to decode product ID, revision, interface width, ROM presence, and vendor bits.

### State, Persistence, Dependencies, And Integration
State is hardware slot address space and ID values returned by devices. Integration is with SGI platform bus probing and drivers for GIO graphics, network, and expansion devices.

### Risks
Some IDs are 8-bit with undefined high bits; callers must mask before comparing. Slot availability differs by machine model, so blindly probing fixed ranges can fault or misdetect devices.

### Test Signals
Boot SGI IP22-class configs with known GIO devices, verify ID decode and slot resource assignment, and test absent-slot probing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/gio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/heart.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/heart.h

### Purpose
`sgi/heart.h` defines the SGI IP30 HEART system controller register map, timer constants, memory-bank layout, interrupt priorities/vectors, error/status masks, and raw 64-bit register access aliases.

### Important APIs, Types, And Functions
Key type is `struct ip30_heart_regs`, mapping mode, SDRAM, memory config, flow control, status/error registers, interrupt mask/status/cause, counter/compare/trigger, CPU ID, and sync registers. Important macros include `HEART_MEMORY_BANKS`, `HEART_MAX_CPUS`, `HEART_XKPHYS_BASE`, `HEART_NS_PER_CYCLE`, `HEART_CYCLES_PER_SEC`, `HEART_*` masks, `HM_*` mode bits, memory refresh/config fields, status/cause fields, `HEART_NUM_IRQS`, priority masks `HEART_L*_INT_MASK`, interrupt vector numbers, external `heart_regs`, and `heart_read`/`heart_write`.

### Control Flow
Platform code maps `heart_regs`, reads/writes 64-bit registers, configures memory controller and interrupts, uses HEART count/compare for timing, and clears/sets interrupt status through dedicated registers.

### State, Persistence, Dependencies, And Integration
State is IP30 system controller MMIO: memory configuration, error latches, interrupt masks/status, timer count/compare, and reset/mode bits. Dependencies include Linux types/time and raw 64-bit I/O helpers. Integration covers IP30 memory discovery, interrupt controller, timer, reset/error handling, and Xtalk/Bridge error propagation.

### Risks
All registers are 64-bit-wide but memory config requires 32-bit reads for useful bank values. Many fields are marked not fully understood, so changing masks can affect hardware behavior. Incorrect interrupt priority masks can route errors to wrong CPU pins.

### Test Signals
Boot IP30, validate memory bank detection, timer frequency, IRQ routing across priority levels, bus/memory error handling, and 32-bit versus 64-bit mem_cfg access behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/heart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/hpc3.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/hpc3.h

### Purpose
`sgi/hpc3.h` maps the SGI HPC3 peripheral controller: PBUS DMA channels, SCSI DMA, SEEQ Ethernet DMA/control, interrupt status, EEPROM, PROM, RTC, battery-backed RAM, and peripheral timing/config registers.

### Important APIs, Types, And Functions
Key types are `struct hpc_dma_desc`, `struct hpc3_pbus_dmacregs`, `struct hpc3_scsiregs`, `struct hpc3_ethregs`, and `struct hpc3_regs`. Important macros cover DMA descriptor flags (`HPCDMA_*`), PBUS DMA control, SCSI byte count/control/config, Ethernet RX/TX control and descriptors, IRQ status bits, GIO misc/endian bits, EEPROM/PROM controls, DMA/PIO timing fields, chip base addresses, globals `hpc3c0`/`hpc3c1`, and `sgihpc_init`.

### Control Flow
Drivers build descriptor chains, program descriptor pointers and byte counts, set control bits to start DMA, inspect status/interrupt registers, and clear/reset channels. Ethernet and SCSI drivers access external device registers through HPC3 windows and use DMA completion/status bits for progress.

### State, Persistence, Dependencies, And Integration
State is volatile controller MMIO, DMA descriptors in memory, FIFO pointers, EEPROM/PROM/RTC/BBRAM contents, and global mapped-controller pointers. Dependencies include Linux types and page definitions. Integration is with SGI SCSI, Ethernet, parallel/PBUS device drivers, interrupt handling, DMA mapping, and early platform initialization.

### Risks
Descriptor ownership and endian bits must match CPU/device expectations. Some IRQ status bits require reading two different registers due to hardware quirks. Volatile register layout and large padding must stay exact; word access to subdevices can have side effects.

### Test Signals
Boot IP22/IP28-style systems, exercise SCSI and SEEQ Ethernet DMA under load, test PBUS devices, validate EEPROM/RTC access, interrupt status clearing, DMA endian modes, and descriptor ring wrap/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/hpc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ioc.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ioc.h

### Purpose
`sgi/ioc.h` defines SGI I/O Controller and INT2/INT3 register maps for UARTs, keyboard/mouse, parallel-port integration, interrupt masks/status, timer, panel controls, system ID, DMA selection, reset/write controls, and external I/O status.

### Important APIs, Types, And Functions
Types include `struct sgioc_uart_regs`, `struct sgioc_keyb_regs`, `struct sgint_regs`, and `struct sgioc_regs`. Important macros include `SGINT_ISTAT*`, `SGINT_TCWORD_*`, `SGINT_TIMER_CLOCK`, `SGINT_TCSAMP_COUNTER`, `SGIOC_PANEL_*`, `SGIOC_SYSID_*`, `SGIOC_DMASEL_*`, `SGIOC_RESET_*`, `SGIOC_WRITE_*`, `EXTIO_*`, globals `sgi_ioc_reset`, `sgi_ioc_write`, `sgioc`, and `sgint`.

### Control Flow
Platform and drivers read 8-bit registers aligned on 32-bit boundaries, update software shadows for write-only reset/write registers, program 8254 timer control/count registers, and enable/disable interrupt sources through mask registers.

### State, Persistence, Dependencies, And Integration
State is IOC/INT MMIO, software copies of write-only registers, timer counters, panel/system ID latches, and global controller pointers. Dependencies include Linux types and `pi1.h`. Integration covers serial, keyboard/mouse, parallel port, front panel, timer calibration, interrupt controller, power/AC-fail events, and FullHouse external I/O.

### Risks
The file warns that registers are 8-bit and 32-bit aligned; word access can break hardware behavior. Write-only software shadows must stay synchronized. Timer frequency and mask polarity assumptions affect clock and IRQ delivery.

### Test Signals
Boot SGI IOC platforms, test serial/kbd/mouse/panel/timer interrupts, verify 8-bit accessors, compare software shadow values after reset/write changes, and test FullHouse `extio` status decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ioc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ip22.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ip22.h

### Purpose
`sgi/ip22.h` defines SGI IP22/Indy/Indigo2 virtual IRQ numbering, IRQ grouping spaces, individual interrupt assignments, machine-type helper, and board support prototypes.

### Important APIs, Types, And Functions
Macros define IRQ spaces `SGINT_EISA`, `SGINT_CPU`, `SGINT_LOCAL0` through `SGINT_LOCAL3`, `SGINT_END`, individual IRQs such as `SGI_TIMER_IRQ`, `SGI_WD93_0_IRQ`, `SGI_ENET_IRQ`, `SGI_HPCDMA_IRQ`, `SGI_KEYBD_IRQ`, and `SGI_SERIAL_IRQ`, plus `ip22_is_fullhouse()`. Externs include `ip22_eeprom_read`, `ip22_nvram_read`, `ip22_be_interrupt`, `ip22_be_init`, and `indy_8254timer_irq`.

### Control Flow
Interrupt setup maps CPU, local, EISA, and vectored interrupt spaces to controller operations. Drivers use the assigned virtual IRQ constants, while board code handles bus-error and timer interrupts and reads EEPROM/NVRAM.

### State, Persistence, Dependencies, And Integration
State is IRQ controller masks/status, IOC system ID, EEPROM/NVRAM contents, and bus-error latch state. Dependencies include IRQ base definitions and IOC register macros. Integration is SGI IP22 interrupt controller setup, device drivers for SCSI/Ethernet/GIO/serial/keyboard, and board error handling.

### Risks
HPC/MC DMA interrupts are explicitly not supported through the normal virtual IRQ mapping, so drivers must share and inspect status bits. FullHouse detection dereferences `sgioc`; it must be initialized before use.

### Test Signals
Boot Indy/Indigo2 variants, verify IRQ numbering against `/proc/interrupts`, exercise SCSI/Ethernet/GIO/keyboard/serial/timer interrupts, read EEPROM/NVRAM, and inject bus errors if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/ip22.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/mc.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/mc.h

### Purpose
`sgi/mc.h` maps the SGI IP20/IP22/IP26/IP28 memory controller registers and defines control, parity/error, GIO DMA, memory configuration, EEPROM, watchdog, RPSS, and DMA operation bit fields.

### Important APIs, Types, And Functions
The key type is `struct sgimc_regs`. Important macros cover `SGIMC_CCTRL0_*`, `SGIMC_CCTRL1_*`, `SGIMC_SYSID_*`, EEPROM bits, `SGIMC_GIOPAR_*`, memory config bits, CPU/GIO error status bits, DMA registers, base address `SGIMC_BASE`, memory segment base/size constants, global `sgimc`, and `sgimc_init`.

### Control Flow
Platform code maps `sgimc`, configures memory refresh/control, probes memory banks, handles parity/bus errors by reading error/status registers, controls GIO DMA translation and DMA operations, and uses the watchdog/RPSS counters as needed.

### State, Persistence, Dependencies, And Integration
State is memory-controller MMIO, EEPROM bits, memory bank configuration, parity/error latches, DMA TLB entries, DMA transfer state, and global mapped pointer. Integration includes memory sizing, GIO/EISA/HPC endianness, bus-error handling, DMA, watchdog, and platform initialization.

### Risks
Control bits can reset hardware, alter endianness, enable PROM writes, or affect memory refresh. Mis-decoding bank config can expose absent memory or miss RAM. DMA TLB and transfer registers require strict ordering.

### Test Signals
Boot supported SGI systems, verify memory map against physical RAM, test parity/bus-error reporting, GIO/EISA/HPC devices, DMA transfers, EEPROM reads, and watchdog/reset paths under controlled conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/pi1.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/pi1.h

### Purpose
`sgi/pi1.h` defines the SGI PI1 parallel port register layout and control/status/DMA/interrupt/timing bit fields.

### Important APIs, Types, And Functions
The key type is `struct pi1_regs`. Macros include `PI1_CTRL_*`, `PI1_STAT_*`, `PI1_DMACTRL_*`, `PI1_INTSTAT_*`, `PI1_INTMASK_*`, and default timer constants `PI1_TIME1` through `PI1_TIME4`.

### Control Flow
Parallel-port drivers read/write 8-bit registers in the struct, configure direction and IRQ enable, start/abort DMA/FIFO operations, inspect status/interrupt bits, and program timing registers.

### State, Persistence, Dependencies, And Integration
State is PI1 MMIO register contents and FIFO/DMA state; no filesystem persistence. It is embedded in `struct sgioc_regs` and integrates with SGI parallel-port and IOC interrupt handling.

### Risks
Interrupt mask polarity is reset-high/enabled-low. DMA control has write-only side effects such as abort and FIFO clear. Register padding must preserve 8-bit-on-32-bit-boundary layout.

### Test Signals
Test parport probe, IRQ handling, read/write direction switching, DMA/FIFO modes, and timer defaults on SGI IOC systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/pi1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/seeq.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/seeq.h

### Purpose
`sgi/seeq.h` defines platform data for the SGI SEEQ Ethernet driver when attached through HPC3.

### Important APIs, Types, And Functions
The exported type is `struct sgiseeq_platform_data`, containing an `hpc3_regs` pointer, IRQ number, and Ethernet MAC address buffer sized by `ETH_ALEN`.

### Control Flow
Platform setup fills this structure and passes it to the SEEQ driver, which then uses the HPC3 register pointer and IRQ to drive Ethernet DMA/control.

### State, Persistence, Dependencies, And Integration
State is platform-provided hardware pointer, interrupt line, and MAC address. Dependencies include Ethernet address definitions and `hpc3.h`. Integration is SGI onboard Ethernet platform-device setup.

### Risks
An incorrect HPC pointer or IRQ breaks network I/O; an unset or invalid MAC address creates duplicate or unusable Ethernet identity.

### Test Signals
Probe the SEEQ driver, verify MAC address, transmit/receive traffic, IRQ delivery, and HPC3 DMA interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/seeq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/wd.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/wd.h

### Purpose
`sgi/wd.h` defines platform data for SGI WD93 SCSI controllers attached through HPC3.

### Important APIs, Types, And Functions
The exported type is `struct sgiwd93_platform_data`, containing controller unit, IRQ, pointer to `struct hpc3_scsiregs`, and pointer to external WD registers.

### Control Flow
Board setup provides this platform data to the WD93 SCSI driver; the driver uses the HPC3 SCSI DMA register block and external register pointer to issue SCSI commands and handle IRQs.

### State, Persistence, Dependencies, And Integration
State is platform wiring information and SCSI/HPC3 MMIO state, with persistent storage only in attached SCSI devices outside this header. Dependency is `hpc3.h`. Integration is SGI onboard SCSI platform device setup.

### Risks
Wrong register pointers or IRQs can corrupt DMA or hang the SCSI bus. Unit numbering must match physical controller wiring.

### Test Signals
Probe both possible WD93 units, enumerate SCSI disks, run read/write stress, disconnect/reselect tests, and IRQ/DMA error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/wd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgialib.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgialib.h

### Purpose
`sgialib.h` declares the SGI ARCS firmware helper library used during MIPS SGI boot for console I/O, memory descriptors, firmware environment, command-line parsing, file I/O, display status, and PROM mode transitions.

### Important APIs, Types, And Functions
Exports include global `romvec`, `prom_flags`, flags `PROM_FLAG_ARCS`, `PROM_FLAG_USE_AS_CONSOLE`, `PROM_FLAG_DONT_FREE_TEMP`, `prom_getchar`, `prom_getmdesc`, `PROM_NULL_MDESC`, `prom_meminit`, `PROM_NULL_COMPONENT`, `prom_identify_arch`, `ArcGetEnvironmentVariable`, `prom_init_cmdline`, `ArcRead`, `ArcWrite`, `ArcEnterInteractiveMode`, and `ArcGetDisplayStatus`.

### Control Flow
Early SGI boot initializes `romvec`, identifies firmware architecture, reads memory descriptors into kernel memory setup, parses ARCS command-line/environment values, and optionally uses PROM console/file/display services before normal drivers take over.

### State, Persistence, Dependencies, And Integration
State is firmware ROM vector pointer, PROM flags, ARCS memory descriptors, environment variables, file handles, and display status. Dependencies include compiler attributes and `sgiarcs.h`. Integration is with SGI PROM boot, memory initialization, early console, initrd/boot file loading, and architecture identification.

### Risks
Firmware calls may be 32-bit or 64-bit depending on ARCS mode and must match the wrappers in `sgiarcs.h`. PROM memory marked temporary or permanent must not be freed incorrectly. Early console use can conflict with later drivers if flags are wrong.

### Test Signals
Boot SGI ARCS systems, compare memory map from PROM with Linux memblock, read environment variables and command line, test PROM console/file reads early, and verify no calls occur after firmware services are unsafe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgialib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgiarcs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgiarcs.h

### Purpose
`sgiarcs.h` defines the SGI ARC/ARCS firmware ABI: error codes, device-tree component classes/types/identifiers, memory descriptors, file/time/directory structures, ROM vector layout, system parameter block, boot blocks, debugger block, cache/config data, and ARC call wrappers for 32-bit and 64-bit firmware combinations.

### Important APIs, Types, And Functions
Major types include `enum linux_devclass`, `enum linux_devtypes`, `enum linux_identifier`, `struct linux_component`, `struct linux_sysid`, ARCS/ARC memory type enums, `struct linux_mdesc`, `struct linux_tinfo`, `struct linux_vdirent`, `enum linux_omode`, `enum linux_seekmode`, `enum linux_mountops`, `struct linux_bigint`, `struct linux_finfo`, `struct linux_romvec`, `SYSTEM_PARAMETER_BLOCK`, `union linux_cache_key`, `struct linux_cdata`, `struct sgi_partition`, `struct sgi_bootblock`, `struct sgi_bparm_block`, `struct sgi_bsector`, and `struct linux_smonblock`. Important macros include `PROM_E*`, `PROMBLOCK`, `ROMVECTOR`, `SGIPROM_*`, boot block constants, `SMB_DEBUG_MAGIC`, and `ARC_CALL0` through `ARC_CALL5`.

### Control Flow
Firmware clients access the fixed `PROMBLOCK`, retrieve the ROM vector, and invoke function pointers through `ARC_CALL*`. On 64-bit kernels calling 32-bit ARC firmware, wrappers funnel calls through `call_o32` and a dedicated O32 stack; matching-width kernels call function pointers directly.

### State, Persistence, Dependencies, And Integration
State is firmware-owned PROM structures, ROM vector functions, environment variables, memory descriptors, firmware file descriptors, boot blocks, and debugger metadata. Persistent data may include firmware environment and boot media metadata, but the header itself only defines layouts. Dependencies include kernel helpers, MIPS/ARC fixed-width types, endianness macros, and `ARRAY_SIZE` in call-wrapper code.

### Risks
The ABI is firmware-defined; struct packing, pointer width, endianness of `linux_bigint`, and 32/64-bit call conventions must be exact. The fixed PROM block address is unmapped or invalid outside SGI ARCS boot contexts. Wrong call wrappers can corrupt firmware stack/register state.

### Test Signals
Boot 32-bit and 64-bit SGI ARCS configurations, call representative firmware services through `ARC_CALL*`, validate memory descriptors/environment/file I/O, inspect boot partition parsing, and test ARC32-on-64-bit wrapper stack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgiarcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/shmparam.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/shmparam.h

### Purpose
`shmparam.h` defines the MIPS shared-memory attach alignment requirement used to avoid cache aliasing problems.

### Important APIs, Types, And Functions
It exports `__ARCH_FORCE_SHMLBA` and `SHMLBA`, with `SHMLBA` set to `0x40000`.

### Control Flow
SysV shared-memory attach paths use `SHMLBA` when validating or choosing attach addresses.

### State, Persistence, Dependencies, And Integration
There is no local state. Integration is with generic IPC/shmem address placement and MIPS cache-alias avoidance.

### Risks
Lowering the alignment can reintroduce virtual cache alias corruption; raising it can break userspace layout assumptions or waste address space.

### Test Signals
Run SysV shared-memory attach tests, especially with VIPT aliasing-cache CPUs, and verify userspace receives properly aligned mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_int.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_int.h

### Purpose
`bcm1480_int.h` defines Broadcom/SiByte BCM1480 interrupt mapper source numbers, 128-bit high/low register layout, masks, CPU interrupt pin mappings, HyperTransport/LDT interrupt message fields, and vector prefixes.

### Important APIs, Types, And Functions
Important constants include `K_BCM1480_INT_SOURCES`, `_BCM1480_INT_HIGH`, `_BCM1480_INT_LOW`, source IDs for GPIO, PCI, cycle counters, timers, DMA channels, MACs, PMI/PMO, mailboxes, ECC, IO bus, perf/trace, watchdogs, HyperTransport/LDT, SMBus, PCMCIA, UARTs, and GPIO 4-15. Mask helpers include `_BCM1480_INT_MASK`, `_BCM1480_INT_MASK1`, `_BCM1480_INT_OFFSET`, `M_BCM1480_INT_*`, mapper targets `K_BCM1480_INT_MAP_*`, HT fields `S_/M_/V_/G_BCM1480_INT_HT_*`, HT message constants, and vector prefixes `M_BCM1480_HTVECT_*`.

### Control Flow
Interrupt-controller code uses source numbers to select high or low 64-bit registers, computes masks, maps sources to processor pins or special NMI/debug targets, and programs HT/LDT message fields for external interrupt delivery.

### State, Persistence, Dependencies, And Integration
State is BCM1480 interrupt mapper MMIO, 128-bit logical interrupt registers split across high/low addresses, CPU interrupt pins, mailbox state, and HT/LDT message routing. Dependency is `sb1250_defs.h` for bitfield helpers. Integration is with SiByte platform IRQ chips, PCI/HT, timers, MAC/UART/SMBus drivers, perf counters, watchdogs, and SMP/IPI style events.

### Risks
The low 64-bit register is offset unusually from the high register, and bit 0 high can summarize low bits; wrong offset math masks the wrong interrupts. Source numbers are SoC-specific despite similar families. HT field encodings must match external bridge/APIC expectations.

### Test Signals
Boot BCM1480-family platforms, validate all enabled IRQ sources, test timer/UART/MAC/PCI/HT interrupts, mailbox delivery, ECC/error interrupts, high/low mask writes, and interrupt affinity/pin mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_l2c.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_l2c.h

### Purpose
`bcm1480_l2c.h` defines Broadcom/SiByte BCM1480 level-2 cache management address, tag, ECC, way, valid/dirty, and miscellaneous way-allocation/cache-disable bit fields.

### Important APIs, Types, And Functions
Important macros include `S_/M_/V_/G_BCM1480_L2C_MGMT_INDEX`, `S_/M_/V_/G_BCM1480_L2C_MGMT_WAY`, management dirty/valid/ECC bits, `A_BCM1480_L2C_MGMT_TAG_BASE`, `BCM1480_L2C_ENTRIES_PER_WAY`, `BCM1480_L2C_NUM_WAYS`, tag fields for MBZ/index/tag/ECC/way/dirty/valid/data ECC, and misc fields for remote/local/enabled ways, cache disable/quad state, MC priority, ECC cleanup, and agent way allocation.

### Control Flow
L2 cache management code builds management/tag addresses and masks from index and way values, reads tag/ECC/status fields, and interprets or updates miscellaneous allocation controls.

### State, Persistence, Dependencies, And Integration
State is L2 cache tag/data/ECC state and L2 controller configuration registers; it is volatile hardware state. Dependency is `sb1250_defs.h` for standard mask/value/extract macros. Integration is with SiByte cache initialization, diagnostics, ECC handling, performance tuning, and memory-controller interaction.

### Risks
Index/way bit shifts must match the BCM1480 spec. Accidentally writing diagnostic/tag-management addresses can alter cache validity or dirty state. ECC cleanup and cache-disable fields are low-level hardware controls with platform-wide impact.

### Test Signals
Build SiByte cache code, run boot-time L2 detection, cache stress and ECC diagnostics, verify way counts/index ranges, and test any management operations on hardware or a faithful simulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_l2c.h -->
