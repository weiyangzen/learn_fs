# sources/distributed-fs/ceph-client/arch/powerpc/mm subset-b-000791 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_tlb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_tlb.c

Purpose: implements radix MMU TLB, page-walk-cache, LPID, PID, and hypervisor partition invalidation for Book3S64. The file is the low-level bridge between generic Linux TLB APIs, KVM/pseries invalidation contracts, and Power ISA `tlbie`/`tlbiel` instructions.

Important APIs and control flow: `radix__flush_tlb_mm()`, `radix__flush_all_mm()`, page/range variants, `radix__tlb_flush()`, LPID helpers, THP PMD/PUD flushes, and `do_h_rpt_invalidate_prt()` choose local `tlbiel`, global `tlbie`, multicast IPI, or `pseries_rpt_invalidate()` depending on SMP state, GTSE availability, coprocessor users, page size, and range size. The implementation wraps instruction forms with barriers, POWER9 erratum fixups, and debugfs-tunable single-page ceilings.

State and dependencies: persistent state lives in `mm->context.id`, `mm_cpumask`, `active_cpus`, `copros`, per-CPU trim clocks, and debugfs thresholds. It depends on Power ISA features, pseries hypercalls, KVM HV, MMU page-size definitions, and MMU notifier secondary TLB hooks. Risks are ordering bugs, under-flushing coprocessor/nMMU translations, missing PWC invalidations after table frees, and regressions in lazy TLB shootdown trimming. Test signals include TLB stress, THP collapse/split, KVM H_RPT_INVALIDATE, pseries without GTSE, POWER9 erratum systems, and mmu notifier secondary TLB tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/slb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/slb.c

Purpose: manages Segment Lookaside Buffer entries for Book3S64 hash MMU kernels, including bolted kernel entries, user SLB miss handling, context switch flushing/preloading, and diagnostic dumps.

Important APIs and control flow: boot parameters `stress_slb` and `no_slb_preload` toggle static keys. `slb_initialize()` builds bolted linear and stack mappings. `switch_slb()` runs with hard IRQs disabled, invalidates user entries by SLBIA or cached SLBIEs, copies the next `mm` to PACA, ages/preloads recorded user ESIDs, and synchronizes before user return. `do_slb_fault()` routes kernel-region misses to `slb_allocate_kernel()` and user misses to `slb_allocate_user()`, which validates regions, chooses segment size/page size, allocates an SLB slot, writes `slbmte`, and updates PACA caches.

State and dependencies: key state is PACA `slb_cache`, bitmaps, shadow save area, `stab_rr`, thread preload rings, `mmu_slb_size`, and per-mm hash context. It depends on slice page-size selection, VSID generation, mmu feature flags, SPU SLB flushing, and text-patching/static keys. Risks are recursive kernel SLB faults, stale shadow entries during hypervisor preemption, bitmap/SLB divergence, and preloading stale user mappings. Test signals include stress SLB boot mode, context-switch heavy workloads, hugepage slice mappings, PMU interrupt coverage, and SLB dump paths after faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/slb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/slice.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/slice.c

Purpose: implements hash-MMU address-space slices, which assign page-size properties to low and high virtual-address meta-segments and steer mmap placement for normal and hugetlb mappings.

Important APIs and control flow: `slice_get_unmapped_area()` validates alignment, expands the SLB address limit when required, computes masks of already-good, compatible, and free slices, searches bottom-up or top-down through available ranges, allocates extended contexts if high addresses require them, converts empty slices to the requested MMU page size, and flushes SLBs for affected CPUs. `arch_get_unmapped_area*()` delegates here unless radix is enabled. `get_slice_psize()`, `slice_init_new_context_exec()`, `slice_setup_new_exec()`, and `slice_set_range_psize()` expose page-size lookup and initialization.

State and dependencies: state is packed in `mm->context` low/high slice arrays, per-page-size slice masks, SLB address limits, and a global `slice_convert_lock`. It depends on VMA gap lookup, hugetlb hstates, SPU SLB flushing, extended context allocation, and hash-only SLB flushing. Risks are incorrect MAP_FIXED failure semantics, races during 64K-to-4K demotion, stale SLB entries after conversion, and high-limit mistakes around `DEFAULT_MAP_WINDOW`/`TASK_SIZE`. Test signals include mmap hint/fixed/topdown cases, hugepage-only ranges, 32-bit exec setup, and mixed 4K/64K kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/slice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/subpage_prot.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/subpage_prot.c

Purpose: provides the Book3S64 hash-MMU `subpage_prot` syscall, adding 4K subpage restrictions inside larger kernel page sizes for selected user ranges.

Important APIs and control flow: `SYSCALL_DEFINE3(subpage_prot)` rejects radix, validates page alignment and task bounds, rejects hugepage-only ranges, allocates the per-mm subpage protection table on demand, optionally marks/splits THP VMAs, demotes segments to 4K, copies user protection words, and flushes corresponding HPTEs. Passing a null map clears stored restrictions through `subpage_prot_clear()`. `subpage_prot_free()` releases low and high-level protection pages during mm teardown.

State and dependencies: state lives in `mm->context.hash_context->spt`, including low-memory pointers, high-level pointer pages, and `maxaddr`. It depends on `mmap_write_lock`, page-table walking, HPTE invalidation through `pte_update()`, THP split helpers, `demote_segment_4k()`, and user-copy APIs. Risks include partially updated maps if user copy faults after lock dropping, stale HPTEs if flushing misses ranges, THP interaction mistakes, and memory leaks in sparse high-range tables. Test signals are syscall ABI tests, clear/set cycles, THP split coverage, invalid alignment/range errors, and hash-vs-radix behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/subpage_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/trace.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/trace.c

Purpose: hosts tracepoint definition linkage for Book3S64 MM-related tracing, currently pulling in transparent hugepage trace event definitions when THP is enabled.

Important APIs and control flow: there are no runtime functions; the file exists so trace/event headers can instantiate tracepoint data in exactly one compilation unit. Under `CONFIG_TRANSPARENT_HUGEPAGE`, it includes `<trace/events/thp.h>`.

State and dependencies: no persistent state beyond generated tracepoint objects. It depends on kernel tracing infrastructure, THP configuration, and build-system inclusion for Book3S64. Risks are mainly build/linkage risks: duplicate tracepoint definitions if moved incorrectly, or missing THP events if omitted. Test signals are successful THP-enabled builds and ftrace/perf visibility of THP events on Book3S64 kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/cacheflush.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/cacheflush.c

Purpose: implements PowerPC instruction/data cache maintenance required after code modification, user page copy/clear, and folio cache synchronization.

Important APIs and control flow: `flush_icache_range()` first handles coherent-I-cache CPUs with a dummy `icbi`, otherwise cleans D-cache and invalidates I-cache lines or uses 44x `iccci`. `flush_dcache_icache_folio()` covers normal, highmem, BookE, and physical-address fallback paths. `clear_user_page()`, `copy_user_page()`, and `flush_icache_user_page()` integrate cache maintenance with generic user page helpers.

State and dependencies: no durable state; behavior depends on CPU feature bits, cache-line geometry, highmem configuration, MMU type, and local kmap APIs. The highmem physical flush temporarily disables data translation with carefully constrained assembly. Risks are stale executable instructions, over-invalidation on virtually tagged 44x I-caches, unsafe memory accesses while MSR_DR is disabled, and highmem alias mistakes. Test signals include module/kprobe/BPF text patch execution, self-modifying code tests, highmem user executable pages, and 44x/BookE boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/cacheflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/copro_fault.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/copro_fault.c

Purpose: handles memory faults and SLB calculations for PowerPC coprocessors such as SPU/AFU devices that access process address spaces.

Important APIs and control flow: `copro_handle_mm_fault()` validates the target `mm`, finds and locks the VMA, checks read/write access against VMA flags, calls `handle_mm_fault()`, translates `VM_FAULT_*` errors to `-ENOMEM` or `-EFAULT`, and unlocks unless the fault completed. Under hash MMU, `copro_calculate_slb()` builds a `copro_slb` ESID/VSID pair for user, vmalloc, IO, and linear-map regions using slice page size and segment-size helpers.

State and dependencies: it mutates normal process page tables through the generic fault path and reads hash context/slice state to construct SLB entries. Dependencies include VMA locking, `radix_enabled()`, region-id helpers, VSID generation, and exported coprocessor ABI structures. Risks are divergence from `do_page_fault()`, underchecking pkeys or execute faults, stale SLB calculations after slice conversion, and incorrect handling of completed/retry faults. Test signals include AFU/SPU page fault tests, invalid access propagation, radix-vs-hash behavior, and SLB calculation for all region IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/copro_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/dma-noncoherent.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/dma-noncoherent.c

Purpose: provides cache synchronization hooks for non-coherent DMA on PowerPC.

Important APIs and control flow: `arch_sync_dma_for_device()` and `arch_sync_dma_for_cpu()` delegate to `__dma_sync_page()`, which converts physical addresses to pages, handles offsets, and synchronizes the requested buffer. `__dma_sync()` chooses invalidate, clean, or flush according to DMA direction and preserves dirty neighboring bytes by falling back to full flush when FROM_DEVICE buffers are not cache-line aligned. `arch_dma_prep_coherent()` flushes newly allocated coherent pages.

State and dependencies: no persistent state; it depends on page-to-virtual mapping, highmem `kmap_atomic()` when required, D-cache range primitives, DMA direction semantics, and local IRQ protection for highmem mappings. Risks are data corruption from invalidating unaligned dirty cache lines, missing highmem segments across page boundaries, and unnecessary cache churn on bidirectional mappings. Test signals include non-coherent DMA drivers, unaligned buffer DMA tests, highmem multi-page buffers, and DMA API debug instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/dma-noncoherent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/drmem.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/drmem.c

Purpose: parses, tracks, walks, and updates pseries dynamic-reconfiguration memory LMB metadata from device-tree properties.

Important APIs and control flow: `walk_drmem_lmbs_early()` and `walk_drmem_lmbs()` decode v1 `ibm,dynamic-memory` and v2 `ibm,dynamic-memory-v2` formats, passing synthesized `drmem_lmb` records to callbacks. `drmem_init()` builds the global `drmem_info` LMB array at late init. `drmem_update_dt()` clones and rewrites dynamic-memory properties from in-kernel LMB state. `drmem_update_lmbs()` handles hypervisor/device-tree property updates while avoiding feedback from self-generated updates.

State and dependencies: persistent state includes `drmem_info`, LMB size/count/array, root cell sizes, and `in_drmem_update`. It depends on OF flat/live tree APIs, endian conversion, memblock, pseries hotplug conventions, and optional usable-memory properties for kdump. Risks are v1/v2 format drift, incorrect sequence compression, LMB flag leakage from internal reserved bits, missing allocation cleanup, and races with device-tree notifiers. Test signals include pseries memory hotplug, kdump usable-memory parsing, live DT property updates, and LMB size edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/drmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/fault.c

Purpose: implements the PowerPC page-fault and bad-segment exception path, mapping architecture-specific fault bits to generic MM fault handling, signals, or kernel oops recovery.

Important APIs and control flow: `___do_page_fault()` handles debugger/kprobe short-circuits, hardware bad-fault bits, KUAP/KUEP/KFENCE kernel-fault checks, fault-disabled contexts, perf accounting, the RCU `lock_vma_under_rcu()` fast path, fallback `lock_mm_and_find_vma()`, VMA permission/pkey checks, `handle_mm_fault()` retry/completed handling, and SIGBUS/SIGSEGV/OOM conversion. `bad_page_fault()` applies exception-table fixups before dying, and Book3S64 segment interrupt handlers convert SLB/radix addressing failures.

State and dependencies: state touched includes task trap fields, VMA locks, `mmap_lock`, CMO page-in counters, perf events, and page-fault flags. It depends on DSISR/ESR definitions, radix/hash differences, pkeys, KUAP, KFENCE, kprobes, extables, and generic mm fault APIs. Risks are deadlocks while faulting under locks, misclassified KUAP faults, incorrect retry accounting, and signal mismatches for hardware poison. Test signals include user/kernel fault tests, pkey cases, KUAP copy helpers, KFENCE faults, THP/hugetlb faults, and fault injection under fatal signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/hugetlbpage.c

Purpose: provides common PowerPC HugeTLB support, including huge PTE allocation, valid hugepage-size discovery, pseries boot-time gigantic page handling, and CMA sizing.

Important APIs and control flow: `huge_pte_offset()` finds existing huge PTEs via the Linux page-table walker. `huge_pte_alloc()` allocates folded or real PUD/PMD/PTE levels according to hugepage size and has an 8xx contiguous-PTE path. `pseries_add_gpage()` records firmware-provided gigantic pages until `pseries_alloc_bootmem_huge_page()` can add them to `huge_boot_pages`. `hugetlbpage_init()` registers all hardware-supported huge sizes unless disabled or unsupported by hash MMU.

State and dependencies: state includes `hugetlb_disabled`, early `gpage_freearray`, `nr_gpages`, huge hstates, and MMU page-size definitions. It depends on firmware LPAR detection, radix/hash mode, memblock, hugetlb core, and pte allocation helpers. Risks are registering unsupported sizes, exhausting the fixed gigantic-page array, 8xx contiguous mapping mistakes, and wrong CMA order for radix versus 16G hash pages. Test signals include hugetlb boot parameters, pseries expected-pages, 8xx hugepages, multiple hstates, and CMA reservation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/init-common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/init-common.c

Purpose: centralizes shared PowerPC MM initialization state, KUP boot toggles, and page-table slab cache setup.

Important APIs and control flow: early parameters `nosmep` and `nosmap` disable KUEP/KUAP. `setup_kup()` calls architecture implementations of KUAP and KUEP setup. `pgtable_cache_add()` creates zeroing slab caches for higher-level page tables and hugepage page tables, using order-specific constructors and alignment sufficient for RCU freeing metadata. `pgtable_cache_init()` installs caches needed by the configured page-table geometry.

State and dependencies: exported state includes `memstart_addr`, `kernstart_addr`, `kernstart_virt_addr`, `disable_kuep`, `disable_kuap`, optional KFENCE flags, and `pgtable_cache[]`. Dependencies include SMP boot CPU checks, KUP helpers, slab allocation, PGD/PMD/PUD cache index macros, and KVM HV consumers of page-table caches. Risks are misaligned cache allocations, missing constructor coverage if `MAX_PGTABLE_INDEX_SIZE` changes, boot-parameter weakening of protections, and incorrect setup order before allocations. Test signals include boot logs for KUP activation, KVM HV module load, page-table allocation stress, and nosmap/nosmep boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/init-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/init_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/init_32.c

Purpose: performs 32-bit PowerPC MMU initialization, lowmem sizing, linear RAM mapping, early ioremap base setup, KASAN setup, and KUP enablement.

Important APIs and control flow: `MMU_init()` computes `total_memory`, `total_lowmem`, and `lowmem_end_addr` from memblock and `memstart_addr`; allows e500 to reduce lowmem to CAM coverage; enforces configured lowmem limits; calls `MMU_init_hw()`, `mapin_ram()`, initializes `ioremap_bot`, unmaps boot text if applicable, runs `kasan_mmu_init()`, enables KUP, patches MMU feature fixups, and raises the memblock allocation limit to mapped lowmem.

State and dependencies: state includes `total_memory`, `total_lowmem`, `lowmem_end_addr`, `__max_low_memory`, `boot_mapsize`, optional `virt_phys_offset`, and `agp_special_page`. It depends on platform progress callbacks, nohash/hash-specific `MMU_init_hw()` and `mapin_ram()`, memblock limits, KASAN, KUP, and feature fixup patching. Risks are mapping less memory than later allocators assume, wrong highmem enforcement, e500 CAM mis-sizing, and KASAN/KUP ordering regressions. Test signals are 32-bit boots across 8xx/44x/e500/book3s, highmem configs, relocatable kernels, and early ioremap warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/init_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/init_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/init_64.c

Purpose: handles 64-bit PowerPC early MMU feature selection, vmemmap population/freeing, memory-block-size probing, and radix/hash devicetree initialization.

Important APIs and control flow: sparse vmemmap paths allocate backing pages, track mappings in `vmemmap_list`, create/remove mappings, and delegate to radix-specific implementations when radix is active. `mmu_early_init_devtree()` parses `disable_radix`, DT PID/LPID bit widths, hypervisor vector-5 MMU/GTSE support, memory block size, invokes radix or hash early setup, initializes HugeTLB defaults, and panics if no supported MMU type remains.

State and dependencies: persistent state includes `vmemmap_list`, backing free-list counters, `mmu_lpid_bits`, `mmu_pid_bits`, `disable_radix`, and `memory_block_size`. Dependencies include flat DT scanning, memblock/altmap allocation, sparsemem subsection validity, pseries/powernv memory layout, radix/hash setup functions, and KVM LPID export. Risks include vmemmap backing leaks on mapping failure, wrong altmap boundary checks, radix forced/disabled mismatch under a hypervisor, and memory block sizes incompatible with hotplug. Test signals include memory hotplug add/remove, devdax altmap, pseries guests with vector-5 variants, radix-disabled boots, and sparsemem subsection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/init_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap.c

Purpose: provides architecture-generic PowerPC ioremap entry points and early page-by-page kernel mapping support shared by 32-bit and 64-bit implementations.

Important APIs and control flow: `ioremap()`, `ioremap_wc()`, `ioremap_coherent()`, and `ioremap_prot()` select cacheability protections and call `__ioremap_caller()`. `ioremap_prot()` marks writable kernel mappings dirty before mapping. `early_ioremap_range()` maps a physical range at a requested effective address using `map_kernel_page()` with NX protection.

State and dependencies: `ioremap_bot` tracks the early allocator frontier and is exported. The file depends on pgprot cacheability helpers, caller-address capture, `map_kernel_page()`, and platform-specific `__ioremap_caller()` definitions. Risks include wrong cache attributes for device memory, executable early I/O mappings if NX wrapping is broken, and early allocator overlap if `ioremap_bot` is misinitialized by arch init. Test signals include driver MMIO mappings, write-combining mappings, early console/boot ioremap users, and page-table attribute inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap_32.c

Purpose: implements 32-bit PowerPC `__ioremap_caller()` and `iounmap()`, including ISA address adjustment and early top-down ioremap allocation.

Important APIs and control flow: addresses below 16 MiB are treated as ISA memory and adjusted by `_ISA_MEM_BASE`. The mapping is page-aligned, normal RAM is rejected after slab/high_memory are available, existing BAT/LTLB/CAM block mappings are reused via `p_block_mapped()`, late mappings use `generic_ioremap_prot()`, and early mappings allocate downward from `ioremap_bot` through `early_ioremap_range()`. `iounmap()` ignores block-mapped addresses and otherwise calls `generic_iounmap()`.

State and dependencies: relies on `ioremap_bot`, high_memory, `page_is_ram()`, block mapping lookups from subarch MMU code, and vmalloc availability. Risks are accidentally remapping RAM as device memory, early mappings colliding with reserved ioremap space, incorrect ISA offset assumptions, and leaving early mappings permanent. Test signals include 32-bit PCI/ISA MMIO drivers, crash dump RAM remap exceptions, BAT/CAM reuse checks, and early boot warning coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap_64.c

Purpose: implements 64-bit PowerPC `__ioremap_caller()` and `iounmap()` with early upward allocation from `ioremap_bot`.

Important APIs and control flow: it rejects mappings using the unsupported `H_PAGE_4K_PFN` hack, page-aligns physical addresses and offsets, rejects zero/physical-null mappings, uses `generic_ioremap_prot()` after slab is available, and otherwise warns and installs early page mappings at the current `ioremap_bot`, advancing it upward with a guard page. `iounmap()` ignores pre-slab calls and later delegates to `generic_iounmap()`.

State and dependencies: state is the shared `ioremap_bot`; dependencies include generic vmalloc ioremap, `early_ioremap_range()`, page-table protection encodings, and slab availability. Risks are early mapping leaks, incorrect handling of page-offset returns, overlap with vmalloc reservation, and refusing legitimate callers that accidentally pass 4K PFN flags. Test signals include early MMIO users, 64-bit PCI/firmware mappings, `ioremap_prot()` attribute tests, and boot logs for early-use warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/8xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/8xx.c

Purpose: provides 8xx-specific KASAN shadow population optimized for 8 MiB, 512 KiB, and 16 KiB mapping capabilities.

Important APIs and control flow: `kasan_init_region()` allocates shadow backing with 8 MiB alignment, maps aligned portions through `kasan_init_shadow_8M()`, falls back to generic shadow page-table initialization for the tail, writes huge or base PTEs, and flushes the kernel TLB range. `kasan_init_shadow_8M()` replaces early shadow PMDs with real PTE pages and marks PMDs as 8 MiB huge mappings.

State and dependencies: state is page-table mappings under `init_mm` and memblock-allocated backing memory. It depends on `kasan_mem_to_shadow()`, early shadow PTE detection, `pte_mkhuge()`, 8xx huge PTE encodings, and TLB flushes. Risks are alignment mistakes around 8 MiB boundaries, partially populated shadow if allocation fails, and stale early shadow aliases. Test signals include 8xx KASAN boot, shadow coverage for lowmem ranges, KASAN fault reports, and TLB flush validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/Makefile

Purpose: selects architecture-specific PowerPC KASAN initialization objects while disabling instrumentation on the KASAN implementation itself.

Important APIs and control flow: `KASAN_SANITIZE := n` and `KCOV_INSTRUMENT := n` prevent recursive sanitizer/coverage instrumentation. Object selection adds common 32-bit init, 8xx specialization, Book3S32 BAT specialization, and Book3S64 or Book3E64 initializers according to configuration.

State and dependencies: no runtime state. It depends on Kconfig symbols `CONFIG_PPC32`, `CONFIG_PPC_8xx`, `CONFIG_PPC_BOOK3S_32`, `CONFIG_PPC_BOOK3S_64`, and `CONFIG_PPC_BOOK3E_64`. Risks are recursive KASAN faults if instrumentation flags are removed, missing platform initializer objects, and duplicate symbol definitions if mutually exclusive configs are wrong. Test signals are successful KASAN builds for every PowerPC MMU family and early boot before KASAN is fully initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/book3s_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/book3s_32.c

Purpose: implements Book3S 32-bit KASAN shadow mapping, preferring BAT mappings for large aligned shadow ranges and page tables for the remainder.

Important APIs and control flow: `kasan_init_region()` computes the shadow range, repeatedly finds free BATs and suitable block sizes, allocates physical backing, installs BATs, updates BAT hardware, allocates any remaining backing, initializes shadow page tables, clears early shadow mappings over BAT-backed parts, writes per-page PTEs for the rest, flushes TLBs, and zeroes the shadow.

State and dependencies: state includes BAT entries, `init_mm` page tables, memblock allocations, and early shadow mappings. It depends on `bat_block_size()`, `find_free_bat()`, `setbat()`, `update_bats()`, shared 32-bit KASAN helpers, and linear alias handling. Risks are BAT exhaustion, incorrect clearing of early shadow PTEs, stale BAT/TLB state, and holes in shadow coverage. Test signals include Book3S32 KASAN boot, BAT allocation traces, vmalloc/module shadow tests, and KASAN report generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/book3s_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_32.c

Purpose: supplies common 32-bit PowerPC KASAN early, main, and late initialization helpers used by platform specializations.

Important APIs and control flow: `kasan_early_init()` maps the entire shadow through the early shadow page. `kasan_mmu_init()` prepopulates shadow page tables for hash MMU. `kasan_init()` maps real lowmem ranges using `kasan_init_region()`, optionally initializes KASAN vmalloc shadow page tables, remaps early shadow read-only, clears it, enables reports, and calls generic KASAN init. `kasan_late_init()` unmaps vmalloc/module early shadow for KASAN_VMALLOC. Helpers update early shadow PTEs and allocate replacement PTE pages through memblock.

State and dependencies: state includes `kasan_early_shadow_page`, early shadow PTEs, `init_mm` page tables, memblock allocations, and `init_task.kasan_depth`. Dependencies include MMU feature detection, TLB flushing, lowmem bounds, and platform weak `kasan_init_region()` overrides. Risks are writeable zero shadow remaining after init, vmalloc shadow overlap, missing lowmem ranges, and early boot recursion. Test signals include 32-bit KASAN boot across hash/nohash, vmalloc KASAN tests, and lowmem-only coverage checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_book3e_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_book3e_64.c

Purpose: initializes KASAN shadow mappings for 64-bit Book3E PowerPC.

Important APIs and control flow: `kasan_early_init()` builds shared early PTE/PMD/PUD tables pointing all shadow to the early zero page. `kasan_map_kernel_page()` lazily copies early shared tables into private page-table pages before installing a real shadow PTE. `kasan_init_phys_region()` allocates backing pages for each physical memory shadow range. `kasan_init()` maps all memblocks, removes vmalloc zero shadow when enabled, remaps the early shadow page read-only, flushes the shadow TLB range, zeroes the early page, and enables generic KASAN.

State and dependencies: persistent state is page-table content under `init_mm`, early shadow table pages, and memblock-allocated shadow backing. It depends on Book3E page-table geometry, `memblock_alloc_or_panic()`, KASAN vmalloc helpers, and TLB flushing. Risks include failing to break shared early tables before writes, shadow holes for discontiguous memory, and writeable early shadow after init. Test signals include Book3E64 KASAN boot, vmalloc KASAN, sparse memblock layouts, and early fault detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_book3e_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_book3s_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_book3s_64.c

Purpose: initializes KASAN for 64-bit Book3S PowerPC, restricted to radix MMU.

Important APIs and control flow: `kasan_init()` exits with a warning if early radix is not enabled. Otherwise it maps shadow backing for each physical memblock through `map_kernel_page()`, rebuilds early shadow PTE/PMD/PUD tables, maps early zero shadow over iomap and vmemmap shadow ranges, remaps the zero page read-only, clears it with `memset()`, enables reporting through `init_task.kasan_depth`, and calls generic KASAN init. Early and late hooks are empty because Book3S64 enables virtual memory late.

State and dependencies: state includes radix kernel page tables, early shadow page/table arrays, memblock allocations, and generic KASAN state. It depends on radix address layout constants, `map_kernel_page()`, `kasan_populate_early_shadow()`, and memblock ranges. Risks are silently disabled KASAN on hash, incorrect shadow range boundaries around vmalloc/vmemmap, and cache-info sensitivity during early clear. Test signals include Book3S64 radix KASAN boot, hash warning behavior, KASAN vmalloc tests, and physical memblock shadow coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_book3s_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/maccess.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/maccess.c

Purpose: defines the PowerPC policy for `copy_from_kernel_nofault()` source validation.

Important APIs and control flow: `copy_from_kernel_nofault_allowed()` returns true only when the source pointer is a kernel address according to `is_kernel_addr()`. There is no page-table walk or exception handling here; generic nofault copy machinery performs the guarded access later.

State and dependencies: no persistent state. It depends on PowerPC address classification helpers and generic `uaccess`/nofault copy infrastructure. Risks are policy mismatch with special kernel mappings that are not classified as kernel addresses, or allowing aliases that should not be inspected. Test signals include nofault copy tests from kernel, user, vmalloc, ioremap, and invalid addresses, plus callers such as probes and diagnostics that rely on graceful failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/maccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/mem.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/mem.c

Purpose: contains common PowerPC memory initialization, hotplug linear mapping hooks, zone setup, initmem freeing, system RAM resource registration, strict `/dev/mem`, and execmem layout.

Important APIs and control flow: hotplug paths serialize `create_section_mapping()`/`remove_section_mapping()` with `linear_mapping_mutex`, add/remove generic pages, update `max_pfn`/`high_memory`, and flush vmalloc aliases. `paging_init()` configures highmem fixmaps, prints RAM/hole data, sets DMA zone limits, and registers nosave holes. `arch_mm_preinit()` reserves CMA for fadump/kdump/KVM, initializes SWIOTLB bottom-up when needed, runs KASAN late init, and fixes e500 CAM indices. `execmem_arch_setup()` chooses executable allocation ranges and protections.

State and dependencies: state includes `memory_limit`, `zone_dma_limit`, max PFNs, highmem globals, iomem resources, and execmem info. Dependencies span memblock, NUMA, RTAS/fadump/kdump/KVM CMA, SWIOTLB, KASAN, ftrace, and generic memory hotplug. Risks include stale linear mappings during hot-remove, wrong DMA zone limits, `/proc/iomem` resource leaks, and executable memory range/protection mistakes. Test signals include memory hotplug, suspend nosave holes, strict devmem tests, module/kprobe allocation, and kdump/fadump reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/mmu_context.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/mmu_context.c

Purpose: implements the common context-switch wrapper `switch_mm_irqs_off()` and non-Book3S64 mmap-exit cleanup.

Important APIs and control flow: the switch path marks the target `mm` active on the current CPU, increments active CPU accounting, issues a full barrier that pairs with TLB invalidation, updates subarchitecture PGD/PID tracking in the task or PACA, stops Altivec streams, calls membarrier handling when appropriate, and delegates hardware context switching to `switch_mmu_context()`. Non-Book3S64 `arch_exit_mmap()` frees stored PTE fragments.

State and dependencies: state touched includes `mm_cpumask`, `mm->context.active_cpus`, task thread PGD/SR/PID fields, PACA PGD, and PTE fragments. It depends on CPU hotplug-safe current CPU IDs, Altivec feature flags, membarrier, and subarch `switch_mmu_context()`. Risks are missing memory barriers causing stale TLB entries after PTE clearing, incorrect active CPU counts, and PGD/PID tracking mismatches on KUAP BookE. Test signals include context-switch stress, membarrier tests, lazy TLB/mm teardown tests, and PPC32/Book3E64 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/mmu_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/mmu_decl.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/mmu_decl.h

Purpose: declares internal PowerPC MMU functions and shared globals used across architecture MM source files.

Important APIs and control flow: it exposes nohash local/global TLB invalidation helpers, 32-bit mapping initialization hooks, e500 CAM/KASLR routines, block-mapping lookup APIs, strict RWX marking hooks, 8xx IMMR mapping, debug-pagealloc/KFENCE helper, hotplug section mapping, and hash kernel page toggling. Several functions become inline no-ops when their architecture family is not enabled.

State and dependencies: declared state includes memory sizing globals, e500 `TLBCAM[]`, and architecture routines implemented in nohash/hash files. It depends heavily on Kconfig to select correct inline versus extern definitions and includes trace support for nohash TLB operations. Risks are ABI drift between declarations and implementations, incorrect no-op selection hiding missing functionality, and trace/invalidation prototype mismatches. Test signals are allmodconfig-style builds across PowerPC MMU families, sparse/prototype checks, and link coverage for hotplug, KASLR, e500, 8xx, and Book3S variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/mmu_decl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/44x.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/44x.c

Purpose: initializes low-level nohash MMU mappings for 44x/47x processors by pinning lowmem TLB entries and patching TLB miss handler watermarks.

Important APIs and control flow: `MMU_init_hw()` patches 44x high-water constants and flushes I-cache. `mmu_mapin_ram()` pins 256 MiB lowmem entries not covered by the initial boot mapping, using `ppc44x_pin_tlb()` or `ppc47x_pin_tlb()`, then records 47x bolted entries. SMP secondary init repeats the pinning path under strict early constraints. `setup_initial_memory_limit()` caps early memblock allocations to the boot-pinned range.

State and dependencies: state includes `tlb_44x_index`, `tlb_44x_hwater`, `icache_44x_need_flush`, and `tlb_47x_boltmap`. Dependencies include SPR accessors, text-patching sites in TLB miss handlers, cache flushing, memblock, and MMU feature flags. Risks are exhausting bolted slots, patching wrong instruction fields, using unavailable memory before TLBs are pinned on secondary CPUs, and incorrect first-memblock assumptions. Test signals include 44x and 47x boots, SMP bring-up, lowmem sizes beyond 256 MiB, and TLB miss handler stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/44x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/8xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/8xx.c

Purpose: initializes and later tightens 8xx nohash MMU mappings using large TLB/page-table entries for lowmem and IMMR.

Important APIs and control flow: `v_block_mapped()`/`p_block_mapped()` report IMMR and block-mapped RAM translations. `mmu_mapin_immr()` installs the IMMR fixmap once. `mmu_mapin_ram()` maps executable kernel text/init text/data using 16 KiB, 512 KiB, and 8 MiB chunks, adjusts memblock limits, and records `block_mapped_ram`. `mmu_mark_initmem_nx()` and `mmu_mark_rodata_ro()` remap ranges with stricter permissions and optionally pin TLBs. `setup_initial_memory_limit()` caps early memory to 32 MiB.

State and dependencies: state includes `block_mapped_ram` and `immr_is_mapped`. It depends on early page-table allocation, huge PTE encodings, strict RWX/debug-pagealloc/KFENCE decisions, memblock, fixmap constants, and TLB flushing/pinning. Risks include wrong permission boundary alignment, stale TLBs after remap, failure to map IMMR before users need it, and unsupported first-memblock bases. Test signals include 8xx boot, strict kernel RWX, debug_pagealloc/KFENCE configs, IMMR users, and rodata/initmem permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/Makefile

Purpose: builds the nohash PowerPC MMU implementation objects selected by platform Kconfig.

Important APIs and control flow: common nohash objects are `mmu_context.o`, `tlb.o`, `tlb_low.o`, and `kup.o`. Book3E64 adds 64-bit TLB and page-table code, 44x/8xx/e500 add their platform MMU initializers, randomization adds `kaslr_booke.o`, and e500 HugeTLB adds the preload helper. KCOV is disabled for sensitive TLB and e500 code paths needed during early boot and exception handling.

State and dependencies: no runtime state, but object inclusion controls which declarations in `mmu_decl.h` resolve. Risks include missing platform files for configured MMU families, instrumenting code that runs before coverage runtime is safe, and incomplete HugeTLB support if e500 object selection changes. Test signals are Kconfig matrix builds for Book3E64, 44x, 8xx, e500, RANDOMIZE_BASE, HUGETLB_PAGE, and KCOV-enabled kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/book3e_pgtable.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/book3e_pgtable.c

Purpose: implements Book3E nohash kernel page-table mapping helpers and vmemmap mapping for sparse memory.

Important APIs and control flow: `vmemmap_create_mapping()` writes repeated PTEs with the configured vmemmap page-size encoding. `early_alloc_pgtable()` allocates low DMA-reachable page-table pages through memblock before slab. `map_kernel_page()` walks or allocates PGD/P4D/PUD/PMD/PTE levels using slab allocators after boot or memblock before boot, installs the PTE, and issues a write barrier. `__patch_exception()` patches the second instruction of an exception vector branch to preserve single-step semantics.

State and dependencies: state is kernel page-table contents and optional vmemmap mappings. Dependencies include Book3E page-size encodings, memblock, generic page-table allocators, text patching, sparsemem, and interrupt vector symbols. Risks are page-size encoding overflow, early allocation outside accessible memory, missing synchronization after mapping, and incorrect exception branch patch offsets. Test signals include early ioremap users, vmemmap population, memory hotplug builds, exception vector patching, and Book3E64 boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/book3e_pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/e500.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/e500.c

Purpose: initializes e500 BookE TLBCAM-based lowmem mappings, exposes block mapping lookups, supports strict RWX remapping, and handles relocatable/KASLR bootstrap relocation.

Important APIs and control flow: `settlbcam()` builds MAS register images for TLB1 CAM entries. `map_mem_in_cams()` calculates aligned CAM sizes and maps kernel text/init/data with executable or read-only/data protections, then loads entries. `adjust_total_lowmem()` maps as much lowmem as CAMs allow and constrains memblock. `mmu_mark_rodata_ro()` remaps lowmem for strict RWX. Relocatable `relocate_init()` calculates `virt_phys_offset`, may perform a second AS1 relocation if `memstart_addr` differs, and invokes BookE KASLR.

State and dependencies: state includes `tlbcam_index`, `TLBCAM[]`, `tlbcam_addrs[]`, per-PACA TLB core data on 64-bit, and relocation globals. It depends on MAS SPRs, loadcam assembly helpers, memblock, strict RWX, KASLR functions, and `mmu_decl.h` interfaces. Risks are CAM exhaustion, off-by-one mapping limits, permission errors across text/data boundaries, relocation loops, and stale block mapping metadata. Test signals include e500 boot, strict RWX, relocatable kernels, KASLR, lowmem larger than CAM coverage, and ioremap block reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/e500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/e500_hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/e500_hugetlbpage.c

Purpose: preloads e500 Book3E HugeTLB entries into TLB1/CAM hardware after hugetlb page faults.

Important APIs and control flow: `__update_mmu_cache()` calls `book3e_hugetlb_preload()` when the VMA is hugetlb. The preload path disables IRQs, optionally takes an SMT-safe PACA lock, checks whether a matching TLB entry already exists, picks the next TLB1 slot, programs MAS0-MAS3/MAS7 from the VMA page size and PTE attributes, writes `tlbwe`, and unlocks. `flush_hugetlb_page()` invalidates one hugepage-sized TLB entry.

State and dependencies: state includes per-PACA or per-CPU next CAM indices, SMT lock bytes, TLB core data, and PTE dirty/access bits. It depends on MAS SPR access, `vma_mmu_pagesize()`, hugepage hstates, MMU context IDs, and nohash flush helpers. Risks are racing SMT siblings without locks, evicting critical CAM entries, preserving write permissions for clean PTEs, and missing invalidations on size mismatches. Test signals include e500 hugetlb mmap/fault/unmap, SMP/SMT hugepage stress, dirty-bit transitions, and TLB miss rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/e500_hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/kaslr_booke.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/kaslr_booke.c

Purpose: implements early physical kernel randomization for BookE/e500 relocatable kernels.

Important APIs and control flow: `kaslr_choose_location()` reads the boot command line, honors `nokaslr`, combines build/FDT/timebase entropy and an optional FDT `kaslr-seed` that is wiped after reading, computes CAM-mappable lowmem, records DTB/initrd/crash/reserved-memory regions, chooses a 64 MiB bucket and 16 KiB-aligned offset, and searches for a non-overlapping placement. `kaslr_early_init()` updates kernel start globals, creates a temporary TLB entry if needed, copies the kernel, flushes I-cache, and branches to relocated code. `kaslr_late_init()` zeros the original image.

State and dependencies: state includes global `regions`, boot command line, `kernstart_addr`, `kernstart_virt_addr`, and `is_second_reloc`. Dependencies include libfdt, memblock/CAM dry-run sizing, crashkernel parsing, cache flushing, and relocation assembly hooks. Risks are weak entropy without `kaslr-seed`, overlap calculation truncation to 32-bit ranges, incorrect reserved-memory cell parsing, and failure to clear the original kernel. Test signals include randomized and `nokaslr` boots, initrd/crashkernel/reserved-memory overlap cases, seed wiping, and relocation above 64 MiB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/kaslr_booke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/kup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/kup.c

Purpose: initializes Kernel Userspace Access Protection for nohash PowerPC MMUs.

Important APIs and control flow: `setup_kuap()` either clears `MMU_FTR_KUAP` on the boot CPU when disabled, or logs activation and calls `prevent_user_access(KUAP_READ_WRITE)` to start with user read/write access blocked.

State and dependencies: persistent state is the CPU spec MMU feature bit and hardware/software KUAP state. It depends on `CONFIG_PPC_KUAP`, SMP boot CPU checks, and `asm/kup.h` access-control primitives. Risks are leaving user access enabled during boot, inconsistent feature bits across CPUs, and disabling KUAP through `nosmap` unexpectedly widening kernel access. Test signals include KUAP boot logs, copy_to/from_user success, deliberate missing allow-user-access fault tests, and nosmap boot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/kup.c -->
