# sources/distributed-fs/ceph-client/tools/objtool/elf.c

Purpose: objtool ELF access and mutation layer. It reads sections, symbols, relocations, builds lookup indexes, creates new symbols/sections/relocations, patches instruction bytes, writes changed ELF files, and supports temporary ELF creation.

Important APIs/types/functions: lookup APIs include `find_section_by_name()`, `find_symbol_by_offset()`, `find_func_by_offset()`, `find_symbol_containing()`, `find_symbol_by_name()`, and `find_reloc_by_dest_range()`. Readers include `read_sections()`, `read_symbols()`, `mark_group_syms()`, and `read_relocs()`. Mutation APIs include `elf_create_symbol()`, `elf_create_section()`, `elf_create_rela_section()`, `elf_create_reloc()`, `elf_create_section_pair()`, `elf_write_insn()`, `elf_write()`, and `elf_close()`.

Control flow: `elf_open_read()` initializes libelf, opens the file in the requested mode, reads headers, sections, symbols, group links, and relocations. Hash tables and interval trees accelerate lookups. Symbol ingestion demangles local suffixes, tracks aliases, cold subfunctions, prefix symbols, KLP symbols, and section symbols. Relocation creation manages libelf data buffers and internal relocation arrays.

State and persistence behavior: maintains in-memory `struct elf`, section lists, symbol lists, hash tables, symbol trees, relocation arrays, changed flags, and optional temp-file names. Persistent writes happen through `elf_write()` and `elf_close()` rename of temp files. `elf_write_insn()` directly modifies section data buffers before writeback.

Dependencies and integration points: used by nearly every objtool pass. It wraps libelf/GELF, Linux interval trees/hash helpers, architecture relocation aliases from `arch/elf.h`, and warning infrastructure.

Risks: symbol aliasing and cold-function parent/child adjustment are subtle. Libelf over-allocation requires manual truncation. Relocation array reallocation updates symbol-linked relocation lists and hash nodes, which is error-prone. Many allocations are intentionally leaked because objtool exits after one run.

Test signals: tests should cover empty objects, missing `.symtab`, extended section indexes, local/global symbol insertion, section-symbol relocation creation, duplicate reloc detection, changed section writeback, temp-file rename, cold function handling, and generated metadata sections.
