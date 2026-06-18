# sources/distributed-fs/ceph-client/arch/mips/include/asm/tlbex.h

## Purpose

`tlbex.h` declares MIPS TLB management helpers and constants.

## Important APIs, Types, And Functions

The API covers local and SMP TLB flush prototypes, wired-entry helpers, debug dump hooks, runtime TLB handler generation, or unique EntryHi construction depending on the file. Includes: `asm/uasm.h`. Macros/constants: `__ASM_TLBEX_H`. Types/enums/unions: `tlb_write_entry`, `uasm_label`, `uasm_reloc`. Functions/prototypes/helpers: `build_get_pmde64`, `build_get_pgde32`, `build_get_ptep`, `build_update_entries`, `build_tlb_write_entry`, `build_tlb_refill_handler`, `handle_tlbl`, `handle_tlbs`, `handle_tlbm`.

## Control Flow

Callers flush all, mm, range, kernel-range, page, or single virtual-address TLB entries; TLB exception code may build refill handlers dynamically and wired-entry code reserves fixed TLB slots.

## State And Persistence

State is hardware TLB contents, wired-entry count, MM context IDs, generated handler code, and debug output; no filesystem persistence exists.

## Dependencies And Integration Points

It integrates with `mmu_context`, page fault handling, VM unmap/mprotect, SMP shootdowns, KVM/guest mappings where applicable, and low-level exception vectors.

## Risks

Risks are stale translations, missing SMP shootdowns, wrong wired count, TLB refill handler encoding errors, and debug-only code using unsafe register state.

## Test Signals

Test signals are mmap/munmap/mprotect stress, fork/exec, SMP TLB shootdown tests, highmem/cache alias cases, and boot on CPUs with varied TLB sizes.
Static review signal: this source currently has 38 lines and 1014 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
