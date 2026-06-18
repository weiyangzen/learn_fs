# sources/distributed-fs/ceph-client/arch/nios2/include/asm/thread_info.h

Purpose: defines Nios II thread_info layout, stack size, current-thread lookup, and thread flags used by
return-to-user and syscall paths.

Important APIs/types/functions: prototypes: `asm`; types: `thread_info`, `task_struct`, `pt_regs`; macros:
`_ASM_NIOS2_THREAD_INFO_H`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `INIT_THREAD_INFO(tsk)`,
`TIF_SYSCALL_TRACE`, `TIF_NOTIFY_RESUME`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_MEMDIE`,
`TIF_SECCOMP`, `TIF_SYSCALL_AUDIT`, `TIF_NOTIFY_SIGNAL`, and 12 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
