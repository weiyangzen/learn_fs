<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/tlbex.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/tlbex.S

### Purpose
`tlbex.S` contains the low-level LoongArch TLB load, store, modify, protect, PTW fallback, and refill exception handlers.

### Important APIs, Types, And Functions
Symbols include generated `tlb_do_page_fault_0`, `tlb_do_page_fault_1`, `handle_tlb_protect`, `handle_tlb_load`, `handle_tlb_load_ptw`, `handle_tlb_store`, `handle_tlb_store_ptw`, `handle_tlb_modify`, `handle_tlb_modify_ptw`, and 32/64-bit `handle_tlb_refill`. It uses `_PAGE_PRESENT`, `_PAGE_VALID`, `_PAGE_WRITE`, `_PAGE_DIRTY`, `_PAGE_MODIFIED`, `_PAGE_HUGE`, and LoongArch CSR/TLB instructions.

### Control Flow
Load/store/modify handlers save scratch registers, read the fault address, select user `PGDL` or kernel `swapper_pg_dir`, walk page-table levels in assembly, detect huge PMD entries, update PTE valid/dirty/modified bits atomically under SMP using LL/SC, and write paired TLB entrylo values. Missing permissions branch to `tlb_do_page_fault_*`, which saves full regs and calls `do_page_fault()`. Hugepage paths invalidate the ASID/address, synthesize huge entrylo0/1, set huge page size, fill TLB, and restore default size. Refill handlers use either explicit 32-bit walks or 64-bit `lddir`/`ldpte`.

### State, Persistence, And Dependencies
State is CPU registers, CSRs, TLB entries, and page-table PTE bits. Dependencies include saved-register layout, page-table shift constants, LoongArch instruction macros, `do_page_fault()`, `swapper_pg_dir`, and SMP atomic primitives.

### Integration Points
`tlb.c` installs these symbols into exception vectors. `fault.c` handles slow paths. `hugetlbpage.c` and PTE bit definitions must match hugepage entry encoding here.

### Risks
This is extremely layout-sensitive assembly. Branch offsets, LL/SC loops, paired PTE alignment, CSR page-size restoration, and hugepage global-bit conversion are all correctness-critical. A bug can manifest as silent memory corruption, infinite faults, or privilege boundary failures.

### Test Signals
Boot under software refill and hardware PTW configs, run page-fault stress, dirty/accessed-bit tests, SMP mmap/write races, hugepage tests, and instruction-level disassembly review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/tlbex.S -->
