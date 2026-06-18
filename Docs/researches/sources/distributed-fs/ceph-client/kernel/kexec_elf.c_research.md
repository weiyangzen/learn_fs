# sources/distributed-fs/ceph-client/kernel/kexec_elf.c

## Purpose
`kexec_elf.c` parses ELF executable buffers for `kexec_file_load()` loaders. It validates the ELF header and program headers in an endian-aware way, exposes probe/build/free helpers for architecture loaders, and converts `PT_LOAD` program headers into kexec segments through `kexec_add_buffer()`.

## Important APIs, Types, And Functions
The public helpers are `kexec_build_elf_info()`, `kexec_free_elf_info()`, `kexec_elf_probe()`, and `kexec_elf_load()`. Internal conversion helpers `elf16_to_cpu()`, `elf32_to_cpu()`, and `elf64_to_cpu()` honor `EI_DATA`. `elf_read_ehdr()` canonicalizes `struct elfhdr`; `elf_read_phdrs()` allocates a normalized `elf_info->proghdrs` array; sanity helpers reject truncated tables, unsupported class/data, bad entry sizes, wrapping offsets, and wrapping physical addresses.

## Control Flow
`kexec_build_elf_info()` calls `elf_read_from_buffer()`, accepts `ET_EXEC` and `ET_DYN`, requires program headers, and rejects `PT_INTERP`. `kexec_elf_probe()` adds `elf_check_arch()`. `kexec_elf_load()` iterates `PT_LOAD` headers, chooses file bytes no larger than memory bytes, populates a `struct kexec_buf` with source pointer, file size, memory size, alignment, and preferred physical address, then delegates placement to `kexec_add_buffer()`.

## State And Persistence
The only allocated state is `elf_info->proghdrs`, freed by `kexec_free_elf_info()`. Source buffers remain owned by the caller. Loaded state is persisted by the caller's `struct kimage` after `kexec_add_buffer()` records new segments.

## Dependencies And Integration Points
This file integrates with generic ELF definitions, architecture `elf_check_arch()`, and `kexec_file.c` placement through `struct kexec_buf`. It is loader-neutral and does not call sysfs, sysctl, or architecture relocation itself.

## Risks And Edge Cases
Parsing untrusted kernel images makes integer wrapping and bounds checks critical. Endianness conversion must happen before size and offset use. A `PT_LOAD` with `p_filesz > p_memsz` is clipped to memory size; missing loadable segments would leave `lowest_load_addr` as `ULONG_MAX` unless handled by the caller. Rejection of `PT_INTERP` prevents ordinary dynamically linked executables from being treated as kernels.

## Test Signals
Tests should cover little- and big-endian ELF buffers, bad magic/class/data/version, truncated program/section tables, wrapping offsets, `PT_INTERP` rejection, `ET_EXEC`/`ET_DYN` acceptance, arch mismatch via `kexec_elf_probe()`, and correct `kexec_buf` values for multiple `PT_LOAD` segments.
