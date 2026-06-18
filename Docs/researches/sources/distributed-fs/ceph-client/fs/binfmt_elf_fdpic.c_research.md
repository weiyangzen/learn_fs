# sources/distributed-fs/ceph-client/fs/binfmt_elf_fdpic.c

## Purpose
Implements the Linux binary-format handler for FDPIC ELF executables and interpreters, including NOMMU support and optional ELF core dump generation. It is derived from the regular ELF loader but emits FDPIC load maps so position-independent executables and dynamic linkers can discover the actual per-segment load addresses selected by the kernel.

## Important APIs, Types, And Functions
The file registers `elf_fdpic_format` with `register_binfmt()` at `core_initcall()` time and unregisters it at module exit. Its primary entry point is `load_elf_fdpic_binary(struct linux_binprm *bprm)`. Validation is split across `is_elf()`, architecture hooks such as `elf_check_arch()`, `elf_check_fdpic()`, and `elf_check_const_displacement()`, and program-header parsing in `elf_fdpic_fetch_phdrs()`.

Mapping is performed by `elf_fdpic_map_file()`, which builds an `elf_fdpic_loadmap` and delegates to `elf_fdpic_map_file_by_direct_mmap()` or, for NOMMU constant-displacement cases, `elf_fdpic_map_file_constdisp_on_uclinux()`. `create_elf_fdpic_tables()` builds the initial userspace stack, including `argv`, `envp`, `auxv`, platform strings, and executable/interpreter load maps. When `CONFIG_ELF_CORE` is enabled, `elf_fdpic_core_dump()` and helpers such as `fill_prstatus()`, `elf_dump_thread_status()`, and `elf_fdpic_dump_segments()` emit FDPIC-aware core files with load-map addresses in `elf_prstatus_fdpic`.

## Control Flow
`load_elf_fdpic_binary()` copies the ELF header from `bprm->buf`, rejects non-ELF, wrong-architecture, non-mmapable, or unsupported executable types, then reads program headers. It scans `PT_INTERP`; if present, it reads the interpreter path from the executable, opens it with `open_exec()`, applies `would_dump()` so unreadable executables affect dumpability, and reads the interpreter ELF header and program headers.

After deriving stack-executability policy from `PT_GNU_STACK`, it calls `begin_new_exec()` and switches personality flags, including `PER_LINUX_FDPIC` and `READ_IMPLIES_EXEC` when applicable. MMU builds lay out the address space with `elf_fdpic_arch_lay_out_mm()` and `setup_arg_pages()`; NOMMU builds allocate stack/brk memory explicitly. The executable and optional interpreter are mapped through `elf_fdpic_map_file()`, stack/auxiliary tables are created, architecture FDPIC register setup may run through `ELF_FDPIC_PLAT_INIT`, and `start_thread()` transfers control to the interpreter entry if one exists, otherwise to the executable entry.

`elf_fdpic_map_file()` counts `PT_LOAD` headers, allocates the load map, maps the segments, then resolves the runtime entry address, program-header address, and dynamic-section address by matching ELF virtual addresses against load-map entries. It also validates that a `PT_DYNAMIC` section has an integral `Elf_Dyn` array ending with a null tag. On MMU systems, adjacent load-map entries are coalesced when they have matching virtual and actual displacement.

The core dump path first gathers thread status notes, `PRPSINFO`, and `AUXV`, calculates ELF/program-header/note/data offsets, emits one `PT_NOTE` and one `PT_LOAD` header per dumpable VMA plus architecture extras, writes notes, dumps VMA ranges, and writes extended numbering metadata if the segment count exceeds `PN_XNUM`.

## State And Persistence
Runtime state is stored in the new process `mm_struct`: code/data/brk/stack ranges, `mm->saved_auxv`, and `mm->context.exec_fdpic_loadmap`/`interp_fdpic_loadmap`. The load maps are copied onto the userspace stack and referenced by both aux/register setup and core dumps. The loader changes process personality, binfmt ownership through `set_binfmt()`, interpreter file lifetime, and executable write-denial state. Persistent output only occurs when core dumping writes an ELF core file.

## Dependencies And Integration Points
The file sits in the generic `linux_binfmt` exec chain and depends on the VFS exec helpers, memory-management APIs (`vm_mmap()`, `setup_arg_pages()`, `clear_user()`), credentials for auxv UID/GID entries, coredump APIs, ELF architecture macros, and FDPIC ABI structures from `<linux/elf-fdpic.h>`. It integrates with interpreters via `PT_INTERP`, with security through `open_exec()`, `would_dump()`, and dumpability controls, and with debuggers through FDPIC-specific `NT_PRSTATUS` data in core files.

## Risks
Segment mapping is security-sensitive: wrong address arithmetic, BSS clearing, `MAP_FIXED` placement, or dynamic-section validation can corrupt the new image or expose stale memory. NOMMU paths rely on direct reads and anonymous allocations with different sharing assumptions from MMU Linux. The loader must free interpreter files, program headers, and load maps on all pre-commit error paths, while after `begin_new_exec()` failures occur after the old image is gone. Core dumps risk malformed offsets or missing FDPIC load-map data, which would break debuggers even when the crashing program ran correctly.

## Test Signals
Useful signals include successful execution of FDPIC binaries with and without `PT_INTERP`, NOMMU ET_DYN cases, `PT_GNU_STACK` executable/non-executable stack behavior, large or malformed program headers, invalid `PT_DYNAMIC` tables, BSS zeroing across partial pages, and interpreter dumpability transitions. Core dump tests should verify GDB can relocate FDPIC images using the emitted load-map addresses and that extended program-header numbering works for many VMAs.
