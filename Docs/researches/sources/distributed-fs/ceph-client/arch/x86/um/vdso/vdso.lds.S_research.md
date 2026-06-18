<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.lds.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.lds.S

## Purpose
`vdso.lds.S` chooses the UML x86-64 vDSO prelink address and exported symbol version set.

## Important APIs, types, and functions
It defines `VDSO_PRELINK`, includes `vdso-layout.lds.S`, exports `clock_gettime`, `__vdso_clock_gettime`, `gettimeofday`, `__vdso_gettimeofday`, `time`, and `__vdso_time` under `LINUX_2.6`, and defines `VDSO64_PRELINK`.

## Control flow
The linker uses this as both layout and version script when building `vdso.so.dbg`.

## State and persistence behavior
State is build-time symbol visibility/versioning.

## Dependencies and integration points
It depends on the symbols implemented by `um_vdso.c`.

## Risks and edge cases
Version-script omissions make dynamic linker lookups fail; wrong prelink constants can desynchronize kernel macros and DSO layout.

## Test signals
Signals are `readelf --dyn-syms --version-info` checks and runtime auxv/vDSO calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.lds.S -->
