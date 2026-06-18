<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/futex.h

## Purpose
Selects the SH futex atomic backend and implements generic futex compare-exchange and in-user atomic operations over `u32` user words.

## Important APIs, Types, And Functions
Includes `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`, `asm/futex-irq.h`, `asm/futex-cas.h`, `asm/futex-llsc.h`. Key macros/constants include `__ASM_SH_FUTEX_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`, `asm/futex-irq.h`, `asm/futex-cas.h`, `asm/futex-llsc.h`. Kconfig-sensitive paths mention `CONFIG_SMP`, `CONFIG_CPU_J2`, `CONFIG_CPU_SH4A`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 72 lines, 1381 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex.h -->
