<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r3k.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r3k.c

### Purpose
`tlb-r3k.c` implements R2000/R3000-style TLB flushing, update, wired-entry installation, and TLB initialization.

### Important APIs, Types, And Functions
`local_flush_tlb_all()`, `local_flush_tlb_range()`, `local_flush_tlb_kernel_range()`, and `local_flush_tlb_page()` invalidate entries. `__update_tlb()` inserts or updates a PTE for a faulting address. `add_wired_entry()` installs one of the first eight wired entries. `tlb_init()` flushes and builds refill handlers.

### Control Flow
Flush routines save interrupt state and current EntryHi/ASID, probe for matching entries when ranges are small, invalidate by zeroing EntryLo and writing indexed entries, or drop the full MM context when flushing a large range. Updates probe the target page and use random or indexed TLB writes. Initialization clears all entries and calls `build_tlb_refill_handler()`.

### State, Persistence, And Dependencies
State lives in CP0 EntryHi, EntryLo0, Index, wired entry count, and per-MM CPU contexts. Dependencies include R3k TLB instruction helpers, ASID masks, SMP CPU context tracking, and `tlbex.c` handler generation.

### Integration Points
Generic MM and TLB shootdown code call these local flush/update functions on R3k-class CPUs. Wired entries support early permanent mappings.

### Risks
CP0 hazard avoidance is minimal and architecture-specific. The file reserves only eight wired entries. Large-range flushing drops the context rather than walking entries, which affects later ASID refill behavior.

### Test Signals
Run process context-switch and mmap/munmap workloads on R3k, test kernel vmalloc flushes, install wired mappings, and validate page faults refill correctly after `tlb_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r3k.c -->
