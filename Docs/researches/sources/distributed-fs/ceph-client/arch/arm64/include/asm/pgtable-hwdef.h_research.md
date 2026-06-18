# sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-hwdef.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-hwdef.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-hwdef.h

### Purpose
`pgtable-hwdef.h` defines ARM64 hardware page-table geometry, descriptor bit layouts, contiguous-entry sizing, address masks, memory attributes, permission bits, and TCR/TTBR field aliases.

### Important APIs, Types, And Functions
It exports `ARM64_HW_PGTABLE_LEVELS()`, `ARM64_HW_PGTABLE_LEVEL_SHIFT()`, `PTRS_PER_*`, `PMD/PUD/P4D/PGDIR_SHIFT/SIZE/MASK`, contiguous PTE/PMD constants, descriptor type bits, table UXN/PXN bits, PMD/PTE access/dirty/contiguous/XN/user bits, `PHYS_TO_PTE_ADDR_MASK`, `PTE_ATTRINDX()`, permission indirection/overlay bits, stage-2 memory attributes, TCR field aliases, TTBR masks, and 52-bit VA offset constants.

### Control Flow
There is no runtime flow. All page-table manipulation code consumes these masks and shifts when encoding or decoding descriptors and translation-control registers.

### State, Persistence, And Dependencies
No owned state; it defines the binary format of persistent in-memory page tables and CPU register fields. It depends on `asm/memory.h`, page size, VA bits, LPA2/52-bit PA options, and sysreg definitions.

### Integration Points
Foundational for kernel MM, KVM page tables, boot page tables, vmalloc/module mappings, and user page-table operations.

### Risks
Any incorrect bit definition can corrupt translation, permissions, dirty/access flags, or TLB behavior. 52-bit PA/VA and contiguous mappings are especially configuration-sensitive.

### Test Signals
Cross-build 4K/16K/64K, 48/52-bit VA/PA configs; run MM, KVM, dirty-bit, contiguous mapping, and permission fault tests; compare against architectural sysreg specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-hwdef.h -->
