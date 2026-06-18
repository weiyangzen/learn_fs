# sources/distributed-fs/ceph-client/tools/perf/util/genelf.h

## Purpose

`genelf.h` declares JIT ELF generation APIs and selects libelf type aliases/macros for the build architecture.

## Important APIs, Types, and Functions

It declares `jit_write_elf` and, when libdw support is enabled, `jit_add_debug_info`. It defines `GEN_ELF_ARCH`, `GEN_ELF_CLASS`, and `GEN_ELF_ENDIAN` based on compiler architecture/endian macros. It aliases libelf functions and types to 32-bit or 64-bit variants (`elf_newehdr`, `Elf_Ehdr`, `Elf_Sym`, etc.) and defines `GEN_ELF_TEXT_OFFSET` as the aligned location after ELF and program headers.

## Control Flow

Compilation selects one architecture branch or fails with `#error "unsupported architecture"`. The implementation then uses the normalized aliases so `genelf.c` can be mostly architecture-neutral.

## State and Persistence Behavior

The header stores no runtime state. It determines the class, machine type, endian encoding, and text offset of all generated JIT ELF files at compile time.

## Dependencies and Integration Points

It depends on libelf constants/types being visible, architecture compiler macros, and Linux `round_up`. It is included by `genelf.c` and `genelf_debug.c`.

## Risks and Edge Cases

Unsupported or newly added architectures fail the build until mapped. Cross-generation for a different target architecture is not supported; output follows the perf build host. `GEN_ELF_TEXT_OFFSET` depends on selected ELF type aliases.

## Test Signals

Build coverage across supported architectures, endian checks, generated ELF header inspection, and text-offset validation catch most regressions.
