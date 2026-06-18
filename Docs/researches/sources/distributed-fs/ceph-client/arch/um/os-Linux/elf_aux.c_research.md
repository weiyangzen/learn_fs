# sources/distributed-fs/ceph-client/arch/um/os-Linux/elf_aux.c

## Purpose
Scans the host-provided ELF auxiliary vector early in UML startup to record platform and hardware capability information.

## Important APIs, Types, and Functions
Defines `elf_aux_platform` and `elf_aux_hwcap`. `scan_elf_aux()` skips past the environment vector, iterates `Elf32_auxv_t` or `Elf64_auxv_t`, and records `AT_HWCAP` and `AT_PLATFORM`.

## Control Flow, State, and Persistence
The globals are initialized very early and then treated as immutable boot facts. No allocation or persistent files are involved.

## Dependencies and Integration Points
Called from `os-Linux/main.c` before `linux_main()`. Uses host ELF ABI types and is exposed through `internal.h`.

## Risks and Test Signals
Risks are ABI differences in auxv layout and stale platform pointers if environment memory assumptions change. Test 32-bit/64-bit UML startup and feature consumers that read `elf_aux_hwcap/platform`.
