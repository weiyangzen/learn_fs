<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmalloc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmalloc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmalloc.h` customizes arm64 vmalloc/vmap mapping sizes, huge-vmap support, contiguous PTE choices, and tagged vmalloc protections. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_ASM_ARM64_VMALLOC_H`, `arch_vmap_pud_supported`, `arch_vmap_pmd_supported`, `arch_vmap_pte_range_map_size`, `arch_vmap_pte_range_unmap_size`, `arch_vmap_pte_supported_shift`, `arch_vmap_pgprot_tagged`; functions/prototypes/exports: `arch_vmap_pud_supported`, `arch_vmap_pmd_supported`, `arch_vmap_pte_range_map_size`, `arch_vmap_pte_range_unmap_size`, `arch_vmap_pte_supported_shift`, `arch_vmap_pgprot_tagged`. The file is 74 lines / 1869 bytes. Direct includes are `asm/page.h`, `asm/pgtable.h`.

### Control Flow
Generic vmalloc asks these helpers whether PUD/PMD blocks are supported and what PTE range size to use. The PTE helper returns contiguous-PTE mappings only when size and virtual/physical alignment allow it.

### State, Persistence, And Dependencies
Notable global/static state symbols are `max_page_shift`. No local persistent state; decisions affect vmalloc page tables and TLB behavior maintained by the MM subsystem. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Bad alignment checks or unmap size detection can corrupt vmalloc mappings, leak stale TLB entries, or mishandle MTE-tagged vmalloc memory.

### Test Signals
Run vmalloc, module load, BPF JIT, huge-vmap, and KASAN/MTE tagged-vmalloc tests across page-size configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vmalloc.h -->
