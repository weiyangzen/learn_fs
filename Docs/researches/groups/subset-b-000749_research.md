# subset-b-000749 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-32.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-32.c

### Purpose
`pgtable-32.c` initializes 32-bit MIPS kernel page-table roots and fixed mapping ranges. It seeds invalid page-table pointers into `swapper_pg_dir`, prepares fixmap page-table coverage, and wires permanent kmap page tables when highmem is enabled.

### Important APIs, Types, And Functions
`pgd_init()` fills user PGD entries with `invalid_pte_table`. `pagetable_init()` initializes `swapper_pg_dir`, calls `fixrange_init()` for fixmap and highmem pkmap regions, and assigns `pkmap_page_table` under `CONFIG_HIGHMEM`. `set_pmd_at()` is a transparent hugepage helper that stores a PMD directly.

### Control Flow
Boot calls `pagetable_init()`, which initializes both user and kernel halves of `swapper_pg_dir`, computes the final fixed-address virtual range using `__fix_to_virt()`, and allocates intermediate page tables through `fixrange_init()`. In highmem builds, it repeats range setup for `PKMAP_BASE`, then walks PGD/P4D/PUD/PMD/PTE offsets to remember the permanent kmap PTE page.

### State, Persistence, And Dependencies
Persistent state is the kernel page-table tree rooted at `swapper_pg_dir` plus optional `pkmap_page_table`. The file depends on MIPS pgalloc invalid-table symbols, fixmap constants, highmem constants, and generic Linux MM types.

### Integration Points
This code is selected for 32-bit MIPS page-table setup and feeds fixmap, highmem kmap, TLB refill, and later `pgd_alloc()` behavior. It must match the folded page-table model used by the 32-bit architecture configuration.

### Risks
The unrolled `pgd_init()` assumes `USER_PTRS_PER_PGD` is a multiple of eight. Wrong fixmap or pkmap range alignment would leave early virtual mappings without page tables. Highmem state is especially sensitive because `pkmap_page_table` becomes a shared pointer for permanent kmap operations.

### Test Signals
Useful signals are early boot on 32-bit MIPS with and without `CONFIG_HIGHMEM`, fixmap users such as early ioremap, permanent kmap stress, and transparent hugepage builds verifying `set_pmd_at()` linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-64.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-64.c

### Purpose
`pgtable-64.c` initializes 64-bit MIPS top-level and folded or unfolded invalid page-table layers. It prepares invalid PGD/PUD/PMD entries and creates page-table coverage for fixed mappings.

### Important APIs, Types, And Functions
`pgd_init()` fills a PGD page with `invalid_pud_table`, `invalid_pmd_table`, or `invalid_pte_table` depending on folded levels. `pmd_init()` and `pud_init()` initialize invalid lower-level tables when those levels exist. `pagetable_init()` initializes the swapper root and invalid tables, then calls `fixrange_init()`. `pmd_init()` is exported for GPL modules when PMD tables are not folded.

### Control Flow
Boot initializes `swapper_pg_dir`, optionally initializes `invalid_pud_table` and `invalid_pmd_table`, and then computes a PMD-aligned fixmap start from `__fix_to_virt(__end_of_fixed_addresses - 1)`. `fixrange_init()` allocates the tables needed for the fixmap range.

### State, Persistence, And Dependencies
The durable state is the initial kernel page-table hierarchy and invalid-table sentinel contents. Dependencies include the MIPS pgalloc table symbols, folded-level macros, fixmap constants, and TLB flush/MM headers.

### Integration Points
The file is the 64-bit counterpart of `pgtable-32.c` and must agree with `pgd_alloc()`, TLB refill code, hardware page-table walker setup, and the configured number of page-table levels.

### Risks
The initialization loops rely on table counts that are multiples of eight. A mismatch between folded-level configuration and chosen invalid table would send page-table walks into the wrong sentinel table. Fixmap range errors affect early exception, ioremap, and per-CPU fixed mappings.

### Test Signals
Boot 64-bit MIPS with folded and three-level page-table configurations, use fixmap-heavy early boot paths, and verify module users of exported `pmd_init()` on non-folded PMD builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable-64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/pgtable.c

### Purpose
`pgtable.c` provides common MIPS PGD allocation for process address spaces. It allocates a fresh PGD, initializes user entries to invalid tables, and copies the kernel half from `init_mm`.

### Important APIs, Types, And Functions
`pgd_alloc()` calls architecture `__pgd_alloc()`, `pgd_init()`, `pgd_offset(&init_mm, 0UL)`, and `memcpy()` for kernel mappings. It is exported with `EXPORT_SYMBOL_GPL`.

### Control Flow
When a new `mm_struct` needs a PGD, allocation happens first. On success, the entire user portion is initialized with invalid page-table pointers, then entries from `USER_PTRS_PER_PGD` through `PTRS_PER_PGD` are copied from the boot kernel page directory.

### State, Persistence, And Dependencies
The allocated PGD persists as the root page table for a process until freed by the MM subsystem. It depends on the architecture-specific `pgd_init()` implementation in the 32-bit or 64-bit file and on the kernel mappings already present in `init_mm`.

### Integration Points
This function is used by generic Linux process address-space creation and by MIPS TLB refill paths that assume every process PGD has kernel mappings pre-populated.

### Risks
Copy length and `USER_PTRS_PER_PGD` must match the architecture split between user and kernel address ranges. Failure to copy kernel mappings correctly breaks kernel faults taken while running in a user `mm`.

### Test Signals
Signals include process creation under memory pressure, kernel faults while executing in non-init address spaces, and architecture builds covering both 32-bit and 64-bit `pgd_init()` implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/physaddr.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/physaddr.c

### Purpose
`physaddr.c` wraps virtual-to-physical address conversion with debug validation for MIPS linear and kernel-symbol address ranges.

### Important APIs, Types, And Functions
`__virt_to_phys()` warns on invalid non-linear virtual addresses before calling `__virt_to_phys_nodebug()`. `__phys_addr_symbol()` checks that a symbol address lies between `_text` and `_end` before calling `__pa_symbol_nodebug()`. `__debug_virt_addr_valid()` encodes the accepted virtual ranges and special-cases `MAX_DMA_ADDRESS`.

### Control Flow
At conversion time, `__virt_to_phys()` evaluates the address against page offset, segment class, EVA, and highmem rules. Invalid conversions only warn, preserving legacy callers. Symbol conversion uses `VIRTUAL_BUG_ON()` to enforce that `__pa_symbol()` is only used for kernel image symbols.

### State, Persistence, And Dependencies
There is no retained state. Dependencies include address-space macros, kernel section boundaries, DMA constants, and MM debug helpers.

### Integration Points
The functions are exported and used by MIPS drivers, DMA setup, and core memory helpers that need physical addresses. The warning helps catch misuse of `virt_to_phys()` on vmalloc/highmem addresses.

### Risks
The compatibility exception for `MAX_DMA_ADDRESS` preserves old behavior but can mask weak callers. Range rules differ under EVA and highmem, so tests must cover those configurations. Symbol bounds bugs are fatal through `VIRTUAL_BUG_ON()`.

### Test Signals
Exercise `virt_to_phys()` for KSEG0/linear addresses, `MAX_DMA_ADDRESS`, vmalloc addresses, highmem mappings, EVA builds, and `__pa_symbol()` on valid and invalid kernel-image addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/physaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-debugfs.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-debugfs.c

### Purpose
`sc-debugfs.c` exposes a debugfs control for MIPS secondary-cache prefetch state. It creates `/sys/kernel/debug/mips/l2cache/prefetch` under the MIPS debugfs root.

### Important APIs, Types, And Functions
`sc_prefetch_read()` reports `Y\n` or `N\n` from `bc_prefetch_is_enabled()`. `sc_prefetch_write()` parses a user boolean and calls `bc_prefetch_enable()` or `bc_prefetch_disable()`. `sc_debugfs_init()` creates the `l2cache` directory and `prefetch` file with `sc_prefetch_fops`.

### Control Flow
At late init, debugfs entries are created. Reads query current bcache prefetch state and use `simple_read_from_buffer()`. Writes parse the supplied boolean from userspace and synchronously update the bcache operation.

### State, Persistence, And Dependencies
The persistent state lives in the secondary-cache controller accessed via `bcache_ops`; debugfs itself only stores dentries. Dependencies include `mips_debugfs_dir`, debugfs, `linux/uaccess.h`, and bcache prefetch hooks.

### Integration Points
This file is useful with `sc-mips.c`, whose `bcache_ops` supplies prefetch methods on CM2.5+ systems. It gives developers a runtime switch for L2 prefetch behavior.

### Risks
The code does not check for debugfs creation errors, matching common debugfs patterns. If the selected `bcache_ops` lacks prefetch methods, behavior depends on the bcache wrapper implementation. Writes directly affect hardware performance state.

### Test Signals
Mount debugfs on a MIPS system with and without prefetch-capable L2 cache, read the file, write true/false strings, and verify hardware register state or wrapper-reported state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-ip22.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-ip22.c

### Purpose
`sc-ip22.c` implements Indy IP22 R4600/R5000 secondary-cache management. It probes cache size from SGI EEPROM, enables or disables the cache with CP0 mode switches, and provides DMA cache maintenance callbacks.

### Important APIs, Types, And Functions
`indy_sc_wipe()` performs the low-level indexed write sequence in inline MIPS3 assembly. `indy_sc_wback_invalidate()` handles range flushing with wraparound across the fixed 512 KiB index space. `indy_sc_enable()`, `indy_sc_disable()`, and `indy_sc_probe()` manage hardware state. `indy_sc_init()` installs `indy_sc_ops` into global `bcops`.

### Control Flow
Initialization reads EEPROM byte 17, computes cache size, enables the cache, and registers bcache operations. DMA cache maintenance computes first and last cache-line indexes, disables interrupts, and either wipes a contiguous range or splits the operation around the end of the index space.

### State, Persistence, And Dependencies
`scache_size` records probed size. Hardware state persists in secondary-cache enable bits and cache contents. Dependencies include SGI IP22 EEPROM access, CP0 status manipulation, KSEG address construction, and bcache operation dispatch.

### Integration Points
The file integrates with SGI IP22 platform setup and the generic MIPS bcache hooks used by DMA mapping and cache flush code.

### Risks
Inline assembly temporarily enters 64-bit mode from a 32-bit kernel context, so CP0 status save/restore and hazard nops are critical. The wipe algorithm assumes 32-byte lines and a 512 KiB index mask. `BUG_ON(size == 0)` catches bad DMA callers but turns misuse into a hard failure.

### Test Signals
Boot on IP22 with and without secondary cache, run DMA-heavy devices, validate wraparound range flushes, and verify CP0 status is restored after enable/disable and wipe operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-ip22.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-mips.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-mips.c

### Purpose
`sc-mips.c` provides generic MIPS32/MIPS64 L2 cache detection and bcache operations for platforms using standard Config2 or CM3 L2 configuration registers.

### Important APIs, Types, And Functions
`mips_sc_wback_inv()` and `mips_sc_inv()` implement DMA cache maintenance. Prefetch control helpers use CM GCR L2 prefetch registers. `mips_sc_is_activated()`, `mips_sc_probe_cm3()`, and `mips_sc_probe()` populate `current_cpu_data.scache`. `mips_sc_init()` enables prefetch and installs `mips_sc_ops`.

### Control Flow
Probe first marks secondary cache not present, then uses CM3 L2 configuration when available or older Config1/Config2 fields otherwise. It rejects unsupported ISA or inactive/bypassed cache states, applies Ingenic XBurst corrections, fills sets/ways/line size/way size, clears the not-present flag, enables prefetch, and registers bcache operations.

### State, Persistence, And Dependencies
Persistent state is stored in `current_cpu_data.scache`, `current_cpu_data.options`, CM prefetch control registers, and the global `bcops` pointer. Dependencies include MIPS CM accessors, CP0 Config registers, cache op helpers, and machine type identifiers.

### Integration Points
The file feeds DMA cache maintenance, optional debugfs prefetch control, and CPU cache descriptors consumed by other architecture code. It is the generic L2 path for many MIPS cores.

### Risks
Config2 bit 12 is implementation-defined but interpreted as an L2 bypass bit for selected CPUs. Incorrect set/way/line decoding breaks cache flushing. Prefetch enable is gated on CM2.5+ and present prefetch units but still changes hardware performance behavior globally.

### Test Signals
Boot on representative CPUs covering Config2, CM3, QEMU generic, BMIPS, and XBurst overrides; validate reported cache geometry, DMA correctness, and debugfs prefetch enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-r5k.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-r5k.c

### Purpose
`sc-r5k.c` implements R5000 secondary-cache support. It detects cache presence/size, enables or disables the secondary cache, and provides page-granular invalidation for DMA.

### Important APIs, Types, And Functions
`blast_r5000_scache()` invalidates all secondary-cache pages. `r5k_dma_cache_inv_sc()` invalidates an affected range or the whole cache when the request covers at least `scache_size`. `r5k_sc_enable()`, `r5k_sc_disable()`, `r5k_sc_probe()`, and `r5k_sc_init()` manage lifecycle and `bcops`.

### Control Flow
Probe checks `CONF_SC`; if cache exists, it derives size from `R5K_CONF_SS`. Enabling sets `R5K_CONF_SE`, blasts the cache, and restores interrupts. DMA invalidation rounds the range to 128-line secondary-cache page boundaries because smaller invalidation is not supported.

### State, Persistence, And Dependencies
`scache_size` is the file-local persistent cache geometry. Hardware state lives in CP0 Config secondary-cache enable bits. Dependencies include `cache_op(R5K_Page_Invalidate_S)`, CP0 config helpers, and bcache operations.

### Integration Points
The registered bcache operations are used by DMA mapping and cache maintenance code on R5000 systems.

### Risks
The secondary cache is physically indexed and write-through, with invalidation granularity larger than normal cache lines. Wrong size calculation or boundary rounding can leave stale data. `BUG_ON(size == 0)` makes bad DMA caller inputs fatal.

### Test Signals
Boot R5000 systems with and without secondary cache, test DMA on small and whole-cache-sized buffers, and verify enable/disable paths preserve interrupt state and CP0 configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-r5k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-rm7k.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-rm7k.c

### Purpose
`sc-rm7k.c` manages RM7000 secondary and optional tertiary caches. It handles cache geometry reporting, cache enable/disable, tertiary-cache probing, and DMA cache maintenance.

### Important APIs, Types, And Functions
`rm7k_sc_wback_inv()` and `rm7k_sc_inv()` maintain secondary and tertiary caches for DMA. `__rm7k_sc_enable()` and `__rm7k_tc_enable()` initialize tags while running uncached. `__probe_tcache()` detects tertiary-cache wraparound size. `rm7k_sc_init()` populates cache descriptors and installs `rm7k_sc_ops`.

### Control Flow
Initialization checks for secondary-cache presence, fills `current_cpu_data.scache`, enables secondary cache if needed, registers bcache ops, then probes tertiary cache when Config says it is present. The tertiary probe enables TC, writes known tags across increasing powers of two, detects wraparound by reading tags, disables TC, and later enables it for use.

### State, Persistence, And Dependencies
Persistent state includes `rm7k_tcache_init`, `tcache_size`, CP0 config bits, and CPU cache descriptors. The file depends on `run_uncached()`, CP0 tag registers, cache op encodings, and primary cache geometry globals.

### Integration Points
DMA cache operations use these callbacks through `bcops`. CPU cache information is visible to generic MIPS cache management and diagnostics.

### Risks
The tertiary-cache size probe depends on tag behavior and address aliasing; mistakes can corrupt cache state. Enable routines must run uncached to avoid executing through cache being reinitialized. Secondary and tertiary page granularities differ, so range math must stay exact.

### Test Signals
Boot RM7000 with and without tertiary cache, verify reported cache sizes, run DMA coherency tests across ranges crossing tertiary-cache page boundaries, and exercise enable/disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-rm7k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-funcs.S -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlb-funcs.S

### Purpose
`tlb-funcs.S` reserves executable storage for micro-assembler-generated TLB miss handlers and the PGD setup helper.

### Important APIs, Types, And Functions
It defines `tlbmiss_handler_setup_pgd`, `handle_tlbm`, `handle_tlbs`, and `handle_tlbl`, plus exported end symbols. `tlbmiss_handler_setup_pgd` starts with a dummy self-branch that runtime code overwrites.

### Control Flow
There is no runtime logic beyond the placeholder branch. `tlbex.c` later writes generated instructions into these fixed symbol ranges and flushes the instruction cache.

### State, Persistence, And Dependencies
The reserved instruction areas persist in kernel text and become live exception fastpaths after generation. Dependencies include MIPS assembler macros, register definitions, and symbol export support.

### Integration Points
`tlbex.c` uses these buffers for TLB load, store, modify, and PGD setup handlers. The exported setup helper is also used by code that updates the current PGD for TLB refill.

### Risks
The reserved `FASTPATH_SIZE` and setup area must be large enough for all generated CPU/config variants. Writing past end symbols would corrupt neighboring text, so generator overflow checks are essential.

### Test Signals
Boot builds with different CPU options, verify generated handler size logs stay below end symbols, and trigger TLB load/store/modify exceptions after handler installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-funcs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r3k.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r3k.c

### Purpose
`tlb-r3k.c` implements R2000/R3000-style TLB flushing, update, wired-entry installation, and TLB initialization.

### Important APIs, Types, And Functions
`local_flush_tlb_all()`, `local_flush_tlb_range()`, `local_flush_tlb_kernel_range()`, and `local_flush_tlb_page()` invalidate entries. `__update_tlb()` inserts or updates a PTE for a faulting address. `add_wired_entry()` installs one of the first eight wired entries. `tlb_init()` flushes and builds refill handlers.

### Control Flow
Flush routines save interrupt state and current EntryHi/ASID, probe for matching entries when ranges are small, invalidate by zeroing EntryLo and writing indexed entries, or drop the full MM context when flushing a large range. Updates probe the target page and use random or indexed TLB writes. Initialization clears all entries and calls `build_tlb_refill_handler()`.

### State, Persistence, And Dependencies
State lives in CP0 EntryHi, EntryLo0, Index, wired entry count, and per-MM CPU contexts. Dependencies include R3k TLB instruction helpers, ASID masks, SMP CPU context tracking, and `tlbex.c` handler generation.

### Integration Points
Generic MM and TLB shootdown code call these local flush/update functions on R3k-class CPUs. Wired entries support early permanent mappings.

### Risks
CP0 hazard avoidance is minimal and architecture-specific. The file reserves only eight wired entries. Large-range flushing drops the context rather than walking entries, which affects later ASID refill behavior.

### Test Signals
Run process context-switch and mmap/munmap workloads on R3k, test kernel vmalloc flushes, install wired mappings, and validate page faults refill correctly after `tlb_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r3k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r4k.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r4k.c

### Purpose
`tlb-r4k.c` implements TLB maintenance for R4000-style MIPS MMUs, including VTLB/FTLB invalidation, MMID support, hugepage updates, wired mappings, TLB uniquification, boot-time configuration, and CPU power-management restore.

### Important APIs, Types, And Functions
Flush APIs include `local_flush_tlb_all()`, range/page/kernel flushes, and `local_flush_tlb_one()`. Update and setup APIs include `__update_tlb()`, `add_wired_entry()`, `add_temporary_entry()`, `has_transparent_hugepage()`, and `tlb_init()`. Internal helpers include `flush_micro_tlb()`, `r4k_tlb_uniquify_*()`, `r4k_tlb_configure()`, and the CPU PM notifier.

### Control Flow
Flush paths stop the hardware table walker, preserve EntryHi/MMID, probe matching entries for small ranges, write unique invalid EntryHi values, restart HTW, and flush Loongson micro-TLBs as needed. `__update_tlb()` walks the software page tables, handles huge PMD leaves when configured, loads even/odd EntryLo values including XPA forms, and writes random or indexed entries. `tlb_init()` configures PageMask, wired/framed mask state, RIXI/PageGrain bits, optional `ntlb=` restriction, TLB uniquification, and generated refill handlers.

### State, Persistence, And Dependencies
Persistent hardware state includes CP0 PageMask, Wired, EntryHi/EntryLo, MMID, PageGrain, temporary TLB index, and TLB contents. Software state includes `temp_tlb_entry`, optional `ntlb`, and CPU cache/TLB descriptors. Dependencies include HTW controls, hazard macros, memblock/slab allocation, sort, hugepage and XPA PTE layouts, and `tlbex.c`.

### Integration Points
This is the main TLB backend for most MIPS CPUs. It integrates with generic MM TLB shootdowns, hugepage support, power management, boot command-line parsing, and generated exception refill handlers.

### Risks
Races with HTW or shared FTLB require careful stop/start sequencing. Uniquification must avoid wired/global collisions or later flushes can fail. XPA wired entries are explicitly unsupported. `ntlb=` can reduce usable entries and change performance. CPU errata and Loongson micro-TLB flushing are easy to regress.

### Test Signals
Exercise ASID and MMID context switching, vmalloc flushes, hugepages, transparent hugepage detection, suspend/resume or CPU PM exit, FTLB/VTLB systems with `cpu_has_tlbinv`, and boot with valid/invalid `ntlb=` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r4k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlbex-fault.S -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlbex-fault.S

### Purpose
`tlbex-fault.S` provides the slowpath page-fault entry points used by generated TLB handlers.

### Important APIs, Types, And Functions
The `tlb_do_page_fault` macro emits `tlb_do_page_fault_0` for read/load faults and `tlb_do_page_fault_1` for write/modify faults. Each saves registers, captures `CP0_BADVADDR`, switches to kernel mode, stores `PT_BVADDR`, and calls `do_page_fault()`.

### Control Flow
The generated fastpath jumps here when it cannot satisfy a TLB exception. The assembly saves the full exception frame, passes `pt_regs *`, write flag, and bad virtual address to `do_page_fault()`, then branches to `ret_from_exception`.

### State, Persistence, And Dependencies
State is the saved exception frame on the kernel stack and `PT_BVADDR`. Dependencies include stackframe macros, CP0 register access, `do_page_fault()`, and `ret_from_exception`.

### Integration Points
`tlbex.c` references these symbols while generating load/store/modify handlers. They are the correctness fallback for invalid, missing, permission, RIXI, and high-segbits faults.

### Risks
The write flag must match the generated handler path. Register-save frame layout must stay consistent with `asm/stackframe.h` and page-fault code. Any bad jump target from microMIPS or normal MIPS generation would break fault recovery.

### Test Signals
Trigger user load faults, store faults, write-protect faults, execute/read-inhibit faults, and kernel vmalloc faults to ensure fastpaths fall back with correct `address` and write mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlbex-fault.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlbex.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlbex.c

### Purpose
`tlbex.c` synthesizes MIPS TLB refill and TLB load/store/modify fastpaths at runtime. It uses the MIPS micro-assembler to generate CPU-specific handlers that walk kernel page tables, update PTE accessed/dirty bits, load EntryLo registers, and fall back to normal page-fault assembly.

### Important APIs, Types, And Functions
Key exported helpers are `build_tlb_refill_handler()`, `build_tlb_write_entry()`, `build_get_pmde64()`, `build_get_pgde32()`, `build_get_ptep()`, and `build_update_entries()`. Important state includes `tlb_handler`, `labels`, `relocs`, `handler_reg_save`, `scratch_reg`, `pgd_reg`, `mips_xpa_disabled`, `check_for_high_segbits`, and `kscratch_used_mask`. Major builders cover R3000 refill/change handlers, R4000 refill/load/store/modify handlers, Loongson3 LDPTE handlers, hugepage tails, PGD setup, HTW setup, XPA setup, and PTE bit tests.

### Control Flow
At `build_tlb_refill_handler()`, the code validates XPA/RIXI requirements, emits debug definitions, probes EntryLo fill bits, chooses R3000 or R4000 style generation, allocates KScratch registers, writes the PGD setup helper, emits load/store/modify fastpaths into `tlb-funcs.S` buffers, emits the refill handler into `ebase`, flushes icache, and then configures XPA and HTW if supported. Generated handlers walk from PGD to PTE, handle vmalloc or high-segbits fallbacks, optionally update huge PMDs, use LL/SC for SMP PTE updates, write TLB entries with CPU-specific hazard sequences, and branch to `tlb_do_page_fault_0/1` on failure.

### State, Persistence, And Dependencies
Generated code persists in exception-vector memory and reserved fastpath buffers. Runtime hardware state includes KScratch, Context, PageMask, PWField/PWSize/PWCtl, KPGD, PageGrain, and EntryLo/EntryHi. Dependencies include `uasm`, CPU feature flags, CP0 hazard rules, TLB errata workarounds, bbit/lwx/ldpte instruction availability, hugepage and XPA PTE layout, SMP register save slots, and `tlbex-fault.S`.

### Integration Points
`tlb-r3k.c` and `tlb-r4k.c` call this during TLB initialization. The generated handlers are core MM exception paths for every process and kernel address-space fault. The `tlbmiss_handler_setup_pgd` helper is used to keep current PGD state in memory, Context, KScratch, or PWBASE depending on configuration.

### Risks
This file has a large CPU/config matrix and many size constraints. Branch delay slots, relocation offsets, KScratch allocation, high-segbits checks, RIXI fill-bit rotation, XPA high PFN writes, LL/SC retry loops, HTW races, and CPU-specific TLB write hazards are all sensitive. Buffer overflow checks panic, but subtle wrong code generation can cause silent memory corruption or fault loops.

### Test Signals
High-value tests are booting R3000, R4000, microMIPS, Loongson3 LDPTE, Octeon bbit/lwx, SMP, hugepage, XPA, HTW, and high-vmbits configurations; forcing TLB load/store/modify faults; vmalloc faults; page permission upgrades; dirty/accessed bit races; and checking debug dumps for handler length and relocation sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlbex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm-micromips.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/uasm-micromips.c

### Purpose
`uasm-micromips.c` provides the microMIPS instruction encoding backend for the shared MIPS micro-assembler.

### Important APIs, Types, And Functions
It defines microMIPS field positions, the `M()` encoding macro, `insn_table_MM`, `build_bimm()`, `build_jimm()`, `build_insn()`, and `__resolve_relocs()`. It includes shared `uasm.c`, which generates the exported `uasm_i_*` and label/relocation helpers.

### Control Flow
Callers invoke shared `uasm_i_*` helpers. Those helpers call this file's `build_insn()`, which validates opcode support, maps variadic operands into microMIPS-specific fields, swaps halfwords for little-endian builds, writes the encoded word, and advances the buffer pointer. Relocation resolution patches PC16 branch immediates, also respecting endian halfword placement.

### State, Persistence, And Dependencies
There is no mutable global state. Persistent output is generated instruction words in caller-provided buffers. Dependencies include `asm/inst.h`, microMIPS opcode constants, `asm/uasm.h`, and shared `uasm.c`.

### Integration Points
`tlbex.c` uses the same public uasm API regardless of ISA mode; selecting this backend lets generated TLB handlers work for `CONFIG_CPU_MICROMIPS`.

### Risks
Many normal MIPS opcodes are intentionally unsupported in `insn_table_MM` and will panic if emitted in a microMIPS build. Operand order differs for some CP0/FPU control instructions. Branch and jump immediates use halfword scaling and optional ISA16 target low bit, so relocation mistakes misdirect exception handlers.

### Test Signals
Build and boot microMIPS kernels, trigger generated TLB handlers, validate unsupported instruction paths are not reached, and inspect generated handler disassembly for correct endian halfword order and branch targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm-micromips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm-mips.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/uasm-mips.c

### Purpose
`uasm-mips.c` provides the standard MIPS32/MIPS64 instruction encoding backend for the shared micro-assembler.

### Important APIs, Types, And Functions
It defines standard register/immediate field positions, `M()` and `M6()` encoding macros, `insn_table`, `build_bimm()`, `build_jimm()`, `build_insn()`, and `__resolve_relocs()`. It includes shared `uasm.c` to expose the instruction-emitter API.

### Control Flow
The shared emitter calls `build_insn()` with an opcode and operands. This backend rejects unsupported opcodes or the R4k DADDIU erratum case, builds fixed opcode bits plus requested fields, writes a 32-bit instruction, and advances the output pointer. PC16 relocations are later resolved as byte deltas from the branch delay-slot PC.

### State, Persistence, And Dependencies
No global mutable state is kept. Output instructions persist in generated handler buffers. Dependencies include MIPS opcode definitions, CPU errata helpers, ELF relocation constants, and shared uasm declarations.

### Integration Points
This is the normal backend used by `tlbex.c` and any other MIPS code that builds short instruction sequences at runtime.

### Risks
Opcode tables must match the CPU ISA revision, including MIPS R6 encodings for cache, LL/SC, JR, DIV/MOD, and multiplication variants. Immediate overflow only warns in field builders, while unsupported opcodes panic. Branch immediate range is limited and must be handled by callers.

### Test Signals
Boot generated TLB handlers on MIPS32, MIPS64, and MIPS R6 systems; run disassembly checks for emitted opcodes; force branch relocations near range limits; and test CPU errata builds such as DADDIU workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm-mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/uasm.c

### Purpose
`uasm.c` is the shared source for a compact MIPS micro-assembler used by runtime code generators. It defines opcode IDs, field builders, public instruction-emitter wrappers, label/relocation management, address materialization helpers, and labeled-branch convenience functions.

### Important APIs, Types, And Functions
Core pieces include `enum opcode`, `struct insn`, `build_rs/rt/rd/re/simm/uimm/scimm/func/set()`, the `I_*` wrapper macros that export `uasm_i_*`, `uasm_build_label()`, `uasm_r_mips_pc16()`, `uasm_resolve_relocs()`, `uasm_move_relocs()`, `uasm_move_labels()`, `uasm_copy_handler()`, `uasm_insn_has_bdelay()`, `UASM_i_LA_mostly()`, `UASM_i_LA()`, and the `uasm_il_*` labeled branch helpers.

### Control Flow
Architecture backends include this file after defining instruction tables and `build_insn()`. Public emitters append encoded instructions to caller buffers. Label helpers record target addresses, relocation helpers record branch sites, copy/move helpers adjust metadata when generated handlers are folded, and `uasm_resolve_relocs()` patches pending branches once all labels are known.

### State, Persistence, And Dependencies
There is no shared mutable state. Callers own instruction buffers, label arrays, and relocation arrays. Dependencies are supplied by the including backend and by `asm/uasm.h`; Octeon builds also apply a prefetch erratum substitution.

### Integration Points
`tlbex.c` is the main consumer, using uasm to build exception handlers and move/copy handler fragments safely. The API is exported for other MIPS runtime code-generation users.

### Risks
The assembler intentionally does not hide branch delay slots or pipeline hazards, so callers must emit correct nops and hazard instructions. Label arrays require `UASM_LABEL_INVALID` termination. Address materialization must match 32-bit compatibility and 64-bit sign-extension rules. Copying handler fragments requires relocation and label moves to stay in sync.

### Test Signals
Validate generated handler disassembly, branch relocation at positive and negative offsets, handler folding across delay slots, 32-bit and 64-bit address loads, Octeon prefetch substitution, and exported helper use under module or built-in code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/uasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/mobileye/Kconfig

### Purpose
`mobileye/Kconfig` defines MIPS Mobileye EyeQ SoC selection and optional FIT image FDT inclusion for EyeQ5 development boards.

### Important APIs, Types, And Functions
The file is Kconfig data, not C code. Symbols are `MACH_EYEQ5`, `MACH_EYEQ6H`, `MACH_EYEQ6LPLUS`, and `FIT_IMAGE_FDT_EPM5`.

### Control Flow
When `EYEQ` is enabled, Kconfig presents a choice with EyeQ5 as default. `FIT_IMAGE_FDT_EPM5` is available only for `MACH_EYEQ5` and controls embedding the EPM5 FDT into the FIT kernel image.

### State, Persistence, And Dependencies
State is the generated kernel `.config`. Dependencies include the parent `EYEQ` platform symbol and downstream build rules that consume `FIT_IMAGE_FDT_EPM5`.

### Integration Points
The symbols feed Mobileye platform compilation and FIT image assembly in the MIPS boot path.

### Risks
Only EyeQ5 has a selectable embedded EPM5 FDT option here. A mismatched SoC choice can select wrong platform support. The help text assumes U-Boot FIT boot flow.

### Test Signals
Run Kconfig selection for each EyeQ SoC, verify default choice behavior, and build EyeQ5 with and without `FIT_IMAGE_FDT_EPM5`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/mobileye/Makefile

### Purpose
`mobileye/Makefile` currently only carries the SPDX license header and defines no object rules.

### Important APIs, Types, And Functions
There are no targets, variables, or functions beyond the license comment.

### Control Flow
Including this Makefile has no build effect.

### State, Persistence, And Dependencies
No state is produced. It depends only on the surrounding Kbuild include path.

### Integration Points
The file reserves a Mobileye platform Makefile location for future objects while current platform support is likely driven elsewhere.

### Risks
Because no objects are listed, enabling Mobileye symbols does not compile code from this directory through this Makefile. Future contributors must add explicit `obj-*` entries.

### Test Signals
Build Mobileye configurations and verify no missing object rules are expected from this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/board-epm5.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/mobileye/board-epm5.its.S

### Purpose
`board-epm5.its.S` adds an EyeQ5 EPM5 device-tree image and configuration fragment to a FIT image source.

### Important APIs, Types, And Functions
The DTS fragment defines an `images/fdt-mobileye-epm5` node that incbins `boot/dts/mobileye/eyeq5-epm5.dtb`, declares it as a MIPS flat DT with SHA1 hash, and a `configurations/conf-1` node that pairs `kernel` with that FDT.

### Control Flow
The assembler/preprocessor emits DTS/ITS text consumed by FIT image tooling. At boot, U-Boot can select `conf-1`, loading the kernel and associated EPM5 FDT.

### State, Persistence, And Dependencies
Persistent output is the FIT image containing the DTB blob. Dependencies include the built `eyeq5-epm5.dtb`, a `kernel` image node supplied by the base ITS, and U-Boot FIT support.

### Integration Points
This fragment works with `vmlinux.its.S` and the `FIT_IMAGE_FDT_EPM5` Kconfig option to package board-specific DT with the kernel.

### Risks
The incbin path must match the DTB build output. The configuration assumes the kernel image node is named `kernel`. A missing or stale DTB would fail FIT build or boot with wrong hardware description.

### Test Signals
Build EyeQ5 FIT images with EPM5 FDT enabled, inspect `dumpimage -l`, and boot via U-Boot selecting `conf-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/board-epm5.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/vmlinux.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/mobileye/vmlinux.its.S

### Purpose
`vmlinux.its.S` is a generic preprocessed FIT image source for a MIPS Linux kernel image.

### Important APIs, Types, And Functions
It defines root `description`, address-cell width, an `images/kernel` node with incbin `VMLINUX_BINARY`, type `kernel`, arch `mips`, compression `VMLINUX_COMPRESSION`, load and entry addresses, and SHA1 hash. It also defines a default configuration pointing to `kernel`.

### Control Flow
Build rules preprocess macros such as `KERNEL_NAME`, `ADDR_CELLS`, `ADDR_BITS`, `VMLINUX_BINARY`, `VMLINUX_LOAD_ADDRESS`, and `VMLINUX_ENTRY_ADDRESS`, then pass the ITS to FIT tooling.

### State, Persistence, And Dependencies
Persistent output is a FIT image containing the kernel. Dependencies include build-defined macros, the compressed or raw vmlinux binary, and `mkimage` or equivalent FIT processing.

### Integration Points
Board fragments such as `board-epm5.its.S` can extend the `images` and `configurations` nodes to add FDTs and board-specific configs.

### Risks
Incorrect load or entry address macros produce unbootable FIT images. Compression metadata must match the binary contents. SHA1 is a compatibility hash, not a strong security boundary.

### Test Signals
Build FIT images for supported address widths and compression modes, inspect resulting ITS/FIT metadata, and boot the default configuration plus board-extended configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/vmlinux.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/Makefile

### Purpose
`mti-malta/Makefile` selects the Malta platform support objects and adds the libfdt include path for the DT shim.

### Important APIs, Types, And Functions
It builds `malta-dtshim.o`, `malta-init.o`, `malta-int.o`, `malta-memory.o`, `malta-platform.o`, `malta-setup.o`, and `malta-time.o`. `CFLAGS_malta-dtshim.o` adds `scripts/dtc/libfdt`.

### Control Flow
When the Malta platform directory is selected by Kbuild, all listed objects are linked into the kernel.

### State, Persistence, And Dependencies
The build output is platform object code. Dependencies include libfdt headers for `malta-dtshim.c` and the surrounding MIPS platform Kbuild.

### Integration Points
This Makefile ties together Malta boot, memory, interrupt, platform device, setup, and time initialization.

### Risks
Missing any listed object breaks a required platform hook. The relative libfdt include path must remain valid if the tree layout changes.

### Test Signals
Build `MIPS_MALTA` configurations with device tree shim enabled and verify all platform hooks link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-dtshim.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-dtshim.c

### Purpose
`malta-dtshim.c` mutates firmware or built-in Malta device trees at boot to add memory nodes and adjust interrupt topology when a GIC is absent.

### Important APIs, Types, And Functions
`malta_dt_shim()` is the public entry. `append_memory()` reads firmware memory size, command-line overrides, memory-map version, and writes `/memory` `reg` plus `linux,usable-memory`. `remove_gic()` detects CM/ROCit GIC presence, nops the GIC node when absent, and redirects the i8259 interrupt parent. `gen_fdt_mem_array()` creates v1/v2 Malta memory ranges.

### Control Flow
The shim validates and opens the FDT into a 16 KiB aligned buffer, checks root compatibility for `mti,malta`, appends memory only if no memory node exists, removes or enables GIC handling as needed, packs the FDT, and returns either the modified buffer or original FDT for non-Malta compatibles.

### State, Persistence, And Dependencies
Persistent state is the modified flattened device tree handed to `__dt_setup_arch()`, plus global `physical_memsize`. Dependencies include libfdt, firmware environment access, ARC command line, ROCit/MSC registers, CM probing, and Malta revision macros.

### Integration Points
`malta-setup.c` calls this from `plat_mem_setup()`. The output affects memblock setup, interrupt controller probing, GIC timer availability, and i8259 routing.

### Risks
The fixed 16 KiB FDT buffer must be large enough after edits. Big-endian Malta subtracts a page for a SOC-it DMA quirk. Memory map v2 discards the IO-obscured 256 MiB window. If GIC detection is wrong, interrupt routing in the DT will not match hardware.

### Test Signals
Boot Malta with GT64120, Bonito, SOCit, and ROCit controllers; with and without CM/GIC; with `memsize=` and `ememsize=` env/cmdline overrides; and validate `/proc/device-tree` memory and interrupt-parent properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-dtshim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-init.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-init.c

### Purpose
`malta-init.c` performs early Malta PROM/platform initialization. It detects the system controller, maps controller registers, configures PCI byte swapping and IO bases, installs NMI/EJTAG vectors, initializes firmware command line and memory, sets console defaults, and chooses SMP operations.

### Important APIs, Types, And Functions
`prom_init()` is the main platform entry. `console_config()` parses `modetty0` and appends early console/console arguments when absent. `mips_nmi_setup()` and `mips_ejtag_setup()` copy exception vectors. `mips_cpc_default_phys_base()` returns the CPC base. Globals include revision IDs and controller base addresses.

### Control Flow
Early boot maps Bonito to identify emulation boards, resolves `mips_revision_sconid`, then switches over GT64120, Bonito, SOCit/ROCit, or SOCitSC controllers. It configures PCI swaps, DMA mappings, retry policy, IO port base, and then registers board exception setup callbacks. Finally it initializes firmware command line, memory, serial console, CPC probing, and SMP ops in CPS/vSMP/UP priority order.

### State, Persistence, And Dependencies
Persistent state includes mapped controller bases, revision globals, firmware command line, IO port base, installed exception vectors, and selected SMP ops. Dependencies include YAMON/fw helpers, board revision registers, controller register macros, PCI constants, cache flush, and CPS support.

### Integration Points
This is the earliest Malta platform setup used by later memory, interrupt, PCI, and time code. `malta-dtshim.c`, `malta-int.c`, and `malta-setup.c` depend on the detected system controller state.

### Risks
Wrong system-controller detection leads to wrong register mappings and IO base. Console string appends directly into firmware command line storage. PCI byte-lane swap settings differ by endianness and controller. The default unknown-controller path intentionally spins forever.

### Test Signals
Boot Malta variants across controller IDs and endian modes, verify serial console defaults, PCI enumeration, NMI/EJTAG vectors, and SMP startup mode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-int.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-int.c

### Purpose
`malta-int.c` initializes Malta interrupt routing and handles fatal CoreHi interrupts.

### Important APIs, Types, And Functions
`arch_init_irq()` reserves i8259 virtual IRQs, sets i8259 poll callback, calls `irqchip_init()`, initializes MSC IRQ maps, chooses CoreHi IRQ routing, and requests the CoreHi handler. `mips_pcibios_iack()` performs controller-specific PCI IACK. `corehi_irqdispatch()` dumps controller state and calls `die()`.

### Control Flow
Boot reserves the legacy i8259 range before other irqchips allocate descriptors. PCI IACK is routed through MSC, GT64120, or Bonito registers based on `mips_revision_sconid`. MSC interrupt controllers are initialized differently for VEIC and non-VEIC modes. CoreHi is wired through GIC, VEIC handler, or CPU IRQ and registered as a non-threaded interrupt.

### State, Persistence, And Dependencies
State includes reserved IRQ descriptors, i8259 poll function, MSC interrupt controller setup, and registered CoreHi IRQ action. Dependencies include irqchip DT probing, Malta revision globals, i8259, MSC01, GT64120, Bonito, GIC, VEIC, and exception register access.

### Integration Points
This file connects platform interrupt hardware to Linux IRQ domains and legacy i8259 behavior. It relies on `malta-init.c` controller detection and FDT shim interrupt topology.

### Risks
If i8259 descriptors are not reserved early, irqchip probing can allocate conflicting virqs. Bonito PCI IACK uses a special config mapping sequence and IO barriers. CoreHi is treated as fatal, so false routing to CoreHi halts the system.

### Test Signals
Boot with GIC, VEIC, and legacy CPU interrupt modes; verify i8259 IRQ allocation, PCI interrupts, timer/perf IRQs, and deliberate CoreHi diagnostics on hardware or emulator support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-memory.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-memory.c

### Purpose
`malta-memory.c` provides Malta firmware memory initialization hooks and a CDMM physical base.

### Important APIs, Types, And Functions
`fw_meminit()` sets `free_init_pages_eva` when EVA is enabled. `free_init_pages_eva_malta()` frees unused kernel init pages using `__pa_symbol()`. `mips_cdmm_phys_base()` returns `0x1fc10000`. `physical_memsize` is a global filled by the DT shim.

### Control Flow
During PROM initialization, `fw_meminit()` chooses the EVA-specific free-init callback or leaves it null. CDMM users later call `mips_cdmm_phys_base()` for a fixed typically-unused address.

### State, Persistence, And Dependencies
Persistent state is `physical_memsize` and optional `free_init_pages_eva` function pointer. Dependencies include memblock/init memory helpers, EVA configuration, MAAR/CDMM headers, and firmware setup.

### Integration Points
`malta-init.c` calls `fw_meminit()`. `malta-dtshim.c` updates `physical_memsize`. Core MIPS CDMM code consumes `mips_cdmm_phys_base()`.

### Risks
The EVA free path relies on `__pa_symbol()` because kernel virtual addresses may not map normally. The CDMM base is a convention and could conflict with unusual memory maps.

### Test Signals
Boot Malta EVA and non-EVA kernels, verify init memory is freed correctly, and test CDMM device discovery or absence at the fixed physical base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-platform.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-platform.c

### Purpose
`malta-platform.c` registers Malta legacy platform devices, primarily 8250 UART ports and the CBUS UART.

### Important APIs, Types, And Functions
`SMC_PORT()` describes SuperIO serial ports. `uart8250_data` contains COM1, COM2, and CBUS UART descriptors. `malta_add_devices()` registers `malta_uart8250_device` through `platform_add_devices()` at `device_initcall`.

### Control Flow
At device init, the serial8250 platform device is added with static port data. The CBUS UART uses MMIO, endian-dependent IO type, remapped memory, and a CPU IRQ.

### State, Persistence, And Dependencies
Persistent state is the platform device and its serial port descriptors. Dependencies include serial8250 platform support, platform device core, Malta IRQ numbering, and endian configuration.

### Integration Points
The serial driver probes these ports and exposes Malta console/serial devices. This complements early console setup in `malta-init.c`.

### Risks
The file intentionally avoids generic `8250_platform.c` ordering because it would make CBUS `ttyS0`. Wrong IRQ or IO type breaks serial. CBUS clock is double the usual rate and must stay accurate.

### Test Signals
Boot with serial8250, verify ttyS ordering, console on COM1, CBUS UART availability, and big-endian CBUS access mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-setup.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-setup.c

### Purpose
`malta-setup.c` performs Malta platform memory and device setup after PROM initialization. It installs DT data, reserves standard IO resources, configures DMA/coherency, PCI clock hints, optional floppy and VGA console setup, and board quirks.

### Important APIs, Types, And Functions
`get_system_type()` returns `"MIPS Malta"`. `plat_get_fdt()` returns `__dtb_start`. `plat_mem_setup()` is the main setup routine. Helpers include `plat_setup_iocoherency()`, `pci_clock_check()`, `bonito_quirks_setup()`, `fd_activate()`, and optional `screen_info_setup()`.

### Control Flow
`plat_mem_setup()` obtains and shims the FDT, calls `__dt_setup_arch()`, initializes PCI BIOS, inserts standard PC IO resources, enables DMA channel 4, applies Bonito debug/coherency quirks, detects IOCU/Bonito hardware coherency, appends `pci_clock=` when jumpers report a non-33 MHz PCI clock, and sets up optional floppy/VGA state.

### State, Persistence, And Dependencies
Persistent state includes DT setup, IO resource reservations, DMA default coherency, PCI command-line updates, SuperIO state, and screen info. Dependencies include Malta revision state, firmware command line, Bonito/ROCit registers, PCI, DMA, and optional console/floppy drivers.

### Integration Points
This file connects early Malta controller setup with generic PCI, DMA, DT, console, and platform device probing.

### Risks
Command-line mutation must fit available buffer space. Coherency detection changes DMA behavior globally. IOCU disabled by switch falls back to software coherency. PCI clock hints affect IDE timing and must not duplicate user-supplied `pci_clock=`.

### Test Signals
Boot Malta under Bonito and IOCU-capable ROCit, check DMA coherency mode logs, PCI enumeration, `pci_clock=` command line, resource reservations, floppy activation, and VGA console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-time.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-time.c

### Purpose
`malta-time.c` initializes Malta timekeeping, RTC access, CPU/GIC frequency estimation, timer IRQ routing, and performance/FDC interrupt routing.

### Important APIs, Types, And Functions
`plat_time_init()` initializes RTC, estimates frequencies, prints CPU/GIC clocks, starts PIT and timer probing. `estimate_frequencies()` measures CP0 Count and GIC counter against CMOS RTC update edges. `get_c0_compare_int()`, `get_c0_perfcount_int()`, and `get_c0_fdc_int()` choose interrupt lines. `read_persistent_clock64()` reads MC146818 time.

### Control Flow
RTC is set to 32 KHz and run mode. Frequency estimation disables interrupts, synchronizes with RTC update-in-progress edges, samples CP0/GIC counters across elapsed seconds, and restores interrupts. Timer/perf IRQs are routed through VEIC handlers, GIC helpers, or CPU IRQs. If GIC timer is present, the DT `clock-frequency` property is updated before timer probing.

### State, Persistence, And Dependencies
Persistent state includes `mips_hpt_frequency`, `gic_frequency`, selected timer/perf IRQ globals, and optional OF property storage. Dependencies include CMOS RTC, GIC, VEIC, CP0 Count, PIT, timer framework, and Malta interrupt constants.

### Integration Points
Generic MIPS clocksource/clockevent setup calls these platform hooks. Perf event and FDC code use the exported interrupt selectors.

### Risks
RTC polling loops assume functional CMOS and can stall on broken emulation. Frequency rounding and 20KC/25KF count-rate handling must be correct. Some cores advertise FDC routing that Malta bitstreams do not wire, so the function explicitly rejects them.

### Test Signals
Boot with and without GIC, VEIC, PIT, and GIC clocksource; compare measured CPU/GIC frequencies to expected values; read persistent clock; test perf interrupts and FDC IRQ selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/n64/Makefile

### Purpose
`n64/Makefile` builds Nintendo 64 platform initialization and IRQ support.

### Important APIs, Types, And Functions
It sets `obj-y := init.o irq.o`.

### Control Flow
When the N64 platform is selected, Kbuild links both objects into the kernel.

### State, Persistence, And Dependencies
Build state is the linked platform support objects. Dependencies are the surrounding MIPS platform Kbuild selection.

### Integration Points
The Makefile connects `init.c` platform setup and `irq.c` CPU IRQ initialization to the kernel build.

### Risks
No conditional object selection is present; any missing dependency must be handled by the C files or platform Kconfig.

### Test Signals
Build the N64 platform and verify both platform hooks link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/init.c -->
## sources/distributed-fs/ceph-client/arch/mips/n64/init.c

### Purpose
`n64/init.c` implements basic Nintendo 64 platform setup: command line initialization, memory resource bounds, memblock RAM declaration, fixed timer frequency, platform devices for audio/cart/controller, and a simple framebuffer.

### Important APIs, Types, And Functions
`prom_init()` initializes firmware command line. `plat_mem_setup()` sets IO memory resource bounds and adds 8 MiB RAM. `plat_time_init()` sets `mips_hpt_frequency`. `n64_platform_init()` registers `n64audio`, `n64cart`, `n64joy`, programs RDP video registers, allocates framebuffer memory, and registers `simple-framebuffer`.

### Control Flow
At arch initcall, device resources are constructed for MI/AI/PI/SI register banks and RCP IRQ, then platform devices are registered. A DMA-capable framebuffer buffer is allocated with extra bytes, physically aligned to 64 bytes, and its address is written into the RDP register sequence for 320x240 NTSC output.

### State, Persistence, And Dependencies
Persistent state includes memblock RAM, IO resource boundaries, registered platform devices, allocated framebuffer memory, RDP register values, and timer frequency. Dependencies include platform device core, simplefb, raw MMIO writes through CKSEG1, firmware command-line helper, and MIPS CPU IRQ numbering.

### Integration Points
N64-specific audio/cart/joy drivers bind to these platform devices. The simple framebuffer gives early display output without a full DRM driver.

### Risks
The framebuffer allocation is never freed, by design, but allocation failure disables simplefb. RAM is hard-coded to 8 MiB with a note that bootloader blocks 4 MiB config. Video timing is fixed to NTSC 320x240 and the RDP register programming assumes hardware state.

### Test Signals
Boot on N64 or accurate emulator, verify 8 MiB memory map, timer rate, platform device probing, RCP IRQ delivery, and simplefb output with correct physical alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/n64/irq.c

### Purpose
`n64/irq.c` initializes the Nintendo 64 platform's CPU interrupt controller.

### Important APIs, Types, And Functions
`arch_init_irq()` calls `mips_cpu_irq_init()`.

### Control Flow
During IRQ initialization, the generic MIPS CPU IRQ controller is initialized. N64-specific interrupt device details are left to platform devices/drivers.

### State, Persistence, And Dependencies
Persistent state is the CPU IRQ domain/descriptors created by `mips_cpu_irq_init()`. Dependencies include `asm/irq_cpu.h` and Linux IRQ core headers.

### Integration Points
The IRQ numbers used in `n64/init.c` for RCP and timer IRQs rely on this CPU IRQ setup.

### Risks
This minimal setup assumes all needed interrupts arrive through standard MIPS CPU interrupt lines. Additional cascade controllers would require more platform-specific code.

### Test Signals
Boot N64 platform and verify timer interrupt, RCP IRQ delivery, and platform device IRQ requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/n64/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/net/Makefile

### Purpose
`arch/mips/net/Makefile` selects MIPS eBPF JIT compiler objects.

### Important APIs, Types, And Functions
When `CONFIG_BPF_JIT` is enabled, it builds `bpf_jit_comp.o` plus `bpf_jit_comp32.o` for 32-bit kernels or `bpf_jit_comp64.o` otherwise.

### Control Flow
Kbuild evaluates `CONFIG_32BIT` to select the ABI-width-specific backend alongside the common JIT file.

### State, Persistence, And Dependencies
Build output is the MIPS BPF JIT implementation. Dependencies include the BPF JIT config and either 32-bit or 64-bit MIPS backend source.

### Integration Points
The selected objects provide `bpf_int_jit_compile()` and backend `build_prologue()`, `build_epilogue()`, and `build_insn()` implementations used by the Linux BPF core.

### Risks
Exactly one width-specific backend must be selected. Misconfigured builds would leave common code without backend symbols.

### Test Signals
Build 32-bit and 64-bit MIPS kernels with `CONFIG_BPF_JIT=y`, verify selected object lists, and run BPF selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.c -->
## sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.c

### Purpose
`bpf_jit_comp.c` implements common MIPS eBPF JIT logic shared by 32-bit and 64-bit backends. It manages register save/restore helpers, ALU and jump emission, atomic 32-bit sequences, branch relaxation, multi-pass offset convergence, executable image allocation, and the public JIT compile entry.

### Important APIs, Types, And Functions
Public/common helpers include `push_regs()`, `pop_regs()`, `get_target()`, `get_offset()`, `emit_mov_i()`, `emit_mov_r()`, `valid_alu_i()`, `rewrite_alu_i()`, `emit_alu_i()`, `emit_alu_r()`, `emit_atomic_r()`, `emit_cmpxchg_r()`, `emit_bswap_r()`, `valid_jmp_i()`, `setup_jmp_i()`, `setup_jmp_r()`, `finish_jmp()`, `emit_jmp_i()`, `emit_jmp_r()`, `emit_ja()`, `emit_exit()`, `bpf_jit_needs_zext()`, and `bpf_int_jit_compile()`.

### Control Flow
Compilation first dry-runs the body to discover register/stack use. A second phase builds the prologue and repeatedly dry-runs the body to compute instruction offsets, converting out-of-range PC-relative branches into inverted-branch plus absolute-jump sequences until descriptors converge. It then emits the epilogue, allocates JIT memory filled with trap instructions, performs the real code generation pass, fills line info, locks the image read-only executable, flushes icache, optionally dumps code, and marks the program jited.

### State, Persistence, And Dependencies
State lives in `struct jit_context`: BPF program, descriptor table, target buffer, indices, branch conversion count, accessed/clobbered masks, and stack sizes. Persistent output is the executable BPF image and updated `struct bpf_prog`. Dependencies include Linux BPF verifier/JIT APIs, MIPS uasm, CPU feature/ISA flags, cache flush, JIT binary allocator, and backend-specific prologue/epilogue/instruction builders.

### Integration Points
The Linux BPF core calls `bpf_int_jit_compile()`. `bpf_jit_comp32.c` or `bpf_jit_comp64.c` supply width-specific instruction translation. The verifier is told zero-extension is needed through `bpf_jit_needs_zext()`.

### Risks
Branch offset convergence is subtle; failure falls back to interpreter after warning. Absolute jumps require target and PC to share upper address bits. Atomic LL/SC loops include R10000 and Loongson workarounds. MIPS 32-bit ALU sign extension means verifier-inserted zext is required. Any wrong descriptor index corrupts jump targets or line info.

### Test Signals
Run BPF selftests on 32-bit and 64-bit MIPS, especially long programs with far branches, atomics, cmpxchg, byte swaps, signed/unsigned JMP32, JIT line info, zext insertion, `bpf_jit_enable > 1` dumps, and allocation failure fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.h -->
## sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.h

### Purpose
`bpf_jit_comp.h` declares shared MIPS eBPF JIT register constants, internal descriptor flags, the JIT context structure, emission macros, errata workarounds, and common/backend function interfaces.

### Important APIs, Types, And Functions
It defines MIPS register numbers, `MIPS_JMP_MASK`, `JIT_MAX_ITERATIONS`, `JIT_JNSET`, `JIT_JNOP`, `JIT_DESC_CONVERT`, `struct jit_context`, `emit()`/`__emit()`, LL/SC and JALR workaround macros, `access_reg()`, `clobber_reg()`, all common emitter prototypes, and backend hooks `build_prologue()`, `build_epilogue()`, and `build_insn()`.

### Control Flow
The header itself has no runtime control flow beyond inline helpers. The `emit` macro either writes an instruction through `uasm_i_*` when the target buffer exists or just increments `jit_index` during dry runs. Access/clobber helpers update bitmasks used by prologue/epilogue generation.

### State, Persistence, And Dependencies
Persistent state is caller-owned `struct jit_context`. Dependencies include Linux BPF types, MIPS register/ISA conventions, uasm emitters, and CPU errata config symbols.

### Integration Points
Common JIT code and 32-bit/64-bit backends include this header to share ABI, register, and helper contracts.

### Risks
Register aliases differ between o32 and n64 argument registers. The emit macro must keep dry-run and real-run instruction counts identical. Errata macros change branch offsets and loop sizes, so code using fixed offsets must include `LLSC_offset`.

### Test Signals
Compile both width backends, inspect prologue save masks and stack sizes, run atomic BPF programs on errata-enabled builds, and compare dry-run instruction counts against emitted code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp.h -->
