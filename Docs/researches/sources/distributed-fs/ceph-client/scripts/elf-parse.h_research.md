# sources/distributed-fs/ceph-client/scripts/elf-parse.h

Purpose: Provides endian- and class-neutral ELF accessor types and inline functions backed by the global `elf_parser` dispatch table.

Important APIs/types: Defines union wrappers `Elf_Ehdr`, `Elf_Shdr`, `Elf_Sym`, and `Elf_Rela`; declares `struct elf_funcs` function pointers; exports `elf_map()`, `elf_unmap()`, `elf_map_machine()`, and `elf_map_long_size()`. Inline accessors cover ELF header section fields, section header fields, symbol fields, relocation fields and writes, and endian read/write helpers.

Control flow: After `elf_map()` initializes `elf_parser`, callers use generic helpers such as `ehdr_shoff()`, `shdr_size()`, `sym_value()`, and `rela_write_addend()` without branching on class or endian.

State/persistence: All inline generic accessors depend on process-global `elf_parser`; using them before successful `elf_map()` or after mapping a second file with different attributes is unsafe.

Dependencies/integration: Includes `<elf.h>` and kernel tools byte-shift helpers. Integrated with `elf-parse.c` and scripts manipulating ELF relocation/symbol data.

Risks: The header defines `SHDR_WORD` twice identically, which is harmless but brittle. Several accessors cast relocation field addresses to unaligned integer pointers and rely on byte-shift helpers. `compare_extable` is in the dispatch struct but not initialized in this file.

Test signals: Compile users with both 32/64-bit ELF files, verify all accessors match readelf output, and test relocation addend writes on endian variants.
