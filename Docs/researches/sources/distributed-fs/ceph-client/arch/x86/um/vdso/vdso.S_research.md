<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.S

## Purpose
`vdso.S` embeds the built UML vDSO shared object into kernel init data.

## Important APIs, types, and functions
It exports `vdso_start` and `vdso_end` around an `.incbin` of `arch/x86/um/vdso/vdso.so`.

## Control flow
The kernel link includes the stripped vDSO bytes; `vma.c` copies them into a page during init.

## State and persistence behavior
State is embedded init data only until copied to `um_vdso`.

## Dependencies and integration points
It depends on `vdso.so` being built first and linkage macros for init data.

## Risks and edge cases
Stale or oversized embedded bytes break vDSO mapping.

## Test signals
Signals are successful link and `vma.c` size check under one page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.S -->
