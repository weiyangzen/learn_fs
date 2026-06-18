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
