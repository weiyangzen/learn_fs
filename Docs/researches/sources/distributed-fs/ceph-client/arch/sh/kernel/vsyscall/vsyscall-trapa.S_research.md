# sources/distributed-fs/ceph-client/arch/sh/kernel/vsyscall/vsyscall-trapa.S

Purpose: implements the primary SH vDSO syscall entry point and includes the signal-return trampoline code.

Important symbols and sections: `__kernel_vsyscall`, `.LSTART_vsyscall`, `.LEND_vsyscall`, `.eh_frame` CIE/FDE records, and included `vsyscall-sigreturn.S`.

Control flow: `__kernel_vsyscall` executes the SH `trapa #0x10` instruction and returns with `rts`; signal-return routines are appended through include. Unwind metadata describes the syscall trampoline for debuggers.

State and persistence: no mutable state; this code is linked into `vsyscall.so` and later copied into the kernel-owned vDSO page.

Dependencies and integration: consumed by `vsyscall.lds.S`, build rules, `vsyscall.c`, and user-space libc syscall/vDSO paths.

Risks: ABI breakage here affects every process using the vDSO syscall helper. Unwind range errors can impair stack traces even if syscall execution works.

Test signals: syscall smoke tests through vDSO, signal-return tests, and `readelf --debug-dump=frames` on the generated vDSO.
