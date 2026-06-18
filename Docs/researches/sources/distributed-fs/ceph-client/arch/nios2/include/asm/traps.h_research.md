# sources/distributed-fs/ceph-client/arch/nios2/include/asm/traps.h

Purpose: declares the Nios II trap exception helper and syscall trap ID used by assembly entry and C trap
code.

Important APIs/types/functions: prototypes: `Copyright`; macros: `_ASM_NIOS2_TRAPS_H`, `TRAP_ID_SYSCALL`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
