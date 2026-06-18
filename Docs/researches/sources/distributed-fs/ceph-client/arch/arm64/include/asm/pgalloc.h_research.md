# sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgalloc.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgalloc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgalloc.h

### Purpose
`pgalloc.h` defines ARM64 page-table allocation/population helpers for PGD/P4D/PUD/PMD/PTE levels.

### Important APIs, Types, And Functions
Key exports include `PGD_SIZE`, `__pud_populate()`, `pud_populate()`, `pud_free()`, `__p4d_populate()`, `p4d_populate()`, `__pgd_populate()`, `pgd_populate()`, `pgd_alloc()`, `pgd_free()`, and `__pmd_populate()`/PMD population helpers. It also declares architecture-specific PGD/PUD free support.

### Control Flow
MM code allocates page-table pages, then population helpers install table descriptors with physical addresses and protections. Free helpers release unused levels, with compile-time folding depending on configured page-table levels.

### State, Persistence, And Dependencies
State is process/kernel page-table memory. It depends on hardware page-table definitions, processor/cacheflush/TLB flush helpers, and generic pgalloc.

### Integration Points
Used by process address-space creation, vmalloc/module mappings, page faults, and KVM-related page-table code indirectly.

### Risks
Population helpers must use correct descriptor types and barriers/cache maintenance. Folded-level configurations must not free nonexistent tables.

### Test Signals
Cross-build all page-table levels/page sizes; run fork/exec, vmalloc, memory hotplug, page fault, and TLB flush tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgalloc.h -->
