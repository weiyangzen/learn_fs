## sources/distributed-fs/ceph-client/arch/x86/entry/syscall_32.c

Purpose: 32-bit syscall dispatch and entry-state management for native i386 and IA32 emulation. It maps syscall numbers to generated `__ia32_*` handlers and implements C-side INT80, SYSENTER, and compat SYSCALL behavior.

Important APIs/functions: `ia32_sys_call()`, `syscall_32_enter()`, `do_syscall_32_irqs_on()`, `do_int80_emulation()`, FRED `int80_emulation`, `do_int80_syscall_32()`, `__do_fast_syscall_32()`, `do_fast_syscall_32()`, and `do_SYSENTER_32()`. State includes optional `sys_call_table[]` for tracing and `__ia32_enabled` controlled by `ia32_emulation=`.

Control flow: syscall numbers are converted to unsigned and guarded with `array_index_nospec()` before dispatch through generated `syscalls_32.h`. INT80 validates user origin, enters kernel context, optionally rejects external vector-0x80 injections, normalizes `orig_ax`, enables IRQs for syscall work, dispatches, and exits to user mode. Fast SYSENTER/SYSCALL fetches the sixth argument from the user stack/vDSO-stashed EBP, then validates whether a fast return is legal.

State/persistence: sets `TS_COMPAT`, updates `regs->orig_ax/ax/ip/sp/bp/flags`, uses `current->mm->context.vdso` and `vdso32_image.sym_int80_landing_pad`, and honors the boot-time IA32 enable flag.

Integration points: assembly stubs in `entry_64_compat.S`, FRED dispatch, generated syscall tables, seccomp/ptrace/syscall entry common code, APIC ISR checks, vDSO32, and KASLR stack offset randomization.

Risks: user-controlled stack reads for EBP can fault and must force IRET. External INT80 injection handling differs under FRED. Fast returns require exact landing-pad, CS/SS, and flag validation. Test signals include 32-bit glibc/vDSO syscall tests, ptrace syscall rewriting, seccomp, `ia32_emulation=false`, FRED INT80, APIC injection hardening, and signal restart through INT80.
