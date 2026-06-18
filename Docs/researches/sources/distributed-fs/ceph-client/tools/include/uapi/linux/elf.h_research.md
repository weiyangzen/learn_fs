# sources/distributed-fs/ceph-client/tools/include/uapi/linux/elf.h

Purpose: exposes Linux ELF base types, constants, and structures for 32-bit and 64-bit ELF parsing. It covers executable/shared-object/core-file metadata used by loaders, debuggers, coredump readers, and kernel/userspace tooling.

Important APIs/types: defines `Elf32_*` and `Elf64_*` scalar types; program, file, dynamic, symbol, relocation, section, note, and auxiliary-vector constants; macros such as `ELF_ST_BIND`, `ELF_ST_TYPE`, `ELF32_R_SYM`, `ELF32_R_TYPE`, `ELF64_R_SYM`, and `ELF64_R_TYPE`; structures including `Elf32/64_Dyn`, `Rel`, `Rela`, `Sym`, `Ehdr`, `Phdr`, `Shdr`, `Nhdr`, `Move`, `Lib`, and symbol version records.

Control flow, state, and persistence: the file defines serialized ELF layout. Readers validate `e_ident`, then traverse headers, sections, program headers, dynamic entries, symbol tables, relocation tables, notes, and version tables. Persistent state is the ELF file or core image.

Dependencies and integration points: depends on `<linux/types.h>` and `<linux/elf-em.h>`. It integrates Linux binfmt loaders, core dumps, perf/debug tools, dynamic linkers, crash analyzers, and architecture-specific ELF constants.

Risks and test signals: risks include endian/word-size confusion, extended numbering (`PN_XNUM`) mishandling, malformed offsets/sizes, GNU/processor-specific constant interpretation, and ABI incompatibility if structures change. Tests should parse 32/64-bit relocatable, executable, shared, and core ELF files; validate symbol and relocation macros; and fuzz malformed header/section length combinations.
