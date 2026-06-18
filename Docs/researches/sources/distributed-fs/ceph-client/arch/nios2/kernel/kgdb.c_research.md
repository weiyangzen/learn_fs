# sources/distributed-fs/ceph-client/arch/nios2/kernel/kgdb.c

Purpose: maps Nios II pt_regs into KGDB register packets, handles breakpoint exceptions, and wires
architecture KGDB operations into the generic debugger core.

Important APIs/types/functions: functions: `dbg_set_reg`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_set_pc`,
`kgdb_arch_handle_exception`, `kgdb_breakpoint_c`, `kgdb_arch_init`, `kgdb_arch_exit`; prototypes:
`kgdb_handle_exception`; types: `dbg_reg_def_t`, `pt_regs`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `linux/ptrace.h`, `linux/kgdb.h`, `linux/kdebug.h`, `linux/io.h`. Integration
points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and
cache/TLB subsystems plus Nios II control-register assembly. This source is part of the Nios II
architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
