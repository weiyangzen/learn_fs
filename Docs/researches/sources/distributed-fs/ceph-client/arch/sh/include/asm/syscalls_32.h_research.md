<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls_32.h

## Purpose
Declares SH syscall entry, tracing, and wrapper interfaces used by low-level entry code and generic syscall tracing.

## Important APIs, Types, And Functions
Includes `linux/compiler.h`, `linux/linkage.h`, `linux/types.h`. Key macros/constants include `__ASM_SH_SYSCALLS_32_H`. Structures include `pt_regs`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/compiler.h`, `linux/linkage.h`, `linux/types.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 27 lines, 979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/syscalls_32.h -->
