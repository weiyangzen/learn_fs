# subset-b-000699 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/cache.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/cache.c

### Purpose
`cache.c` initializes LoongArch cache metadata, installs the cache-error exception vector, provides a full-cache flush path, and defines the architecture VM protection map used by generic `mmap` and fault code. It is architecture support for the imported Ceph client kernel tree; Ceph depends on it indirectly through page cache, networking, DMA, and executable mapping correctness.

### Important APIs, Types, And Functions
Key functions are `cache_error_setup()`, `flush_cache_leaf()`, `__flush_cache_all()`, and `cpu_cache_init()`. The `populate_cache_properties()` macro decodes `LOONGARCH_CPUCFG16/17+leaf` into `struct cache_desc` fields: level, type, flags, ways, sets, and line size. `protection_map[16]` and `DECLARE_VM_GET_PAGE_PROT` provide page protections for `VM_READ`, `VM_WRITE`, `VM_EXEC`, and `VM_SHARED` combinations.

### Control Flow
Boot calls `cpu_cache_init()`, reads CPU configuration, enumerates L1 instruction/unified and data caches, then shifts through higher-level cache fields. It sets `CACHE_PRIVATE`, `CACHE_INCLUSIVE`, `CACHE_PRESENT`, and `LOONGARCH_CPU_PREFETCH`. `__flush_cache_all()` either flushes the last inclusive cache leaf or all present leaves. `flush_cache_leaf()` walks sets and ways over DMW0 addresses, repeating for all NUMA nodes unless the leaf is private.

### State, Persistence, And Dependencies
Persistent state is CPU-local kernel metadata in `current_cpu_data.cache_leaves`, `cache_leaves_present`, and `options`; there is no filesystem persistence. Dependencies include `asm/cpu.h`, `asm/cpu-features.h`, `asm/cacheflush.h`, LoongArch CPU config registers, NUMA node count, DMW address layout, and generic `cacheinfo`/MM protection machinery.

### Integration Points
`__flush_cache_all()` is used by suspend/resume assembly and other low-level maintenance paths. `cpu_cache_init()` feeds cacheinfo and PCI cache-line sizing. `protection_map` integrates with generic VM code so user mappings receive LoongArch PTE bits such as `_CACHE_CC`, `_PAGE_VALID`, `_PAGE_WRITE`, `_PAGE_NO_EXEC`, and `_PAGE_NO_READ`.

### Risks
Wrong CPUCFG bit decoding can report invalid cache topology or flush too little memory. Inclusive-cache assumptions are performance and correctness sensitive. The protection map is security-critical: incorrect read/write/execute or present/protnone bits can cause privilege, fault, or W^X regressions.

### Test Signals
Cross-build LoongArch configs, boot with cacheinfo enabled, compare reported cache topology with hardware, run cache alias/DMA stress, suspend/resume cache-coherency tests, and MM tests covering executable, writable, shared, and protnone mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/extable.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/extable.c

### Purpose
`extable.c` implements LoongArch exception-table fixups for kernel faults, including ordinary fixup jumps, uaccess error/zero fixups, and BPF JIT fixups.

### Important APIs, Types, And Functions
The exported runtime API is `fixup_exception(struct pt_regs *regs)`. Helpers include `get_ex_fixup()`, `regs_set_gpr()`, `ex_handler_fixup()`, and `ex_handler_uaccess_err_zero()`. It consumes `struct exception_table_entry` fields `insn`, `fixup`, `type`, and `data`, plus `EX_TYPE_FIXUP`, `EX_TYPE_UACCESS_ERR_ZERO`, and `EX_TYPE_BPF`.

### Control Flow
On a kernel exception, `fixup_exception()` searches exception tables using `exception_era(regs)`. A normal fixup sets `regs->csr_era` to the relative fixup target. A uaccess fixup extracts error and zero register numbers from `ex->data`, writes `-EFAULT` and `0` into those saved GPR slots, then redirects execution. BPF entries delegate to `ex_handler_bpf()`.

### State, Persistence, And Dependencies
State changes are limited to the interrupted `pt_regs`; no persistent storage exists. Dependencies include generic exception-table search, LoongArch saved-register layout, bitfield helpers, uaccess error conventions, and `asm/asm-extable.h` type/data encoding.

### Integration Points
Fault handling calls this through `no_context()` in `fault.c`. BPF probe-memory loads and stores add extable entries in `net/bpf_jit.c`, and those entries are resolved here via `EX_TYPE_BPF`.

### Risks
Register-offset encoding must match `struct pt_regs`; otherwise fault recovery corrupts state. Relative fixup calculations must stay in range and compatible with sorted exception tables. Unknown types hit `BUG()`, so type drift between assembler/JIT emitters and this dispatcher is fatal.

### Test Signals
Run uaccess fault tests, BPF probe-memory selftests, kernel fault-injection around copy helpers, and cross-build checks for exception-table encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/fault.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/fault.c

### Purpose
`fault.c` is the LoongArch page-fault handler. It classifies user and kernel faults, validates VMA permissions, calls the generic memory-fault engine, reports signals, and falls back to exception fixups or kernel oops paths.

### Important APIs, Types, And Functions
Public state/API includes `show_unhandled_signals` and `do_page_fault(struct pt_regs *, unsigned long write, unsigned long address)`. Internal handlers are `spurious_fault()`, `no_context()`, `do_out_of_memory()`, `do_sigbus()`, `do_sigsegv()`, and `__do_page_fault()`. It uses `vm_fault_t`, `FAULT_FLAG_*`, `VM_FAULT_*`, `lock_vma_under_rcu()`, `lock_mm_and_find_vma()`, and `handle_mm_fault()`.

### Control Flow
`do_page_fault()` enters irqentry state, conditionally enables interrupts based on parent CSR state, then invokes `__do_page_fault()`. The core handler first lets kprobes consume the fault, rejects kernel-space/user-limit violations, and avoids taking mmap locks when fault handling is disabled or no `mm` exists. For user faults it tries the RCU VMA-lock fast path, validates write/read/exec access, calls `handle_mm_fault()`, then retries under the mmap lock if needed. Fault errors map to OOM, SIGSEGV, SIGBUS, or BUG. Kernel faults try spurious TLB acceptance, exception-table fixups, KFENCE handling, then oops.

### State, Persistence, And Dependencies
State mutations include `current->thread.csr_badvaddr`, `thread.error_code`, `thread.trap_nr`, perf software counters, VMA lock accounting, page tables through generic MM, and signal delivery. Dependencies include LoongArch CSR exception state, `asm/branch.h`, `asm/mmu_context.h`, generic MM fault code, KFENCE, kprobes, perf, context tracking, and signal APIs.

### Integration Points
The assembly TLB handlers in `tlbex.S` tail-call this for missing/protection faults. `extable.c` supplies kernel fault recovery. Generic memory management resolves demand paging, COW, file-backed page cache faults, and hugepage-related faults. For distributed filesystem behavior, this is the path by which Ceph client file mappings fault pages into user processes.

### Risks
The permission checks distinguish instruction fetches by comparing `address == exception_era(regs)`; errors can allow wrong execute/read behavior or produce incorrect SIGSEGV codes. Lockless VMA handling must release locks on all exits. Kernel-space `__UA_LIMIT` decisions and interrupt-state handling are architecture-critical.

### Test Signals
Run mmap/read/write/exec fault tests, signal-delivery tests, kprobe/KFENCE fault injection, page-fault stress under signals, Ceph/file-backed mmap tests, and LoongArch TLB miss/protection validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/highmem.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/highmem.c

### Purpose
`highmem.c` provides the LoongArch highmem kmap TLB flush hook.

### Important APIs, Types, And Functions
The single exported function is `kmap_flush_tlb(unsigned long addr)`, exported with `EXPORT_SYMBOL`.

### Control Flow
Callers pass a virtual address whose highmem mapping changed. The function delegates directly to `flush_tlb_one(addr)`.

### State, Persistence, And Dependencies
It has no local persistent state. It depends on generic highmem/kmap users, `asm/fixmap.h`, and LoongArch `flush_tlb_one()`.

### Integration Points
Highmem kmap code uses this after changing temporary or permanent kernel mappings so stale TLB entries do not outlive a remap. It complements `fixrange_init()` and `pkmap_page_table` setup in `init.c`/`pgtable.c`.

### Risks
Insufficient flushing can expose stale highmem translations. Excessive flushing can hurt kmap-heavy I/O paths.

### Test Signals
Build with `CONFIG_HIGHMEM`, run highmem kmap stress, filesystem I/O on highmem pages, and TLB shootdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/highmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/hugetlbpage.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/hugetlbpage.c

### Purpose
`hugetlbpage.c` supplies LoongArch hugepage page-table helpers and converts huge PMD encodings into TLB entrylo values.

### Important APIs, Types, And Functions
Functions are `huge_pte_alloc()`, `huge_pte_offset()`, and `pmd_to_entrylo()`. They operate on `struct mm_struct`, `struct vm_area_struct`, PGD/P4D/PUD/PMD levels, huge PMD bits, `_PAGE_HUGE`, `_PAGE_HGLOBAL`, and `_PAGE_GLOBAL`.

### Control Flow
Allocation walks PGD to PUD and allocates lower directories until it can return a PMD treated as `pte_t *`. Lookup follows only present levels and returns `NULL` for missing PMDs. `pmd_to_entrylo()` verifies the PMD is a leaf huge entry, clears the huge bit by xor, and maps the huge global bit into the normal TLB global bit.

### State, Persistence, And Dependencies
State is page-table memory in the target `mm`; no filesystem persistence exists. Dependencies include generic hugetlb, LoongArch PTE bit definitions, and TLB update code in `tlb.c`/`tlbex.S`.

### Integration Points
Generic hugetlb code calls allocation/lookup helpers. `tlb.c` and `tlbex.S` use `pmd_to_entrylo()` semantics when inserting hugepage TLB entries.

### Risks
Treating PMDs as PTEs is layout-sensitive. Incorrect huge/global bit conversion can create invalid TLB entries or wrong global sharing across ASIDs. The `panic()` on non-leaf PMDs is intentionally fatal.

### Test Signals
Run hugetlb mmap, fork, COW, unmap, and TLB invalidation tests; verify hugepage entrylo values under debug; cross-build with and without `CONFIG_HUGETLB_PAGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/init.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/init.c

### Purpose
`init.c` owns early LoongArch memory-management setup: zone limits, initmem freeing, highmem fixed ranges, memory hotplug hooks, vmemmap population, fixmap PTE creation, global invalid page-table roots, and executable memory range setup.

### Important APIs, Types, And Functions
Key functions include `page_is_ram()`, `arch_zone_limits_init()`, `free_initmem()`, `fixrange_init()`, `arch_add_memory()`, `arch_remove_memory()`, `vmemmap_set_pmd()`, `vmemmap_check_pmd()`, `vmemmap_populate()`, `populate_kernel_pte()`, `__set_fixmap()`, and `execmem_arch_setup()`. Global tables include `swapper_pg_dir`, `invalid_pg_dir`, optional `invalid_pud_table`, optional `invalid_pmd_table`, and `invalid_pte_table`.

### Control Flow
Boot sets zone PFN limits for DMA32, normal, and highmem. Highmem builds PTE pages for pkmap and fixmap virtual ranges. Sparse vmemmap uses huge PMDs when possible. `populate_kernel_pte()` allocates missing P4D/PUD/PMD/PTE pages from memblock, initializes folded levels as needed, and returns the target PTE. `__set_fixmap()` writes or clears a fixed-address PTE and flushes on clear. Execmem setup describes the module range as executable allocation space.

### State, Persistence, And Dependencies
Persistent kernel state is early page-table memory, memblock reservations, zone PFN limits, vmemmap mappings, fixmap mappings, and exported invalid page-table tables. Dependencies include memblock, sparsemem/vmemmap, memory hotplug, highmem, hugetlb, execmem, LoongArch page-table allocators, and TLB flush APIs.

### Integration Points
`pgtable.c` initializes these tables; `kasan_init.c` temporarily switches page-directory roots; fixmap users include early ioremap, APIC/firmware mappings, and highmem. Memory hotplug calls `arch_add_memory()`/`arch_remove_memory()`.

### Risks
Memblock allocation failures panic during early boot. Incorrect invalid table initialization can make page-table walkers treat empty levels as present. Fixmap replacement checks reject non-empty PTEs; misuse can leave stale mappings. Hotplug removal currently delegates to generic removal and empty vmemmap free under vmemmap hotplug.

### Test Signals
Boot matrix across page-table levels, highmem, sparsemem, memory hotplug, and KASAN; run fixmap users, memory add/remove tests, vmemmap verification, and module allocation/execution tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/ioremap.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/ioremap.c

### Purpose
`ioremap.c` implements early LoongArch ioremap/memremap helpers used before full virtual-memory services are available.

### Important APIs, Types, And Functions
Functions are `early_ioremap()`, `early_iounmap()`, `early_memremap_ro()`, and `early_memremap_prot()`.

### Control Flow
`early_ioremap()` returns a cached direct-map address via `TO_CACHE(phys_addr)`. `early_iounmap()` is a no-op. Read-only and protected early memremap variants defer to generic `early_memremap()` and ignore the requested protection value.

### State, Persistence, And Dependencies
There is no local mapping allocator or persistent state. Dependencies are LoongArch direct-map address conversion and generic early ioremap declarations.

### Integration Points
Early firmware/ACPI/device discovery code can use these helpers before normal `ioremap()` is ready. Later PCI ACPI code uses normal remap paths.

### Risks
Returning cached mappings for I/O regions can be wrong for device registers unless callers only use memory-like firmware data at this phase. Ignoring protection in `early_memremap_prot()` may surprise callers expecting uncached or read-only semantics.

### Test Signals
Boot with ACPI/firmware table parsing, early console/device discovery, and debug checks for early I/O accesses on LoongArch platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/kasan_init.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/kasan_init.c

### Purpose
`kasan_init.c` builds LoongArch KASAN shadow-memory mappings for direct-map, vmalloc/KFENCE, and module ranges, and translates between memory and shadow addresses for multiple LoongArch virtual ranges.

### Important APIs, Types, And Functions
Important functions are `kasan_mem_to_shadow()`, `kasan_shadow_to_mem()`, `kasan_early_init()`, and `kasan_init()`. Internal helpers allocate and populate PGD/P4D/PUD/PMD/PTE levels: `kasan_alloc_zeroed_page()`, `kasan_*_offset()`, `kasan_*_populate()`, `kasan_map_populate()`, and `clear_pgds()`. Static state includes `kasan_pg_dir`.

### Control Flow
Early init checks PGDIR alignment. Full init verifies `KASAN_SHADOW_END` is usable for current VA bits, copies `swapper_pg_dir` into a temporary KASAN PGD, installs it in `LOONGARCH_CSR_PGDH`, clears existing KASAN PGDs, maps the full shadow to the early zero page, populates vmalloc/KFENCE shadow, populates shadow for every memblock memory range and module range, converts early shadow PTEs to read-only zero-page mappings, restores `swapper_pg_dir`, flushes TLBs, and enables generic KASAN.

### State, Persistence, And Dependencies
Persistent state is KASAN shadow page-table memory and `init_task.kasan_depth`. It depends on memblock, LoongArch segmented address ranges, `kasan_early_shadow_*` objects, `swapper_pg_dir`, CSR page-directory registers, generic KASAN, and TLB flushes.

### Integration Points
Generic KASAN instrumentation calls `kasan_mem_to_shadow()` and `kasan_shadow_to_mem()`. `init.c` and `pgtable.c` supply page-table roots and invalid tables. KFENCE and vmalloc ranges are shadowed during init.

### Risks
Shadow-offset math is architecture-specific and can warn/return `NULL` for unsupported ranges. Misdetecting folded page-table levels can reuse early shadow tables incorrectly. Temporarily switching `PGDH` and clearing PGDs must be paired with TLB flushes. Systems with too-small VA bits intentionally disable KASAN.

### Test Signals
Boot LoongArch KASAN configs across page-table levels and VA widths, run KASAN selftests, vmalloc/KFENCE/module shadow tests, and early boot memory-allocation fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/kasan_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/maccess.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/maccess.c

### Purpose
`maccess.c` defines the architecture policy for nofault kernel memory reads.

### Important APIs, Types, And Functions
The only function is `copy_from_kernel_nofault_allowed(const void *unsafe_src, size_t size)`.

### Control Flow
The helper returns true only when the source pointer has its highest address bit set, treating that as kernel space. The `size` argument is not inspected.

### State, Persistence, And Dependencies
No state is stored. It depends on pointer-width constants and the LoongArch virtual address split.

### Integration Points
Generic `copy_from_kernel_nofault()` users call this to reject user-space probes before attempting exception-table-backed kernel reads.

### Risks
The high-bit test must match all kernel address ranges on supported LoongArch modes. Ignoring size means overflow/range-end validation is left to the caller or fault path.

### Test Signals
Run nofault access tests for direct-map, vmalloc/module, invalid kernel, and user addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/maccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/mmap.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/mmap.c

### Purpose
`mmap.c` implements LoongArch unmapped-area selection, address validity checks, and `/dev/mem` physical-range validation.

### Important APIs, Types, And Functions
Key functions are `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `__virt_addr_valid()`, `valid_phys_addr_range()`, and `valid_mmap_phys_addr_range()`. Internal `arch_get_unmapped_area_common()` uses `struct vm_unmapped_area_info` and cache-color alignment macros.

### Control Flow
For `MAP_FIXED`, the code validates the range is below `TASK_SIZE` and rejects shared mappings whose address/pgoff violates `SHMLBA` coloring. Non-fixed requests align requested hints, check for a gap via `find_vma()`, then call `vm_unmapped_area()` bottom-up or top-down. Top-down failures fall back to bottom-up. `__virt_addr_valid()` accepts KFENCE addresses, rejects non-direct-map and vmalloc-range addresses, then checks `pfn_valid()`. Physical range checks use memblock coverage and CPU physical address width.

### State, Persistence, And Dependencies
It does not persist data; it reads `current->mm`, VMA layout, memblock, CPU physical address bits, and KFENCE state. Dependencies include generic mmap, hugepage alignment, memblock, and LoongArch address conversion.

### Integration Points
Generic `mmap()` and shared-memory code call the unmapped-area hooks. `/dev/mem` read/mmap paths use the physical-range validators. `virt_addr_valid()` users rely on `__virt_addr_valid()`.

### Risks
Cache coloring alignment affects shared mappings and ABI compatibility. Top-down fallback limits must avoid collisions with stack and mmap base. Physical range width checks must handle overflow correctly.

### Test Signals
Run mmap layout tests, SysV shared-memory alignment tests, hugetlb mmap tests, `/dev/mem` policy tests, and KFENCE/direct-map address validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/page.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/page.S

### Purpose
`page.S` provides optimized LoongArch assembly implementations of page clearing and page copying.

### Important APIs, Types, And Functions
Exports are `clear_page` and `copy_page`, both declared with `SYM_FUNC_*` and exported via `EXPORT_SYMBOL`.

### Control Flow
`clear_page` computes the end address for one page and loops, storing zero to 16 word-sized slots per iteration. `copy_page` computes the destination end, loads 16 word-sized values from the source, stores them to the destination with interleaving, advances both pointers, and repeats until one page is copied.

### State, Persistence, And Dependencies
State is only registers and the target memory page. Dependencies include LoongArch register definitions, `PAGE_SHIFT`, `LONGSIZE`, and calling conventions.

### Integration Points
Generic MM uses these for zeroing newly allocated pages and copying COW or forked pages, including page cache pages used by filesystems.

### Risks
The loops assume page-sized, aligned buffers and must preserve ABI registers correctly. Any off-by-one or register clobber corrupts memory broadly.

### Test Signals
Run boot memory tests, fork/COW stress, page allocator poisoning checks, KASAN/KMSAN where available, and compare disassembly for 32/64-bit configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/pageattr.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/pageattr.c

### Purpose
`pageattr.c` changes kernel mapping attributes such as execute, read-only/read-write, and direct-map valid/default state.

### Important APIs, Types, And Functions
Public functions are `set_memory_x()`, `set_memory_nx()`, `set_memory_ro()`, `set_memory_rw()`, `kernel_page_present()`, `set_direct_map_default_noflush()`, `set_direct_map_invalid_noflush()`, and `set_direct_map_valid_noflush()`. Internal pieces are `struct pageattr_masks`, `set_pageattr_masks()`, page-table walk callbacks for all levels, and `__set_memory()`.

### Control Flow
`__set_memory()` builds set/clear masks, locks `init_mm` for write, walks the kernel page-table range, updates leaf entries at any level or PTEs, unlocks, and flushes the kernel TLB range. Attribute helpers skip addresses below `vm_map_base`. `kernel_page_present()` manually walks the direct or vmapped page tables and treats leaf entries as present.

### State, Persistence, And Dependencies
State is kernel page-table entries and TLB state; no filesystem persistence. Dependencies include generic pagewalk, memblock, `init_mm`, LoongArch PTE bits, and TLB flush APIs.

### Integration Points
Module/JIT/text permission changes, rodata protection, memory hotplug, and direct-map hardening use these hooks. BPF JIT finalization indirectly relies on executable text mappings and I-cache flushing.

### Risks
The `set_direct_map_valid_noflush()` `nr` argument is ignored and only one page is changed, which is a notable review point if callers expect multi-page behavior. Leaf-level updates must preserve unrelated PTE bits. Skipping low direct-map addresses below `vm_map_base` may be intentional but limits hardening.

### Test Signals
Run LKDTM ro/rw/nx tests, module load/unload, BPF JIT execution, direct-map invalidation tests, and page-table walk debug checks for huge mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/pageattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/pgtable.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/pgtable.c

### Purpose
`pgtable.c` provides LoongArch page-table allocation, initialization, virtual-to-page helpers, PMD update flushing, and early page-table setup.

### Important APIs, Types, And Functions
Functions include `dmw_virt_to_page()`, `tlb_virt_to_page()`, `pgd_alloc()`, `pgd_init()`, optional `pmd_init()`, optional `pud_init()`, `kernel_pte_init()`, `set_pmd_at()`, and `pagetable_init()`.

### Control Flow
`pgd_alloc()` allocates a user PGD, initializes all entries to invalid tables, then copies kernel entries from `init_mm` above `USER_PTRS_PER_PGD`. Table init functions fill entries with the appropriate invalid next-level table or `_PAGE_GLOBAL`. `set_pmd_at()` writes the PMD and flushes all TLBs. `pagetable_init()` initializes swapper/invalid tables and, under highmem, allocates pkmap/fixmap PTE ranges and records `pkmap_page_table`.

### State, Persistence, And Dependencies
Persistent state is page-table memory, invalid-table globals from `init.c`, and highmem pkmap metadata. Dependencies include LoongArch folded page-table configuration, `asm/pgalloc.h`, `asm/fixmap.h`, and TLB flushes.

### Integration Points
Generic MM calls `pgd_alloc()` for new processes. `init.c` allocates kernel PTEs and owns invalid table storage. TLB handlers depend on these table layouts and invalid pointers.

### Risks
Invalid table pointers must be valid kernel virtual addresses and match folded-level configuration. `set_pmd_at()` flushes globally, which is safe but costly. Copying kernel PGD entries must avoid leaking user-space entries.

### Test Signals
Boot across page-table levels, fork/exec stress, highmem/fixmap tests, page-table debug checks, and TLB handler validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/pgtable.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/tlbex.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/tlbex.S

### Purpose
`tlbex.S` contains the low-level LoongArch TLB load, store, modify, protect, PTW fallback, and refill exception handlers.

### Important APIs, Types, And Functions
Symbols include generated `tlb_do_page_fault_0`, `tlb_do_page_fault_1`, `handle_tlb_protect`, `handle_tlb_load`, `handle_tlb_load_ptw`, `handle_tlb_store`, `handle_tlb_store_ptw`, `handle_tlb_modify`, `handle_tlb_modify_ptw`, and 32/64-bit `handle_tlb_refill`. It uses `_PAGE_PRESENT`, `_PAGE_VALID`, `_PAGE_WRITE`, `_PAGE_DIRTY`, `_PAGE_MODIFIED`, `_PAGE_HUGE`, and LoongArch CSR/TLB instructions.

### Control Flow
Load/store/modify handlers save scratch registers, read the fault address, select user `PGDL` or kernel `swapper_pg_dir`, walk page-table levels in assembly, detect huge PMD entries, update PTE valid/dirty/modified bits atomically under SMP using LL/SC, and write paired TLB entrylo values. Missing permissions branch to `tlb_do_page_fault_*`, which saves full regs and calls `do_page_fault()`. Hugepage paths invalidate the ASID/address, synthesize huge entrylo0/1, set huge page size, fill TLB, and restore default size. Refill handlers use either explicit 32-bit walks or 64-bit `lddir`/`ldpte`.

### State, Persistence, And Dependencies
State is CPU registers, CSRs, TLB entries, and page-table PTE bits. Dependencies include saved-register layout, page-table shift constants, LoongArch instruction macros, `do_page_fault()`, `swapper_pg_dir`, and SMP atomic primitives.

### Integration Points
`tlb.c` installs these symbols into exception vectors. `fault.c` handles slow paths. `hugetlbpage.c` and PTE bit definitions must match hugepage entry encoding here.

### Risks
This is extremely layout-sensitive assembly. Branch offsets, LL/SC loops, paired PTE alignment, CSR page-size restoration, and hugepage global-bit conversion are all correctness-critical. A bug can manifest as silent memory corruption, infinite faults, or privilege boundary failures.

### Test Signals
Boot under software refill and hardware PTW configs, run page-fault stress, dirty/accessed-bit tests, SMP mmap/write races, hugepage tests, and instruction-level disassembly review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/tlbex.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/Makefile -->
## sources/distributed-fs/ceph-client/arch/loongarch/net/Makefile

### Purpose
This Makefile selects LoongArch networking architecture support objects.

### Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_BPF_JIT) += bpf_jit.o`.

### Control Flow
Kbuild includes `bpf_jit.o` only when `CONFIG_BPF_JIT` is enabled.

### State, Persistence, And Dependencies
No runtime state exists. It depends on kernel Kbuild and the `CONFIG_BPF_JIT` option.

### Integration Points
Controls whether `arch/loongarch/net/bpf_jit.c` participates in the kernel build.

### Risks
Incorrect gating would either omit JIT support when enabled or build it into unsupported configs.

### Test Signals
Cross-build LoongArch with `CONFIG_BPF_JIT=y/m/n` as applicable and verify no unresolved BPF architecture symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.c

### Purpose
`bpf_jit.c` is the LoongArch eBPF JIT backend. It translates BPF instructions into LoongArch machine code, handles BPF text patching and invalidation, emits BPF trampoline code, supports kfuncs/arenas/fsession/subprog tailcalls, and frees JIT images.

### Important APIs, Types, And Functions
Major public functions are `bpf_jit_supports_kfunc_call()`, `bpf_jit_supports_far_kfunc_call()`, `ex_handler_bpf()`, `bpf_arch_text_copy()`, `bpf_arch_text_poke()`, `bpf_arch_text_invalidate()`, `arch_alloc_bpf_trampoline()`, `arch_free_bpf_trampoline()`, `arch_protect_bpf_trampoline()`, `arch_prepare_bpf_trampoline()`, `arch_bpf_trampoline_size()`, `bpf_int_jit_compile()`, `bpf_jit_free()`, and support booleans for speculation bypass, arenas, fsession, and subprog tailcalls. Core internals are `build_prologue()`, `build_body()`, `build_insn()`, `build_epilogue()`, `emit_bpf_tail_call()`, atomic emitters, exception handler creation, text patch helpers, and trampoline invocation helpers.

### Control Flow
`bpf_int_jit_compile()` exits if JIT was not requested, then performs a sizing pass with `ctx.image == NULL`, allocates RW/RO packed BPF binary memory plus extable space, emits real instructions, validates no `INSN_BREAK` holes remain and extable counts match, finalizes ROX text, flushes I-cache, fills line info, and handles subprogram extra passes through `prog->aux->jit_data`. `build_insn()` translates arithmetic, moves, endian swaps, branches, calls, tail calls, loads/stores, atomics, probe-memory modes, arena-relative access, and exits. Trampoline preparation computes a stack frame for saved args, return values, metadata, cookies, run context, tail-call context, and stack args; it emits fentry/fmod_ret/fexit/original-call flow and patches reserved conditional branches after targets are known.

### State, Persistence, And Dependencies
Persistent runtime state includes generated executable BPF images, optional extable entries in `prog->aux->extable`, `prog->jited`, `prog->jited_len`, `prog->bpf_func`, trampoline images, and temporary `jit_data` across subprogram passes. Dependencies include generic BPF verifier/JIT APIs, BTF kfunc models, BPF trampoline/session-cookie infrastructure, LoongArch instruction encoders from `asm/inst.h`, text patching via `larch_insn_text_copy()`, cache flushing, `text_mutex`, CPU hotplug read locks, and exception handling in `mm/extable.c`.

### Integration Points
The Makefile gates this file under `CONFIG_BPF_JIT`. Probe-memory extable entries are dispatched by `fixup_exception()`. BPF program pack allocation and kallsyms integrate with generic BPF. Text poking supports fentry/fexit, calls, and BPF program entry patching. Atomic instructions depend on LoongArch CPU features such as `cpu_has_lam_bh`.

### Risks
JIT correctness is security-critical. Branch offsets are limited to signed 26-bit or 16-bit tail-call branches and return `-E2BIG`/`-EINVAL` when too far. Register mapping and ABI extension must match BPF and LoongArch calling conventions. Probe-memory extable offsets use RO/RW image address translation and range checks. Text patching must compare old instructions exactly to avoid racing wrong code. Atomic byte/halfword operations require hardware support. Trampoline frame layout is complex and flag-dependent.

### Test Signals
Run `test_bpf`, BPF selftests, verifier/JIT differential tests, tail-call and bpf2bpf tests, kfunc/trampoline/fentry/fexit/fmod_ret/fsession tests, arena/probe-memory tests, atomic instruction tests on CPUs with and without LAM_BH, text-poke stress, and JIT hardening/constant blinding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.h -->
## sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.h

### Purpose
`bpf_jit.h` defines the shared LoongArch BPF JIT context and instruction-emission helpers used by `bpf_jit.c`.

### Important APIs, Types, And Functions
Types are `struct jit_ctx` and `struct jit_data`. Emission helpers include `emit_insn`, `emit_nop()`, immediate-range macros, `bpf2la_offset()`, `epilogue_offset()`, zero/sign extension helpers, `emit_abi_ext()`, `move_addr()`, `move_imm()`, `move_reg()`, `invert_jmp_cond()`, `cond_jmp_offset()`, `emit_cond_jmp()`, `emit_uncond_jmp()`, `emit_tailcall_jmp()`, and `bpf_flush_icache()`.

### Control Flow
Most helpers are inline. During sizing passes `emit_insn` only increments `ctx->idx`; during emission it writes a LoongArch instruction word then increments. Branch helpers convert BPF relative offsets into LoongArch instruction offsets and use inverted conditional branch plus unconditional branch for 26-bit conditional jumps.

### State, Persistence, And Dependencies
State lives in `jit_ctx`: current program, instruction index, offsets, image/ro_image pointers, extable count, stack size, and BPF arena address bases. Dependencies include generic BPF headers, LoongArch instruction encoders, cache flushing, and bitfield helpers.

### Integration Points
`bpf_jit.c` includes this header for every emission path. Extable and arena fields connect instruction generation with runtime fault recovery and BPF arena addressing.

### Risks
Immediate-range checks and branch offset conversions must be exact; JIT passes rely on deterministic `ctx->idx` increments. `move_imm()` chooses variable-length sequences that affect branch offsets, so sizing and emission must remain identical.

### Test Signals
Build with JIT enabled, run BPF JIT selftests with long programs/branches, inspect emitted instruction sequences, and validate I-cache flushes after finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/net/bpf_jit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/Makefile -->
## sources/distributed-fs/ceph-client/arch/loongarch/pci/Makefile

### Purpose
This Makefile selects LoongArch PCI architecture support objects.

### Important APIs, Types, And Functions
Rules are `obj-y += pci.o` and `obj-$(CONFIG_ACPI) += acpi.o`.

### Control Flow
`pci.o` is always built for this directory; ACPI PCI root scanning support is conditional on `CONFIG_ACPI`.

### State, Persistence, And Dependencies
No runtime state exists. Dependencies are Kbuild and `CONFIG_ACPI`.

### Integration Points
Controls inclusion of generic PCI hooks and ACPI ECAM/root-bridge support.

### Risks
Wrong object selection can break PCI enumeration or introduce ACPI dependencies into non-ACPI builds.

### Test Signals
Cross-build LoongArch PCI configs with and without ACPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/acpi.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/pci/acpi.c

### Purpose
`acpi.c` implements LoongArch ACPI PCI root scanning, ECAM config-window setup, resource preparation, NUMA node assignment, and root-info cleanup.

### Important APIs, Types, And Functions
It defines `struct pci_root_info` and functions `pcibios_add_bus()`, `pcibios_root_bridge_prepare()`, `acpi_pci_bus_find_domain_nr()`, `pci_acpi_scan_root()`, plus helpers `acpi_release_root_info()`, `acpi_prepare_root_resources()`, `arch_pci_ecam_create()`, and `pci_acpi_setup_ecam_mapping()`.

### Control Flow
Root scan allocates `pci_root_info` and ops, maps ECAM from MCFG or Loongson defaults, assigns release/resource/pci ops, reuses an existing bus if found or creates one through `acpi_pci_root_create()`, claims/preserves resources when requested, assigns unassigned resources, and configures child bus settings. Resource prep probes ACPI windows and, when the `PCIH` method is absent, extends memory resources with high address bits from `mcfg_addr`. Custom ECAM creation reserves iomem, maps config space, calls ops init, and cleans up on conflicts/errors.

### State, Persistence, And Dependencies
State includes allocated root info, ECAM mappings, iomem resource reservations, PCI bus `sysdata`, ACPI companions, NUMA node assignment, and resource lists. Dependencies include ACPI PCI root support, PCI ECAM ops, Loongson default ECAM ops/addressing, NUMA `pa_to_nid()`, and generic PCI resource assignment.

### Integration Points
Generic ACPI PCI calls `pci_acpi_scan_root()`. `pci.c` supplies `mcfg_addr_init()` and default Loongson PCI behavior. Device drivers rely on resulting PCI buses, resources, IRQ/MSI domains, and config-space ops.

### Risks
MCFG fallback address construction and nonstandard `bus_shift` handling are platform-sensitive. Resource high-bit adjustment can produce wrong host windows if ACPI firmware methods are misread. Cleanup must free ops and ECAM mappings on all failure paths.

### Test Signals
Boot ACPI LoongArch systems with standard/nonstandard MCFG, enumerate PCIe devices, inspect `/proc/iomem`, run hotplug/resource reassignment tests, and validate NUMA node placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/pci.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/pci/pci.c

### Purpose
`pci.c` implements LoongArch generic PCI hooks, default ECAM address construction, cache-line sizing, MSI/IRQ setup, VGA fixups, and Loongson GPU DMA-hang workarounds.

### Important APIs, Types, And Functions
Functions are `raw_pci_read()`, `raw_pci_write()`, `mcfg_addr_init()`, `pcibios_device_add()`, `pcibios_alloc_irq()`, and init/fixup helpers. PCI fixups are registered for Loongson display controller and GPU device IDs using `DECLARE_PCI_FIXUP_*`.

### Control Flow
Raw config access looks up a domain/bus and delegates to bus ops. `pcibios_init()` sets `pci_dfl_cache_line_size` from the last-level CPU cache. Device add finds the PCH MSI domain and assigns it. IRQ allocation defers to ACPI unless MSI is enabled. VGA fixup chooses a non-Loongson VGA device as default. GPU DMA-hang fixups map display-controller registers behind the GPU, save CRTC enable state early, disable outputs, then restore outputs at final fixup time with polling.

### State, Persistence, And Dependencies
State includes PCI default cache-line size, per-device MSI domain, VGA default device, static `crtc_status`, temporary ioremaps, and device registers. Dependencies include PCI core, ACPI IRQ code, Loongson PCH MSI lookup, IO accessors, and cacheinfo.

### Integration Points
Called by generic PCI enumeration and fixup infrastructure. `acpi.c` uses `mcfg_addr_init()`. Display/GPU workarounds affect Loongson hardware during PCI probing.

### Risks
Config access returns `-EINVAL` when bus lookup fails. MSI domain lookup can return `NULL` on firmware/domain mismatch. GPU workaround assumes device-function layout and BAR/register offsets; wrong assumptions can write unrelated MMIO.

### Test Signals
Boot PCI/ACPI LoongArch systems, enumerate MSI devices, test legacy INTx fallback, validate VGA arbitration, exercise affected Loongson GPUs, and run PCI config-space access tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/Makefile -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/Makefile

### Purpose
This Makefile selects LoongArch platform power-management objects.

### Important APIs, Types, And Functions
Rules are `obj-y += platform.o`, `obj-$(CONFIG_SUSPEND) += suspend.o suspend_asm.o`, and `obj-$(CONFIG_HIBERNATION) += hibernate.o hibernate_asm.o`.

### Control Flow
Platform support is always built; suspend and hibernation support are conditional on their kernel config options.

### State, Persistence, And Dependencies
No runtime state exists. It depends on Kbuild and PM config symbols.

### Integration Points
Controls whether ACPI S3 and swsusp architecture hooks are available.

### Risks
Incorrect selection can leave unresolved symbols between C and assembly halves of suspend/hibernate.

### Test Signals
Cross-build with suspend and hibernation enabled/disabled independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/hibernate.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/hibernate.c

### Purpose
`hibernate.c` implements LoongArch CPU state save/restore and swsusp architecture hooks for hibernation.

### Important APIs, Types, And Functions
Functions are `save_processor_state()`, `restore_processor_state()`, `pfn_is_nosave()`, `swsusp_arch_suspend()`, and `swsusp_arch_resume()`. State includes saved CRMD/PRMD/EUEN/ECFG CSRs, per-CPU base, and global `struct pt_regs saved_regs` used by assembly.

### Control Flow
Before image creation, CPU state and counters are saved; current FPU state is saved if owned. Resume restores counters, CSRs, per-CPU base, and FPU state. `pfn_is_nosave()` excludes the linker-provided nosave section from the hibernation image. Suspend enables PCI wake and enters `swsusp_asm_suspend()`. Resume flushes all TLBs before `swsusp_asm_resume()`.

### State, Persistence, And Dependencies
State persists across hibernation in static variables and memory image context. Dependencies include LoongArch CSRs, FPU ownership helpers, time counter sync, linker nosave symbols, TLB flushes, PCI wake setup, and assembly routines in `hibernate_asm.S`.

### Integration Points
Generic swsusp calls these arch hooks. `platform.c` provides wake enablement. `hibernate_asm.S` saves/restores callee state and copies restored pages.

### Risks
Missing CSR/FPU/percpu state causes resume instability. Nosave PFN boundaries must match linker script sections. TLB flush before resume is required to avoid stale translations.

### Test Signals
Run hibernate/resume cycles with FPU users, PCI wake devices, memory pressure, and TLB/page-table debug enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/hibernate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/hibernate_asm.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/hibernate_asm.S

### Purpose
`hibernate_asm.S` supplies the low-level swsusp suspend/resume routines that save registers and restore the hibernated memory image.

### Important APIs, Types, And Functions
Symbols are `swsusp_asm_suspend` and `swsusp_asm_resume`. It uses `saved_regs`, `restore_pblist`, `PBE_ADDRESS`, `PBE_ORIG_ADDRESS`, and `PBE_NEXT`.

### Control Flow
Suspend stores return address, thread pointer, stack pointer, selected saved registers, and frame pointer into `saved_regs`, then branches to generic `swsusp_save`. Resume walks the restore page-backup list, copying each saved page from backup to original address word by word, restores saved registers, sets `a0` to zero, and returns through restored `ra`.

### State, Persistence, And Dependencies
State is CPU registers plus the hibernation page backup list. Dependencies include asm offsets, LoongArch ABI register names, and `saved_regs` from `hibernate.c`.

### Integration Points
Called by `swsusp_arch_suspend()` and `swsusp_arch_resume()`. Generic swsusp supplies `swsusp_save` and `restore_pblist`.

### Risks
Register coverage and offsets must match `struct pt_regs`. The copy loop must handle exactly one page per backup entry. Returning with corrupted `sp`/`ra` bricks resume.

### Test Signals
Hibernate/resume tests, objdump review of offsets, memory image restore validation, and stress with large memory images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/hibernate_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/platform.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/platform.c

### Purpose
`platform.c` provides LoongArch platform wake setup, cpufreq platform-device registration, and ACPI S3 suspend target discovery.

### Important APIs, Types, And Functions
Functions are `enable_gpe_wakeup()`, `enable_pci_wakeup()`, `loongson_cpufreq_init()`, `default_suspend_addr()`, and `loongson3_acpi_suspend_init()`. Static state includes `loongson3_cpufreq_device`.

### Control Flow
Wake helpers return early if ACPI is disabled or reduced-hardware mode is active. GPE wake enables all wake GPEs; PCI wake clears wake status and enables PCIe wake if the FADT advertises it. Cpufreq registration runs at arch init only if `cpu_has_scalefreq`. ACPI S3 init enables SCI, checks S3 support, evaluates `\SADR`, and stores either a default ACPI sleep function or the physical-to-virtual SADR target in `loongson_sysconf.suspend_addr`.

### State, Persistence, And Dependencies
State includes ACPI wake registers, registered platform device, and `loongson_sysconf.suspend_addr`. Dependencies include ACPI core, Loongson system config, boot CPU feature flags, and platform-device APIs.

### Integration Points
Suspend and hibernate call wake helpers. `suspend_asm.S` calls the firmware suspend address prepared here. Cpufreq driver probing depends on the platform device.

### Risks
ACPI reduced-hardware handling must avoid unsupported register accesses. A bad `\SADR` conversion sends suspend assembly to the wrong firmware entry. Wake bits must be set before entering S3/hibernate.

### Test Signals
Boot ACPI systems with/without S3, inspect `\SADR`, test suspend wake from GPE/PCIe, and validate cpufreq device registration on scalable-frequency CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/suspend.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/suspend.c

### Purpose
`suspend.c` implements common LoongArch ACPI suspend/resume state handling around the assembly sleep entry.

### Important APIs, Types, And Functions
It defines `loongarch_suspend_addr`, `struct saved_registers`, static `saved_regs`, and functions `loongarch_common_suspend()`, `loongarch_common_resume()`, and `loongarch_acpi_suspend()`.

### Control Flow
Suspend saves counters, user/kernel PGD CSRs, page-walk controls, exception config, extended-unit enable, per-CPU base, and the firmware suspend address. `loongarch_acpi_suspend()` enables wake sources, saves common state, calls `loongarch_suspend_enter()`, then restores common state. Resume syncs counters, flushes TLBs, reinstalls exception vector CSRs, restores page-table/page-walk CSRs, exception config, EUEN, and per-CPU base.

### State, Persistence, And Dependencies
State survives S3 in static saved registers and firmware-managed CPU state. Dependencies include ACPI wake setup, LoongArch CSRs, exception vector symbols `eentry`/`tlbrentry`, TLB flushes, timer counter sync, and assembly in `suspend_asm.S`.

### Integration Points
Generic suspend path calls `loongarch_acpi_suspend()`. `platform.c` provides `loongson_sysconf.suspend_addr`. `tlb.c` originally installed the exception vectors restored here.

### Risks
Missing CSR restoration can break page walking, exceptions, or percpu addressing after resume. Wake setup and firmware entry must be valid before assembly enters sleep.

### Test Signals
ACPI S3 suspend/resume cycles, timer continuity checks, page-fault/TLB stress after resume, CPU hotplug after resume, and wake-source validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/suspend_asm.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/suspend_asm.S

### Purpose
`suspend_asm.S` is the low-level Loongson-3 sleep/wakeup routine used for ACPI S3 suspend.

### Important APIs, Types, And Functions
Macros are `SETUP_SLEEP` and `SETUP_WAKEUP`. Symbols are `loongarch_suspend_enter` and global inner label `loongarch_wakeup_start`.

### Control Flow
The entry saves key registers on the stack, stores the saved stack pointer in `acpi_saved_sp`, flushes all caches, passes wakeup PC and SP to firmware through `a0/a1`, and calls the firmware suspend routine at `loongarch_suspend_addr`. Wakeup sets DMW windows, jumps to virtual addressing, enables paging via CRMD, reloads the saved stack pointer, restores registers, and returns.

### State, Persistence, And Dependencies
State includes stack-saved registers, `acpi_saved_sp`, firmware-provided sleep/wakeup context, DMW configuration, and CRMD paging state. Dependencies include cache flushing, address-space setup macros, LoongArch CSRs, and `loongarch_suspend_addr` from `suspend.c`.

### Integration Points
Called by `loongarch_acpi_suspend()`. Firmware calls back to `loongarch_wakeup_start` after resume.

### Risks
Firmware ABI assumptions are strict: argument registers, wakeup physical/virtual transition, and stack preservation must match platform firmware. Cache flushes before sleep are important for firmware visibility.

### Test Signals
ACPI S3 cycles on Loongson-3 hardware, firmware wake path tracing, cache coherency checks after resume, and objdump review of wakeup code alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/suspend_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/Makefile -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/Makefile

### Purpose
This Makefile builds the LoongArch vDSO shared object, embeds it into the kernel, and generates symbol-offset headers.

### Important APIs, Types, And Functions
It defines `obj-vdso-y`, optional `vgettimeofday.o`, `ccflags-vdso`, `cflags-vdso`, `aflags-vdso`, linker flags, `gen-vdsosym`, targets for `vdso.lds`, `vdso.so.dbg`, `vdso.so`, and final `vdso.o`.

### Control Flow
Kbuild compiles vDSO objects with restricted C/ASM flags and `-D__VDSO__`, links `vdso.so.dbg` with `vdso.lds`, runs generic vDSO checks, strips to `vdso.so`, generates `include/generated/vdso-offsets.h` from `NM` plus `gen_vdso_offsets.sh`, and builds `vdso.o` that incbins the shared object.

### State, Persistence, And Dependencies
Build outputs are generated vDSO ELF files and offset headers. Dependencies include generic `lib/vdso/Makefile.include`, compiler support flags, `NM`, `OBJCOPY`, `CONFIG_GENERIC_GETTIMEOFDAY`, and generated C-vDSO include selections.

### Integration Points
`vdso.S` embeds the generated `vdso.so`; kernel ELF/vDSO setup uses generated offsets to expose vDSO entry points to userspace.

### Risks
Compiler flags must avoid kernel instrumentation and unsupported ABI options. Linker script/version exports must match actual objects. Offset generation relies on `VDSO_*` symbols in `vdso.lds.S`.

### Test Signals
Cross-build 32/64-bit LoongArch vDSO, run vDSO check, inspect exported symbols, and run userspace gettime/getcpu/getrandom/sigreturn tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/elf.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/elf.S

### Purpose
`elf.S` adds a Linux version ELF note to the LoongArch vDSO.

### Important APIs, Types, And Functions
It uses `ELFNOTE_START(Linux, 0, "a")`, emits `LINUX_VERSION_CODE`, and closes with `ELFNOTE_END`.

### Control Flow
There is no runtime control flow; the assembler emits note data into the vDSO ELF.

### State, Persistence, And Dependencies
The output is persistent build-time ELF metadata. Dependencies include `asm/vdso/vdso.h`, `linux/elfnote.h`, and `linux/version.h`.

### Integration Points
The vDSO linker includes this object so userspace/core tooling can identify the kernel version associated with the vDSO.

### Risks
Incorrect note formatting can break ELF consumers or vDSO validation.

### Test Signals
Inspect `readelf -n vdso.so.dbg` and build-time vDSO checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/elf.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/gen_vdso_offsets.sh -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/gen_vdso_offsets.sh

### Purpose
`gen_vdso_offsets.sh` converts vDSO symbol addresses from `nm` output into C preprocessor constants.

### Important APIs, Types, And Functions
The script is a shell wrapper around one `sed` command that matches symbols named `VDSO_*` and emits `#define vdso_offset_<name> 0x<addr>`.

### Control Flow
It reads standard input, strips leading zeroes from hex addresses, filters matching symbol lines, captures the suffix after `VDSO_`, and prints defines. The Makefile sorts its output.

### State, Persistence, And Dependencies
No runtime state. Build output is `include/generated/vdso-offsets.h`. Dependencies are POSIX shell, `sed`, `nm` output format, and `LC_ALL=C` sorting in the caller.

### Integration Points
The vDSO Makefile invokes it after linking `vdso.so.dbg`.

### Risks
Any change in `nm` output format, symbol type character, or `VDSO_*` naming can omit offsets. The regex only matches lines with ` . ` as the type field.

### Test Signals
Build vDSO and verify generated offsets for `sigreturn` and all exported vDSO entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/gen_vdso_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/sigreturn.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/sigreturn.S

### Purpose
`sigreturn.S` implements the LoongArch vDSO `__vdso_rt_sigreturn` signal trampoline.

### Important APIs, Types, And Functions
The exported signal function is `__vdso_rt_sigreturn`, declared with `SYM_SIGFUNC_START/END`.

### Control Flow
The routine loads `__NR_rt_sigreturn` into syscall register `a7` and executes `syscall 0`.

### State, Persistence, And Dependencies
It has no persistent local state. Dependencies include LoongArch syscall ABI, UAPI syscall numbers, and signal-frame expectations.

### Integration Points
The vDSO linker exports this symbol and `vdso.lds.S` also aliases `VDSO_sigreturn` for kernel offset generation. Userspace signal return uses this trampoline.

### Risks
Wrong syscall number/register breaks signal return for every userspace process on this ABI.

### Test Signals
Run signal delivery/return tests, `strace` signal paths, and vDSO symbol inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/sigreturn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.S

### Purpose
`vdso.S` embeds the built LoongArch `vdso.so` binary into a page-aligned kernel object.

### Important APIs, Types, And Functions
It defines global symbols `vdso_start` and `vdso_end` and uses `.incbin "arch/loongarch/vdso/vdso.so"`.

### Control Flow
No runtime code executes here. The assembler aligns data to a page, includes the vDSO image, aligns the end, and returns to the previous section.

### State, Persistence, And Dependencies
State is the embedded vDSO byte image in the kernel binary. Dependencies include page alignment macros and the Makefile-produced `vdso.so`.

### Integration Points
Kernel vDSO mapping code references `vdso_start`/`vdso_end` to map the shared object into userspace.

### Risks
Path or alignment mismatch can embed stale/missing data or violate vDSO mapping assumptions.

### Test Signals
Build kernel, inspect `vdso_start`/`vdso_end`, verify userspace maps a valid vDSO ELF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.lds.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.lds.S

### Purpose
`vdso.lds.S` is the linker script and symbol version map for the LoongArch vDSO.

### Important APIs, Types, And Functions
It sets `OUTPUT_ARCH(loongarch)`, emits `VDSO_VVAR_SYMS`, defines ELF sections and PHDRs, exports version `LINUX_5.10`, and defines `VDSO_sigreturn = __vdso_rt_sigreturn`.

### Control Flow
At link time, sections are laid out after ELF headers; hash, dynamic symbol, note, text, unwind, dynamic, and rodata sections are assigned to read/execute or read-only program headers. Data/bss/GNU-stack attributes are discarded. The version block exposes selected vDSO symbols and hides all others.

### State, Persistence, And Dependencies
Output is the linked vDSO ELF layout and symbol table. Dependencies include generated asm offsets, vDSO datapage definitions, and config-gated gettimeofday symbols.

### Integration Points
The Makefile uses this script to link `vdso.so.dbg`; `gen_vdso_offsets.sh` consumes `VDSO_*` symbols from the resulting ELF.

### Risks
Incorrect exported symbol list breaks userspace ABI. Discarding or PHDR mistakes can make the ELF invalid or writable. Version-name changes affect dynamic linker expectations.

### Test Signals
Run vDSO link checks, `readelf -l -s -V`, userspace calls to exported functions, and ABI comparison against expected LoongArch vDSO symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetcpu.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetcpu.c

### Purpose
`vgetcpu.c` provides the LoongArch vDSO fast path for `getcpu()`.

### Important APIs, Types, And Functions
Functions are `read_cpu_id()` and `__vdso_getcpu(unsigned int *cpu, unsigned int *node, void *unused)`.

### Control Flow
`read_cpu_id()` uses `rdtime.d` on 64-bit or `rdtimel.w` on 32-bit with `$zero` time output to read the CPU id. `__vdso_getcpu()` writes the CPU id if `cpu` is non-null and writes the node from `vdso_u_arch_data.pdata[cpu_id].node` if `node` is non-null.

### State, Persistence, And Dependencies
State is read from hardware and the vDSO architecture data page. Dependencies include LoongArch time/CPU-id instruction semantics and `vdso_u_arch_data`.

### Integration Points
Exported by `vdso.lds.S` as `__vdso_getcpu` for libc/userspace.

### Risks
CPU id must index a valid vDSO pdata entry. Migration during the call can return a CPU/node pair that is momentarily stale, which is normal for getcpu-style fast paths but must stay within ABI expectations.

### Test Signals
Run `getcpu()` userspace tests under CPU migration, CPU hotplug, and NUMA systems; compare syscall fallback values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom-chacha.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom-chacha.S

### Purpose
`vgetrandom-chacha.S` implements a LoongArch ChaCha20 block generator for vDSO getrandom without spilling sensitive key material to the stack.

### Important APIs, Types, And Functions
The exported function is `__arch_chacha20_blocks_nostack(output, key, counter, nblocks)`. Internal macros map state registers and define `OP_4REG` for four parallel operations.

### Control Flow
The function saves callee-saved registers, loads ChaCha constants, key words, and a 64-bit counter, then loops over 64-byte blocks. Each block performs 10 double rounds using add/xor/rotate sequences for column and diagonal rounds, adds the original state, stores 16 words to output, increments the counter with carry, advances output, and repeats. At the end it stores the updated counter, clears sensitive temporary state registers, restores saved registers, and returns.

### State, Persistence, And Dependencies
Persistent output is generated random bytes and updated counter memory. Sensitive key/state remain in registers; only ABI callee-saved registers are spilled and later restored. Dependencies include LoongArch integer instructions, ABI register conventions, and vDSO getrandom generic code.

### Integration Points
`vgetrandom.c` calls generic `__cvdso_getrandom()`, which can use this arch ChaCha helper for userspace random generation.

### Risks
ChaCha round constants, rotation counts, counter update, and little-endian word stores must be exact. The no-sensitive-stack property depends on not spilling state/key registers beyond the saved ABI registers. Register aliasing is dense and review-sensitive.

### Test Signals
Run known-answer ChaCha20 vectors through the vDSO helper, getrandom vDSO selftests, counter wrap tests, and inspect assembly for unintended stack spills of key/state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom-chacha.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom.c

### Purpose
`vgetrandom.c` exposes the LoongArch vDSO `getrandom()` entry point.

### Important APIs, Types, And Functions
The function is `__vdso_getrandom(void *buffer, size_t len, unsigned int flags, void *opaque_state, size_t opaque_len)`.

### Control Flow
It forwards all arguments directly to generic `__cvdso_getrandom()`.

### State, Persistence, And Dependencies
State is in caller buffer and opaque vDSO random state managed by generic code. Dependencies include `linux/types.h`, generic vDSO getrandom implementation included by the build, and optional ChaCha helper assembly.

### Integration Points
Exported by `vdso.lds.S` and built by the vDSO Makefile. Userspace libc can call this instead of the syscall when supported.

### Risks
The wrapper is thin; risk is mainly ABI signature drift with generic `__cvdso_getrandom()` or missing arch helper linkage.

### Test Signals
Run vDSO getrandom selftests, compare syscall fallback behavior for flags/lengths, and verify symbol export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgettimeofday.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgettimeofday.c

### Purpose
`vgettimeofday.c` exposes LoongArch vDSO time functions through generic vDSO timekeeping helpers.

### Important APIs, Types, And Functions
Functions are `__vdso_clock_gettime()`, `__vdso_gettimeofday()`, and `__vdso_clock_getres()`.

### Control Flow
Each wrapper forwards directly to the corresponding generic helper: `__cvdso_clock_gettime()`, `__cvdso_gettimeofday()`, or `__cvdso_clock_getres()`.

### State, Persistence, And Dependencies
State is read from the vDSO data page and timekeeper data managed by generic code. Dependencies include `vdso/gettime.h`, LoongArch vDSO build includes, and `CONFIG_GENERIC_GETTIMEOFDAY`.

### Integration Points
Conditionally built and exported by the vDSO Makefile/linker script. Userspace time calls use these symbols for fast clock reads.

### Risks
Thin-wrapper risks are ABI mismatch and config/linker mismatch. Correctness largely depends on generic vDSO time data and architecture clocksource support.

### Test Signals
Run vDSO clock/gettimeofday/getres tests across clocks, compare with syscalls, and test under time adjustments and CPU migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/Makefile -->
## sources/distributed-fs/ceph-client/arch/m68k/68000/Makefile

### Purpose
This Makefile selects object files for m68k 68000-core based CPU/platform support.

### Important APIs, Types, And Functions
It always builds `entry.o`, `ints.o`, `timers.o`, `m68328.o`, and `head.o`; conditionally builds `romvec.o` for `CONFIG_ROM`, `dragen2.o` for `CONFIG_DRAGEN2`, and `ucsimm.o` for `CONFIG_UCSIMM` or `CONFIG_UCDIMM`.

### Control Flow
Kbuild evaluates configuration symbols and composes the directory object list. There is no runtime code in this file.

### State, Persistence, And Dependencies
No runtime state exists. Dependencies are Kbuild, m68k platform config symbols, and the listed source objects.

### Integration Points
This controls which 68000 startup, interrupt, timer, SoC, ROM vector, and board files are linked into m68k kernel builds.

### Risks
Wrong conditional object selection can omit board initialization or duplicate shared board code. Since `ucsimm.o` is used for both UCSIMM and UCDIMM, it must support both configs.

### Test Signals
Cross-build m68k 68000 configs for ROM, DRAGEN2, UCSIMM, and UCDIMM variants and check link coverage for entry/head/platform symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/Makefile -->
