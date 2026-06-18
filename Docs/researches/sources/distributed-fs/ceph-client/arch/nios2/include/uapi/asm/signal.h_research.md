# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/signal.h

Purpose: defines the Nios II user ABI surface for `signal.h`, exported to userspace through headers_install.

Important APIs/types/functions: macros: `_ASM_NIOS2_SIGNAL_H`, `SA_RESTORER`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `asm-generic/signal.h`. Integration points include generic Linux MM, irq,
signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
