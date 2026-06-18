<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/mmap.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/mmap.c

### Purpose
`mmap.c` implements LoongArch unmapped-area selection, address validity checks, and `/dev/mem` physical-range validation.

### Important APIs, Types, And Functions
Key functions are `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `__virt_addr_valid()`, `valid_phys_addr_range()`, and `valid_mmap_phys_addr_range()`. Internal `arch_get_unmapped_area_common()` uses `struct vm_unmapped_area_info` and cache-color alignment macros.

### Control Flow
For `MAP_FIXED`, the code validates the range is below `TASK_SIZE` and rejects shared mappings whose address/pgoff violates `SHMLBA` coloring. Non-fixed requests align requested hints, check for a gap via `find_vma()`, then call `vm_unmapped_area()` bottom-up or top-down. Top-down failures fall back to bottom-up. `__virt_addr_valid()` accepts KFENCE addresses, rejects non-direct-map and vmalloc-range addresses, then checks `pfn_valid()`. Physical range checks use memblock coverage and CPU physical address width.

### State, Persistence, And Dependencies
It does not persist data; it reads `current->mm`, VMA layout, memblock, CPU physical address bits, and KFENCE state. Dependencies include generic mmap, hugepage alignment, memblock, and LoongArch address conversion.

### Integration Points
Generic `mmap()` and shared-memory code call the unmapped-area hooks. `/dev/mem` read/mmap paths use the physical-range validators. `virt_addr_valid()` users rely on `__virt_addr_valid()`.

### Risks
Cache coloring alignment affects shared mappings and ABI compatibility. Top-down fallback limits must avoid collisions with stack and mmap base. Physical range width checks must handle overflow correctly.

### Test Signals
Run mmap layout tests, SysV shared-memory alignment tests, hugetlb mmap tests, `/dev/mem` policy tests, and KFENCE/direct-map address validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/mmap.c -->
