# sources/distributed-fs/ceph-client/arch/csky/include/asm/kprobes.h

## Purpose

declares kprobe instruction slots, breakpoint opcodes, and arch hooks

## Important APIs, Types, and Functions

Source read size: 48 lines, 1158 bytes. Includes: `asm-generic/kprobes.h`, `linux/types.h`,
`linux/ptrace.h`, `linux/percpu.h`, `asm/probes.h`. Key macros/defines: `__ASM_CSKY_KPROBES_H`,
`__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot(p)`, `kretprobe_blacklist_size`.
Local structs: `prev_kprobe`, `kprobe`, `kprobe_step_ctx`, `kprobe_ctlblk`.

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
