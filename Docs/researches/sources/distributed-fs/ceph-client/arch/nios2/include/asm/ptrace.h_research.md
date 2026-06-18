# sources/distributed-fs/ceph-client/arch/nios2/include/asm/ptrace.h

Purpose: defines the kernel pt_regs and switch_stack layouts consumed by exception entry, ptrace, signal
delivery, kgdb, and context switching.

Important APIs/types/functions: prototypes: `show_regs`; types: `pt_regs`, `switch_stack`; macros: `_ASM_NIOS2_PTRACE_H`,
`user_mode(regs)`, `instruction_pointer(regs)`, `profile_pc(regs)`, `user_stack_pointer(regs)`,
`current_pt_regs()`, `force_successful_syscall_return()`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `uapi/asm/ptrace.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
