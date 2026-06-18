<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/elf.h

## Purpose
This header defines m68k ELF ABI parameters for executable loading, core dumps, relocation constants, register sets, FDPIC initialization, and platform metadata.

## Important APIs, Types, And Functions
- `R_68K_*` constants define m68k relocation types.
- `elf_greg_t`, `elf_gregset_t`, and `elf_fpregset_t` define core/user register set types.
- `elf_check_arch()` accepts `EM_68K`.
- `ELF_CLASS`, `ELF_DATA`, `ELF_ARCH`, `ELF_EXEC_PAGESIZE`, and `ELF_ET_DYN_BASE` define loader ABI values.
- `ELF_PLAT_INIT()` clears `%a1`; `ELF_FDPIC_PLAT_INIT()` seeds `%d3`/`%d4`/`%d5`.
- `ELF_CORE_COPY_REGS()` copies saved pt_regs and switch_stack state into the ELF core register array.
- `ELF_HWCAP`, `ELF_PLATFORM`, and `ELF_FDPIC_CORE_EFLAGS` expose platform capability metadata.

## Control Flow
The ELF loader checks architecture, initializes process registers, selects load addresses/page size, and sets FDPIC registers where needed. Core-dump code calls `ELF_CORE_COPY_REGS()` to serialize task register state.

## State And Persistence Behavior
The header defines ABI state in process register initialization and core files. It does not store mutable kernel state. Core dump output persists register snapshots for debuggers.

## Dependencies And Integration Points
It depends on `ptrace.h`, `user.h`, `rdusp()`, `struct switch_stack`, and generic ELF binfmt code. It integrates with exec, dynamic linking, FDPIC, ptrace, and coredump paths.

## Risks And Edge Cases
Register array indexes are ABI-sensitive and comments acknowledge awkward mapping. `ELF_ET_DYN_BASE` differs for Sun3. FDPIC register initialization must match userspace ABI expectations.

## Test Signals
Run m68k ELF and FDPIC executable tests, dynamic loader tests, coredump/gdb register inspection, ptrace register validation, and Sun3 load-address tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/elf.h -->
