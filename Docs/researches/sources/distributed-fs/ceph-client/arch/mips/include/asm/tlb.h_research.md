# sources/distributed-fs/ceph-client/arch/mips/include/asm/tlb.h

## Purpose

`tlb.h` declares MIPS TLB management helpers and constants.

## Important APIs, Types, And Functions

The API covers local and SMP TLB flush prototypes, wired-entry helpers, debug dump hooks, runtime TLB handler generation, or unique EntryHi construction depending on the file. Includes: `asm/cpu-features.h`, `asm/mipsregs.h`, `asm-generic/tlb.h`. Macros/constants: `__ASM_TLB_H`, `_UNIQUE_ENTRYHI`, `UNIQUE_ENTRYHI`, `UNIQUE_GUEST_ENTRYHI`. Functions/prototypes/helpers: `num_wired_entries`, `read_c0_wired`.

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
Static review signal: this source currently has 27 lines and 613 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
