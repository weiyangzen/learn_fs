# sources/distributed-fs/ceph-client/scripts/recordmcount.h

Purpose: `recordmcount.h` is implementation code, not a conventional declaration header. `recordmcount.c` includes it twice, once for 32-bit ELF and once with `RECORD_MCOUNT_64`, to generate parallel `do32()` and `do64()` implementations for adding ftrace `__mcount_loc` metadata.

Important APIs, types, and functions: macro aliases map generic names such as `Elf_Ehdr`, `Elf_Shdr`, `Elf_Rel`, `append_func`, `sift_rel_mcount`, `nop_mcount`, `find_secsym_ndx`, `has_rel_mcount`, and `do_func` to 32-bit or 64-bit variants. `get_symindex()`, `get_shnum()`, `set_shnum()`, and `get_shstrndx()` handle extended ELF section numbering. `find_symtab()` locates symbol and extended-symbol-index tables. `append_func()` appends the new section-string table, rewritten section header table, `__mcount_loc`, and its relocation section. `get_mcountsym()`, `sift_rel_mcount()`, and `nop_mcount()` identify and transform mcount relocations.

Control flow: `do_func()` computes a conservative relocation-space bound, allocates mcount location and relocation arrays, scans all section headers, and distinguishes traceable executable text sections from ignored executable sections. Traceable sections require a non-weak local or global section symbol from `find_secsym_ndx()` so final link relocations remain valid. Ignored sections are optionally NOPed or warned. If any mcount locations were collected, `append_func()` writes all appended ELF structures and updates `e_shoff` and section count.

State and persistence: all persistent file mutation is done through callbacks and globals in `recordmcount.c`, especially `uwrite()`, endian conversion functions, `file_updated`, and architecture hooks. The header itself maintains per-specialization static hooks for fake mcount filtering and relocation info packing.

Dependencies and integration points: it depends on the global variables and helpers defined before inclusion in `recordmcount.c`, plus architecture overrides installed by `do_file()`. It integrates with the kernel linker's expectation that `__mcount_loc` points at relocatable call-site addresses and that ignored notrace sections do not leave active profiling calls.

Risks: macro-generated dual inclusion makes review and debugging harder because each static identifier expands differently. The code assumes valid, bounded ELF offsets after initial checks; malformed objects may still stress pointer arithmetic. The upper-bound allocation of `totrelsz` avoids dynamic growth but depends on correct section sizes. Extended section index logic is critical for large objects.

Test signals: compare 32-bit and 64-bit builds on supported architectures, inspect generated relocations with `readelf`, validate duplicate-section no-op behavior, and test objects with weak-only symbols, local section symbols, extended section indexes, REL and RELA relocations, and notrace text sections.
