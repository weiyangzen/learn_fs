# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/elf.h

Purpose: Defines objtool ELF object model and APIs for reading, creating, mutating, hashing, and writing sections, symbols, and relocations.

Important APIs/types/functions: `elf_write_insn`, `elf_write`, `elf_close`, `iterate_global_symbol_by_demangled_name`, `find_symbol_hole_containing`, `has_multiple_files`, `elf_addr_size`, `elf_rela_size`, `is_undef_sym`, `is_null_sym`, `is_sec_sym`, `is_object_sym`.

Control flow: Clients open an ELF, iterate sections/symbols/relocs through cached lists and hash tables, create or update data/relocations, mark changed sections, then write and close the file.

State and persistence behavior: Owns process-local `struct elf` caches plus modified libelf data buffers; persistence occurs only through `elf_write()`.

Dependencies and integration points: Wraps libelf/GElf, Linux rbtree/list helpers, endianness utilities, checksum types, and architecture relocation helpers.

Risks: Relocation accessors must preserve 32/64-bit layout and byte order; section change flags and symbol aliases/twins/clones drive livepatch correctness.

Test signals: ELF mutation tests for 32/64-bit, endian-swapped objects, RELA creation, symbol lookup by range/name, and idempotent write/close.

Source coverage: researched from the complete local file (534 lines, 13872 bytes).
