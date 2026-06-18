# sources/distributed-fs/ceph-client/arch/csky/include/asm/uprobes.h

## Purpose

defines uprobes breakpoint and instruction slot constants

## Important APIs, Types, and Functions

Source read size: 33 lines, 669 bytes. Includes: `asm/probes.h`. Key macros/defines:
`__ASM_CSKY_UPROBES_H`, `MAX_UINSN_BYTES`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`,
`UPROBE_XOL_SLOT_BYTES`. Local structs: `arch_uprobe_task`, `arch_uprobe`, `arch_probe_insn`.

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
