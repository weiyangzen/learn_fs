<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso.c

### Purpose
`vdso.c` maps the PA-RISC vDSO into new processes and initializes special mapping page lists for 32-bit and 64-bit vDSO images.

### Important APIs, Types, And Functions
Key items are `vdso32_start/end`, `vdso64_start/end`, `vdso_mremap()`, `vdso32_mapping`, `vdso64_mapping`, `arch_setup_additional_pages()`, `vdso_setup_pages()`, and `vdso_init()`.

### Control Flow
During exec, the code locks the mm, chooses 64-bit or compat vDSO image, randomizes the base near `mmap_base`, finds an unmapped area, installs a read/exec special mapping with may-write for debugger COW breakpoints, records `mm->context.vdso_base`, and unlocks. Init converts embedded image ranges into NULL-terminated `struct page **` arrays for special mappings.

### State, Persistence, And Dependencies
Persistent state includes per-mm `vdso_base` and static special mapping page arrays. Dependencies include ELF exec, mm locks, randomization, `get_unmapped_area()`, time namespaces includes, and wrapper-embedded VDSO images.

### Integration Points
Signal delivery uses VDSO symbol offsets relative to `vdso_base`; exec uses `arch_setup_additional_pages()`.

### Risks
Mapping failure cleanup currently calls `do_munmap()` for one page regardless of full vDSO length. Randomization is small. Incorrect image selection breaks compat signal and restart trampolines.

### Test Signals
Exec native and compat binaries, inspect `[vdso]` mapping permissions/base randomization, mremap vDSO, set debugger breakpoints, and deliver signals requiring VDSO trampolines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso.c -->
