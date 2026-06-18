<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/elf.h

## Purpose
Defines OpenRISC ELF ABI constants, relocation numbers, register-set types, and core-dump metadata shared with userspace.

## Important APIs, Types, And Functions
Defines `R_OR1K_*` relocation constants, old `R_OR32_*` aliases, `elf_greg_t`, `ELF_NGREG`, `elf_gregset_t`, `elf_fpregset_t`, `EM_OR32`, `ELF_ARCH`, `ELF_CLASS`, and `ELF_DATA`.

## Control Flow
No executable flow. Module relocation, binutils, loaders, core dumps, ptrace users, and debuggers consume these constants.

## State And Persistence
Defines ABI layouts for persisted ELF files and core dumps.

## Dependencies And Integration Points
Includes `asm/ptrace.h` for `struct user_regs_struct` and FPU state. `kernel/module.c` implements a subset of relocations from this list.

## Risks
Relocation numbering and ELF metadata are stable ABI. Mismatches with toolchain definitions break module loading, dynamic linking, debugging, and core analysis.

## Test Signals
OpenRISC toolchain relocation tests, module relocation tests, core dump register inspection, and ELF header validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/elf.h -->
