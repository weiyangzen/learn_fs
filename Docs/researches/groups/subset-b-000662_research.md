# subset-b-000662 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/cache.c

### Purpose
Defines the ARM `struct cpu_cache_fns` dispatch tables that bind generic cache/DMA maintenance call sites to CPU-family assembly implementations selected by Kconfig and CPU probing. It is glue, not algorithmic cache code: the real operations live in low-level assembly symbols such as `v7_dma_map_area`, `xscale_flush_user_cache_range`, and `feroceon_range_dma_flush_range`.

### Important APIs, Types, And Functions
Exports initialized `cpu_cache_fns` instances for V4, V4WB, V4WT, FA, V6, V7/B15, NOP, V7M, ARM1020/1020E/1022/1026, ARM920/922/925/926/940/946, XScale, XSC3, Mohawk, and Feroceon variants. Each table fills `flush_icache_all`, `flush_kern_all`, `flush_kern_louis`, `flush_user_all`, `flush_user_range`, `coherent_kern_range`, `coherent_user_range`, `flush_kern_dcache_area`, `dma_map_area`, `dma_unmap_area`, and `dma_flush_range`.

### Control Flow
There is no runtime branch beyond compile-time `#ifdef` selection. Processor setup copies one of these tables into the active `cpu_cache` vector, after which higher-level code in DMA, flush, ptrace, and fault handling calls the selected function pointers.

### State, Dependencies, And Integration
State is `__initconst` table data discarded after boot once copied. It depends on `<asm/cacheflush.h>` and assembly objects matching the declared symbol names. Integration points are `dma.h` macros, `flush.c`, `dma-mapping*.c`, cache type probing, and CPU proc descriptors.

### Risks And Test Signals
Risks are table/symbol mismatches, selecting a function set with wrong cache semantics, and family quirks such as Broadcom B15 RAC or XScale 80200 DMA mapping. Build every enabled CPU cache configuration, boot with cache-policy logging, and run DMA/cache coherency stress plus executable-page modification tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/context.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/context.c

### Purpose
Implements ARM MMU context switching with ASID allocation, rollover handling, per-CPU active/reserved ASID tracking, optional PID-in-CONTEXTIDR updates, and safe TTBR0 switching for classic MMU systems.

### Important APIs, Types, And Functions
Key state includes `asid_generation`, `asid_map`, per-CPU `active_asids`, per-CPU `reserved_asids`, `cpu_asid_lock`, and `tlb_flush_pending`. Main entry point is `check_and_switch_context(mm, tsk)`. Helpers include `flush_context`, `check_update_reserved_asid`, `new_context`, `cpu_set_reserved_ttbr0`, and erratum-specific `a15_erratum_get_cpumask`.

### Control Flow
`check_and_switch_context` first syncs vmalloc page tables, switches TTBR0 to reserved global mappings on non-LPAE, then fast-paths if the current ASID generation is valid and active. Otherwise it locks ASID state, allocates/reuses an ASID, handles generation rollover by reserving active ASIDs and queuing TLB flushes, performs pending local TLB/BP flush, records CPU membership, and finally calls `cpu_switch_mm`.

### State, Dependencies, And Integration
ASID state persists for the running kernel and is protected by a raw spinlock plus atomic64 per-CPU values. It depends on SMP, TLB flush, proc-fns, thread notifiers, and `check_vmalloc_seq`. It integrates with scheduler context switches, CPU errata workarounds, trace/debug context IDs, and speculative-walk mitigation.

### Risks And Test Signals
Risks include ASID reuse without required TLB invalidation, reserved ASID loss across rollover, TTBR0 updates racing speculative walks, and PID/context ID corruption. Test with heavy fork/exec on SMP, CPU hotplug, vmalloc faults across processes, ASID rollover stress, and ARM erratum-specific TLB shootdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-fa.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-fa.c

### Purpose
Provides Faraday FA526-optimized implementations of `copy_user_highpage` and `clear_user_highpage` for page fault and COW paths.

### Important APIs, Types, And Functions
Exports `fa_user_fns` with `fa_copy_user_highpage` and `fa_clear_user_highpage`. The private `fa_copy_user_page` inline assembly copies 32-byte chunks using ARM load/store multiple and CP15 clean+invalidate operations.

### Control Flow
Both public functions temporarily map highmem pages with `kmap_atomic`, run a PAGE_SIZE loop in inline assembly, perform write-buffer drain, and unmap. Clear fills registers with zero and stores them across the page.

### State, Dependencies, And Integration
No persistent state. Depends on highmem atomic mappings, CP15 cache operations, and the CPU user function selection path. Integrates with generic page copy/clear hooks used by memory management.

### Risks And Test Signals
Risks are incorrect clobbers, cacheline maintenance ordering, and assumptions about page size or FA cache behavior. Validate with FA build coverage, highmem page copy tests, COW faults, fork/exec stress, and cache aliasing data-integrity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-fa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-feroceon.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-feroceon.c

### Purpose
Implements Marvell Feroceon-specific user highpage copy and clear routines optimized for its ARMv5TE-like cache behavior.

### Important APIs, Types, And Functions
Exports `feroceon_user_fns`. Public functions are `feroceon_copy_user_highpage` and `feroceon_clear_user_highpage`; private `feroceon_copy_user_page` uses prefetch (`pld`), multi-register transfers, CP15 clean+invalidate per 32-byte line, and final write-buffer drain.

### Control Flow
Copy maps source and destination atomically, flushes the source userspace cache alias with `flush_cache_page`, performs an unrolled PAGE_SIZE copy, then unmaps. Clear maps destination, stores zeros in a 32-byte loop, cleans/invalidates each line, drains the write buffer, and unmaps.

### State, Dependencies, And Integration
No persistent state. Depends on highmem, `flush_cache_page`, CP15 cache ops, and CPU user function setup. Integration is the ARM `cpu_user` copy/clear vector.

### Risks And Test Signals
Risks include stale aliases if `flush_cache_page` is omitted, Feroceon line-size assumptions, and inline assembly register constraints. Test with Feroceon configs, shared/private page faults, highmem COW, mmap write/readback, and DMA/cache stress where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-feroceon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4mc.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4mc.c

### Purpose
Implements ARMv4 mini-dcache user-page copy/clear routines for CPUs where using a mini-cache mapping avoids thrashing the main data cache during page faults.

### Important APIs, Types, And Functions
Exports `v4_mc_user_fns`. Important items are `minicache_pgprot`, `minicache_lock`, `v4_mc_copy_user_highpage`, `v4_mc_clear_user_highpage`, private `mc_copy_user_page`, and `set_top_pte(COPYPAGE_MINICACHE, ...)`.

### Control Flow
Copy ensures source folio D-cache cleanliness via `PG_dcache_clean` and `__flush_dcache_folio`, locks the mini-cache mapping, installs a temporary top-level PTE for the source page, copies from the fixed alias to the destination, unlocks, and unmaps. Clear stores zeros to the destination while invalidating D-cache lines.

### State, Dependencies, And Integration
Persistent state is only the raw spinlock. It depends on `mm.h` fixed copy-page addresses, page-table helper `set_top_pte`, highmem, folio cache-clean flags, and ARMv4 cache operations. It integrates with CPU user function selection.

### Risks And Test Signals
Risks include fixed-alias races without the lock, wrong mini-cache PTE attributes, and stale source data if folio clean state is mishandled. Test page COW, tmpfs/page-cache mappings, highmem, VIPT/VIVT alias workloads, and ARMv4 mini-cache builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4wb.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4wb.c

### Purpose
Provides ARMv4 write-back cache optimized user page copy and clear routines.

### Important APIs, Types, And Functions
Exports `v4wb_user_fns` with `v4wb_copy_user_highpage` and `v4wb_clear_user_highpage`. Private `v4wb_copy_user_page` uses load/store multiple loops, invalidates destination D lines before write allocation, and drains the write buffer.

### Control Flow
Copy maps both pages atomically, flushes the source userspace alias, runs a 64-byte loop with destination invalidations, and unmaps. Clear maps the page, writes zeros in four 16-byte stores per iteration, invalidates relevant destination lines, drains the write buffer, then unmaps.

### State, Dependencies, And Integration
No persistent state. Depends on highmem, `flush_cache_page`, CP15 c7 operations, and CPU user function registration. It integrates with generic `copy_user_highpage` and `clear_user_highpage` dispatch.

### Risks And Test Signals
Risks are cache alias corruption, incorrect write-buffer drain placement, and unsupported invalidate-line instructions on non-conforming ARMv4 CPUs. Test COW, fork, anonymous clear, mmap shared aliasing, and write-back ARMv4 build/boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4wb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4wt.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4wt.c

### Purpose
Provides ARMv4 write-through cache user page copy/clear routines where dirty data does not require write-back handling, but I/D cache freshness still matters.

### Important APIs, Types, And Functions
Exports `v4wt_user_fns`. Public routines are `v4wt_copy_user_highpage` and `v4wt_clear_user_highpage`; private `v4wt_copy_user_page` performs the bulk copy and finishes with a CP15 flush ID cache operation.

### Control Flow
Copy maps source and destination with `kmap_atomic`, performs an unrolled PAGE_SIZE copy, flushes ID cache, and unmaps. Clear maps the destination, stores zeros through the whole page, flushes ID cache, and unmaps.

### State, Dependencies, And Integration
No persistent state. It depends on highmem and ARMv4 CP15 cache maintenance. Integration is through the CPU user function vector.

### Risks And Test Signals
Risks include using this path on a write-back CPU, missing instruction-cache visibility after writing executable pages, and assembly clobber errors. Test write-through ARMv4 configs, page copy/clear selftests, executable anonymous mappings, and repeated fork/exec workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4wt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v6.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v6.c

### Purpose
Implements ARMv6 user page copy/clear functions, switching at boot between simple non-aliasing helpers and VIPT alias-aware fixed-color mappings.

### Important APIs, Types, And Functions
Exports initial `v6_user_fns`, later patched by `v6_userpage_init` when `cache_is_vipt_aliasing()`. Helpers include `v6_copy_user_highpage_nonaliasing`, `v6_clear_user_highpage_nonaliasing`, `discard_old_kernel_data`, `v6_copy_user_highpage_aliasing`, and `v6_clear_user_highpage_aliasing`.

### Control Flow
Non-aliasing paths use `kmap_atomic`, `copy_page`, and `clear_page`. Aliasing paths compute `CACHE_COLOUR(vaddr)`, flush source folio data if needed, discard old kernel data, lock `v6_lock`, install color-matched fixed PTEs at `COPYPAGE_V6_FROM/TO`, run copy/clear, and unlock.

### State, Dependencies, And Integration
State is the raw spinlock and the runtime mutation of `cpu_user` function pointers. It depends on `mm.h` fixed aliases, cache type helpers, TLB flush via `set_top_pte`, highmem, and folio `PG_dcache_clean`. It integrates with core ARM page fault/COW machinery.

### Risks And Test Signals
Risks include fixed alias races, highmem unsafety noted in comments for `page_address`, wrong cache-color computation, and stale executable aliases. Test ARMv6 VIPT aliasing and non-aliasing systems, highmem configurations, COW/page-cache sharing, and executable mmap coherency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-xsc3.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-xsc3.c

### Purpose
Provides Intel XScale3 optimized highpage copy/clear routines for systems without the older mini-dcache copy strategy.

### Important APIs, Types, And Functions
Exports `xsc3_mc_user_fns`. Main routines are `xsc3_mc_copy_user_highpage`, `xsc3_mc_clear_user_highpage`, and private `xsc3_mc_copy_user_page`, which uses XScale `pld`, doubleword transfers, and D-line invalidation to avoid write-allocate cache pollution.

### Control Flow
Copy maps pages atomically, flushes the source userspace cache page, runs a prefetching unrolled copy loop, and unmaps. Clear maps the destination and writes zero doublewords while invalidating lines.

### State, Dependencies, And Integration
No persistent state. Depends on highmem mappings, `flush_cache_page`, XScale assembly support, and CPU user function registration. Integration is the page fault/COW copy vector.

### Risks And Test Signals
Risks are XScale-specific instruction availability, line-size assumptions, and cache pollution/coherency regressions. Test XSC3 build and boot, COW and anonymous clear paths, highmem, shared mappings, and cache aliasing stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-xsc3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-xscale.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-xscale.c

### Purpose
Implements XScale mini-dcache optimized user highpage copy/clear, reducing main D-cache thrash during page faults.

### Important APIs, Types, And Functions
Exports `xscale_mc_user_fns`. Important items include `minicache_pgprot`, `minicache_lock`, `xscale_mc_copy_user_highpage`, `xscale_mc_clear_user_highpage`, private `mc_copy_user_page`, and `set_top_pte(COPYPAGE_MINICACHE, ...)`.

### Control Flow
Copy flushes the source folio if `PG_dcache_clean` was not already set, locks the single fixed mini-cache alias, maps the source page there, copies with XScale prefetch/doubleword assembly into the destination, and unlocks. Clear writes zero doublewords and performs D-line clean/invalidate operations.

### State, Dependencies, And Integration
Persistent state is `minicache_lock`. It depends on highmem, folio cache-clean tracking, `mm.h` fixed alias helpers, XScale CP15 operations, and generic ARM CPU user-vector setup.

### Risks And Test Signals
Risks include alias serialization bugs, incorrect mini-cache memory type, source folio clean-bit misuse, and assembly portability. Test XScale configs, highmem COW, page-cache aliases, fork/exec loops, and cache-coherency stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/copypage-xscale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/dma-mapping-nommu.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/dma-mapping-nommu.c

### Purpose
Implements minimal ARM DMA cache synchronization and coherency setup for NOMMU/MPU style builds.

### Important APIs, Types, And Functions
Key exported architecture hooks are `arch_sync_dma_for_device`, `arch_sync_dma_for_cpu`, and `arch_setup_dma_ops`. They use `dmac_map_area`, `dmac_unmap_area`, `outer_inv_range`, `outer_clean_range`, `cacheid`, and `get_cr()`.

### Control Flow
Device sync always performs inner-cache map maintenance and then invalidates outer cache for `DMA_FROM_DEVICE` or cleans it for other directions. CPU sync invalidates outer and inner caches for incoming or bidirectional DMA, skipping pure `DMA_TO_DEVICE`. DMA setup marks devices coherent when v7-M has no detected cache or when MMU/MPU is off; otherwise it follows the supplied firmware/bus coherency value.

### State, Dependencies, And Integration
No local persistent state beyond `dev->dma_coherent`. Depends on `dma.h`, cache type detection, CP15 control register state, and outer cache hooks. Integrates with generic DMA map ops for NOMMU ARM.

### Risks And Test Signals
Risks include treating cached systems as coherent too early, missing outer-cache maintenance, and direction-specific invalidation mistakes. Test NOMMU and v7-M builds, DMA_FROM_DEVICE data freshness, DMA_TO_DEVICE clean behavior, and boots with/without cache detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/dma-mapping-nommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/dma-mapping.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/dma-mapping.c

### Purpose
Provides ARM MMU DMA allocation, cache maintenance, contiguous/CMA remapping, atomic coherent pools, and optional IOMMU-backed DMA map ops.

### Important APIs, Types, And Functions
Important types are `arm_dma_alloc_args`, `arm_dma_free_args`, `arm_dma_allocator`, and `arm_dma_buffer`. Allocation paths include `__dma_alloc`, `__arm_dma_free`, `__alloc_simple_buffer`, `__alloc_from_contiguous`, `__alloc_remap_buffer`, `__alloc_from_pool`, and their free counterparts. Cache hooks are `arch_sync_dma_for_device` and `arch_sync_dma_for_cpu`. IOMMU support includes `arm_iommu_create_mapping`, `arm_iommu_attach_device`, `arm_iommu_detach_device`, `arm_iommu_alloc_attrs`, SG/page map/unmap/sync helpers, and `iommu_ops`. Setup hooks are `arch_setup_dma_ops`, `arch_teardown_dma_ops`, `arch_dma_alloc`, and `arch_dma_free`.

### Control Flow
Boot builds `atomic_pool` after CMA is ready and may remap reserved CMA lowmem as `MT_MEMORY_DMA_READY`. `__dma_alloc` chooses CMA, coherent simple, remapped noncoherent, or atomic pool allocation based on blocking context, device coherency, CMA availability, and `DMA_ATTR_NO_KERNEL_MAPPING`; it records the allocator in `arm_dma_bufs` so free can dispatch correctly. Streaming sync walks physical/highmem pages and runs inner plus outer cache maintenance. IOMMU paths allocate IOVA bitmap ranges, allocate pages, map contiguous PFN runs or SG chunks into an IOMMU domain, and unmap/free on release.

### State, Dependencies, And Integration
Persistent state includes `arm_dma_bufs`, `atomic_pool`, early CMA remap records, and per-device `dma_iommu_mapping` bitmaps/domains. Depends on genalloc, CMA, memblock, vmap, outer cache, cache-vector `dmac_*` calls, generic DMA/IOMMU APIs, Xen DMA setup, and `mmu.c` mapping types.

### Risks And Test Signals
Risks are allocator/free mismatches, atomic pool exhaustion, stale highmem cache lines, outer-cache ordering errors, wrong page attributes for coherent mappings, IOVA leaks/bitmap extension bugs, and SG merging mistakes. Test DMA API debug, noncoherent devices, highmem DMA, CMA/no-CMA boots, atomic GFP_ATOMIC allocations, IOMMU attach/detach, SG map/unmap under failures, and cache-coherency hardware tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/dma-mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/dma.h -->
## sources/distributed-fs/ceph-client/arch/arm/mm/dma.h

### Purpose
Private ARM DMA-cache helper header that maps generic DMA maintenance names to either compile-time cache-specific symbols or runtime `cpu_cache` function pointers.

### Important APIs, Types, And Functions
Defines `dmac_map_area` and `dmac_unmap_area`. In non-`MULTI_CACHE` builds they glue to `_CACHE_dma_map_area`/`_CACHE_dma_unmap_area`; in `MULTI_CACHE` builds they resolve to `cpu_cache.dma_map_area` and `cpu_cache.dma_unmap_area`.

### Control Flow
No executable control flow. Inclusion controls whether callers bind statically or indirectly through the active cache vtable.

### State, Dependencies, And Integration
No private state. Depends on `<asm/glue-cache.h>` and `cpu_cache` definitions from cacheflush infrastructure. Integrated by `dma-mapping.c` and `dma-mapping-nommu.c`.

### Risks And Test Signals
Risks are using these private helpers outside DMA API ownership transitions or selecting the wrong cache backend. Build both `MULTI_CACHE` and single-cache configurations, then run DMA sync direction tests and symbol resolution checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/dump.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/dump.c

### Purpose
Implements ARM kernel page-table dumping and W+X checking through ptdump/debugfs.

### Important APIs, Types, And Functions
Important structures are `pg_state`, `prot_bits`, and `pg_level`. Key routines include `dump_prot`, `note_prot_wx`, `note_page`, `walk_pte`, `walk_pmd`, `walk_pud`, `walk_p4d`, `walk_pgd`, `ptdump_walk_pgd`, `ptdump_check_wx`, and `ptdump_init`. It defines address markers for KASAN shadow, modules, kernel mapping, vmalloc, FDT, fixmap, and vectors.

### Control Flow
`ptdump_init` initializes masks and registers `kernel_page_tables`. Walkers traverse `init_mm` page tables from PGD down to PTE, coalesce adjacent ranges with identical level/domain/protection, print decoded attributes, and optionally count writable-executable mappings.

### State, Dependencies, And Integration
State is static decode tables and marker metadata. Depends on debugfs/seq_file, ARM PTE/PMD bit definitions, domains, fixmap constants, and ptdump core. Integration points are debugfs diagnostics and strict RWX validation via `arm_debug_checkwx`.

### Risks And Test Signals
Risks include stale bit decoding after page-table format changes, bad folded-level handling, and false W+X results if ro/nx bit masks are wrong. Test by reading debugfs `kernel_page_tables`, enabling KASAN and LPAE/non-LPAE builds, and checking boot W+X logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/extable.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/extable.c

### Purpose
Provides ARM exception-table fixup handling for recoverable kernel faults, especially uaccess and nofault probes.

### Important APIs, Types, And Functions
The single exported architecture hook is `fixup_exception(struct pt_regs *regs)`. It calls `search_exception_tables(instruction_pointer(regs))`, sets `regs->ARM_pc` to the fixup target, and clears Thumb-2 IT state when needed.

### Control Flow
On a kernel fault, fault handling asks this helper whether the current PC has a fixup entry. If yes, execution resumes at the fixup address and the fault is considered handled; otherwise normal oops processing continues.

### State, Dependencies, And Integration
No local persistent state. Depends on generic exception table lookup, `pt_regs`, uaccess, and Thumb-2 CPSR definitions. Integrated by `fault.c` in `__do_kernel_fault`.

### Risks And Test Signals
Risks are incorrect PC rewrite, missing IT-state clearing for Thumb-2, or broken exception table generation. Test uaccess fault recovery, `copy_from_kernel_nofault`, probe_kernel_read-style users, and Thumb-2 kernel builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fault-armv.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/fault-armv.c

### Purpose
Implements ARMv4/v5-era cache and write-buffer coherency fixups used when installing PTEs and checking legacy write-buffer aliasing behavior.

### Important APIs, Types, And Functions
Main exported hook is `update_mmu_cache_range` for `__LINUX_ARM_ARCH__ < 6`. Helpers include `do_adjust_pte`, `adjust_pte`, `make_coherent`, `check_writebuffer`, and `check_writebuffer_bugs`. Important state is `shared_pte_mask`, initially bufferable and downgraded to uncached if write-buffer coherency fails.

### Control Flow
When a valid PTE is installed, `update_mmu_cache_range` ignores invalid/zero PFNs, flushes dirty kernel D-cache data for the folio, then handles mapping aliases: VIVT shared mappings may be walked through `mapping->i_mmap` and converted to `shared_pte_mask`; executable mappings may trigger full I-cache flush. Boot-time `check_writebuffer_bugs` maps the same page twice, probes whether writes remain coherent, and changes the shared PTE policy if not.

### State, Dependencies, And Integration
State is `shared_pte_mask`. Depends on folio cache-clean flags, interval-tree VMA mapping locks, PTE locks, outer cache, vmap, and TLB/cache flushes. Integrates with generic MM fault/PTE installation.

### Risks And Test Signals
Risks include PTE-lock deadlocks, missing alias conversion, stale I-cache for executable mappings, and false write-buffer test results. Test old ARM builds, shared mmap aliasing, executable file mappings, fork/COW, and boot log write-buffer coherency result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fault-armv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fault.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/fault.c

### Purpose
Implements ARM data and prefetch abort dispatch, page fault handling, vmalloc fault synchronization, user signal delivery, kernel oops handling, and runtime FSR table patching.

### Important APIs, Types, And Functions
Important functions include `show_pte`, `do_bad_area`, `do_page_fault`, `do_translation_fault`, `do_sect_fault`, `do_DataAbort`, `do_PrefetchAbort`, `hook_fault_code`, `hook_ifault_code`, and `early_abt_enable`. Important helpers include `is_write_fault`, `vmalloc_fault`, `do_kernel_address_page_fault`, `__do_user_fault`, and `__do_kernel_fault`. `struct fsr_info` tables come from `fsr-2level.c` or `fsr-3level.c`.

### Control Flow
Abort entry computes an FSR index and calls the table handler. Page faults separate kernel-space addresses from user addresses, handle vmalloc synchronization for kernel translation faults, use kprobe and TTBR0 PAN checks, attempt RCU VMA-lock fault handling for user faults, fall back to mmap locking, call `handle_mm_fault`, and translate errors into SIGSEGV/SIGBUS/OOM or kernel fixup/oops. Prefetch aborts add `FSR_LNX_PF` to mark execute faults.

### State, Dependencies, And Integration
State is the mutable FSR/IFSR dispatch tables. Depends on generic MM fault code, signal delivery, kprobes, KFENCE, perf software events, branch predictor hardening, exception tables, and ARM page-table helpers. Integration points are low-level abort vectors and generic VM.

### Risks And Test Signals
Risks include wrong FSR decoding, sleeping in invalid contexts, missing vmalloc PMD copies, bad user/kernel address classification, signal-code regressions, and execute-fault mislabeling. Test page fault selftests, vmalloc access from kernel threads, kprobe faults, KFENCE, user SIGSEGV/SIGBUS cases, and prefetch abort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fault.h -->
## sources/distributed-fs/ceph-client/arch/arm/mm/fault.h

### Purpose
Defines ARM fault status register bit extraction and shared abort-handler prototypes.

### Important APIs, Types, And Functions
Defines `FSR_LNX_PF`, `FSR_CM`, `FSR_WRITE`, architecture-specific fault status encodings, `fsr_fs`, `is_translation_fault`, and `is_permission_fault`. Declares `do_bad_area`, `early_abt_enable`, `do_DataAbort`, and `do_PrefetchAbort`.

### Control Flow
Inline helpers decode either LPAE 6-bit FSR fields or classic 5-bit fields with split bit 10. Callers in `fault.c` use the predicates to choose page-fault, permission, execute, or oops paths.

### State, Dependencies, And Integration
No persistent state. Depends on bit macros and `CONFIG_ARM_LPAE`. It is shared by `fault.c` and `mmu.c` initialization paths.

### Risks And Test Signals
Risks are incorrect FSR masks when switching translation formats and signal misclassification. Test LPAE and non-LPAE abort cases, translation vs permission faults, write faults, and prefetch execute faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/flush.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/flush.c

### Purpose
Implements ARM cache flush/coherency helpers above the CPU-specific cache vector, including VIPT/VIVT alias handling, ptrace/uprobe write visibility, folio D-cache maintenance, and anonymous-page flushing.

### Important APIs, Types, And Functions
Important entry points are `flush_cache_mm`, `flush_cache_range`, `flush_cache_pages`, `copy_to_user_page`, `flush_uprobe_xol_access`, `__flush_dcache_folio`, `__sync_icache_dcache`, `flush_dcache_folio`, `flush_dcache_page`, and `__flush_anon_page`. `arm_heavy_mb` is exported when configured.

### Control Flow
VIVT paths delegate to VIVT helpers. VIPT aliasing paths map a fixed alias at `FLUSH_ALIAS_START` with cache color and perform line or page flushes. Ptrace/uprobe writes copy data then flush D/I aliases based on executable mapping and current CPU membership. Folio flushes either lazily clear `PG_dcache_clean` or perform kernel mapping flushes, user alias walks, and I-cache flushes as required.

### State, Dependencies, And Integration
State includes optional `soc_mb` callback and folio `PG_dcache_clean` bits. Depends on cache type helpers, highmem mappings, mapping interval trees, `mm.h` fixed aliases, SMP broadcast behavior, outer cache sync, and CPU cache-vector functions. Integrates with VM, ptrace, uprobes, page cache, DMA coherency, and executable mapping setup.

### Risks And Test Signals
Risks are stale instruction fetch after code modification, lost D-cache dirty data, over/under-flushing highmem folios, and SMP broadcast assumptions. Test ptrace text pokes, uprobes, JIT/module exec mappings, shared file mmap writes, highmem folios, and cache aliasing platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fsr-2level.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/fsr-2level.c

### Purpose
Provides classic two-level ARM fault status decode tables for data aborts and instruction aborts.

### Important APIs, Types, And Functions
Defines static `fsr_info[]` and `ifsr_info[]` arrays of `struct fsr_info`, mapping FSR indices to handler function, signal, si_code, and diagnostic name. Handlers referenced include `do_bad`, `do_translation_fault`, `do_page_fault`, and `do_sect_fault`.

### Control Flow
Included directly by `fault.c` in non-LPAE builds. `do_DataAbort` and `do_PrefetchAbort` index these tables using `fsr_fs()` and dispatch to the selected handler; runtime initialization may patch entries with `hook_fault_code`.

### State, Dependencies, And Integration
The tables are mutable static state in `fault.c`'s compilation unit. They depend on signal constants and handler definitions visible before include. Integration is low-level ARM abort dispatch for short-descriptor page tables.

### Risks And Test Signals
Risks are wrong table index meanings, mismatched signal codes, and missing CPU-specific fault overrides. Test non-LPAE translation, permission, alignment, external abort, section fault, and prefetch abort cases plus boot-time `exceptions_init` patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fsr-2level.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fsr-3level.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/fsr-3level.c

### Purpose
Provides LPAE/three-level ARM fault status decode table for both data and instruction aborts.

### Important APIs, Types, And Functions
Defines static `fsr_info[]` with 64 entries and aliases `ifsr_info` to it. Entries map LPAE fault status values to `do_translation_fault`, `do_page_fault`, `do_bad`, signal numbers, si_codes, and names such as level translation, access flag, permission, external abort, parity error, debug event, and implementation faults.

### Control Flow
Included by `fault.c` when `CONFIG_ARM_LPAE` is enabled. Abort handlers index the shared table through the LPAE `fsr_fs()` helper.

### State, Dependencies, And Integration
The table is mutable inside the `fault.c` translation unit. Depends on LPAE FSR definitions and generic signal constants. Integration point is all LPAE abort dispatch.

### Risks And Test Signals
Risks include wrong 6-bit FSR entry mapping, using one table for instruction/data cases where future hardware differs, and signal-code mismatches. Test LPAE translation, permission, access flag, alignment, debug, external abort, and parity paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/fsr-3level.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/idmap.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/idmap.c

### Purpose
Builds and uses static identity page tables for reboot/reset code that must run with predictable virtual-to-physical mappings while disabling the MMU.

### Important APIs, Types, And Functions
Important globals are `idmap_pgd` and `arch_phys_to_idmap_offset`. Main routines are `init_static_idmap`, `identity_mapping_add`, `idmap_add_pud`, `idmap_add_pmd`, and `setup_mm_for_reboot`.

### Control Flow
Early init allocates a PGD, maps `__idmap_text_start` to `__idmap_text_end` with section/PMD entries, preserving kernel image PMDs under LPAE where needed, and flushes cache to make page tables visible. Reboot setup switches to `idmap_pgd`, flushes branch predictor, and flushes TLBs on ASID-capable systems.

### State, Dependencies, And Integration
State is `idmap_pgd` and physical offset metadata marked `__ro_after_init`. Depends on page table allocation, CPU architecture checks, XIP handling, HWCAP_LPAE, proc-fns `cpu_switch_mm`, and section symbols. Integration points are CPU reset/reboot and low-level idmap text.

### Risks And Test Signals
Risks include incomplete identity range coverage, bad section attributes on ARMv5/XScale, page-table visibility without cache flush, and TLB conflicts from ASID reuse. Test reboot/kexec-like reset paths, LPAE and non-LPAE builds, XIP builds, and CPU reset on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/init.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/init.c

### Purpose
Handles ARM memory initialization around memblock reservation, DMA zone limits, initrd tags, highmem limits, init memory freeing, strict kernel permissions, and executable memory ranges.

### Important APIs, Types, And Functions
Key entry points include `__clear_cr`, `setup_dma_zone`, `arch_zone_limits_init`, `pfn_valid`, `arm_memblock_steal`, `arm_memblock_init`, `bootmem_init`, `arch_mm_preinit`, `free_initmem`, `free_initrd_mem`, and `execmem_arch_setup`. Strict RWX support uses `section_perm`, `section_update`, `set_section_perms`, `fix_kernmem_perms`, and `mark_rodata_ro`.

### Control Flow
Boot reserves kernel/initrd/page tables/platform regions, scans reserved FDT memory, reserves CMA, freezes memblock stealing, finds PFN limits, and performs early memtest. Preinit checks address layout and initializes SWIOTLB for LPAE when needed. After init, strict RWX uses `stop_machine` to update section permissions across process page tables, then init memory is poisoned and freed.

### State, Dependencies, And Integration
Persistent state includes DMA zone limit globals, `arm_memblock_steal_permitted`, and `execmem_info`. Depends on memblock, initrd/FDT, CMA, SWIOTLB, stop_machine, set_memory, ptdump, and machine descriptors. Integrates with zone setup, bootmem, module/JIT executable allocation, and rodata hardening.

### Risks And Test Signals
Risks include incorrect PFN validity near rounded pageblocks, DMA zone mis-sizing, freeing reserved memory, strict-permission section misalignment, and initrd poisoning bounds. Test boot on highmem/LPAE/non-LPAE systems, initrd load/free, DMA mask allocations, strict RWX W+X checks, and module allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/iomap.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/iomap.c

### Purpose
Provides ARM IO-port, VGA, PCI IO, and PCI memory mapping helpers.

### Important APIs, Types, And Functions
Exports `vga_base`, optional `ioport_map` and `ioport_unmap`, PCI globals `pcibios_min_io` and `pcibios_min_mem`, and `pci_iounmap`.

### Control Flow
`ioport_map` translates a port number through `__io` when available; unmap is a no-op for that static mapping model. `pci_iounmap` only calls `iounmap` for addresses inside the vmalloc range, leaving static or direct mappings alone.

### State, Dependencies, And Integration
State is global VGA/PCI minimum resource values. Depends on PCI, IO resource, io accessors, and optional `__io` platform macro. Integrates with generic PCI resource setup and driver IO-port mapping.

### Risks And Test Signals
Risks are incorrect static-vs-vmalloc unmap decisions, platform-specific `__io` translation mistakes, and bad PCI resource minima. Test PCI device probe/remove, IO port drivers, VGA access, and repeated `pci_iomap`/`pci_iounmap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/ioremap.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/ioremap.c

### Purpose
Implements ARM physical-to-kernel virtual remapping for MMIO, cached/WC device memory, executable external memory, memremap, static mappings, PCI IO space, and vmalloc page-table synchronization.

### Important APIs, Types, And Functions
Important state is `static_vmlist`, `arch_ioremap_caller`, and PCI `pci_ioremap_mem_type`. Key functions include `find_static_vm_vaddr`, `add_static_vm_early`, `ioremap_page`, `__check_vmalloc_seq`, `__arm_ioremap_caller`, `__arm_ioremap_pfn`, `ioremap`, `ioremap_cache`, `ioremap_wc`, `__arm_ioremap_exec`, `__arm_iomem_set_ro`, `arch_memremap_wb`, `iounmap`, `pci_remap_iospace`, `pci_remap_cfgspace`, and `early_ioremap_init`.

### Control Flow
Static mappings are registered early and reused when an ioremap request fits the same physical range and memory type. Dynamic ioremap validates wraparound, memory type, RAM attribute conflicts, and high-address alignment, allocates vmalloc space, then maps via section/supersection optimization on safe UP non-LPAE builds or page mappings otherwise. `iounmap` ignores static mappings and specially tears down section mappings before `vunmap`.

### State, Dependencies, And Integration
State is sorted static VM metadata and vmalloc sequence counters in `init_mm.context`. Depends on memblock, vmap/vmalloc, page-table helpers, cache/TLB flushing, KASAN vmalloc shadow syncing, PCI mapping constants, and `mmu.c` memory types. Integrates with drivers, early IO, PCI, memremap, and per-mm vmalloc fault avoidance.

### Risks And Test Signals
Risks include mapping RAM with conflicting attributes, stale per-mm vmalloc PGDs, static mapping overlap mistakes, section unmap races, and high physical address alignment failures. Test driver probe/remove loops, static map reuse, KASAN_VMALLOC, SMP vs UP section paths, PCI IO remap, and invalid ioremap inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/kasan_init.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/kasan_init.c

### Purpose
Initializes ARM KASAN shadow mappings, first with a shared early shadow page and later with real lowmem/module/pkmap shadow pages.

### Important APIs, Types, And Functions
Important state is `tmp_pgd_table` and LPAE `tmp_pmd_table`. Main routines are `kasan_early_init`, `kasan_init`, `kasan_pgd_populate`, `kasan_pmd_populate`, `kasan_pte_populate`, `clear_pgds`, and local `create_mapping`.

### Control Flow
Early init locates processor operations, verifies shadow layout, and maps the whole KASAN shadow range to `kasan_early_shadow_page`. Full init copies current page tables to temporary tables so instrumented code can run while early shadow is removed, switches MMU to the temporary PGD, clears shadow PMDs, populates real shadow for lowmem ranges under `arm_lowmem_limit`, optionally modules and pkmap, makes early shadow PTEs read-only, switches back to `swapper_pg_dir`, clears the early shadow page, and starts generic KASAN.

### State, Dependencies, And Integration
State is boot-only page-table scratch storage and allocated shadow pages from memblock. Depends on memblock allocation below `MAX_DMA_ADDRESS`, ARM page-table helpers, CPU proc lookup, `arm_lowmem_limit`, module/vmalloc config, and generic KASAN. Integrates with early MMU setup and vmalloc KASAN handling.

### Risks And Test Signals
Risks include executing instrumented code with missing shadow, mapping highmem shadow incorrectly, LPAE PGD/PMD layout assumptions, and stale TLBs across PGD switches. Test KASAN boot, lowmem/highmem split, module load with/without KASAN_VMALLOC, LPAE and non-LPAE builds, and deliberate KASAN fault detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/kasan_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/l2c-common.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/l2c-common.c

### Purpose
Provides a shared helper to disable the outer/L2 cache under strict CPU and interrupt conditions.

### Important APIs, Types, And Functions
Single function: `outer_disable`. It checks interrupts are disabled and only one CPU is online, then calls `outer_cache.disable` if supplied.

### Control Flow
The helper is synchronous and has no retry or state machine. It is meant for shutdown/suspend/reset-style contexts where other CPUs cannot use the cache concurrently.

### State, Dependencies, And Integration
No local state. Depends on `outer_cache` ops and SMP CPU online count. Integrates with platform L2 cache controller power management.

### Risks And Test Signals
Risks include disabling L2 while interrupts or secondary CPUs are active, which could corrupt memory or hang. Test suspend/resume and shutdown paths with lockdep/WARN monitoring and CPU hotplug preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/l2c-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/l2c-l2x0-resume.S -->
## sources/distributed-fs/ceph-client/arch/arm/mm/l2c-l2x0-resume.S

### Purpose
Assembly helper for secure-world early resume of L2C-310/L2X0 cache controller settings before normal CPU state restoration.

### Important APIs, Types, And Functions
Exports `l2c310_early_resume`. It reads `l2x0_saved_regs` via PC-relative offset and programs L2X0/L310 registers: auxiliary control, tag/data latency, address filters, prefetch control, power control, and enable.

### Control Flow
On entry it resolves saved-register storage, returns immediately if the controller base is zero, conditionally restores revision-dependent prefetch and power controls, returns if L2 is already enabled, then restores latency/filter/auxiliary registers and enables the controller.

### State, Dependencies, And Integration
State lives in `l2x0_saved_regs` maintained by L2X0 platform code. Depends on secure-world MMIO access and cache-l2x0 register offsets. Integrates with platform suspend/resume firmware paths.

### Risks And Test Signals
Risks include running outside secure world, invalid saved base address, wrong revision checks, and enabling L2 with stale latency/filter settings. Test suspend/resume on L2C-310 platforms, secure firmware path selection, and cache data integrity after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/l2c-l2x0-resume.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/mm.h -->
## sources/distributed-fs/ceph-client/arch/arm/mm/mm.h

### Purpose
Private ARM MM header shared by memory-management implementation files for fixed alias addresses, top-level PTE helpers, memory type descriptors, static ioremap metadata, and boot memory globals.

### Important APIs, Types, And Functions
Defines `COPYPAGE_MINICACHE`, `COPYPAGE_V6_FROM`, `COPYPAGE_V6_TO`, `FLUSH_ALIAS_START`, `VM_ARM_SECTION_MAPPING`, `VM_ARM_STATIC_MAPPING`, `VM_ARM_EMPTY_MAPPING`, and `VM_ARM_MTYPE`. Provides inline `set_top_pte` and `get_top_pte`. Defines `struct mem_type` and `struct static_vm`; declares `top_pmd`, `icache_size`, `get_mem_type`, `__flush_dcache_folio`, `static_vmlist`, `find_static_vm_vaddr`, `add_static_vm_early`, `arm_lowmem_limit`, DMA limits, `bootmem_init`, `arm_mm_memblock_reserve`, `dma_contiguous_remap`, and `__clear_cr`.

### Control Flow
Header-only inline control is limited to PTE installation/lookup in the top PMD plus local TLB flush. Other content is shared declarations.

### State, Dependencies, And Integration
State is external and owned by `mmu.c`, `ioremap.c`, `init.c`, and related files. Integrates fixed alias page-copy/flush code, ioremap metadata, DMA remap setup, and boot memory initialization.

### Risks And Test Signals
Risks include overlapping fixed virtual aliases, stale top-PTE TLB entries, and flag collisions in `vm_struct->flags`. Test builds across MMU/NOMMU, highmem, VIPT aliasing copy/flush paths, and ioremap section/static mapping paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/mmap.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/mmap.c

### Purpose
Provides ARM-specific unmapped-area selection for mmap with cache-color alignment and validates `/dev/mem` physical ranges.

### Important APIs, Types, And Functions
Main functions are `arch_get_unmapped_area`, `arch_get_unmapped_area_topdown`, `valid_phys_addr_range`, and `valid_mmap_phys_addr_range`. Important macro is `COLOUR_ALIGN`.

### Control Flow
For VIPT aliasing caches, shared/file mappings are aligned so object page offset and virtual address share the required `SHMLBA` color. `MAP_FIXED` enforces alignment for shared mappings or fails with `-EINVAL`. Non-fixed mappings first honor a suitable requested address, then call `vm_unmapped_area`; topdown allocation falls back to bottom-up on `-ENOMEM`.

### State, Dependencies, And Integration
No private persistent state. Depends on current `mm`, cache type helpers, generic unmapped-area search, VMA gap helpers, and physical memory constants. Integrates with `mmap`, SysV/shared mappings, and `/dev/mem`.

### Risks And Test Signals
Risks include cache alias corruption from bad alignment, incorrect topdown fallback, and over-permissive physical memory validation. Test mmap shared/file mappings on VIPT aliasing hardware, `MAP_FIXED` misalignment failures, ASLR/topdown mappings, and `/dev/mem` boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/mmu.c -->
## sources/distributed-fs/ceph-client/arch/arm/mm/mmu.c

### Purpose
Builds ARM MMU memory type tables, early and final kernel mappings, fixmaps, vectors, lowmem/kernel mappings, device/static IO mappings, and page-table setup for boot.

### Important APIs, Types, And Functions
Important globals are `top_pmd`, `user_pmd_table`, `pgprot_user`, `pgprot_kernel`, `mem_types`, `protection_map`, `vmalloc_size`, and `arm_lowmem_limit`. Major functions include `init_default_cache_policy`, early params `cachepolicy/nocache/nowb/ecc/vmalloc`, `get_mem_type`, `early_fixmap_init`, `__set_fixmap`, `build_mem_type_table`, mapping builders `alloc_init_*`, `create_mapping_late`, `iotable_init`, `vm_reserve_area_early`, `adjust_lowmem_bounds`, `arm_mm_memblock_reserve`, `devicemaps_init`, `kmap_init`, `map_lowmem`, `map_kernel`, `early_paging_init`, `early_fixmap_shutdown`, `paging_init`, `early_mm_init`, and `set_ptes`.

### Control Flow
Early MM init derives memory/cache attributes from CPU architecture, cache policy, SMP, TEX remap, LPAE, domains, ECC, and initial PMD attributes. Boot then adjusts lowmem/vmalloc bounds, clears unsafe page-table regions, maps lowmem around kernel sections, maps executable and non-executable kernel sections, remaps DMA/CMA regions, converts early fixmap entries to normal mappings, maps vectors/FDT/cache-flush regions/platform IO, initializes kmap/fixmap PTEs, and finishes bootmem. `set_ptes` synchronizes I/D cache for user executable mappings and marks user PTEs non-global.

### State, Dependencies, And Integration
Persistent state includes memory type/protection tables, top PMD pointer, vmalloc sizing, and lowmem limit. Depends on memblock, machine descriptors, fixmap, page-table allocation, CPU/cache type detection, FDT/ATAGS, TCM, DMA contiguous remap, KASAN-aware layout, and fault early abort enabling. Integrates with nearly every ARM MM path: ioremap, DMA, page faults, mmap, modules, vectors, and strict permissions.

### Risks And Test Signals
Risks include conflicting memory attributes, wrong section/supersection alignment, clearing needed early mappings, lowmem truncation errors, cache policy changes after boot tables, LPAE physical offset fixup failures, and user/kernel PTE permission mistakes. Test boot across LPAE/non-LPAE, SMP/UP, highmem, XIP, KASAN, vmalloc size overrides, static IO maps, `/proc/iomem`/ptdump output, DMA/CMA remap, module loading, and executable mmap coherency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mm/mmu.c -->
