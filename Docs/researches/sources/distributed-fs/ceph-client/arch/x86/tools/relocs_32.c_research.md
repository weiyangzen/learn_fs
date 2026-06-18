<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs_32.c

## Purpose
`relocs_32.c` specializes the shared relocation extraction implementation for 32-bit i386 ELF files.

## Important APIs, types, and functions
It defines `ELF_BITS=32`, `ELF_MACHINE=EM_386`, `SHT_REL_TYPE=SHT_REL`, `Elf_Rel=ElfW(Rel)`, and ELF32 access macros before including `relocs.c`.

## Control flow
Compilation produces the 32-bit `process_32()` function. The common code then validates ELF headers, walks REL relocation sections, and emits kernel or realmode relocation offsets.

## State and persistence behavior
State is the static parser state instantiated from `relocs.c` for this translation unit.

## Dependencies and integration points
It depends on `relocs.h` and the common implementation honoring the macros defined here.

## Risks and edge cases
Wrong macro specialization would decode REL entries as RELA or accept the wrong machine type, corrupting relocation streams.

## Test signals
Signals are `relocs` processing of 32-bit vmlinux/realmode ELF and failure on unsupported relocation types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_32.c -->
