<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/highmem.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/highmem.c

### Purpose
`highmem.c` provides the LoongArch highmem kmap TLB flush hook.

### Important APIs, Types, And Functions
The single exported function is `kmap_flush_tlb(unsigned long addr)`, exported with `EXPORT_SYMBOL`.

### Control Flow
Callers pass a virtual address whose highmem mapping changed. The function delegates directly to `flush_tlb_one(addr)`.

### State, Persistence, And Dependencies
It has no local persistent state. It depends on generic highmem/kmap users, `asm/fixmap.h`, and LoongArch `flush_tlb_one()`.

### Integration Points
Highmem kmap code uses this after changing temporary or permanent kernel mappings so stale TLB entries do not outlive a remap. It complements `fixrange_init()` and `pkmap_page_table` setup in `init.c`/`pgtable.c`.

### Risks
Insufficient flushing can expose stale highmem translations. Excessive flushing can hurt kmap-heavy I/O paths.

### Test Signals
Build with `CONFIG_HIGHMEM`, run highmem kmap stress, filesystem I/O on highmem pages, and TLB shootdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/highmem.c -->
