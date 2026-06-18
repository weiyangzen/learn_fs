# sources/distributed-fs/ceph-client/arch/nios2/kernel/syscall_table.c

Purpose: defines the Nios II syscall dispatch table from generated syscall table macros.

Important APIs/types/functions: macros: `__SYSCALL(nr, call)`, `__SYSCALL_WITH_COMPAT(nr, native, compat)`, `sys_mmap2`,
`sys_clone3`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/syscalls.h`, `linux/signal.h`, `linux/unistd.h`, `asm/syscalls.h`,
`asm/syscall_table_32.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
