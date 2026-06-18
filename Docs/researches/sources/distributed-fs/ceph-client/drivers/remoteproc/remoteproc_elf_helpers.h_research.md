# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_elf_helpers.h

## Purpose
Provides inline helpers for class-neutral ELF32/ELF64 field access used by remoteproc firmware loading and coredump generation.

## Important APIs, Types, And Functions
`fw_elf_get_class()` reads `EI_CLASS` from firmware. `elf_hdr_init_ident()` initializes core ELF identity bytes. `ELF_GEN_FIELD_GET_SET()` generates getters and setters for selected ELF header, program-header, and section-header fields. `ELF_STRUCT_SIZE()` generates structure-size helpers. `elf_strtbl_add()` appends a name to the section string table and returns its offset.

## Control Flow
Callers determine an ELF class, then pass it to generated helpers. Each helper casts the buffer to the 32-bit or 64-bit ELF structure and reads or writes the requested field. Coredump section-mode uses `elf_strtbl_add()` while advancing a caller-owned string-table index.

## State And Persistence Behavior
No global state is kept. The helpers only mutate caller-provided ELF buffers and, for string-table addition, the optional index pointer.

## Dependencies And Integration Points
Included by `remoteproc_elf_loader.c` and `remoteproc_coredump.c`. Depends on kernel ELF definitions, `struct firmware`, and standard memory/string helpers available in kernel context.

## Risks
The helpers do not validate bounds, string-table capacity, endian compatibility, or class correctness. `elf_hdr_init_ident()` writes little-endian identity bytes, which is appropriate for current coredump generation but not a generic endian abstraction. `elf_strtbl_add()` uses `strcpy()` into caller-managed storage, so caller size calculations must be exact.

## Test Signals
Build both ELF32 and ELF64 paths, validate generated coredump headers/sections with ELF tooling, and feed 32-bit and 64-bit firmware through the loader to confirm offsets and sizes match kernel ELF structures.
