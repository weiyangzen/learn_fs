# sources/distributed-fs/ceph-client/scripts/elf-parse.c

Purpose: Maps an ELF file read/write and initializes a global endian/class dispatch table for generic ELF header, section, symbol, and relocation accessors.

Important APIs/functions: `elf_map()` maps and validates a file, initializes `elf_parser`, and returns the mapping. `elf_unmap()` unmaps it. `elf_map_machine()` returns `e_machine`. `elf_map_long_size()` returns 4 or 8 from ELF class. Internal `map_file()` uses `open`, `fstat`, and shared writable `mmap`; `elf_parse()` validates magic/version/type and assigns accessor callbacks.

Control flow: `elf_map()` calls `map_file()`, then `elf_parse()`. `elf_parse()` first sets endian read/write functions from `EI_DATA`, validates ELF magic/current version, verifies allowed type bitmask, then selects ELF32 or ELF64 field accessor functions and checks header and section header sizes.

State/persistence: Global `struct elf_funcs elf_parser` is overwritten for each mapped file. Mappings are `MAP_SHARED` and writable, so relocation writes through accessors can persist to the file.

Dependencies/integration: Paired with `elf-parse.h`; used by kernel scripts that need endian/class-neutral ELF access. Depends on POSIX mmap/stat/open and `<elf.h>`.

Risks: Not reentrant for multiple simultaneous ELF files with different class/endian because the parser dispatch table is global. `map_file()` returns `MAP_FAILED` rather than `NULL` if mmap fails after printing, which callers treat as non-null unless parsing fails; this is a notable edge risk. Minimal bounds checking trusts header offsets and sizes after initial validation.

Test signals: Map valid/invalid ELF32 and ELF64, little and big endian, disallowed type masks, non-regular files, corrupt header sizes, and mmap failure paths.
