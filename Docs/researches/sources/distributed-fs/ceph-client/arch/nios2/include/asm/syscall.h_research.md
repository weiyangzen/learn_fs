# sources/distributed-fs/ceph-client/arch/nios2/include/asm/syscall.h

Purpose: implements generic syscall tracing helpers for Nios II, including syscall number, arguments, return
value, rollback, and audit architecture values.

Important APIs/types/functions: functions: `Corporation`, `syscall_set_nr`, `syscall_rollback`, `syscall_get_error`,
`syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`,
`syscall_set_arguments`, `syscall_get_arch`; types: `pt_regs`; macros: `__ASM_NIOS2_SYSCALL_H__`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `uapi/linux/audit.h`, `linux/err.h`, `linux/sched.h`. Integration points
include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and
cache/TLB subsystems plus Nios II control-register assembly. This source is part of the Nios II
architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
