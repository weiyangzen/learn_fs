# sources/distributed-fs/ceph-client/arch/csky/include/asm/elf.h

## Purpose

assembles C-SKY ELF core dump, loader, and HWCAP behavior from ABI-specific definitions

## Important APIs, Types, and Functions

Source read size: 90 lines, 2723 bytes. Includes: `asm/ptrace.h`, `abi/regdef.h`, `abi/elf.h`. Key
macros/defines: `__ASM_CSKY_ELF_H`, `ELF_ARCH`, `EM_CSKY_OLD`, `R_CSKY_NONE`, `R_CSKY_32`,
`R_CSKY_PCIMM8BY4`, `R_CSKY_PCIMM11BY2`, `R_CSKY_PCIMM4BY2`, `R_CSKY_PC32`,
`R_CSKY_PCRELJSR_IMM11BY2`, `R_CSKY_GNU_VTINHERIT`, `R_CSKY_GNU_VTENTRY`, `R_CSKY_RELATIVE`,
`R_CSKY_COPY`, `R_CSKY_GLOB_DAT`, `R_CSKY_JUMP_SLOT`, `R_CSKY_ADDR_HI16`, `R_CSKY_ADDR_LO16`; plus
13 more. Local structs: `task_struct`, `linux_binprm`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
