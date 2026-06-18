<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/ioremap.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/ioremap.c

### Purpose
`ioremap.c` implements early LoongArch ioremap/memremap helpers used before full virtual-memory services are available.

### Important APIs, Types, And Functions
Functions are `early_ioremap()`, `early_iounmap()`, `early_memremap_ro()`, and `early_memremap_prot()`.

### Control Flow
`early_ioremap()` returns a cached direct-map address via `TO_CACHE(phys_addr)`. `early_iounmap()` is a no-op. Read-only and protected early memremap variants defer to generic `early_memremap()` and ignore the requested protection value.

### State, Persistence, And Dependencies
There is no local mapping allocator or persistent state. Dependencies are LoongArch direct-map address conversion and generic early ioremap declarations.

### Integration Points
Early firmware/ACPI/device discovery code can use these helpers before normal `ioremap()` is ready. Later PCI ACPI code uses normal remap paths.

### Risks
Returning cached mappings for I/O regions can be wrong for device registers unless callers only use memory-like firmware data at this phase. Ignoring protection in `early_memremap_prot()` may surprise callers expecting uncached or read-only semantics.

### Test Signals
Boot with ACPI/firmware table parsing, early console/device discovery, and debug checks for early I/O accesses on LoongArch platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/ioremap.c -->
