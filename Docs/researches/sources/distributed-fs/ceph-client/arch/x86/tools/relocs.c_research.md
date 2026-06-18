<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs.c

## Purpose
`relocs.c` is the shared ELF parser and relocation classifier for x86 kernel and real-mode relocation streams.

## Important APIs, types, and functions
Major pieces include ELF type macros, global ELF/section state, symbol regex policies, `regex_init()`, `read_ehdr()`, `read_shdrs()`, `read_strtabs()`, `read_symtabs()`, `read_relocs()`, `walk_relocs()`, `do_reloc32()`, `do_reloc64()`, `do_reloc_real()`, `emit_relocs()`, and `process()`.

## Control flow
The processor validates ELF metadata, loads sections/string/symbol/relocation tables, optionally reports absolute symbols/relocs or relocation info, otherwise walks allocated relocation sections and emits sorted relocation offsets. Kernel mode ignores PC-relative relocations and rejects unsafe absolute relocations. Realmode mode separates 16-bit segment relocations from 32-bit linear relocations.

## State and persistence behavior
State is process-static ELF header/section arrays and relocation vectors `relocs16`, `relocs32`, and `relocs64`. Output persistence is the binary or textual relocation stream consumed at boot/build time.

## Dependencies and integration points
It depends on ELF32/ELF64 specializations, regex whitelists for linker-script symbols, endian conversion helpers, and Linux build-time conventions for `pa_` realmode symbols.

## Risks and edge cases
Whitelists are security- and boot-correctness sensitive: accepting a bad absolute relocation can make a relocated kernel fail, while rejecting valid linker-script symbols can break builds. Realmode validation must distinguish segment and linear references.

## Test signals
Signals are build failures on unsupported relocation types, `--abs-relocs` audits, `--reloc-info` diagnostics across linkers, and successful boot of relocated kernels/realmode trampolines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs.c -->
