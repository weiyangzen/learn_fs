<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r4k.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r4k.c

### Purpose
`tlb-r4k.c` implements TLB maintenance for R4000-style MIPS MMUs, including VTLB/FTLB invalidation, MMID support, hugepage updates, wired mappings, TLB uniquification, boot-time configuration, and CPU power-management restore.

### Important APIs, Types, And Functions
Flush APIs include `local_flush_tlb_all()`, range/page/kernel flushes, and `local_flush_tlb_one()`. Update and setup APIs include `__update_tlb()`, `add_wired_entry()`, `add_temporary_entry()`, `has_transparent_hugepage()`, and `tlb_init()`. Internal helpers include `flush_micro_tlb()`, `r4k_tlb_uniquify_*()`, `r4k_tlb_configure()`, and the CPU PM notifier.

### Control Flow
Flush paths stop the hardware table walker, preserve EntryHi/MMID, probe matching entries for small ranges, write unique invalid EntryHi values, restart HTW, and flush Loongson micro-TLBs as needed. `__update_tlb()` walks the software page tables, handles huge PMD leaves when configured, loads even/odd EntryLo values including XPA forms, and writes random or indexed entries. `tlb_init()` configures PageMask, wired/framed mask state, RIXI/PageGrain bits, optional `ntlb=` restriction, TLB uniquification, and generated refill handlers.

### State, Persistence, And Dependencies
Persistent hardware state includes CP0 PageMask, Wired, EntryHi/EntryLo, MMID, PageGrain, temporary TLB index, and TLB contents. Software state includes `temp_tlb_entry`, optional `ntlb`, and CPU cache/TLB descriptors. Dependencies include HTW controls, hazard macros, memblock/slab allocation, sort, hugepage and XPA PTE layouts, and `tlbex.c`.

### Integration Points
This is the main TLB backend for most MIPS CPUs. It integrates with generic MM TLB shootdowns, hugepage support, power management, boot command-line parsing, and generated exception refill handlers.

### Risks
Races with HTW or shared FTLB require careful stop/start sequencing. Uniquification must avoid wired/global collisions or later flushes can fail. XPA wired entries are explicitly unsupported. `ntlb=` can reduce usable entries and change performance. CPU errata and Loongson micro-TLB flushing are easy to regress.

### Test Signals
Exercise ASID and MMID context switching, vmalloc flushes, hugepages, transparent hugepage detection, suspend/resume or CPU PM exit, FTLB/VTLB systems with `cpu_has_tlbinv`, and boot with valid/invalid `ntlb=` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-r4k.c -->
