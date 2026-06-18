<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_32.h

## Purpose
This header defines the SPARC32 ELF ABI contract for executable loading, core dumps, hardware capabilities, and register sets.

## Important APIs, Types, and Functions
It defines SPARC relocation constants, `HWCAP_SPARC_*`, `ELF_NGREG`, register-set typedefs, `elf_check_arch`, `ELF_ARCH`, `ELF_CLASS`, `ELF_DATA`, `ELF_EXEC_PAGESIZE`, `ELF_ET_DYN_BASE`, `ELF_HWCAP`, and `ELF_PLATFORM`.

## Control Flow
The ELF loader checks binary architecture, configures process personality, maps PIE/interpreter regions, and emits auxv/core-dump data using these macros.

## State and Persistence Behavior
No kernel state is stored here; it defines persistent userspace ABI values.

## Dependencies and Integration Points
It integrates with binfmt_elf, ptrace/core dumps, signal/register layouts, and userspace dynamic loaders.

## Risks
Changing relocation or register constants breaks userspace ABI and core dump compatibility.

## Test Signals
Run SPARC32 ELF binaries, PIE/static/dynamic loads, core dumps, ptrace register inspection, and auxv checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/elf_32.h -->
