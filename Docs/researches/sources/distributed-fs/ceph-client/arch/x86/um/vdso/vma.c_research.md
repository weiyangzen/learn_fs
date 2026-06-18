<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vma.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vma.c

## Purpose
`vma.c` allocates and maps the UML vDSO page into new 64-bit user address spaces.

## Important APIs, types, and functions
Important symbols are `um_vdso_addr`, static `um_vdso`, `init_vdso()`, and `arch_setup_additional_pages()`.

## Control flow
At subsys init it checks the embedded DSO fits in one page, chooses `task_size - PAGE_SIZE`, allocates a page, and copies the image. During exec it installs a special read/exec mapping at `um_vdso_addr`.

## State and persistence behavior
Persistent state is the allocated `um_vdso` page and exported `um_vdso_addr` used by ELF auxv and VMA naming.

## Dependencies and integration points
It depends on embedded `vdso_start`/`vdso_end`, mm special mappings, and ELF `ARCH_DLINFO`.

## Risks and edge cases
Failure to allocate panics. Mapping must hold `mmap_write_lock` and preserve special mapping semantics.

## Test signals
Signals are `/proc/pid/maps` showing `[vdso]`, auxv `AT_SYSINFO_EHDR`, and successful vDSO time calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vma.c -->
