# sources/distributed-fs/ceph-client/tools/lib/bpf/elf.c

## Purpose
`elf.c` centralizes libbpf ELF symbol lookup helpers used for uprobe attachment and symbol-pattern resolution. It opens ELF objects, walks symbol tables, handles GNU symbol version metadata, and converts symbol virtual addresses into file offsets expected by kernel uprobes.

## APIs, Types, and Functions
Public helpers include `elf_open()`, `elf_close()`, `elf_find_func_offset()`, `elf_find_func_offset_from_file()`, `elf_resolve_syms_offsets()`, and `elf_resolve_pattern_offsets()`. The main internal iterator is `struct elf_sym_iter`, which owns libelf data pointers for symbols, version symbols, version definitions, string table indexes, current symbol index, and target `STT_*` type. `struct elf_sym` carries the current name, `GElf_Sym`, containing section header, version index, and hidden-version flag.

## Control Flow, State, and Persistence
`elf_open()` initializes libelf, opens the file with `O_CLOEXEC`, and creates an mmap-backed ELF handle; `elf_close()` releases both. `elf_sym_iter_new()` finds a requested symbol section, binds its string table and data, and for dynamic symbols optionally attaches `SHT_GNU_versym` and `SHT_GNU_verdef` data. `elf_sym_iter_next()` filters by symbol type, resolves names and containing sections, and records GNU version state. Single function lookup parses optional `@` or `@@` library versions, searches dynamic then regular symbol tables, handles weak versus non-weak duplicates, and translates `st_value` to file offset via section address and section file offset.

## Dependencies and Integration
The file depends on libelf/GElf, `open/close`, libbpf logging/error helpers, `glob_match()`, and standard `qsort`/`bsearch`. It integrates with libbpf uprobe and USDT attachment paths that need symbol-to-offset resolution, as well as APIs that resolve a list of named symbols or a glob pattern against ELF function symbols.

## Risks and Test Signals
Risks include versioned symbol matching differences between `.dynsym` and `.symtab`, ambiguity when multiple non-weak symbols match different offsets, stripped/static binaries that expose only one symbol table, shared-library offset interpretation, and duplicate offsets from searching both dynamic and normal symbols. `elf_resolve_syms_offsets()` sorts only requested names and currently performs exact-name bsearch without version parsing, while pattern lookup stops after the first symbol table with matches to avoid duplicates. Test signals include uprobes on stripped binaries, shared libraries with `foo@@VER`, static binaries without dynsym, weak/non-weak duplicate symbols, glob pattern resolution, malformed ELF files, and zero-valued symbols that should be rejected for shared objects.
