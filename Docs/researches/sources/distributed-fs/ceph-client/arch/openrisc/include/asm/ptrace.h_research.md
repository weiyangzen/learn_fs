# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/ptrace.h

Purpose: defines OpenRISC kernel register frames, ptrace offsets, user/kernel mode predicates, and register-
query helpers.

Important APIs/types/functions: functions: `instruction_pointer`, `instruction_pointer_set`, `kernel_stack_pointer`,
`regs_return_value`, `regs_get_register`; prototypes: `regs_query_register_offset`; types:
`pt_regs`; macros: `__ASM_OPENRISC_PTRACE_H`, `STACK_FRAME_OVERHEAD`, `MAX_REG_OFFSET`,
`user_mode(regs)`, `user_stack_pointer(regs)`, `profile_pc(regs)`, `PT_SR`, `PT_SP`, `PT_GPR2`,
`PT_GPR3`, `PT_GPR4`, `PT_GPR5`, and 28 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `asm/spr_defs.h`, `uapi/asm/ptrace.h`, `linux/compiler.h`. Integration points
include generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops,
futex, ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port
under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
