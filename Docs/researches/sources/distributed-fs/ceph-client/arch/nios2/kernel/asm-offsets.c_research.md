# sources/distributed-fs/ceph-client/arch/nios2/kernel/asm-offsets.c

Purpose: emits structure offsets and constants consumed by Nios II assembly for pt_regs, switch_stack,
thread_info, task_struct, and thread_struct fields.

Important APIs/types/functions: functions: `Copyright`; prototypes: `OFFSET`; macros: `COMPILE_OFFSETS`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/stddef.h`, `linux/sched.h`, `linux/kernel_stat.h`, `linux/ptrace.h`,
`linux/hardirq.h`, `linux/thread_info.h`, `linux/kbuild.h`. Integration points include generic Linux
MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus
Nios II control-register assembly. This source is part of the Nios II architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
