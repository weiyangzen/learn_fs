<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/Makefile

## Purpose
`um/vdso/Makefile` builds the 64-bit UML vDSO shared object and embeds it into the kernel.

## Important APIs, types, and functions
It defines vDSO objects `vdso-note.o` and `um_vdso.o`, kernel objects `vdso.o` and `vma.o`, generated targets `vdso.so`, `vdso.so.dbg`, `vdso.lds`, and special PIC/shared linker flags.

## Control flow
Kbuild compiles vDSO objects with user-style PIC flags and no profiling, links `vdso.so.dbg` with the linker script, strips it to `vdso.so`, and rebuilds `vdso.o` from the embedded binary.

## State and persistence behavior
State is build artifacts and the embedded vDSO image.

## Dependencies and integration points
It depends on 64-bit compiler/linker support, `vdso.lds.S`, objcopy, and UML build rules.

## Risks and edge cases
Wrong flags can introduce undefined symbols, stack protectors, profiling calls, or non-vDSO-safe relocations.

## Test signals
Signals are successful vDSO link, readelf checks on the shared object, and runtime `[vdso]` mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/Makefile -->
