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
