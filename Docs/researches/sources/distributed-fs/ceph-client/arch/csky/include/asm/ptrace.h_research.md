# sources/distributed-fs/ceph-client/arch/csky/include/asm/ptrace.h

## Purpose

defines kernel pt_regs accessors and register helpers

## Important APIs, Types, and Functions

Source read size: 102 lines, 2594 bytes. Includes: `uapi/asm/ptrace.h`, `asm/traps.h`,
`linux/types.h`, `linux/compiler.h`. Functions: `instruction_pointer_set`, `in_syscall`,
`forget_syscall`, `regs_return_value`, `regs_set_return_value`, `kernel_stack_pointer`,
`frame_pointer`, `frame_pointer_set`, `regs_get_register`. Key macros/defines:
`__ASM_CSKY_PTRACE_H`, `PS_S`, `USR_BKPT`, `arch_has_single_step()`, `current_pt_regs()`,
`user_stack_pointer(regs)`, `user_mode(regs)`, `instruction_pointer(regs)`, `profile_pc(regs)`,
`trap_no(regs)`, `MAX_REG_OFFSET`.

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
