## sources/distributed-fs/ceph-client/include/uapi/linux/elf.h

Purpose: This header defines Linux ELF base types, file/program/section/dynamic/symbol/relocation structures, magic values, note types, and GNU property constants for userspace and kernel consumers.

Important APIs and types: It declares 32-bit and 64-bit ELF scalar typedefs; program header types (`PT_LOAD`, `PT_DYNAMIC`, `PT_TLS`, GNU stack/relro/property, AArch64 MTE); file types; dynamic tags; symbol bindings/types; relocation macros and structs; symbol structs; ELF headers; program headers; section headers; identification indexes and magic; OS ABI values; note names and note type IDs for core dumps and ptrace regsets; GNU AArch64 BTI property; and version definition auxiliary structs.

Control flow and state: There are no executable functions, but these structures drive ELF loading, dynamic linking, relocation, core-dump generation, ptrace register set exchange, and debugger parsing. Extended program-header numbering uses `PN_XNUM` with section header zero to carry real counts when values exceed 16-bit fields.

Persistence and dependencies: Most structures are persistent on-disk ELF ABI. Note structures also define core dump and ptrace data exchange. The header depends on `<linux/types.h>` and `linux/elf-em.h`.

Integration points: It is central to `binfmt_elf`, module/toolchain parsers, crash dump readers, debuggers, loaders, architecture regset exports, livepatch section flags, and security features such as GNU property notes.

Risks and test signals: Risks include ABI layout changes, endian/class confusion, extended numbering bugs, note-size assumptions despite warnings, architecture note ID collisions, and parser trust in unvalidated offsets/sizes. Tests should parse 32/64-bit little/big-endian ELFs, extended header counts, PT_GNU_STACK/RELRO/property handling, relocation macros, core notes for supported architectures, malformed section/program tables, and compatibility with binutils/gdb expectations.
