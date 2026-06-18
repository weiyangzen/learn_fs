# sources/distributed-fs/ceph-client/arch/arc/mm/tlb.c

Purpose: manages ARC MMU/TLB flush, insertion, diagnostics, feature discovery, and initialization for MMUv3/MMUv4.

Important APIs/functions: TLB flush APIs include `local_flush_tlb_all()`, `local_flush_tlb_mm()`, `local_flush_tlb_range()`, `local_flush_tlb_page()`, kernel-range flushes, SMP wrappers, and THP PMD flushes. Insertion/update paths are `create_tlb()`, `update_mmu_cache_range()`, and `update_mmu_cache_pmd()`. Init/reporting APIs are `arc_mmu_mumbojumbo()`, `pae40_exist_but_not_enab()`, `arc_mmu_init()`, and duplicate handler `do_tlb_overlap_fault()`.

Control flow: MMUv3 lookup/probe/write and MMUv4 delete/insert paths differ behind helpers. Large flushes prefer ASID rollover or full flush; smaller ranges erase entries one by one under IRQ disable. Page-fault completion pre-installs TLB entries for the current mm and flushes D/I cache for executable pages with dirty kernel mappings. Boot decodes MMU BCRs, validates page and superpage sizes, enables ASID 0, and caches the kernel PGD.

State and persistence: per-CPU `asid_cache`, global `mmuinfo`, and debug knob `dup_pd_silent` persist. It mutates hardware aux registers, TLB entries, PTE accessed/dirty/present bits, and folio `PG_dc_clean`.

Dependencies and integration: integrates with `tlbex.S` fast refill, `fault.c`, MMU context code, cache maintenance, THP, SMP IPIs, PAE40, and ARC aux registers.

Risks: ASID and IRQ ordering are critical; checking ASID and erasing entries must be atomic with respect to context switches/interrupts. PAE40 high descriptor writes must match hardware. Preinstalling TLB entries assumes `current->active_mm == vma->vm_mm`. Duplicate TLB recovery scans hardware sets and should remain conservative.

Test signals: fork/exit/munmap flush behavior, SMP TLB shootdowns, THP faults/flushes, executable page cache coherency, PAE40 builds, duplicate TLB fault recovery, and MMU feature mismatch boot panics.
