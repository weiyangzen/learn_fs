<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/elf.h

## Purpose
Defines Xtensa ELF ABI constants, relocation IDs, register-set types, binary compatibility checks, process startup register initialization, FDPIC handling, and core-dump optional register layout.

## Important APIs, Types, And Functions
Key definitions include `EM_XTENSA_OLD`, `R_XTENSA_*`, `elf_greg_t`, `xtensa_gregset_t`, `ELF_NGREG`, `elf_check_arch`, `elf_check_fdpic`, `ELF_DATA`, `ELF_CLASS`, `ELF_ARCH`, `ELF_ET_DYN_BASE`, `ELF_PLAT_INIT`, `ELF_FDPIC_PLAT_INIT`, `elf_xtregs_t`, and `SET_PERSONALITY`.

## Control Flow
Exec-time macros validate architecture and initialize user registers. Core-dump code uses register-set typedefs and optional/coprocessor state aggregates. Endianness selects ELF data encoding.

## State And Persistence
State is user register initialization at exec and data emitted into ELF core files. No filesystem persistence except generated core dumps.

## Dependencies And Integration Points
Depends on ptrace registers, coprocessor save-area types, Linux ELF loader, FDPIC loader, and personality handling.

## Risks And Edge Cases
Register clearing must preserve stack pointer while avoiding stale state. FDPIC register conventions must match userspace ABI. Optional register core layout must match coprocessor definitions.

## Test Signals
Run ELF exec tests, dynamic loader tests, FDPIC if supported, core dumps with optional registers, ptrace register-set tests, and big/little endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/elf.h -->
