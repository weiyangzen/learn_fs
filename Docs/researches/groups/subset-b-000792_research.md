# subset-b-000792 research

This grouped report covers PowerPC MMU, page-table diagnostics, NUMA, and BPF JIT source files from `sources/distributed-fs/ceph-client`. Each source file section is delimited for deterministic reconciliation into the required per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/mmu_context.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/mmu_context.c

## Purpose
This file manages address-space context IDs for non-hash PowerPC MMUs such as 8xx, 4xx/47x, and BookE. It allocates, switches, steals, and destroys per-`mm_struct` PID/context numbers that hardware TLB entries use to distinguish user address spaces. It also maintains per-CPU stale context state for SMP so stolen context IDs are invalidated before reuse on a CPU that may still have old translations.

## Important APIs, Types, And Functions
The exported lifecycle hooks are `mmu_context_init()`, `init_new_context()`, `destroy_context()`, and `switch_mmu_context()`. `set_context()` programs `SPRN_M_TWB`/`SPRN_M_CASID` on 8xx or `SPRN_PID` on other nohash parts, gated by `kuap_is_disabled()`. Internal state is global: `context_map`, `stale_map[NR_CPUS]`, `context_mm`, `next_context`, `nr_free_contexts`, and `context_lock`. `steal_context_smp()`, `steal_context_up()`, and `steal_all_contexts()` implement replacement under different CPU-count and 8xx constraints.

## Control Flow
`mmu_context_init()` allocates context maps with `memblock`, reserves IDs below `FIRST_CONTEXT`, initializes `init_mm.context.active`, and registers CPU hotplug callbacks for stale-map allocation. `switch_mmu_context()` takes `context_lock`, updates `active` counts on SMP, reuses an existing `mm->context.id` when valid, otherwise allocates the next clear bit or steals a victim. Stolen SMP contexts are marked stale on CPUs and sibling threads from the victim `mm_cpumask()`. Before installing a context, the current CPU checks `stale_map[cpu]`, flushes that mm locally, clears sibling stale bits, updates optional `abatron_pteptrs`, and writes the hardware context.

## State And Persistence
Context IDs persist in `mm->context.id` until `destroy_context()` or stealing resets them to `MMU_NO_CONTEXT`. `context_mm[id]` links a PID back to its owning `mm`, while `context_map` is the allocation bitmap. `stale_map` is per-CPU transient invalidation debt and survives until the target CPU switches back to that context and flushes. CPU-hotplug teardown frees non-boot CPU stale maps and clears task `mm_cpumask` bits.

## Dependencies And Integration Points
This code depends on `asm/mmu_context.h`, `asm/tlbflush.h`, CPU sibling helpers, CPU hotplug, `memblock`, `mm_cpumask()`, `local_flush_tlb_mm()`, `_tlbil_all()`, and KUAP behavior. It is called by the scheduler's address-space switch path and feeds the low-level TLB flush assembly through PID values.

## Risks And Test Signals
Primary risks are stale TLB reuse, incorrect `active` accounting, CPU-hotplug stale-map lifetime, and global-lock scalability. SMP tests should stress process migration, CPU hotplug, context exhaustion, and workloads with more active address spaces than hardware PIDs. 8xx needs extra coverage because it can flush all contexts and programs `M_CASID` as `id - 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/mmu_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb.c

## Purpose
This file provides TLB flush operations for non-hash PowerPC MMUs. It defines supported software page sizes for e500 and 8xx configurations, maps page size identifiers into hardware TLB invalidate sizes, and implements local and SMP invalidation routines for mm, page, range, and kernel address spaces.

## Important APIs, Types, And Functions
The main public functions are `local_flush_tlb_mm()`, `__local_flush_tlb_page()`, `local_flush_tlb_page()`, `local_flush_tlb_page_psize()`, `flush_tlb_mm()`, `__flush_tlb_page()`, `flush_tlb_page()`, `flush_tlb_kernel_range()`, `flush_tlb_range()`, and `tlb_flush()`. `mmu_psize_defs[]` describes supported page shifts. SMP support uses `struct tlb_flush_param`, `do_flush_tlb_mm_ipi()`, `do_flush_tlb_page_ipi()`, and `tlbivax_lock`.

## Control Flow
Local flushes disable preemption, snapshot `mm->context.id`, and call `_tlbil_pid()` or `_tlbil_va()` only when the mm has a valid PID. SMP `flush_tlb_mm()` snapshots the PID, sends IPIs to CPUs in `mm_cpumask(mm)` when the mm is not core-local, and invalidates locally. `__flush_tlb_page()` chooses broadcast `tlbivax` when the CPU advertises `MMU_FTR_USE_TLBIVAX_BCAST`; otherwise it sends per-CPU IPIs and invalidates locally. `flush_tlb_range()` optimizes single-page ranges to page flushes and otherwise falls back to whole-mm flushes.

## State And Persistence
This file owns little persistent state. The e500 `next_tlbcam_idx` per-CPU variable supports CAM assignment elsewhere. Flush correctness depends on externally persistent `mm->context.id`, `mm_cpumask()`, and `mmu_psize_defs`.

## Dependencies And Integration Points
It bridges generic Linux MMU gather and VMA flush hooks to low-level nohash assembly labels such as `_tlbil_pid`, `_tlbil_va`, `_tlbil_all`, and `_tlbivax_bcast`. It integrates with hugetlb through `flush_hugetlb_page()`, with CPU feature flags for broadcast invalidation, and with device tree early init to disable broadcast invalidation on 47x cooperative partitions.

## Risks And Test Signals
Risks include PID races during context stealing, missing remote CPUs in `mm_cpumask`, broadcast invalidation errata requiring `tlbivax_lock`, and excessive whole-mm flushing for ranges. Test signals include mmap/munmap stress, hugepage faults, SMP migration, broadcast-capable 47x/e500 systems, and `tlb_flush()` paths from page-table freeing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_64e.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_64e.c

## Purpose
This file performs early MMU and TLB setup for 64-bit Book3E systems. It discovers supported hardware page sizes, configures hardware tablewalk mode for e6500-style processors, sets default MAS4 behavior, bolts the early linear map into TLBCAMs, and constrains usable memory to what the early nohash mapping can cover.

## Important APIs, Types, And Functions
Global state includes `mmu_vmemmap_psize`, `book3e_htw_mode`, `linear_map_top`, and `extlb_level_exc`; the internal `mmu_pte_psize` chooses the PTE-page TLB size. Key functions are `tlb_flush_pgtable()`, `setup_page_sizes()`, `early_init_this_mmu()`, `early_init_mmu_global()`, `early_mmu_set_memory_limit()`, `early_init_mmu()`, `early_init_mmu_secondary()`, and `setup_initial_memory_limit()`.

## Control Flow
Boot CPU init calls `early_init_mmu_global()` to set a 4K vmemmap page size, inspect `MMUCFG`, `TLB0CFG`, `TLB1CFG`, `TLB1PS`, and `EPTCFG`, mark supported direct or indirect page sizes, optionally patch TLB miss vectors to e6500 handlers, set `linear_map_top` to DRAM end, and initialize `ioremap_bot`. `early_init_this_mmu()` programs MAS4, selects 2M PTE pages in e6500 tablewalk mode or the virtual page size otherwise, maps a quarter of TLB1 CAMs for the linear map once per core, and synchronizes. Boot then enforces the linear-map memory limit. Secondary CPUs only run the per-core MMU setup.

## State And Persistence
Page-size flags in `mmu_psize_defs[]`, `book3e_htw_mode`, MAS4, and TLBCAM mappings persist for runtime TLB miss handling. `linear_map_top` becomes both a mapping bound for low-level handlers and a memory availability limit.

## Dependencies And Integration Points
This file is tightly coupled to Book3E SPRs, `map_mem_in_cams()`, exception patching via `patch_exception()`, memblock, and assembly handlers in `tlb_low_64e.S`. `tlb_flush_pgtable()` integrates page-table freeing with indirect TLB entry invalidation and calls `__flush_tlb_page()`.

## Risks And Test Signals
Major risks are misdetecting hardware tablewalk capability, using unsupported page size combinations, mapping insufficient linear memory, and failing to invalidate indirect entries when PTE pages are freed. Useful tests boot e6500 and non-HTW Book3E variants, verify memory above the bolted range is excluded, exercise vmemmap/page-table free paths, and confirm patched exception vectors handle user, kernel, and hugepage misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_64e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_low.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_low.S

## Purpose
This assembly file provides low-level TLB invalidation primitives for non-hash PowerPC CPUs. It implements the hardware-specific backends used by C flush code: invalidate by virtual address, by PID/context, all entries, broadcast invalidation, and TLBCAM loading for e500-style systems.

## Important APIs, Types, And Labels
Important exported labels include `__tlbil_va`, `_tlbil_pid`, `_tlbil_all`, `_tlbivax_bcast`, `loadcam_entry`, and `loadcam_multi`. The implementation is selected by configuration: 8xx has inline handling elsewhere, 44x/47x uses `tlbsx`/`tlbwe` or set/way sweeps, PPC_85xx uses MMUCSR0 or `tlbilx`, and BOOK3E_64 uses MAS6 plus `tlbilx`/`tlbivax`.

## Control Flow
For 44x, `__tlbil_va` writes the target TID into MMUCR, disables normal interrupts to protect MMUCR during `tlbsx`, and invalidates the matching entry. 47x all/PID invalidation sweeps sets and ways while preserving bolted entries via `tlb_47x_boltmap`; `_tlbivax_bcast` performs broadcast invalidation and includes a 476 DD2 instruction-cache workaround. PPC_85xx paths choose between `MMUCSR0_TLBFI` full invalidation and targeted `tlbilx` feature sections. BOOK3E_64 paths program MAS6 with SPID, TSIZE, and indirect-entry bits before issuing `tlbilx` or `tlbivax`.

## State And Persistence
The file manipulates architectural state directly: MSR interrupt enable, MMUCR, MAS0/1/2/3/6/7, MMUCSR0, and TLB CAM entries. `loadcam_multi()` can temporarily switch to address space 1 and installs/removes a temporary TLB entry to safely rewrite multiple CAM entries.

## Dependencies And Integration Points
The C code in `tlb.c`, `tlb_64e.c`, and platform initialization call these labels. The code depends on SPR definitions, feature-fixup sections, bolted-entry maps, TLBCAM arrays, and CPU errata flags.

## Risks And Test Signals
Risks are architecture-specific: interrupt masking must protect clobbered SPRs, bolted entries must not be invalidated accidentally, MAS6 must include correct PID/page-size/indirect fields, and broadcast invalidations require ordering (`mbar`, `tlbsync`, `sync`, `isync`). Test signals include SMP invalidation storms, 44x/47x errata systems, e500 CAM reload across mappings, and boot tests with feature-fixup alternatives enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_low.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_low_64e.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_low_64e.S

## Purpose
This file contains Book3E 64-bit TLB miss handlers. It covers bolted-linear software-loaded TLB handling, e6500 hardware tablewalk indirect-entry handling, virtual page-table second-level faults, and linear-map miss recovery.

## Important APIs, Types, And Labels
Key exception entry labels include `data_tlb_miss_bolted`, `instruction_tlb_miss_bolted`, `data_tlb_miss_e6500`, and `instruction_tlb_miss_e6500`. Internal shared labels include `tlb_miss_common_bolted`, `tlb_miss_common_e6500`, `virt_page_table_tlb_miss`, and `tlb_load_linear`. Macros `tlb_prolog_bolted` and `tlb_epilog_bolted` save and restore a compact exception frame in PACA scratch storage.

## Control Flow
Bolted handlers save volatile state, derive the faulting address from DEAR or SRR0, reject invalid effective addresses, choose user or kernel page tables, walk PGD/PUD/PMD/PTE levels, verify present/accessed/write/execute permissions, build MAS2 and MAS7/MAS3, and execute `tlbwe`. Fault cases branch to Book3E data or instruction storage handlers. e6500 handlers use hardware tablewalk with indirect TLB1 entries, maintain a per-core `tlb_per_core` lock for SMT and erratum A-008139, reuse or install indirect entries with software round-robin ESELs, and special-case huge pages as direct entries. `virt_page_table_tlb_miss` services faults on virtual page-table memory, and `tlb_load_linear` installs 1G linear mappings below `linear_map_top`.

## State And Persistence
The code mutates MAS registers, TLB entries, PACA exception frames, per-core ESEL counters, and per-core tablewalk locks. It relies on PACA fields for current and kernel page-directory pointers and on preserved first-level exception data for nested faults.

## Dependencies And Integration Points
It is selected or patched by early setup in `tlb_64e.c`, depends on PACA layout offsets, KVM BookE hooks, KUAP checks, BTB flush sections, feature-fixup macros, Book3E page-table bit encodings, and storage exception labels.

## Risks And Test Signals
Risks include register-save mistakes in exception context, incorrect permission-mask construction, nested fault unwinding errors, SMT tablewalk races, stale indirect entries, and hugepage MAS size bugs. Test signals should include user and kernel instruction/data faults, KUAP faults, e6500 SMT systems, hugepages, virtual page-table faults, linear-map faults near `linear_map_top`, and KVM BookE configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_low_64e.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/numa.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/numa.c

## Purpose
This file implements PowerPC NUMA topology discovery, CPU-to-node mapping, memory-to-node assignment, distance calculation, memory hotplug node lookup, and virtual processor home node updates. It primarily targets pSeries/LPAR/OPAL systems using device-tree associativity properties and hypervisor VPHN calls.

## Important APIs, Types, And Functions
Exported or externally visible APIs include `map_cpu_to_node()`, `unmap_cpu_from_node()`, `cpu_relative_distance()`, `__node_distance()`, `of_node_to_nid()`, `update_numa_distance()`, `of_drconf_to_nid_single()`, `dump_numa_cpu_topology()`, `mem_topology_setup()`, `initmem_init()`, `hot_add_scn_to_nid()`, `memory_hotplug_max()`, `find_and_update_cpu_nid()`, and `cpu_to_coregroup_id()`. Persistent tables are `numa_cpu_lookup_table`, `node_to_cpumask_map`, `numa_distance_table`, `distance_lookup_table`, and `numa_id_index_table`.

## Control Flow
`early_param("numa", early_numa)` handles `numa=off` and fake node boundaries. `mem_topology_setup()` initializes PFN bounds, temporarily offlines node 0, parses NUMA properties, falls back to `setup_nonnuma()`, intersects possible and online node maps, discovers possible nodes, allocates node cpumasks, resets CPU lookup, and maps all possible CPUs. `parse_numa_properties()` discovers affinity form, primary domain index, distance tables, CPU nodes, memory nodes, PCI nodes, and dynamic reconfiguration memory LMBs, assigning memblocks to NUMA nodes. `initmem_init()` allocates `NODE_DATA` for online nodes and registers CPU hotplug preparation.

## State And Persistence
The resulting node online/possible maps, memblock node assignments, `NODE_DATA`, CPU lookup table, cpumasks, and distance tables persist after boot and feed scheduler, memory allocator, hotplug, and topology code. VPHN can update CPU node association later.

## Dependencies And Integration Points
Dependencies include Open Firmware device-tree APIs, memblock, SPARSEMEM, DRCONF memory, RTAS/OPAL firmware feature flags, hypervisor calls, CPU sibling helpers, cpuhp, cpuset/topology code, and pSeries SPLPAR VPHN.

## Risks And Test Signals
Risks include malformed associativity arrays, invalid node IDs, distance-table size mismatch, fake NUMA boundary parsing, dynamic memory LMB assignment, CPU thread siblings landing on different nodes, and hotplug fallback to `first_online_node`. Test signals include `numa=off`, `numa=fake=`, form 0/1/2 firmware, OPAL and RTAS roots, memoryless node 0, CPU hotplug, LPM/VPHN updates, and memory hot-add from both memory nodes and DRCONF memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pageattr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/pageattr.c

## Purpose
This file implements PowerPC `set_memory_*` style page attribute changes over existing kernel mappings. It updates PTE permission and presence bits atomically, performs required synchronization, and flushes kernel TLB entries.

## Important APIs, Types, And Functions
The main public API is `change_memory_attr()`, used by set-memory wrappers. `change_page_attr()` is the callback passed to `apply_to_existing_page_range()`. `pte_update_delta()` computes bit removals/additions around `pte_update()`. Under debug page allocation or KFENCE, `__kernel_map_pages()` toggles page presence for debug allocator poisoning.

## Control Flow
`change_memory_attr()` aligns the start address, rejects zero-page requests, rejects huge vmalloc/module mappings, and on Book3S hash rejects non-vmalloc/non-IO regions because linear mappings are not represented in Linux page tables. It then applies `change_page_attr()` over the existing range. The callback switches on action values such as `SET_MEMORY_RO`, `SET_MEMORY_ROX`, `SET_MEMORY_RW`, `SET_MEMORY_NX`, `SET_MEMORY_X`, `SET_MEMORY_NP`, and `SET_MEMORY_P`, updates PTE bits, issues `ptesync` for radix, and calls `flush_tlb_kernel_range()` for the page.

## State And Persistence
The persistent state is the modified kernel PTE attributes in `init_mm`. No separate cache is kept. For debug page allocation, page presence is toggled until the allocator re-enables it.

## Dependencies And Integration Points
It depends on generic `apply_to_existing_page_range()`, PowerPC PTE helpers, radix/hash selection, `is_vmalloc_or_module_addr()`, huge vmalloc detection, `hash__kernel_map_pages()`, and `flush_tlb_kernel_range()`. It is used by strict RWX, module permission changes, debug pagealloc, and KFENCE.

## Risks And Test Signals
Risks include changing unmapped or huge mappings, missing TLB flushes, incorrectly clearing dirty state, and unsupported Book3S hash linear-map updates. Tests should exercise module/text ROX changes, vmalloc permission changes, radix and hash builds, debug pagealloc/KFENCE toggles, and invalid huge-vmalloc requests returning `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pageattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable-frag.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable-frag.c

## Purpose
This file implements allocation and freeing of PTE tables using fragments carved from page-table pages. It lets PowerPC share one physical page across several PTE fragments where `PTE_FRAG_NR > 1`, while preserving refcounts, page-table constructors/destructors, RCU freeing, and THP deferral rules.

## Important APIs, Types, And Functions
The public functions are `pte_fragment_alloc()`, `pte_fragment_free()`, `pte_frag_destroy()`, and under THP `pte_free_defer()`. Internal helpers include `get_pte_from_cache()`, `__alloc_for_ptecache()`, and `pte_free_now()`. State is stored in `mm->context` through `pte_frag_get()`/`pte_frag_set()` and in `ptdesc->pt_frag_refcount`.

## Control Flow
Allocation first tries `get_pte_from_cache()` under `mm->page_table_lock`, consumes the next fragment pointer, and clears the cache when the page boundary wraps. If the cache is empty, `__alloc_for_ptecache()` allocates a page-table descriptor, runs `pagetable_pte_ctor()`, initializes the fragment refcount, and either returns the whole page for single-fragment configurations or caches the remaining fragments for the mm. Freeing converts the address to `ptdesc`, handles reserved tables specially, decrements the fragment refcount, and either frees immediately for kernel or inactive folios, or schedules RCU freeing when user page tables may still be walked.

## State And Persistence
Fragment availability persists in the per-mm cached pointer. Refcounts persist in `pt_frag_refcount` until all fragments of a page-table page are released. Folio active state marks deferred freeing for THP-related paths.

## Dependencies And Integration Points
This integrates with generic page-table allocation (`pagetable_alloc/free`, `pagetable_pte_ctor/dtor`), mm locking, RCU, hugepage/THP paths, and the `mm->context` storage initialized by `init_new_context()` in the nohash context code.

## Risks And Test Signals
Risks include fragment refcount imbalance, cache pointer wrap errors, freeing reserved page tables incorrectly, and RCU lifetime bugs under concurrent page-table walkers. Test signals include fork/exit churn, THP collapse/split, user and kernel PTE allocation, `PTE_FRAG_NR == 1` builds, and page-table debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable-frag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable.c

## Purpose
This file contains common PowerPC page-table operations: the kernel `swapper_pg_dir`, PTE filtering for I-cache/D-cache coherency and execute permission, PTE installation, access-flag updates, hugepage PTE writes, debug lock assertions, vmalloc-to-physical lookup, Linux page-table walking, and the VM protection map.

## Important APIs, Types, And Functions
Important APIs include `set_ptes()`, `set_pte_at_unchecked()`, `unmap_kernel_page()`, `ptep_set_access_flags()`, `huge_ptep_set_access_flags()`, `set_huge_pte_at()`, `assert_pte_locked()`, `vmalloc_to_phys()`, and `__find_linux_pte()`. Helpers `set_pte_filter()`, `set_pte_filter_hash()`, `set_access_flags_filter()`, and `maybe_pte_to_folio()` enforce cache and execute semantics.

## Control Flow
PTE installation filters the requested PTE before writing it. Hash or embedded nohash systems without coherent I-cache/no-execute support may flush `flush_dcache_icache_folio()` and set `PG_dcache_clean`, or temporarily remove execute permission until an execution fault proves the page must execute. `set_ptes()` writes a run of PTEs after `page_table_check_ptes_set()` and asserts no hardware-valid replacement is happening without flush. Access-flag updates apply the execution-fault filter and call `__ptep_set_access_flags()` when changed. `__find_linux_pte()` walks PGD/P4D/PUD/PMD safely using local copies and detects leaf huge mappings.

## State And Persistence
Persistent state includes `swapper_pg_dir`, modified PTEs, folio `PG_dcache_clean`, and protection constants in `protection_map`. No separate allocator state is owned here.

## Dependencies And Integration Points
It integrates generic Linux MM hooks with PowerPC MMU feature flags, radix/hash detection, hugetlb, THP serialization states, page-table check, TLB flush helpers, and cache maintenance.

## Risks And Test Signals
Risks include executable stale I-cache, over-filtering `_PAGE_EXEC`, writing hardware-valid PTEs without invalidation, THP split/collapse races in `__find_linux_pte()`, and hugepage size stepping errors. Test signals include JIT or mmap executable faults, `mprotect(PROT_EXEC)`, hugetlb mappings, THP stress, page-table debug, vmalloc lookups, and non-coherent embedded CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable_32.c

## Purpose
This file contains 32-bit PowerPC page-table setup helpers for early ioremap, kernel page mapping, low-memory RAM mapping, and strict kernel permission changes for init text and rodata.

## Important APIs, Types, And Functions
Key functions are `early_ioremap_init()`, `early_alloc_pgtable()`, `early_pte_alloc_kernel()`, `map_kernel_page()`, `mapin_ram()`, `mark_initmem_nx()`, and under strict RWX `mark_rodata_ro()`. The file owns `early_fixmap_pagetable[]`.

## Control Flow
`early_ioremap_init()` populates fixmap PMDs with the static early PTE table and then calls `early_ioremap_setup()`. `map_kernel_page()` finds the kernel PMD, allocates a PTE via slab or memblock depending on boot phase, asserts an existing valid/hash PTE is not overwritten, installs the PFN PTE, and issues a write barrier. `mapin_ram()` iterates memblock ranges below `total_lowmem`, lets `mmu_mapin_ram()` map platform-supported block ranges first, then maps remaining pages individually with executable permissions only for core kernel text. `mark_initmem_nx()` and `mark_rodata_ro()` delegate to block-map MMU helpers when possible or use set-memory APIs.

## State And Persistence
The file builds persistent kernel page-table entries in `init_mm` and static fixmap early tables. Permission changes persist in kernel mappings after init.

## Dependencies And Integration Points
It depends on memblock, early ioremap, fixmap constants, `pmd_off_k()`, PTE allocation, `set_pte_at()`, platform `mmu_mapin_ram()`, `v_block_mapped()`, `mmu_mark_initmem_nx()`, `mmu_mark_rodata_ro()`, and generic set-memory functions.

## Risks And Test Signals
Risks include early fixmap table size/index mismatches, overwriting existing mappings, wrong executable permission for kernel text/data, and divergence between block mappings and page-table mappings. Test signals include 32-bit boot with early ioremap, strict kernel RWX, module RWX warnings on hash MMU, lowmem holes, and initmem permission transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable_64.c

## Purpose
This file provides 64-bit PowerPC page-table globals and helpers. For Book3S 64 it exports runtime page-table geometry, partition/process table pointers, kernel virtual region bounds, vmemmap, and PTE fragment sizing. It also provides page-descriptor helpers for upper-level entries and strict RWX dispatch.

## Important APIs, Types, And Functions
Global symbols include `process_tb`, `partition_tb`, `__pte_index_size`, `__pmd_index_size`, `__pud_index_size`, `__pgd_index_size`, table sizes, value-bit sizes, virtual region bounds, `vmemmap`, `__pte_frag_nr`, and `__pte_frag_size_shift`. Functions include `p4d_page()` when PUD is not folded, `pud_page()`, `pmd_page()`, `mark_rodata_ro()`, and `mark_initmem_nx()`.

## Control Flow
The page helper functions distinguish leaf huge mappings from pointers to lower-level tables. For leaf entries they return `pte_page()` from the converted PTE; for table pointers they return `virt_to_page()` on the next-level table address. Strict RWX functions choose radix or hash implementations at runtime, with a feature check for `MMU_FTR_KERNEL_RO` before trying to mark rodata read-only.

## State And Persistence
The exported geometry variables define the runtime page-table layout and are consumed across the architecture. `process_tb` and `partition_tb` persist as ISA 3.0 translation structures. Region-bound globals persist as the canonical Book3S64 kernel virtual layout.

## Dependencies And Integration Points
This file integrates Book3S64 radix/hash setup code, vmalloc/vmemmap helpers, hugetlb/huge-vmap page lookup, and strict RWX implementations `radix__mark_*` and `hash__mark_*`.

## Risks And Test Signals
Risks include returning wrong `struct page` for leaf huge-vmap entries, stale exported geometry values, and silently failing strict RWX when CPU features cannot enforce it. Test signals include vmalloc-to-page on huge vmap, radix and hash boots, strict RWX verification, and Book3S64 page table geometry self-consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/pgtable_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/8xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/8xx.c

## Purpose
This file supplies the page-table dump flag descriptions for PPC 8xx. It does not walk page tables itself; it defines how generic `ptdump.c` should decode 8xx PTE bits at each level.

## Important APIs, Types, And Functions
The key data is `flag_array[]` and exported `pg_level[5]`. Entries describe huge-page flags (`_PAGE_HUGE` or `_PAGE_SPS` depending on page size), read/write/NA combinations, execute, present, guarded, dirty, accessed, no-cache, and special bits.

## Control Flow
At runtime `ptdump.c` consults `pg_level[level].flag`, `.num`, and a computed `.mask` to group and print page-table ranges. This file's only active behavior is static initialization of those decode tables.

## State And Persistence
The decode table is static kernel data and persists for the lifetime of the debug page-table dump facility. It does not modify MMU state.

## Dependencies And Integration Points
It depends on 8xx page-bit definitions from `linux/pgtable.h` and the shared `ptdump.h` structure layout. It is selected by the ptdump Makefile under `CONFIG_PPC_8xx`.

## Risks And Test Signals
Risks are stale or incorrect flag names/masks leading to misleading debugfs output and W+X checks masking unknown bits incorrectly. Test signals include reading `/sys/kernel/debug/kernel_page_tables` on 8xx, verifying huge-page labels under 16K and non-16K builds, and checking unknown flag reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/Makefile

## Purpose
This Makefile selects the PowerPC page-table dump objects built for each MMU family and debugfs configuration.

## Important APIs, Types, And Functions
There are no C APIs here. Build outputs include the common `ptdump.o`, flag-table providers such as `shared.o`, `8xx.o`, and `book3s64.o`, plus debugfs-only helpers `bats.o`, `segment_regs.o`, and `hashpagetable.o`.

## Control Flow
`obj-y += ptdump.o` always includes the main walker. Configuration conditions then choose exactly one appropriate `pg_level` provider for 44x, 8xx, e500, Book3S32, or Book3S64. When `CONFIG_PTDUMP_DEBUGFS` is enabled, Book3S32 gets BAT and segment-register dumpers, and 64S hash MMU gets the hash page-table dumper.

## State And Persistence
The file controls build composition only. Its effect persists in the linked kernel image through selected object files.

## Dependencies And Integration Points
It integrates Kconfig symbols with the ptdump subsystem and must avoid duplicate `pg_level` definitions while ensuring `ptdump.o` always has one provider for the target architecture.

## Risks And Test Signals
Risks include missing a flag provider for a configuration, linking multiple `pg_level` definitions, or exposing debugfs files on unsupported MMUs. Test signals are allyesconfig/allmodconfig style PowerPC builds across 8xx, e500, 44x, Book3S32, Book3S64 radix, and Book3S64 hash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/bats.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/bats.c

## Purpose
This file exposes Book3S 32-bit Block Address Translation register contents through debugfs. It decodes instruction and data BAT upper/lower SPR pairs into virtual ranges, physical base addresses, size, privilege scope, permissions, and cache attributes.

## Important APIs, Types, And Functions
Important functions are `bat_show_603()`, `bats_show()`, and `bats_init()`. The `BAT_SHOW_603` macro reads SPR pairs and dispatches to the decoder. `DEFINE_SHOW_ATTRIBUTE(bats)` creates the seq-file file operations.

## Control Flow
`bats_init()` creates `arch_debugfs_dir/block_address_translation`. Reading the file calls `bats_show()`, which prints instruction BATs 0-3, optional high BATs 4-7 when `MMU_FTR_USE_HIGH_BATS` is present, then data BATs in the same pattern. `bat_show_603()` treats `k == 0` as invalid, computes BEPI, block length, BRPN, range size, permission text, and WIMG attributes.

## State And Persistence
No state is persisted beyond debugfs registration. Output reflects live SPR values at read time.

## Dependencies And Integration Points
It depends on debugfs, seq_file, BAT SPR definitions, `PHYS_BAT_ADDR()`, `pt_dump_size()`, `arch_debugfs_dir`, and MMU feature detection. It is built only for Book3S32 ptdump debugfs.

## Risks And Test Signals
Risks include incorrect size/range decoding, format mismatch for 64-bit physical addresses, and reading unsupported high BAT SPRs. Test signals include debugfs output on 603-style and high-BAT CPUs and cross-checking ranges against early block mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/bats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/book3s64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/book3s64.c

## Purpose
This file defines Book3S64 page-table flag decoding for the generic ptdump walker. It maps Linux PTE and hash-specific bits into readable labels for debugfs page-table dumps and W+X checking.

## Important APIs, Types, And Functions
The primary data structures are `flag_array[]` and exported `pg_level[5]`. Flags include user/privileged, read, write, execute, leaf PTE, valid/present, hash PTE state, dirty/accessed, non-idempotent/tolerant cache attributes, busy, 64K combo or 4K PFN state, f_gix/f_second for non-64K pages, and special.

## Control Flow
There is no executable control path beyond static data initialization. `ptdump.c` later computes per-level masks from this table and uses it to group and print page-table ranges.

## State And Persistence
The flag tables are persistent read-only kernel data. They do not mutate page tables.

## Dependencies And Integration Points
This file depends on Book3S64 PTE/hash bit definitions and the shared `ptdump.h` ABI. It is selected by the ptdump Makefile for `CONFIG_PPC_BOOK3S_64`.

## Risks And Test Signals
Risks include misleading diagnostics if bit definitions drift, especially around hash HPTE status and 64K subpage encodings. Test signals include debugfs `kernel_page_tables` output on radix and hash Book3S64, 64K and non-64K page configurations, and W+X check output containing no unknown expected bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/book3s64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/hashpagetable.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/hashpagetable.c

## Purpose
This file implements the Book3S64 hash page-table debugfs dump. It walks kernel virtual areas, searches native or pSeries hash page-table entries, decodes HPTE V/R flags, base and actual page sizes, RPN, and prints mappings found in the hardware hash table.

## Important APIs, Types, And Functions
Key functions include `native_find()`, `pseries_find()`, `base_hpte_find()`, `hpte_find()`, `decode_r()`, `dump_hpte_info()`, `walk_pte()`, `walk_pmd()`, `walk_pud()`, `walk_p4d()`, `walk_pagetables()`, `walk_linearmapping()`, `walk_vmemmap()`, `populate_markers()`, `ptdump_show()`, and `ptdump_init()`. It defines local `flag_info` arrays for HPTE V and R fields.

## Control Flow
`ptdump_init()` registers `kernel_hash_pagetable` only when radix is disabled. On read, `ptdump_show()` walks the linear map by `mmu_linear_psize`, kernel page tables from `KERN_VIRT_START`, and vmemmap backing entries. `hpte_find()` checks primary and secondary hash groups through `native_find()` or `pseries_find()`, decodes large-page LP/RPN fields, validates actual page size, and prints the entry. `walk_pte()` also warns when a hardware HPTE exists but the Linux PTE lacks `H_PAGE_HASHPTE`, suggesting a bolted pre-Linux mapping.

## State And Persistence
No state is modified. The output is a live view of hash table contents, memblock DRAM size, vmemmap backing list, and Linux page tables.

## Dependencies And Integration Points
It depends on hash MMU globals such as `htab_address`, `htab_hash_mask`, `mmu_psize_defs`, `mmu_kernel_ssize`, `mmu_*_psize`, pSeries `plpar_pte_read_4()`, firmware feature flags, memblock, and debugfs.

## Risks And Test Signals
Risks include wrong AVPN/hash calculation, architecture 3.0 HPTE old/new format conversion mistakes, LP decoding errors, and racing against mapping changes during debugfs reads. Test signals include hash-only Book3S64 boots, pSeries LPAR and native modes, large pages, vmemmap, bolted mappings, and no file registration under radix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/hashpagetable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/ptdump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/ptdump.c

## Purpose
This file is the generic PowerPC kernel page-table dumper. It traverses `init_mm` page tables, groups contiguous ranges with the same flags and level, prints region markers and decoded attributes to debugfs, and provides a boot/runtime W+X mapping check.

## Important APIs, Types, And Functions
Important types are `struct pg_state` and `struct addr_marker`. Key functions include `pt_dump_size()`, `dump_flag_info()`, `dump_addr()`, `note_prot_wx()`, `note_page_update_state()`, `note_page()`, `populate_markers()`, per-level `note_page_*()` callbacks, `ptdump_show()`, `build_pgtable_complete_mask()`, `ptdump_check_wx()`, and `ptdump_init()`.

## Control Flow
`ptdump_init()` sets the ptdump address range for PPC64, populates marker addresses, computes masks from the selected `pg_level[]` provider, and registers `kernel_page_tables` when debugfs ptdump is enabled. `ptdump_show()` initializes callbacks and calls `ptdump_walk_pgd()`. During walking, `note_page()` starts a range on the first entry and flushes/prints whenever flags, level, or address marker changes. `ptdump_check_wx()` performs the same walk without seq output and counts writable-executable pages.

## State And Persistence
The file maintains static marker and range arrays after init. Per-read state is stack-local. W+X warnings are emitted but no mapping state is changed.

## Dependencies And Integration Points
It depends on generic `linux/ptdump.h`, PowerPC region constants, `pg_level[]` from architecture-specific providers, KASAN/fixmap/vmalloc constants, debugfs, and `init_mm`.

## Risks And Test Signals
Risks include incorrect marker ordering, missing flags in `pg_level[].mask`, false W+X positives/negatives, and PPC64 range start differences between radix and hash. Test signals include debugfs `kernel_page_tables`, `ptdump_check_wx()` during strict RWX boot, KASAN/highmem/fixmap builds, and unknown flag reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/ptdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/ptdump.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/ptdump.h

## Purpose
This header defines the local data contract between the generic PowerPC ptdump walker and MMU-specific flag table providers.

## Important APIs, Types, And Functions
`struct flag_info` describes a bit mask, expected value, string when set or clear, optional value-style formatting, and shift. `struct ptdump_pg_level` describes one page-table level with a flag table, name, count, and aggregate mask. It declares `pg_level[5]` and `pt_dump_size()`.

## Control Flow
There is no runtime control flow in the header. Providers initialize `pg_level[]`; `ptdump.c` computes masks and uses these descriptors when walking page tables.

## State And Persistence
The persistent state is the externally defined `pg_level[]` array. Its `.mask` fields are filled during ptdump init.

## Dependencies And Integration Points
It depends on `linux/types.h` and `seq_file`. It is included by all ptdump providers and by the main walker.

## Risks And Test Signals
Risks include ABI drift between providers and walker, too-small `name[4]` for future level names, and incorrect `is_val`/`shift` interpretation. Build coverage across all ptdump providers is the main signal; runtime debugfs output confirms table decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/ptdump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/segment_regs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/segment_regs.c

## Purpose
This file exposes Book3S 32-bit segment register contents through debugfs. It decodes the 16 segment registers into user/kernel virtual segments, keys, device mappings, no-execute state, and VSID values.

## Important APIs, Types, And Functions
Key functions are `seg_show()`, `sr_show()`, and `sr_init()`. `DEFINE_SHOW_ATTRIBUTE(sr)` provides seq-file operations.

## Control Flow
`sr_init()` registers `arch_debugfs_dir/segment_registers`. Reading the file calls `sr_show()`, which prints user segments up to aligned `TASK_SIZE`, then kernel segments through register 15. `seg_show()` reads each segment register with `mfsr(i << 28)` and decodes key bits, device-vs-VSID format, and no-execute bit.

## State And Persistence
No persistent runtime state is owned. Output reflects live segment register values at read time.

## Dependencies And Integration Points
It depends on debugfs, seq_file availability through included headers, `TASK_SIZE`, `ALIGN`, `SZ_256M`, `mfsr()`, and `arch_debugfs_dir`. The ptdump Makefile builds it for Book3S32 ptdump debugfs.

## Risks And Test Signals
Risks include incorrect user/kernel split for unusual `TASK_SIZE`, misdecoding device segment fields, and reading unsupported segment registers on the wrong MMU family. Test signals include debugfs reads on Book3S32 and comparison with expected segment setup during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/segment_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/shared.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/shared.c

## Purpose
This file defines a shared ptdump flag table for several non-Book3S64 PowerPC MMU configurations, including 44x, e500, and Book3S32. It supplies the generic walker with readable names for common PTE bits.

## Important APIs, Types, And Functions
The important data is `flag_array[]` and exported `pg_level[5]`. Flags cover read, write, execute, present, coherent, guarded, dirty, accessed, write-through, no-cache, and special states.

## Control Flow
There is no active control flow. `ptdump.c` reads the static descriptors when grouping and printing page-table ranges.

## State And Persistence
The static `pg_level[]` table persists for the lifetime of the kernel. It does not mutate page tables.

## Dependencies And Integration Points
It depends on common PowerPC PTE bit definitions and `ptdump.h`. The Makefile selects it for 44x, PPC_E500, and PPC_BOOK3S_32.

## Risks And Test Signals
Risks include shared labels being too generic for one MMU family and incorrect unknown-bit masking. Test signals include debugfs ptdump output on 44x/e500/Book3S32, strict W+X checks, and build coverage for each selected configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/net/Makefile

## Purpose
This Makefile builds the PowerPC architecture-specific networking code for BPF JIT support.

## Important APIs, Types, And Functions
There are no source APIs. When `CONFIG_BPF_JIT` is enabled, it builds the common `bpf_jit_comp.o` plus a word-size-specific backend selected by `$(BITS)`, such as `bpf_jit_comp32.o` on 32-bit PowerPC.

## Control Flow
The single object rule is conditional on `CONFIG_BPF_JIT`. Build-time expansion of `$(BITS)` selects the backend matching the target ABI.

## State And Persistence
The file affects the linked kernel image by including or excluding JIT objects. It has no runtime state.

## Dependencies And Integration Points
It connects Kconfig `CONFIG_BPF_JIT` with architecture backend source files and must stay aligned with available `bpf_jit_comp$(BITS).c` implementations.

## Risks And Test Signals
Risks include missing backend objects for a new bitness, compiling BPF JIT code when unsupported, or omitting the common compiler. Test signals include 32-bit and 64-bit PowerPC builds with `CONFIG_BPF_JIT=y` and disabled JIT builds that omit these objects cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit.h

## Purpose
This header defines shared infrastructure for the PowerPC BPF JIT compiler. It provides instruction emission macros, immediate-loading helpers, branch range handling, condition-code constants, code generation context, private-stack guard constants, and cross-file function prototypes.

## Important APIs, Types, And Functions
Key macros include `EMIT`, `PPC_JMP`, `PPC_BCC_SHORT`, `PPC_BCC_CONST_SHORT`, `PPC_BCC`, `PPC_LI32`, `PPC_LI64`, `PPC_LI_ADDR`, and `PPC64_LOAD_PACA`. `struct codegen_context` tracks emitted instruction index, seen registers/features, stack sizes, BPF-to-PPC register mapping, exception table index, alternate exit, arena bases, subprogram/exception flags, and private stack state. Feature bits include `SEEN_FUNC` and `SEEN_TAILCALL`.

## Control Flow
The macros either emit real instructions when `image` is non-null or advance `ctx->idx` conservatively in sizing passes. Branch macros validate offset ranges and synthesize long conditional branches by inverting the condition and emitting an unconditional branch when needed. Immediate loaders use shorter encodings when possible but reserve worst-case length during dry runs.

## State And Persistence
The header does not own global state, but `codegen_context` is the persistent per-compile state passed across prologue, body, epilogue, trampoline, and exception-table generation.

## Dependencies And Integration Points
It depends on PPC opcode helpers, BPF register constants, kernel branch-range helpers, PACA layout, and text patching conventions. It is shared by the common JIT driver and 32/64-bit backends.

## Risks And Test Signals
Risks include dry-run instruction counts diverging from real emission, branch range validation bugs, incorrect ABI handling for function descriptors and TOC/PACA, and register usage tracking errors. Test signals include BPF selftests with large programs, long jumps, helper calls, tail calls, trampoline attachment, private stack programs, and both PPC32/PPC64 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp.c

## Purpose
This file is the common PowerPC eBPF JIT orchestration layer. It allocates and finalizes packed executable images, drives multi-pass code generation, manages line-info and exception-table fixups, supports private BPF stacks, provides trampoline generation, and patches BPF program entry text for trampoline attach/detach.

## Important APIs, Types, And Functions
Key APIs include `bpf_int_jit_compile()`, `bpf_add_extable_entry()`, `bpf_arch_text_copy()`, `bpf_arch_text_invalidate()`, `bpf_jit_free()`, `arch_alloc_bpf_trampoline()`, `arch_prepare_bpf_trampoline()`, `arch_bpf_trampoline_size()`, and `bpf_arch_text_poke()`. `struct powerpc_jit_data` stores deferred subprogram JIT state. Helper functions include `bpf_jit_build_fentry_stubs()`, `bpf_jit_emit_exit_insn()`, private-stack guard init/check, trampoline invocation helpers, and text modification helpers.

## Control Flow
`bpf_int_jit_compile()` exits unless JIT was requested, allocates per-program JIT data, optionally allocates a guarded per-CPU private stack, runs a dry body pass to compute addresses and seen features, optionally repeats for tail calls or large programs, reallocates registers, sizes prologue/epilogue, allocates packed RW/RO images plus fixup/extable space, emits two real passes, writes ABI v1 function descriptors, finalizes text, updates `fp->bpf_func`, line info, and instruction pointers, or stores partial state for subprogram finalization. `bpf_add_extable_entry()` emits fixup instructions and relative exception-table entries for probe-memory loads. Trampoline generation builds a PPC ABI stack frame, saves args/cookies/metadata, invokes fentry/fmod_ret/fexit programs, optionally calls the original function, restores state, and emits safe return paths.

## State And Persistence
Persistent state includes packed JIT image text, optional `fp->aux->jit_data`, `fp->aux->extable`, `fp->aux->priv_stack_ptr`, BPF kallsyms metadata, and static stub size offsets `bpf_jit_ool_stub`/`bpf_jit_long_branch_stub`.

## Dependencies And Integration Points
It integrates with the architecture backends declared in `bpf_jit.h`, BPF verifier metadata, packed BPF image allocator, PowerPC text patching, ftrace/trampoline APIs, exception tables, kfunc/support capability hooks, and PPC64 ABI details.

## Risks And Test Signals
Risks include pass-size instability, extable relative offset overflow, RO/RW image offset mistakes, private stack guard corruption, trampoline ABI frame errors, stale instruction-cache synchronization in text poking, and unsupported PPC32 trampoline paths. Test signals include kernel BPF selftests, probe-memory loads, subprograms, tail calls, kfuncs, trampolines/fentry/fexit/fmod_ret, attach/detach stress, private stack overflow detection, and `bpf_jit_enable > 1` dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp32.c

## Purpose
This file is the 32-bit PowerPC eBPF JIT backend. It maps 64-bit eBPF registers onto pairs of 32-bit PPC registers, builds PPC32 prologue/epilogue code, emits helper calls and tail calls, and translates BPF ALU, load/store, atomic, endian, branch, call, and exit instructions into PPC opcodes.

## Important APIs, Types, And Functions
Backend entry points include `bpf_jit_init_reg_mapping()`, `bpf_jit_realloc_regs()`, `prepare_for_fsession_fentry()`, `store_func_meta()`, `bpf_jit_build_prologue()`, `bpf_jit_build_epilogue()`, `bpf_jit_emit_func_call_rel()`, and `bpf_jit_build_body()`. Internal helpers include `bpf_jit_stack_offsetof()`, `bpf_has_stack_frame()`, `bpf_jit_emit_common_epilogue()`, and `bpf_jit_emit_tail_call()`.

## Control Flow
Register mapping assigns each eBPF 64-bit register to an even/odd high-low PPC register pair, with nonvolatile registers used for callee-saved BPF state. The prologue emits an attachable NOP, initializes or preserves tail-call count, creates a stack frame when needed, saves nonvolatile registers, maps input `r3` into BPF R1, and sets the BPF frame pointer. The body loop records `addrs[]`, tracks seen registers, performs a MOV-combine optimization, and emits per-opcode instruction sequences. Unsupported 64-bit division/modulo cases return `-EOPNOTSUPP` except power-of-two immediates. The epilogue moves BPF R0 into PPC return register, restores state, returns, and appends fentry stubs.

## State And Persistence
Compile-time state lives in `codegen_context`: seen registers, stack size, register map, emitted index, and feature flags. Runtime state is the generated machine code, BPF stack frame, saved nonvolatile registers, and tail-call counter slot.

## Dependencies And Integration Points
It depends on common JIT macros, PPC raw opcode helpers, BPF verifier flags such as `verifier_zext`, BPF helper address resolution, exception-table support for `BPF_PROBE_MEM`, and the common compiler driver.

## Risks And Test Signals
Risks include high/low word ordering mistakes, signed versus unsigned branch errors, dry-run and real-pass divergence, unsupported instruction handling, atomic memory-ordering mistakes, probe-memory fixup offsets, and stack-frame save/restore bugs. Test signals include BPF ALU32/ALU64 selftests, endian conversion, signed comparisons, atomics, probe-memory loads, tail calls, helper calls, verifier zext and non-zext modes, and PPC32 JIT build/runtime selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp32.c -->
