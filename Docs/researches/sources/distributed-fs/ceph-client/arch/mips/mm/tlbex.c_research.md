<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlbex.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlbex.c

### Purpose
`tlbex.c` synthesizes MIPS TLB refill and TLB load/store/modify fastpaths at runtime. It uses the MIPS micro-assembler to generate CPU-specific handlers that walk kernel page tables, update PTE accessed/dirty bits, load EntryLo registers, and fall back to normal page-fault assembly.

### Important APIs, Types, And Functions
Key exported helpers are `build_tlb_refill_handler()`, `build_tlb_write_entry()`, `build_get_pmde64()`, `build_get_pgde32()`, `build_get_ptep()`, and `build_update_entries()`. Important state includes `tlb_handler`, `labels`, `relocs`, `handler_reg_save`, `scratch_reg`, `pgd_reg`, `mips_xpa_disabled`, `check_for_high_segbits`, and `kscratch_used_mask`. Major builders cover R3000 refill/change handlers, R4000 refill/load/store/modify handlers, Loongson3 LDPTE handlers, hugepage tails, PGD setup, HTW setup, XPA setup, and PTE bit tests.

### Control Flow
At `build_tlb_refill_handler()`, the code validates XPA/RIXI requirements, emits debug definitions, probes EntryLo fill bits, chooses R3000 or R4000 style generation, allocates KScratch registers, writes the PGD setup helper, emits load/store/modify fastpaths into `tlb-funcs.S` buffers, emits the refill handler into `ebase`, flushes icache, and then configures XPA and HTW if supported. Generated handlers walk from PGD to PTE, handle vmalloc or high-segbits fallbacks, optionally update huge PMDs, use LL/SC for SMP PTE updates, write TLB entries with CPU-specific hazard sequences, and branch to `tlb_do_page_fault_0/1` on failure.

### State, Persistence, And Dependencies
Generated code persists in exception-vector memory and reserved fastpath buffers. Runtime hardware state includes KScratch, Context, PageMask, PWField/PWSize/PWCtl, KPGD, PageGrain, and EntryLo/EntryHi. Dependencies include `uasm`, CPU feature flags, CP0 hazard rules, TLB errata workarounds, bbit/lwx/ldpte instruction availability, hugepage and XPA PTE layout, SMP register save slots, and `tlbex-fault.S`.

### Integration Points
`tlb-r3k.c` and `tlb-r4k.c` call this during TLB initialization. The generated handlers are core MM exception paths for every process and kernel address-space fault. The `tlbmiss_handler_setup_pgd` helper is used to keep current PGD state in memory, Context, KScratch, or PWBASE depending on configuration.

### Risks
This file has a large CPU/config matrix and many size constraints. Branch delay slots, relocation offsets, KScratch allocation, high-segbits checks, RIXI fill-bit rotation, XPA high PFN writes, LL/SC retry loops, HTW races, and CPU-specific TLB write hazards are all sensitive. Buffer overflow checks panic, but subtle wrong code generation can cause silent memory corruption or fault loops.

### Test Signals
High-value tests are booting R3000, R4000, microMIPS, Loongson3 LDPTE, Octeon bbit/lwx, SMP, hugepage, XPA, HTW, and high-vmbits configurations; forcing TLB load/store/modify faults; vmalloc faults; page permission upgrades; dirty/accessed bit races; and checking debug dumps for handler length and relocation sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlbex.c -->
