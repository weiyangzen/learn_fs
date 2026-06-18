<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-layout.lds.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-layout.lds.S

## Purpose
`vdso-layout.lds.S` defines the shared layout for the UML x86-64 vDSO ELF image.

## Important APIs, types, and functions
It lays out hash/dynamic/string/symbol/version/note/eh_frame/rodata/data/alt/text sections and declares PHDRs for one read-execute load segment plus dynamic, note, and GNU EH frame headers.

## Control flow
The linker places the DSO at `VDSO_PRELINK + SIZEOF_HEADERS`, keeps code aligned away from data, and marks explicit program headers so the vDSO has the expected read-only executable shape.

## State and persistence behavior
State is linker-script layout only.

## Dependencies and integration points
It depends on `VDSO_PRELINK` from `vdso.lds.S` and linker support for the specified PHDR types.

## Risks and edge cases
Layout mistakes can break dynamic symbol lookup, unwinding, build-id/note discovery, or runtime mapping permissions.

## Test signals
Signals are readelf layout checks and successful userland vDSO symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-layout.lds.S -->
