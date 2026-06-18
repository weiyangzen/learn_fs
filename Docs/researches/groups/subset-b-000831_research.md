# Research Report: subset-b-000831

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/dump_pagetables.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/dump_pagetables.c

Purpose: implements s390 kernel page table dumping and W+X validation for the kernel address space. It plugs into generic `ptdump_walk_pgd()` callbacks, exposes `kernel_page_tables` through debugfs when `CONFIG_PTDUMP_DEBUGFS` is enabled, and provides `ptdump_check_wx()` for boot/runtime validation of writable executable mappings.

Important APIs, types, and functions: `struct addr_marker` describes named virtual address ranges; `struct pg_state` embeds `struct ptdump_state` and carries output state, current protection, marker position, and W+X counters. `note_page_*()` callbacks normalize PGD/P4D/PUD/PMD/PTE entries into protection summaries. `ptdump_check_wx()` walks `init_mm` without seq output and returns false if unexpected W+X pages are found. `ptdump_show()` serializes dumping with `cpa_mutex`. `pt_dump_init()` computes `max_addr`, creates markers for kernel image, lowcore, identity map, modules, vmemmap, vmalloc, KASAN/KMSAN/KFENCE ranges, sorts them, and registers debugfs.

Control flow: the walker calls `note_page()` for each entry level. `note_page()` collapses adjacent ranges while protection and level stay unchanged, emits marker boundaries when the next marker start is crossed, and flushes the final range on level `-1`. W+X checking flows through `note_prot_wx()`, which skips invalid, read-only, NX, and documented lowcore executable cases. Initialization adds paired start/end markers, sorts everything except the sentinel, and leaves `markers` as persistent global state for later debugfs reads.

State and persistence: persistent globals are `max_addr`, `markers`, and `markers_cnt`. Debugfs output is read-only and derived from current kernel page tables. W+X counters are per-walk. The dump is protected by `cpa_mutex` to avoid racing with kernel page attribute changes.

Dependencies and integration points: depends on generic ptdump, debugfs, seq_file, s390 page table bits, `init_mm`, lowcore, KASAN/KMSAN/KFENCE layout constants, `nospec_uses_trampoline()`, `cpu_has_bear()`, and `cpu_has_nx()`. It integrates with `pageattr.c` through the external `cpa_mutex` and with kernel hardening through `CONFIG_DEBUG_WX`.

Risks: wrong marker sorting can mislabel nested ranges; stale or missing markers can make debug output misleading. W+X detection has architecture exceptions for lowcore, so changes to lowcore execution requirements must be reflected here. `max_addr` derives from kernel ASCE type and bounds the generic walker; a bad bound could access non-existent page-table levels or miss mappings.

Test signals: boot logs from `ptdump_check_wx()` should report pass/fail accurately; `/sys/kernel/debug/kernel_page_tables` should contain coherent named sections and protection summaries. Useful coverage includes NX-enabled and NX-disabled machines, BEAR and no-BEAR lowcore behavior, debug_pagealloc/pageattr changes during dumps, and configurations with KASAN, KMSAN, and KFENCE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/dump_pagetables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/extable.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/extable.c

Purpose: implements s390 exception table lookup and fixup dispatch. It handles normal kernel exception tables, the special amode31 table, user-access fixups, BPF probe fixups, floating-point-control cleanup, zeropad partial loads, and MVCOS retry behavior.

Important APIs, types, and functions: `s390_search_extables()` searches normal tables first and then `__start_amode31_ex_table` to `__stop_amode31_ex_table`. `fixup_exception()` is the exported dispatcher used by fault handling. Handler helpers include `ex_handler_fixup()`, `ex_handler_ua_fault()`, `ex_handler_ua_load_reg()`, `ex_handler_zeropad()`, `ex_handler_fpc()`, and `ex_handler_ua_mvcos()`. `struct insn_ssf` decodes MVCOS SSF-format operands from the fixup instruction.

Control flow: fault handling calls `fixup_exception()` with pt_regs. If no table entry matches the current instruction pointer, it returns false. Otherwise it switches on `ex->type`, adjusts `regs->psw.addr` to `extable_fixup(ex)`, and edits registers according to the fixup contract. MVCOS faults are retried by trimming the length register to the first page boundary or to zero, ensuring a follow-up instruction completes with condition code zero.

State and persistence: no persistent state is owned here. The only state changes are in `pt_regs`: PSW address, error registers set to `-EFAULT`, zeroed destination registers, data register for zeropad, and FPC reset through `fpu_sfpc(0)`.

Dependencies and integration points: depends on Linux extable helpers, s390 `asm-extable` data encoding, `ex_handler_bpf()` from the BPF JIT, s390 FPU helpers, and `fault.c` kernel fault recovery. It is tightly coupled to assembly annotations that encode `EX_DATA_REG_ADDR`, `EX_DATA_REG_ERR`, and exception type values.

Risks: register metadata in exception table entries must match the faulting instruction; a mismatch can corrupt pt_regs and return to unsafe code. `ex_handler_zeropad()` dereferences an aligned kernel address after a faulting access, so its use must be limited to annotated sequences where that recovery is valid. Unknown exception types deliberately panic.

Test signals: user access helpers should return `-EFAULT` or zeroed data instead of oopsing. BPF probe-memory tests should recover through `EX_TYPE_BPF`. MVCOS boundary tests should show partial-copy progress. Kernel fault tests should verify that unannotated faults still oops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/extmem.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/extmem.c

Purpose: manages z/VM DCSS external memory segments on s390. It can query, load, unload, save, and change shared/nonshared access for named segments, maps loaded segments into the kernel address space, reserves their physical ranges, and exports the segment API to loadable users.

Important APIs, types, and functions: `struct dcss_segment` stores EBCDIC name, resource name, start/end, refcount, access mode, VM segment type, ranges, segment count, and `struct resource`. `segment_type()`, `segment_load()`, `segment_unload()`, `segment_save()`, `segment_modify_shared()`, and `segment_warning()` are exported. Internals include `dcss_mkname()`, `dcss_diag()`, `query_segment_type()`, `segment_overlaps_others()`, and `__segment_load()`.

Control flow: callers enter `segment_load()`, which rejects non-VM machines, serializes on `dcss_lock`, reuses an already loaded segment if access mode matches, or allocates a new `dcss_segment`. `__segment_load()` queries segment metadata through diagnose x'64', rejects unsupported multipart layouts, checks overlap with loaded DCSS entries and `iomem_resource`, creates kernel virtual mapping via `vmem_add_mapping()`, then issues shared or nonshared load diagnose. Failures unwind mapping, resource, and allocation state. `segment_modify_shared()` only reloads when the segment refcount is one. `segment_unload()` drops the refcount, releases resources and mappings at zero, and purges on CPU 0 for a documented z/VM workaround. `segment_save()` constructs DEFSEG/SAVESEG CP commands from stored ranges.

State and persistence: persistent in-kernel state is `dcss_list`, guarded by `dcss_lock`, plus per-segment resource reservations and virtual mappings. VM-side persistent state can be changed by `segment_save()`. `loadshr_scode`, `loadnsr_scode`, `purgeseg_scode`, and `segext_scode` hold diagnose subcodes.

Dependencies and integration points: depends on z/VM detection, diagnose x'64', EBCDIC conversion, CPCMD, mem resources, `vmem_add_mapping()`/`vmem_remove_mapping()`, and exported extmem headers. It integrates with users of DCSS segments that need shared memory, exclusive writable segments, or saved segment contents.

Risks: mapping/resource/diagnose ordering must remain exact to avoid leaked resources or stale mappings. Segment overlap checks compare megabyte-shifted ranges and must match DCSS granularity. `segment_modify_shared()` frees and removes a segment on reload failure, so callers must handle invalidation. `segment_save()` command construction depends on bounded string formatting and stored range metadata.

Test signals: VM-only tests should cover query, load shared, load nonshared, duplicate load refcounting, access-mode mismatch `-EPERM`, unload-to-zero purge, unsupported multipart segment `-EOPNOTSUPP`, range overflow `-ERANGE` from `vmem_add_mapping()`, and save command response handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/extmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/fault.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/fault.c

Purpose: handles s390 translation, protection, and secure-storage faults. It decodes TEID state, performs VMA lookup and `handle_mm_fault()` integration, reports user faults, attempts exception-table/KFENCE recovery for kernel faults, and turns unrecoverable faults into signals or oopses.

Important APIs, types, and functions: `do_protection_exception()`, `do_dat_exception()`, and, under KVM, `do_secure_storage_access()` are architecture entry points. Helpers include `is_kernel_fault()`, `get_fault_address()`, `fault_is_write()`, `dump_pagetable()`, `dump_fault_info()`, `report_user_fault()`, `handle_fault_error_nolock()`, `handle_fault_error()`, `do_sigsegv()`, `do_sigbus()`, and `do_exception()`. `show_unhandled_signals` is exposed as `kernel/userprocess_debug`.

Control flow: DAT faults call `do_exception()` with access flags; protection faults may rewind PSW for suppressing exceptions, validate TEID bit 61, special-case NX faults, then call `do_exception(VM_WRITE)`. `do_exception()` clears single-step trap state, lets kprobes handle page faults, rejects kernel/faulthandler-disabled/no-mm cases to the kernel-error path, then attempts a VMA-lock fast path for user faults before falling back to `lock_mm_and_find_vma()`. Fault results dispatch to OOM, SIGSEGV, SIGBUS, or BUG for unexpected flags. Kernel faults first try `fixup_exception()` and KFENCE before dumping table state and dying.

State and persistence: persistent state is the sysctl-backed `show_unhandled_signals`. Fault handling mutates current thread flags, pt_regs PSW address, mm fault statistics, signal state, and, for secure storage, folio secure/shared state. No durable storage is written.

Dependencies and integration points: depends on generic mm fault APIs, VMA lock fast path, kprobes, perf software events, exception tables, KFENCE, s390 TEID/ASCE layout, lowcore ASCEs, UV protected virtualization helpers, and KVM secure-storage behavior.

Risks: TEID interpretation is facility-dependent; invalid bit-61 handling is intentionally fatal for unexpected user protection exceptions. Locking paths must release mmap/VMA locks exactly once across retry and `VM_FAULT_COMPLETED`. Secure-storage conversion must hold folio references correctly and avoid kernel continuation if conversion fails. Fault address synthesis for NX combines TEID and PSW page bits and is sensitive to architecture semantics.

Test signals: page fault tests should cover user map errors, access errors, write faults, OOM/sigbus paths, VMA lock retry, kernel uaccess fixups, KFENCE faults, NX protection, no-mm/faulthandler-disabled faults, and secure guest storage conversion under KVM/UV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/gmap_helpers.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/gmap_helpers.c

Purpose: provides exported helper routines for KVM guest mapping code to discard swapped userspace backing pages, mark PTEs as unused, and disable COW sharing for a process that backs guest memory.

Important APIs, types, and functions: exported functions are `gmap_helper_zap_one_page()`, `gmap_helper_discard()`, `gmap_helper_try_set_pte_unused()`, and `gmap_helper_disable_cow_sharing()`. Internal helpers include `ptep_zap_softleaf_entry()`, `find_zeropage_pte_entry()`, `find_zeropage_ops`, and `__gmap_helper_unshare_zeropages()`.

Control flow: `gmap_helper_zap_one_page()` requires the mmap lock, skips missing/hugetlb VMAs, obtains a locked PTE, and clears swap entries while adjusting mm counters and swap references. `gmap_helper_discard()` walks intersecting VMAs and zaps non-hugetlb ranges. `gmap_helper_try_set_pte_unused()` walks page-table levels locklessly enough to find a regular PTE, uses `spin_trylock()` on the PTE lock to avoid inversion with KVM mmu_lock, validates the PMD, and atomically sets `_PAGE_UNUSED`. `gmap_helper_disable_cow_sharing()` requires write mmap lock, flips `mm->context.allow_cow_sharing`, unshares mapped zeropages through page walking and `FAULT_FLAG_UNSHARE`, disables KSM, and rolls back the flag on error.

State and persistence: mutates PTEs, swap counters, swap references, VMA mappings through zap operations, and `mm->context.allow_cow_sharing`. It can disable KSM for the process but notes user space can re-enable it.

Dependencies and integration points: depends on Linux pagewalk, swap/softleaf helpers, KSM, hugetlb checks, mmap locking, and s390 `_PAGE_UNUSED`. It is exported GPL for KVM gmap users that need memory discard semantics and private/nonshared backing.

Risks: `gmap_helper_try_set_pte_unused()` intentionally skips optimization on lock contention; callers must tolerate normal swapping. COW-sharing disable does not address fork-shared anonymous pages, only KSM and zeropages. Zeropage unshare loops must handle races where faulting does not immediately replace the zeropage. Incorrect lock context can deadlock or violate assertions.

Test signals: KVM guest memory tests should verify swapped pages are discarded, hugetlb VMAs are skipped, unused-page optimization does not deadlock under mmu_notifier contention, KSM is disabled, zeropages are replaced with anonymous pages, and errors restore `allow_cow_sharing`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/gmap_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/hugetlbpage.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/hugetlbpage.c

Purpose: implements s390 huge TLB page table operations, converting between Linux PTE encodings and s390 segment/region-table large-entry encodings for 1 MiB PMD and 2 GiB PUD huge pages.

Important APIs, types, and functions: `__pte_to_rste()` and `__rste_to_pte()` convert present, empty, prot-none, dirty/young, soft-dirty, noexec, and swap encodings. `__set_huge_pte_at()`, `set_huge_pte_at()`, `huge_ptep_get()`, `__huge_ptep_get_and_clear()`, `huge_pte_alloc()`, `huge_pte_offset()`, `arch_hugetlb_valid_size()`, and `arch_hugetlb_cma_order()` implement the arch hugetlb interface.

Control flow: setting a huge PTE converts the Linux PTE to an RSTE and sets PMD large or PUD region3-large bits based on the existing table slot type. Getting reverses the encoding. Clearing uses `pudp_xchg_direct()` for region3 entries or `pmdp_xchg_direct()` for segment entries to perform architecture-correct invalidation. Allocation walks PGD/P4D/PUD and returns either the PUD slot for 2 GiB huge pages or a PMD slot for 1 MiB huge pages.

State and persistence: no private persistent state. It mutates page tables through standard mm structures and depends on direct TLB invalidation helpers in `pgtable.c`.

Dependencies and integration points: integrates with generic hugetlb, swap encoding helpers, s390 EDAT1/EDAT2 CPU feature detection, and page-table allocation. CMA hugepage order is only provided for EDAT2/PUD hugepages.

Risks: conversion tables are bit-sensitive; missing a software or hardware bit corrupts hugepage permissions or swap entries. `__set_huge_pte_at()` infers PUD vs PMD from the current slot value, so callers must pass the correct slot. Hugepage sizes are feature-gated; tests on machines without EDAT should reject unsupported sizes.

Test signals: hugetlb mmap/fault/unmap tests for 1 MiB and 2 GiB sizes, swap/migration entries, soft-dirty if enabled, NX and write-protect transitions, and TLB shootdown after clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/init.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/init.c

Purpose: initializes core s390 memory-management state: kernel page directories, zero pages, zone limits, vmem mapping, protected virtualization DMA sharing, per-cpu areas, memory hotplug, CMA offline restrictions, and executable-memory ranges.

Important APIs, types, and functions: global exported state includes `swapper_pg_dir`, `invalid_pg_dir`, `s390_invalid_asce`, noexec masks, `empty_zero_page`, `zero_page_mask`, and `__per_cpu_offset`. Functions include `arch_setup_zero_pages()`, `arch_zone_limits_init()`, `paging_init()`, `mark_rodata_ro()`, `set_memory_encrypted()`, `set_memory_decrypted()`, `force_dma_unencrypted()`, `arch_mm_preinit()`, `memory_block_size_bytes()`, `setup_per_cpu_areas()`, memory hotplug `arch_add_memory()`/`arch_remove_memory()`, and `execmem_arch_setup()`.

Control flow: early setup allocates a power-of-two zero-page pool sized by available memory and sets `zero_page_mask`. `paging_init()` initializes virtual memory mappings and the 31-bit DMA zone limit. `mark_rodata_ro()` enables instruction-execution protection when NX exists and write-protects ro-after-init data. Protected virtualization setup registers restricted virtio memory access and forces SWIOTLB shared bounce buffers. Per-cpu setup uses `pcpu_embed_first_chunk()` and fills offsets. Hot-add creates a vmem direct mapping before `__add_pages()` and unwinds on failure; hot-remove removes pages then tears down mapping. Execmem setup randomizes module load start under KASLR.

State and persistence: establishes long-lived global page directories, zero-page pool, noexec masks, per-cpu offset table, SWIOTLB/PV memory attributes, memory notifier for CMA, and execmem range metadata.

Dependencies and integration points: depends on memblock, vmem, pageattr, UV protected virtualization, SWIOTLB, virtio restricted memory access, CMA, memory hotplug, SCLP memory increment size, percpu allocator, KASLR, KASAN-aware execmem, and generic DMA APIs.

Risks: zero-page order must balance mapping granularity and small-memory pressure. PV encrypted/decrypted naming maps to UV shared/unshared state and is easy to misuse. Memory hotplug requires PAGE_KERNEL mappings and correct vmem unwind. CMA notifier prevents offlining memory that intersects CMA; missing this risks DMA allocation corruption.

Test signals: boot on normal and protected-virtualization guests, memory hot-add/remove, CMA offline rejection, `/proc/meminfo` direct-map counts via pageattr, per-cpu area sanity, rodata write-protection faults, and module allocation within `MODULES_VADDR` to `MODULES_END`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/maccess.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/maccess.c

Purpose: implements s390-specific safe kernel memory access helpers: writing protected kernel memory via real-address stores, copying from real memory through a temporary mapping, and translating `/dev/mem` lowcore/prefix pages into safe bounce buffers.

Important APIs, types, and functions: globals `__memcpy_real_area` and `memcpy_real_ptep` identify the reserved real-memory copy mapping. `__s390_kernel_write()` is the protected write primitive, using `s390_kernel_write_odd()` and a spinlock. `memcpy_real_iter()` and `memcpy_real()` copy from physical memory. `xlate_dev_mem_ptr()` and `unxlate_dev_mem_ptr()` implement `/dev/mem` physical pointer translation. `get_swapped_owner()` locates a CPU owning a swapped prefix page.

Control flow: kernel writes are serialized with `s390_kernel_write_lock` and update up to 8 bytes at a time with read-modify-write and `sturg`, bypassing DAT and page-table write protection. Real-memory copy maps one physical page at a time into `__memcpy_real_area`, invalidates the old PTE when the physical page changes, copies to an iterator, and stops on short copy. `/dev/mem` translation handles absolute lowcore and swapped prefix pages by allocating an atomic bounce page and copying the relevant lowcore view.

State and persistence: persistent state is the reserved mapping address/PTE and locks. The mapping PTE is updated under `memcpy_real_mutex`. Bounce pages allocated by `xlate_dev_mem_ptr()` must be freed by `unxlate_dev_mem_ptr()` when not a direct physical mapping.

Dependencies and integration points: depends on s390 lowcore, absolute lowcore helpers, PTE invalidation, no-fault/real-address assembly, CPU hotplug read locking, and generic iov_iter. It integrates with text patching, memory access debug helpers, and `/dev/mem`.

Risks: protected writes are byte-range read-modify-write operations and must stay serialized to avoid lost updates. `unxlate_dev_mem_ptr()` distinguishes bounce vs direct by comparing physical address and pointer; wrong translation would leak or free the wrong page. Real-memory mapping is single-slot global state, so missing the mutex would race.

Test signals: kernel text/static key patching paths using `s390_kernel_write()`, real-memory copy across page boundaries, short iterator behavior, `/dev/mem` reads of absolute lowcore and per-CPU prefix pages, and CPU hotplug races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/maccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/mmap.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/mmap.c

Purpose: defines s390 virtual memory layout policy for mmap base randomization, top-down vs legacy layout selection, unmapped-area search alignment, ASCE limit checking, and VM protection mapping.

Important APIs, types, and functions: `arch_mmap_rnd()`, `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `arch_pick_mmap_layout()`, `setup_protection_map()`, and `DECLARE_VM_GET_PAGE_PROT` are the arch-facing APIs. Helpers include `stack_maxrandom_size()`, `mmap_is_legacy()`, `mmap_base_legacy()`, `mmap_base()`, and `get_align_mask()`.

Control flow: process setup chooses bottom-up legacy layout when personality, unlimited stack, or sysctl demands it; otherwise it chooses top-down layout below stack with random gap. Unmapped-area search honors MAP_FIXED, caller hints, `mmap_min_addr`, hugepage alignment, shared/file ASLR alignment, and falls back from top-down to bottom-up on `-ENOMEM`. All successful candidate addresses go through `check_asce_limit()` so the process address-space control element supports the requested range.

State and persistence: fills `mm->mmap_base` and `MMF_TOPDOWN` per process. `protection_map[16]` is initialized once after boot and is read-only after init.

Dependencies and integration points: depends on generic mmap search, rlimits, randomization masks, hugetlb file checks, s390 ASCE growth limits, `mmap_min_addr`, stack guard gap, and generic `vm_get_page_prot` declaration.

Risks: ASCE limit checking is architecture-critical because s390 user page tables can upgrade levels lazily. Alignment behavior differs for hugepages, file/shared mappings, and anonymous private mappings; changes can affect ABI-visible mmap placement. Protection map deliberately makes private writable mappings initially read-only for COW, while shared writable maps are RW.

Test signals: mmap layout tests under legacy personality, unlimited/limited stack, ASLR on/off, MAP_FIXED, hint address, hugepage files, large allocations near TASK_SIZE, and permissions in `/proc/*/maps`/fault behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/page-states.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/page-states.c

Purpose: hooks page allocation and free paths into s390 CMMA page-state instructions for guest page hinting of unused and stable pages.

Important APIs, types, and functions: exported global `cmma_flag` selects whether page-state instructions are active and which stable mode to use. `arch_free_page()` calls `__set_page_unused()` for freed pages. `arch_alloc_page()` calls `__set_page_stable_dat()` or `__set_page_stable_nodat()` for allocated pages.

Control flow: both hooks return immediately when `cmma_flag` is zero. On free, the entire buddy order range is marked unused. On allocation, the same range is marked stable; `cmma_flag < 2` selects DAT-aware stable marking, otherwise no-DAT stable marking.

State and persistence: persistent state is boot-preserved `cmma_flag`. Page state is maintained in hardware/firmware metadata through s390 page-state instructions.

Dependencies and integration points: depends on generic page allocator arch hooks, s390 page-state primitives, and boot setup that initializes `cmma_flag`.

Risks: incorrect order/range conversion could hint the wrong memory range. The hooks must remain cheap because they run in allocator paths. Behavior depends on host support and boot-time CMMA enablement.

Test signals: allocation/free stress under CMMA-enabled guests, host page hint counters if available, and boot with CMMA disabled to confirm hooks become no-ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/page-states.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/pageattr.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/pageattr.c

Purpose: changes kernel direct-map and vmalloc page attributes on s390: RO/RW, NX/X, invalid/default, and 4K splitting. It also initializes storage keys, reports direct-map page sizes, checks page presence, and supports debug page allocation/KFENCE map toggling.

Important APIs, types, and functions: exported/shared APIs include `__storage_key_init_range()`, `arch_report_meminfo()`, `split_pud_page()`, `__set_memory()`, `set_direct_map_invalid_noflush()`, `set_direct_map_default_noflush()`, `set_direct_map_valid_noflush()`, `kernel_page_present()`, and `__kernel_map_pages()`. Internal walkers `walk_p4d_level()`, `walk_pud_level()`, `walk_pmd_level()`, and `walk_pte_level()` update tables. `cpa_mutex` serializes changes and is also used by ptdump.

Control flow: `__set_memory()` masks NX operations on non-NX CPUs, normalizes the range, locks `cpa_mutex`, changes the target mapping, then applies RO/RW aliases for vmalloc-backed pages to the direct map. Large PUD/PMD entries are split when 4K pages are requested or a range does not cover a full large entry. Updates use `pgt_set()`, which chooses CRDTE on EDAT2 or CSPG otherwise. Debug map toggling invalidates PTEs with IPTE range support when available.

State and persistence: mutates kernel page tables and direct-map page counters `direct_pages_count[]` under `CONFIG_PROC_FS`. Storage key initialization writes hardware storage keys. No persistent disk state.

Dependencies and integration points: depends on s390 CRDTE/CSPG/IPTE instructions, vmem allocation helpers, direct-map accounting, vmalloc metadata, CPU feature checks, `set_memory` API, KFENCE, and debug_pagealloc.

Risks: splitting large direct-map entries increases page-table memory and must update direct-map counters accurately. Alias propagation intentionally excludes execute permissions; incorrectly propagating X would weaken direct-map NX policy. Page invalid/default changes are noflush APIs, so callers must manage required flushing semantics. Invalid input ranges return `-EINVAL` on missing page-table entries.

Test signals: `set_memory_ro/rw/nx/x/4k` tests on aligned and partial large-page ranges, `/proc/meminfo` DirectMap counters, vmalloc alias permission changes, debug_pagealloc/KFENCE page poisoning, and `kernel_page_present()` around invalidated direct-map pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/pageattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/pfault.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/pfault.c

Purpose: implements z/VM pseudo page fault support, allowing a guest task to sleep when the hypervisor pages in its memory while the virtual CPU runs other work.

Important APIs, types, and functions: boot parameter `nopfault` disables support. `struct pfault_refbk` describes diagnose x'258' init/fini blocks. `__pfault_init()` and `__pfault_fini()` issue the diagnose. `pfault_interrupt()` handles external interrupts. `pfault_cpu_dead()` wakes pending waiters during CPU teardown. `pfault_irq_init()` registers the external IRQ and hotplug callback.

Control flow: early init registers `EXT_IRQ_CP_SERVICE`, initializes the hypervisor feature, registers service-signal subclass, and installs CPU-dead cleanup. Interrupt handling filters subcode, extracts task pid token, references the task, and serializes on `pfault_lock`. Completion interrupts either wake a sleeping task or mark `pfault_wait = -1` if completion won the race. Initial interrupts for current user task set `pfault_wait = 1`, add the thread to `pfault_list`, set state uninterruptible, and request reschedule. CPU dead wakes and dereferences all pending waiters.

State and persistence: persistent globals are `pfault_disable`, `pfault_lock`, and `pfault_list`; per-task state lives in `thread.pfault_wait` and `thread.list`. Hypervisor registration persists until fini.

Dependencies and integration points: depends on s390 external interrupt infrastructure, diagnose x'258', task lookup by pid namespace, scheduler task states, cpuhotplug, and lowcore LPP token layout.

Risks: initial/completion interrupt ordering is explicitly racy and encoded through `pfault_wait` values 1 and -1. The initial interrupt must correspond to `current`; otherwise a warning path avoids sleeping the wrong task. Reference counting must pair list references and interrupt references exactly.

Test signals: z/VM guest paging pressure should show tasks blocking/waking without vCPU stalls. Tests should cover `nopfault`, completion-before-initial, initial-before-completion, CPU offline while tasks wait, module/boot init failure fallback, and absence of stuck `TASK_UNINTERRUPTIBLE` tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/pfault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/pgalloc.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/pgalloc.c

Purpose: allocates and frees s390 page-table and region/segment-table structures, upgrades user address-space table depth, and builds "base" ASCE mappings without enhanced DAT large-page features for I/O users.

Important APIs, types, and functions: `crst_table_alloc_noprof()`, `crst_table_free()`, `crst_table_upgrade()`, `page_table_alloc_noprof()`, `page_table_free()`, optional `pte_free_defer()`, `base_asce_alloc()`, and `base_asce_free()` are the externally relevant APIs. Internal base walkers include `base_page_walk()`, `base_segment_walk()`, `base_region3_walk()`, `base_region2_walk()`, and `base_region1_walk()`.

Control flow: CRST/PTE allocation uses generic pagetable allocation, accounting unless `init_mm`, DAT page-state marking, constructors, and invalid entry initialization. `crst_table_upgrade()` requires mmap write lock, allocates new upper levels when an address exceeds current ASCE limit, swaps `mm->pgd` and context ASCE under `page_table_lock`, then runs `on_each_cpu()` to update active lowcore/user control registers and flush local TLBs. Base ASCE allocation chooses the smallest ASCE type covering `addr + num_pages`, allocates tables recursively, fills PTEs using `lra`, and unwinds through `base_asce_free()` on failure.

State and persistence: mutates `mm->pgd`, `mm->context.asce`, `mm->context.asce_limit`, page table counters, and per-page DAT state. `base_pgt_cache` is lazily created and persists for base page tables.

Dependencies and integration points: depends on generic pagetable constructors/destructors, s390 control-register ASCE handling, TLB flushing, page-state helpers, RCU for THP PTE free, slab cache APIs, and I/O users needing non-EDAT ASCEs.

Risks: ASCE upgrade must update all active CPUs to prevent stale TLBs and incorrect address-space limits. Base ASCEs are explicitly not safe to attach to CPUs; doing so would leave uncleared TLB entries. Constructor/destructor pairing and table-level accounting must stay exact.

Test signals: mmap beyond current ASCE limits, fork/exit page-table allocation/free stress, THP split/free with RCU, I/O paths using `base_asce_alloc()`, low-memory allocation failure unwind, and multi-CPU ASCE upgrade TLB correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/pgalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/pgtable.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/pgtable.c

Purpose: implements s390 page-table entry exchange, TLB invalidation, DAT protection reset, hugepage table exchange helpers, write-combine protection, and THP deposited page-table handling.

Important APIs, types, and functions: exported APIs include `pgprot_writecombine()`, `ptep_xchg_direct()`, `ptep_reset_dat_prot()`, `ptep_xchg_lazy()`, `ptep_modify_prot_start()`, `ptep_modify_prot_commit()`, `pmdp_xchg_direct()`, `pmdp_xchg_lazy()`, `pudp_xchg_direct()`, and THP `pgtable_trans_huge_deposit()`/`pgtable_trans_huge_withdraw()`. Internal invalidation helpers include local/global IPTE and IDTE variants.

Control flow: PTE flush helpers read the old entry, skip invalid entries, increment `mm->context.flush_count`, choose local invalidation when the mm is only on the current CPU and the CPU supports local TLB control, otherwise issue global invalidation. Lazy paths can mark entries invalid and set `flush_mm` when only attached locally, deferring full work. Exchange APIs disable preemption, flush, set the new entry, and re-enable preemption. RDP reset clears hardware protect without invalidating the entry, then writes only software-bit changes.

State and persistence: mutates PTE/PMD/PUD entries, `mm->context.flush_count`, `mm->context.flush_mm`, and THP `pmd_huge_pte()` FIFO list state. `pgprot_writecombine()` uses the global `mio_wb_bit_mask`.

Dependencies and integration points: depends on s390 IPTE/IDTE/RDP instructions, machine guest-TLB support, gmap ASCE state, mm CPU masks, TLB local-control facility, THP, KSM/sysctl includes, and MIO write-combine bit from PCI/MMIO support.

Risks: invalidation options must match host vs guest ASCE state; wrong NODAT/GUEST_ASCE selection can leave stale guest translations. Lazy invalidation relies on CPU attach masks. RDP may only be used when the new PTE differs in permitted bits. THP deposit/withdraw assumes PMD lock and FIFO list layout embedded in page-table memory.

Test signals: mprotect/protection change stress, KVM guest TLB invalidation, THP split/collapse, local-vs-global flush paths on SMP, write-combine mappings for MIO devices, and RDP-specific protect-bit reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/physaddr.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/physaddr.c

Purpose: provides the exported s390 `__phys_addr()` conversion with debug validation.

Important APIs, types, and functions: `__phys_addr(unsigned long x, bool is_31bit)` is exported. It checks that the virtual address is not vmalloc/module space, converts with `__pa_nodebug()`, and optionally asserts the result fits below 2 GiB for 31-bit users.

Control flow: validation happens before and after conversion through `VIRTUAL_BUG_ON()`. The function returns the physical address on success.

State and persistence: no owned state; pure conversion with debug assertions.

Dependencies and integration points: depends on generic mm debug helpers, s390 `__pa_nodebug()`, and callers that need strict physical address conversion.

Risks: callers must not pass vmalloc/module addresses. The 31-bit flag is a hard assertion, not a recoverable error, so misuse can BUG in debug configurations.

Test signals: conversion of direct-map kernel addresses, rejection of vmalloc/module addresses in debug builds, and 31-bit overflow assertion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/physaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/vmem.c -->
## sources/distributed-fs/ceph-client/arch/s390/mm/vmem.c

Purpose: manages s390 kernel virtual memory mappings for the direct map, vmemmap, KASAN range, and ad hoc 4K mappings. It allocates/frees page-table levels, uses large direct-map entries when possible, supports memory hotplug, and initializes kernel text/rodata protections.

Important APIs, types, and functions: `vmem_crst_alloc()`, `vmem_pte_alloc()`, `vmemmap_populate()`, `vmemmap_free()`, `vmem_add_mapping()`, `vmem_remove_mapping()`, `arch_get_mappable_range()`, `vmem_get_alloc_pte()`, `__vmem_map_4k_page()`, `vmem_map_4k_page()`, `vmem_unmap_4k_page()`, and `vmem_map_init()`. Internal walkers are `modify_pte_table()`, `modify_pmd_table()`, `modify_pud_table()`, `modify_p4d_table()`, and `modify_pagetable()`.

Control flow: mapping changes are serialized by `vmem_mutex` at public entry points. `modify_pagetable()` validates alignment and ensures the range is limited to direct-map/vmemmap/KASAN-safe regions, then recursively allocates or removes levels. Direct mappings use 2 GiB PUD or 1 MiB PMD large entries when aligned, supported, and debug pagealloc allows it; vmemmap mappings allocate backing pages or use altmap and optimize partially used PMD frames with `PAGE_UNUSED` markers. Removing mappings clears entries, frees empty tables, and flushes the kernel TLB range. `vmem_map_init()` applies ROX/RO protections to kernel text and rodata and may force 4K direct-map entries under debug pagealloc.

State and persistence: persistent global state includes `vmem_mutex` and `unused_sub_pmd_start`; page tables and direct-map counters are mutated. Vmemmap backing pages may come from memblock, buddy allocator, or altmap.

Dependencies and integration points: depends on memblock, memory hotplug, vmem_altmap, pageattr splitting, direct-map counters, debug_pagealloc, EDAT facilities, KASAN bounds, lowcore/absolute mapping limits, TLB flushing, and kernel section symbols.

Risks: partial vmemmap PMD optimization relies on `PAGE_UNUSED` poisoning and consecutive section behavior. Removal must not touch page tables outside allowed kernel mapping areas. Direct-map large-page accounting must match actual entries. `vmem_get_alloc_pte()` treats existing large entries as errors because callers expect 4K-only areas.

Test signals: memory hot-add/remove, vmemmap populate/free with and without altmap, debug_pagealloc forcing 4K direct map, KASAN shadow mapping, direct-map large-page counters, 4K map/unmap APIs, and rodata/text permission checks after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/mm/vmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/net/Makefile -->
## sources/distributed-fs/ceph-client/arch/s390/net/Makefile

Purpose: declares the s390 architecture-specific networking objects selected by kernel configuration.

Important APIs, types, and functions: build variables add `bpf_jit_comp.o` and `bpf_timed_may_goto.o` when `CONFIG_BPF_JIT` is enabled, and `pnet.o` when `CONFIG_HAVE_PNETID` is enabled.

Control flow: Kbuild conditionally includes objects based on config symbols; there is no runtime control flow.

State and persistence: no runtime state. It controls which object files are linked into the kernel or module build.

Dependencies and integration points: integrates s390 BPF JIT support with core BPF JIT configuration and PNET ID support with network device identification.

Risks: omitting `bpf_timed_may_goto.o` while enabling the JIT would leave the JIT's timed-may-goto support unresolved. Incorrect config guard would compile code on unsupported configurations or miss required helpers.

Test signals: build matrix with `CONFIG_BPF_JIT=y/n` and `CONFIG_HAVE_PNETID=y/n`, plus link checks for `arch_bpf_timed_may_goto` and `pnet_id_by_dev_port`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/net/bpf_jit_comp.c -->
## sources/distributed-fs/ceph-client/arch/s390/net/bpf_jit_comp.c

Purpose: implements the s390x eBPF JIT compiler, BPF exception-table recovery, runtime BPF text patching, BPF trampoline generation, stack walking for BPF exceptions, and architecture capability predicates.

Important APIs, types, and functions: `struct bpf_jit` tracks compiler state, register usage, instruction addresses, program/literal pool offsets, exception entries, PLT locations, arena bases, and stack frame offset. Public hooks include `ex_handler_bpf()`, `bpf_jit_needs_zext()`, `bpf_int_jit_compile()`, `bpf_jit_supports_kfunc_call()`, `bpf_jit_supports_far_kfunc_call()`, `bpf_arch_text_poke()`, `arch_bpf_trampoline_size()`, `arch_prepare_bpf_trampoline()`, `bpf_jit_supports_subprog_tailcalls()`, `bpf_jit_supports_arena()`, `bpf_jit_supports_fsession()`, `bpf_jit_supports_insn()`, `bpf_jit_supports_exceptions()`, `arch_bpf_stack_walk()`, and `bpf_jit_supports_timed_may_goto()`. Major internals include emit macros, `bpf_jit_prologue()`, `bpf_jit_epilogue()`, `bpf_jit_insn()`, `bpf_jit_prog()`, `bpf_jit_alloc()`, `bpf_jit_plt()`, and trampoline helpers around `struct bpf_tramp_jit`.

Control flow: compilation runs multiple passes. Initial passes compute clobbered registers, conservative sizes, literal-pool placement, and instruction address invariants. The final pass allocates executable memory plus exception table storage, emits code, fills extable entries for probe-memory instructions, optionally dumps code, locks the image read-only, and installs `fp->bpf_func`. `bpf_jit_insn()` lowers BPF ALU, endian, memory, atomics, calls, tail calls, exits, and branches to s390 instructions, using short relative branches when possible and literal pools for constants. Probe-memory paths emit paired exception entries so faults land after the protected instruction and clear the destination register as needed. Text patching verifies a hotpatch branch/PLT, updates PLT target and branch mask via `s390_kernel_write()`, then synchronizes text. Trampoline generation computes an s390 ABI stack layout, saves original args/return state, invokes fentry/fmod_ret/fexit programs, optionally calls the original function, handles session cookies and return values, and emits restore/return code.

State and persistence: per-program JIT state lives in `fp->aux->jit_data` across extra subprogram passes and is freed once final line info is filled. Generated code, literal pools, PLTs, and exception tables persist in BPF binary memory. Runtime text patches mutate generated code and PLT targets. No repository or disk state is used.

Dependencies and integration points: depends on core BPF verifier/JIT APIs, s390 instruction encoding, extable format, `s390_kernel_write()` from `maccess.c`, text patch synchronization, nospec branch thunks, unwind/backchain support, BTF function models, BPF trampoline common code, arena support, kfunc call handling, and `arch_bpf_timed_may_goto` from assembly.

Risks: pass invariants require code size to never grow after addresses are established and to remain identical during codegen; violations are WARNed and fail compilation. Instruction encoding, register mapping, tail-call counter handling, and trampoline ABI differences are high risk. Probe-memory exception table counts must match verifier-provided counts after local adjustment for XCHG. Text patching must verify current code before modifying it and handle CPUs already executing old PLTs. Arena mode deliberately rejects some instructions.

Test signals: BPF selftests on s390 with JIT enabled, verifier zext tests, ALU/branch/memory/atomic/tail-call/kfunc tests, probe-read fault recovery, arena tests including unsupported instruction rejection, trampoline fentry/fexit/fmod_ret/fsession tests, live text poke attach/detach, exception stack unwinding, and timed may-goto tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/net/bpf_jit_comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/net/bpf_timed_may_goto.S -->
## sources/distributed-fs/ceph-client/arch/s390/net/bpf_timed_may_goto.S

Purpose: provides the s390 assembly helper `arch_bpf_timed_may_goto` used by the BPF JIT for timed conditional looping support.

Important APIs, types, and functions: `SYM_FUNC_START(arch_bpf_timed_may_goto)` defines a special-ABI function. It calls `bpf_check_timed_may_goto`. It also emits an indirect branch thunk with `GEN_BR_THUNK %r1` and returns using `BR_EX`.

Control flow: the helper receives parameters in `%r12` and `%r13`, return address in `%r0`, and preserves all GPRs except `%r0`, `%r1`, and `%r12`. It saves `%r2`-`%r5`, `%r14`, the return address, `%r15`, and backchain in a compact frame, computes `%r2 = %r12 + %r13`, calls `bpf_check_timed_may_goto`, moves `%r2` back to `%r12`, restores saved registers, loads return address into `%r1`, and branches through the nospec-aware return macro.

State and persistence: no global state. It uses stack frame state only for register preservation and backchain.

Dependencies and integration points: depends on s390 stack frame offsets from `asm-offsets.h`, nospec branch macros, BPF core `bpf_check_timed_may_goto`, and the JIT special-case call path that expects this ABI.

Risks: stack-frame offset math is guarded by a preprocessor check, but ABI drift between the JIT and this helper would corrupt BPF registers or return address. The special clobber set must remain synchronized with `bpf_jit_comp.c`.

Test signals: BPF timed may-goto selftests, register preservation checks across helper calls, stack unwinding/backchain validation, and nospec thunk build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/net/bpf_timed_may_goto.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/net/pnet.c -->
## sources/distributed-fs/ceph-client/arch/s390/net/pnet.c

Purpose: extracts s390 Physical Network Identifier values from CCW group or PCI network devices so upper layers can identify ports attached to the same physical network.

Important APIs, types, and functions: `pnet_id_by_dev_port()` is exported GPL. Internal `pnet_ids_by_device()` fills a 64-byte utility string buffer. Constants define four 16-byte PNET IDs.

Control flow: callers pass a device and port. The code rejects null devices or ports beyond four. For CCW group devices, it reads the utility string from the first child ccw device, converts EBCDIC to ASCII, and copies all PNET IDs. For PCI devices, it copies `zdev->util_str` and converts it. `pnet_id_by_dev_port()` returns the selected nonzero 16-byte ID or `-ENOENT`.

State and persistence: no persistent state. Stack buffers hold copied PNET IDs. Device utility strings are read from CCW or zPCI device state.

Dependencies and integration points: depends on ccwgroup/ccwdev helpers, zPCI device conversion, EBCDIC conversion, and network code configured with `CONFIG_HAVE_PNETID`.

Risks: CCW groups assume the first bundled subchannel utility string represents the group. Empty all-zero IDs are treated as absent. Device type checks must match the actual parent devices passed by networking drivers.

Test signals: CCW group and PCI network devices with populated utility strings, empty utility strings returning `-ENOENT`, invalid port indexes, non-supported device types returning no ID, and ASCII conversion correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/net/pnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/Makefile -->
## sources/distributed-fs/ceph-client/arch/s390/pci/Makefile

Purpose: declares the s390 PCI subsystem object composition for Kbuild.

Important APIs, types, and functions: when `CONFIG_PCI` is enabled it builds core files including `pci.o`, IRQ, CLP, event, debug, instruction, MMIO, bus, KVM hook, report, and fixup support. `CONFIG_PCI_IOV` adds SR-IOV support through `pci_iov.o`; `CONFIG_SYSFS` adds `pci_sysfs.o`.

Control flow: no runtime behavior; Kbuild conditionals select objects.

State and persistence: no runtime state. Build state determines which s390 PCI features exist in the kernel image.

Dependencies and integration points: integrates PCI core support with optional SR-IOV and sysfs layers. `pci.o` depends on the companion objects listed here for IRQ setup, CLP scanning, bus registration, MMIO, and diagnostics.

Risks: missing companion objects would break unresolved symbols or silently drop PCI features. Config guards must stay aligned with source-level `#ifdef`s and exported hooks.

Test signals: build coverage for `CONFIG_PCI=y/n`, `CONFIG_PCI_IOV=y/n`, and `CONFIG_SYSFS=y/n`, plus link validation of the full s390 PCI subsystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci.c -->
## sources/distributed-fs/ceph-client/arch/s390/pci/pci.c

Purpose: implements the s390 zPCI core: global device registry, domain allocation, CLP enable/disable, config-space access, BAR/iomap handling with and without MIO, bus resource setup, PCI device lifecycle, function measurement blocks, hot reset, error-state control, scanning, and subsystem initialization.

Important APIs, types, and functions: global state includes `zpci_list`, `zpci_list_lock`, `zpci_add_remove_lock`, `zpci_domain`, `zpci_iomap_bitmap`, `zpci_iomap_start`, static key `have_mio`, FMB cache, AEN blocks `zpci_aipb`/`zpci_aif_sbv`, boot options, and initialization flag. Exported/public functions include `zpci_zdev_put()`, `get_zdev_by_fid()`, `zpci_remove_reserved_devices()`, `pci_domain_nr()`, `zpci_register_ioat()`, `zpci_unregister_ioat()`, `zpci_fmb_enable_device()`, `zpci_fmb_disable_device()`, `ioremap_prot()`, `iounmap()`, `pci_iomap*()`, `pci_iounmap()`, `pcibios_device_add()`, `pcibios_release_device()`, `pcibios_enable_device()`, `pcibios_disable_device()`, `zpci_alloc_domain()`, `zpci_free_domain()`, `zpci_enable_device()`, `zpci_reenable_device()`, `zpci_disable_device()`, `zpci_hot_reset_device()`, `zpci_create_device()`, `zpci_add_device()`, `zpci_scan_configured_device()`, `zpci_deconfigure_device()`, `zpci_device_reserved()`, `zpci_release_device()`, `zpci_report_error()`, `zpci_clear_error_state()`, `zpci_reset_load_store_blocked()`, `pcibios_setup()`, `zpci_is_enabled()`, and `zpci_scan_devices()`.

Control flow: boot `pci_base_init()` honors `pci=off`, validates facilities 69/71, enables MIO addressing if available and not disabled, initializes debug, memory/iomap/FMB state, IRQs, scans CLP-discovered devices, initializes firmware sysfs, and marks PCI initialized. Device creation allocates `zpci_dev`, queries CLP properties, initializes locks, then `zpci_add_device()` initializes IOMMU, registers a zPCI bus device, initializes kref, and links it globally. PCI core callbacks map resources, claim BARs, enable FMB/debug on device enable, and undo those on release/disable. BAR access either returns function-handle cookies backed by `zpci_iomap_start` or real MIO ioremaps. Enable/disable flows call CLP set PCI function operations and update function handles. Hot reset disables an enabled device, tolerates one z/VM/LPAR inconsistency, and reenables IRQ/IOMMU state. Deconfigure removes from PCI core, disables, calls SCLP deconfigure, and moves to standby. Reserved devices drop their list reference and are freed when kref reaches zero.

State and persistence: persistent kernel state includes the global zPCI list, per-domain bitmap, iomap entries and refcounts, FMB allocations, per-device state locks/krefs/resources/IOMMU state, static MIO branch, and boot option flags. Hardware state is changed through CLP, SCLP, and modify-PCI operations.

Dependencies and integration points: depends on s390 CLP/SCLP PCI facilities, PCI core, zPCI bus/IRQ/IOMMU/debug/sysfs/fixup companions, MIO facility bits, static keys, generic resource tree, kmem caches, list sorting, and exported MMIO/iomap APIs used by drivers.

Risks: global locking and kref lifetime are subtle: `zpci_zdev_put()` nests add/remove mutex with `kref_put_lock()`, and release expects the list lock held. Function-handle cookie mappings must update on FH changes and track counts without underflow/overflow. MIO and non-MIO paths expose different pointer semantics. Error/reset paths must restore IRQ and IOAT state or leave devices disabled. Resource setup can partially allocate BAR resources and needs cleanup on later failure.

Test signals: boot scan on machines with/without PCI facilities and with `pci=off`/`nomio`/`force_floating`/`norid`; PCI config read/write; BAR mapping/unmapping under MIO and FH modes; domain allocation with unique UID and auto fallback; FMB enable/disable; hot reset with IOMMU/IRQ active; device reservation/removal kref paths; CLP error injection; and driver probe/remove using standard PCI APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci.c -->
