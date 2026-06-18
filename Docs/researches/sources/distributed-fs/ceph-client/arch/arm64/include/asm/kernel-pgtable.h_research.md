# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kernel-pgtable.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kernel-pgtable.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kernel-pgtable.h

### Purpose
`kernel-pgtable.h` calculates the early ARM64 kernel and identity-map page table footprint. It is boot-time compile glue used before the full MM subsystem is available, not Ceph client logic directly.

### Important APIs, Types, And Functions
Key exported constants/macros include `SWAPPER_BLOCK_SHIFT`, `SWAPPER_SKIP_LEVEL`, `SWAPPER_PGTABLE_LEVELS`, `IDMAP_VA_BITS`, `IDMAP_LEVELS`, `IDMAP_ROOT_LEVEL`, `SPAN_NR_ENTRIES`, `EARLY_ENTRIES`, `EARLY_LEVEL`, `EARLY_PAGES`, `INIT_DIR_SIZE`, `INIT_IDMAP_DIR_SIZE`, and FDT/idmap extra-page counts. It depends on `_end`, `kimage_limit`, `KIMAGE_VADDR`, `MAX_FDT_SIZE`, `CONFIG_PGTABLE_LEVELS`, `CONFIG_ARM64_4K_PAGES`, `CONFIG_RELOCATABLE`, and `CONFIG_UNMAP_KERNEL_AT_EL0`.

### Control Flow
There is no runtime control flow. The preprocessor selects page-table levels and sizes, then early assembly/C boot code consumes the constants when allocating initial swapper and idmap page tables.

### State, Persistence, And Dependencies
The header has no persistent state; it describes memory reservations for transient early page tables. It includes `asm/boot.h`, `asm/pgtable-hwdef.h`, and `asm/sparsemem.h`.

### Integration Points
It integrates with ARM64 head/boot page-table construction and the kernel image layout. Ceph is affected indirectly because all later filesystem, networking, and page-cache code depends on these mappings being correct.

### Risks
Wrong sizing causes early boot memory overwrite, missing idmap/FDT coverage, or page-table allocation underrun. Configuration-specific branches create risk around 4K pages, relocation, KASLR, and KPTI.

### Test Signals
Cross-build ARM64 page-size and VA-level combinations; boot with relocation/KASLR/KPTI enabled; validate early page table allocation bounds and boot-time FDT access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kernel-pgtable.h -->
