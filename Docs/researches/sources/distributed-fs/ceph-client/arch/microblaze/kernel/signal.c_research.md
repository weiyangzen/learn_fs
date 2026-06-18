# sources/distributed-fs/ceph-client/arch/microblaze/kernel/signal.c

Purpose: implements MicroBlaze signal delivery, rt sigreturn, syscall restart, and user-mode resume work.

Important APIs and state: signal frame types `sigframe` and `rt_sigframe`; `sys_rt_sigreturn()`, `setup_rt_frame()`, `handle_restart()`, `do_notify_resume()`. Signal contexts save full `pt_regs` plus old mask; trampolines contain `__NR_rt_sigreturn` load and `brki r14, 0x8`.

Control flow: delivery selects the alt stack, writes `rt_sigframe`, emits user trampoline instructions, flushes trampoline cache lines by walking the user PTE, sets handler arguments in r5-r7, sets r15 to trampoline minus 8, and sets PC to handler. Return restores mask, altstack, registers, and syscall return value. Restart logic rewinds PC by 4 to re-execute the syscall trap.

State and persistence: mutates user stack, user signal mask, altstack state, and saved registers.

Dependencies and integration: called from entry return paths; depends on uaccess, page tables, cacheflush, syscall numbers, and MicroBlaze return-delay conventions.

Risks and test signals: cache flushing user trampoline must handle unmapped or migrated pages safely. Restart PC adjustment must match syscall trap size. Test signals on normal/alt stacks, SA_SIGINFO, rt_sigreturn tampering, interrupted syscalls, and write-back cache systems.
