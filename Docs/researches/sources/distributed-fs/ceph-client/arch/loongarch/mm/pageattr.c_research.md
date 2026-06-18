<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/pageattr.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/pageattr.c

### Purpose
`pageattr.c` changes kernel mapping attributes such as execute, read-only/read-write, and direct-map valid/default state.

### Important APIs, Types, And Functions
Public functions are `set_memory_x()`, `set_memory_nx()`, `set_memory_ro()`, `set_memory_rw()`, `kernel_page_present()`, `set_direct_map_default_noflush()`, `set_direct_map_invalid_noflush()`, and `set_direct_map_valid_noflush()`. Internal pieces are `struct pageattr_masks`, `set_pageattr_masks()`, page-table walk callbacks for all levels, and `__set_memory()`.

### Control Flow
`__set_memory()` builds set/clear masks, locks `init_mm` for write, walks the kernel page-table range, updates leaf entries at any level or PTEs, unlocks, and flushes the kernel TLB range. Attribute helpers skip addresses below `vm_map_base`. `kernel_page_present()` manually walks the direct or vmapped page tables and treats leaf entries as present.

### State, Persistence, And Dependencies
State is kernel page-table entries and TLB state; no filesystem persistence. Dependencies include generic pagewalk, memblock, `init_mm`, LoongArch PTE bits, and TLB flush APIs.

### Integration Points
Module/JIT/text permission changes, rodata protection, memory hotplug, and direct-map hardening use these hooks. BPF JIT finalization indirectly relies on executable text mappings and I-cache flushing.

### Risks
The `set_direct_map_valid_noflush()` `nr` argument is ignored and only one page is changed, which is a notable review point if callers expect multi-page behavior. Leaf-level updates must preserve unrelated PTE bits. Skipping low direct-map addresses below `vm_map_base` may be intentional but limits hardening.

### Test Signals
Run LKDTM ro/rw/nx tests, module load/unload, BPF JIT execution, direct-map invalidation tests, and page-table walk debug checks for huge mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/pageattr.c -->
