<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/mm/tlbflush_32.c -->
# sources/distributed-fs/ceph-client/arch/sh/mm/tlbflush_32.c

## Purpose
This file implements local TLB invalidation for 32-bit SuperH MMU kernels. It provides page, range, kernel-range, full-mm, and global flush paths that respect the SH ASID/MMU context model.

## Important APIs, Types, and Functions
The main APIs are `local_flush_tlb_page()`, `local_flush_tlb_range()`, `local_flush_tlb_kernel_range()`, `local_flush_tlb_mm()`, and `__flush_tlb_global()`. They operate on `struct vm_area_struct`, `struct mm_struct`, CPU-local `cpu_context()`/`cpu_asid()` state, the current hardware ASID from `get_asid()`, and low-level `local_flush_tlb_one()`, `local_flush_tlb_all()`, `activate_context()`, `set_asid()`, and `MMUCR` accessors.

## Control Flow
Page and small-range flushes first check that the target mm has a valid CPU context. If the target mm is not the current mm, interrupts are disabled, the current ASID is saved, the target ASID is installed, individual TLB entries are flushed, and the saved ASID is restored. Large ranges and whole-mm flushes avoid entry-by-entry invalidation by marking `cpu_context(cpu, mm) = NO_CONTEXT`; if the mm is active, `activate_context()` allocates/reloads a fresh context. Kernel-range flushes use `init_mm`'s ASID or fall back to `local_flush_tlb_all()` when the span exceeds a quarter of the TLB. `__flush_tlb_global()` sets `MMUCR_TI`, invalidating all UTLB/ITLB entries including wired mappings.

## State and Persistence Behavior
The file mutates per-mm/per-CPU context state and transient hardware TLB state. Context invalidation persists until the mm is next activated; ASID swaps are protected by `local_irq_save()` so interrupt handlers do not run with the wrong ASID. There is no storage outside CPU MMU registers and `mm_context` metadata.

## Dependencies and Integration Points
It depends on SH MMU context helpers from `asm/mmu_context.h`, SH TLB primitives from `asm/tlbflush.h`, `current->mm`, `init_mm`, `PAGE_SIZE`, `MMU_NTLB_ENTRIES`, and raw MMUCR I/O. It is called by generic MM unmap, mprotect, page-table teardown, vmalloc/module permission changes, and SMP shootdown wrappers outside this local file.

## Risks
The highest-risk behavior is temporary ASID switching: missing interrupt masking or failed ASID restoration can corrupt unrelated address spaces. The large-range threshold trades correctness for context rollover and must keep active mms reloaded. `__flush_tlb_global()` is destructive because it also removes wired entries; callers must only use it for global invalidation cases.

## Test Signals
Build SH MMU configs and exercise fork/exec/exit, `mmap()`/`munmap()`, `mprotect()`, vmalloc/module loads, and high churn across multiple address spaces. Useful signals are no stale translations after page removal, no faults caused by wrong ASID restore, correct kernel mapping invalidation, and stable behavior around large range flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/mm/tlbflush_32.c -->
