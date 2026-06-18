# sources/distributed-fs/ceph-client/arch/s390/kernel/rethook.h

Purpose: declares the s390 rethook trampoline callback for use by the assembly trampoline implementation.

Important APIs/types/functions: exposes `unsigned long arch_rethook_trampoline_callback(struct pt_regs *regs);` behind the `__S390_RETHOOK_H` include guard.

Control flow: no executable control flow exists in this header. It allows assembly/C boundary code to call the C callback implemented in `rethook.c`.

State and persistence: no state is defined.

Dependencies and integration points: depends on `struct pt_regs` being visible to users of the declaration. It integrates with `arch_rethook_trampoline` assembly and generic rethook handling.

Risks: prototype mismatch with the assembly trampoline would break calling convention expectations. The header is intentionally minimal, so additional declarations should be added only when needed by the trampoline path.

Test signals: compile/link of s390 rethook support, successful trampoline callback calls under kretprobe/fprobe tests, and no unresolved symbol or type conflicts.
