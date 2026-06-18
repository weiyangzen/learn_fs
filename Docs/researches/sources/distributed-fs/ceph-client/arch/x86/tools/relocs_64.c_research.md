<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs_64.c

## Purpose
`relocs_64.c` specializes the shared relocation extraction implementation for x86-64 ELF files.

## Important APIs, types, and functions
It defines `ELF_BITS=64`, `ELF_MACHINE=EM_X86_64`, `SHT_REL_TYPE=SHT_RELA`, `Elf_Rel=Elf64_Rela`, and ELF64 access macros before including `relocs.c`.

## Control flow
The generated `process_64()` validates 64-bit ELF input, walks RELA relocation sections, rejects realmode mode, and emits 64-bit/32-bit relocation streams for compressed kernel relocation.

## State and persistence behavior
State is per-translation-unit static state from `relocs.c`, including 64-bit relocation collection.

## Dependencies and integration points
It depends on ELF64 relocation constants and a binutils environment that emits expected x86-64 relocation types.

## Risks and edge cases
Offsets must fit in 32 bits for output; unsupported or absolute relocations intentionally fail the build.

## Test signals
Signals are successful relocation extraction from 64-bit `vmlinux` and warnings/errors for newly introduced absolute relocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_64.c -->
