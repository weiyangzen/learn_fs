# sources/distributed-fs/ceph-client/arch/x86/kernel/head64.c

## Purpose
Implements early 64-bit C boot setup: dynamic early page table creation, early exception handling, BSS clearing, bootdata copying, SME/TDX/KASAN ordering, and handoff to generic kernel startup.

## Important APIs And State
Defines early page table globals (`early_dynamic_pgts`, `next_early_pgt`, `early_pmd_flags`, `__pgtable_l5_enabled`, `pgdir_shift`, `ptrs_per_p4d`, `page_offset_base`, `vmalloc_base`, `vmemmap_base`) plus `__early_make_pgtable()`, `do_early_exception()`, `clear_bss()`, `x86_64_start_kernel()`, `x86_64_start_reservations()`, and `early_setup_idt()`.

## Control Flow
`x86_64_start_kernel()` resets early page tables, adjusts L5 paging bases, clears BSS/brk, clears `init_top_pgt`, initializes SME before page faults can occur, initializes KASAN, flushes global TLBs, installs early IDT, initializes TDX, copies boot params and command line, loads microcode, seeds the top-level kernel mapping, and calls reservations. Early page faults call `do_early_exception()`, which can lazily build PMD mappings, handle SEV #VC or TDX #VE, or fall back to exception fixups.

## Dependencies And Integration Points
Integrates with assembly `head_64.S`, SME/SEV/TDX early code, KASAN, fixmap, boot params, microcode, early IDT, mem encryption mapping helpers, and exported virtual address base symbols used by the rest of the kernel.

## Risks And Test Signals
Risks include early page table exhaustion/reset behavior, SME decrypted bootdata mapping lifetime, CR3 assumptions, L5 address base selection, and exception handling before full IDT. Tests include 4-level and 5-level paging boots, KASAN boots, SME/SEV/TDX guests, early #PF mapping, kexec bootdata copy, and microcode loading.
