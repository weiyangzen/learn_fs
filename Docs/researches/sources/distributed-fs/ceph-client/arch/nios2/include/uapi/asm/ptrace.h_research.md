# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/ptrace.h

Purpose: defines the Nios II user ABI surface for `ptrace.h`, exported to userspace through headers_install.

Important APIs/types/functions: types: `user_pt_regs`; macros: `_UAPI_ASM_NIOS2_PTRACE_H`, `PTR_R0`, `PTR_R1`, `PTR_R2`, `PTR_R3`,
`PTR_R4`, `PTR_R5`, `PTR_R6`, `PTR_R7`, `PTR_R8`, `PTR_R9`, `PTR_R10`, and 39 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `linux/types.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
