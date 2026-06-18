# sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable.h

### Purpose
This is UMLs central page-table contract, defining PTE flags, protections, vmalloc layout, PTE manipulation, TLB sync marking, and swap PTE encoding.

### Important APIs, Types, And Functions
It defines `_PAGE_*` bits, selects 2- or 4-level geometry, declares `swapper_pg_dir`, defines `PAGE_*` protections, helpers such as `set_pte()`, `set_ptes()`, `um_tlb_mark_sync()`, `pte_same()`, `pfn_pte()`, `pte_modify()`, and swap-entry/exclusive helpers.

### Control Flow
PTE writes mark `_PAGE_NEEDSYNC`; batched `set_ptes()` marks the mm context range for later host mmap/munmap synchronization. Flush helpers also mark ranges, while kernel range flushes sync immediately through TLB code.

### State, Persistence, And Dependencies
State is page-table memory plus `mm->context.sync_tlb_range_from/to` protected by `sync_tlb_lock`. Dependencies include Linux mm types, selected page-table-level headers, UML address layout, and TLB sync implementation.

### Integration Points And Risks
Risks include execute-as-read semantics, `set_ptes()` PFN arithmetic, swap bit packing limits, `_PAGE_NEEDSYNC` comparisons, and lost sync range updates under concurrency. Integration is with generic mm, SKAS page faults, and host TLB synchronization.

### Test Signals
Run mmap/mprotect/munmap, prot-none, swap-entry, vmalloc, fork, and SKAS TLB synchronization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable.h -->
