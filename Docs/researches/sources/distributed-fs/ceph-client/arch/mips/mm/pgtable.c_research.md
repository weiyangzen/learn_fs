<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/pgtable.c

### Purpose
`pgtable.c` provides common MIPS PGD allocation for process address spaces. It allocates a fresh PGD, initializes user entries to invalid tables, and copies the kernel half from `init_mm`.

### Important APIs, Types, And Functions
`pgd_alloc()` calls architecture `__pgd_alloc()`, `pgd_init()`, `pgd_offset(&init_mm, 0UL)`, and `memcpy()` for kernel mappings. It is exported with `EXPORT_SYMBOL_GPL`.

### Control Flow
When a new `mm_struct` needs a PGD, allocation happens first. On success, the entire user portion is initialized with invalid page-table pointers, then entries from `USER_PTRS_PER_PGD` through `PTRS_PER_PGD` are copied from the boot kernel page directory.

### State, Persistence, And Dependencies
The allocated PGD persists as the root page table for a process until freed by the MM subsystem. It depends on the architecture-specific `pgd_init()` implementation in the 32-bit or 64-bit file and on the kernel mappings already present in `init_mm`.

### Integration Points
This function is used by generic Linux process address-space creation and by MIPS TLB refill paths that assume every process PGD has kernel mappings pre-populated.

### Risks
Copy length and `USER_PTRS_PER_PGD` must match the architecture split between user and kernel address ranges. Failure to copy kernel mappings correctly breaks kernel faults taken while running in a user `mm`.

### Test Signals
Signals include process creation under memory pressure, kernel faults while executing in non-init address spaces, and architecture builds covering both 32-bit and 64-bit `pgd_init()` implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/pgtable.c -->
