# sources/distributed-fs/ceph-client/scripts/sorttable.c

Purpose: `sorttable.c` rewrites linked kernel ELF images so exception tables, and conditionally ORC unwind and mcount location tables, are sorted before boot/runtime use. It also clears `main_extable_sort_needed`.

Important APIs, types, and functions: it uses `elf-parse.h` abstraction for endian/class access. Core helpers include `compare_extable_32/64()`, `get_secindex()`, `do_sort()`, `do_file()`, `sort_relative_table()`, and `sort_relative_table_with_data()`. With `UNWINDER_ORC_ENABLED`, `sort_orctable()` sorts `.orc_unwind_ip` and `.orc_unwind` together using relative IP values and weak terminator ordering. With `MCOUNT_SORT_ENABLED`, `parse_symbols()`, `fill_relocs()`, `fill_addrs()`, `sort_mcount_loc()`, and `get_mcount_loc()` sort `__start_mcount_loc` to `__stop_mcount_loc` and optionally filter addresses against an nm symbol list.

Control flow: `main()` optionally parses `-s nm-file`, maps each vmlinux as `ET_EXEC` or `ET_DYN`, and calls `do_file()`. `do_file()` selects architecture-specific exception table entry layout and relative sort strategy, then `do_sort()` locates `__ex_table`, `.symtab`, `.strtab`, optional `.init.data`, and optional ORC sections, launches optional sort threads, sorts the exception table, finds and clears `main_extable_sort_needed`, then joins worker threads and propagates errors.

State and persistence: it mmaps the target through `elf_map()` and mutates table contents in place before `elf_unmap()`. Conditional global state stores ORC pointers, mcount function lists, relocation mode, and error strings.

Dependencies and integration points: invoked late in the kernel link/build process. It depends on symbol names, section names, architecture relocation conventions, pthreads, and optional generated ORC/mcount build defines.

Risks: corrupting sort order or relative encoding breaks exception handling, unwinding, or ftrace. Threaded optional sorts can overwrite `rc` in join paths. Architecture-specific entry sizes and relative encodings must match runtime lookup code. Missing symbols/sections are fatal for the expected configuration.

Test signals: boot tests, exception table selftests, objtool/ORC validation, ftrace tests, and `readelf`/custom checks showing sorted tables and cleared `main_extable_sort_needed`. Exercise all supported architectures and both relocation-backed and direct-address mcount cases.
