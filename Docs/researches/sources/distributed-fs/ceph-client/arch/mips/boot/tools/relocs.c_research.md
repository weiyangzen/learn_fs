# sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs.c

Purpose: shared implementation for the host `relocs` tool that scans MIPS ELF relocation sections, filters relocations relevant to kernel relocation, optionally removes relocation sections, and emits relocation offsets as text or binary.

Important APIs and functions: `regex_init()` builds skip filters, `read_ehdr/read_shdrs/read_strtabs/read_symtabs/read_relocs()` parse ELF metadata, `walk_relocs()` iterates relocation records with symbol context, `add_reloc()` stores accepted offsets, `emit_relocs()` writes sorted relocation entries, `do_reloc_info()` prints diagnostic information, and `remove_relocs()` rewrites relocation section headers out of the image. Byte-order macros and `ElfW` indirection make the file reusable for 32- and 64-bit builds.

Control flow: wrapper files define ELF width/type macros and include this file. The main program opens an ELF, reads all required sections, walks relocation sections, filters by relocation type and symbol, then either prints information, writes relocation offsets, or strips relocation sections.

State and persistence: maintains in-memory section, symbol, string table, and relocation lists; may modify the input/output ELF when stripping relocation sections depending on invocation flags.

Dependencies and integration points: included by `relocs_32.c` and `relocs_64.c`, driven by `relocs_main.c`, and used in MIPS compressed/relocatable kernel build tooling.

Risks and test signals: architecture-specific relocation encodings are subtle, especially MIPS64 RELA packed fields and endian conversion. Test by comparing emitted relocation tables for known 32/64-bit kernels, running `--reloc-info`, and booting relocated compressed kernels.
