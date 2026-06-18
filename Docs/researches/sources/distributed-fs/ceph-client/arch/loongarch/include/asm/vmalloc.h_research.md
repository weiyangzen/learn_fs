<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vmalloc.h

Purpose: supplies LoongArch vmalloc hooks through generic definitions.
Important APIs and types: includes generic vmalloc behavior without additional architecture-specific helpers.
Control flow: runtime vmalloc behavior is implemented by generic MM and page-table code.
State and persistence: vmalloc mappings persist in kernel page tables; this file has no state.
Dependencies and integration: depends on `pgtable.h` address-space layout and generic vmalloc.
Risks and test signals: minimal local risk; signals include vmalloc stress, module loading, ioremap, and KASAN vmalloc coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vmalloc.h -->
