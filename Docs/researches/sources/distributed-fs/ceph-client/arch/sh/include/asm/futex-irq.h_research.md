<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-irq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-irq.h

## Purpose
Implements the uniprocessor futex compare-exchange fallback by disabling local interrupts around user get/put.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_FUTEX_IRQ_H`. Register or hardware-address constants include `__ASM_SH_FUTEX_IRQ_H`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call. Atomicity is implemented by CPU-specific primitives or by interrupt exclusion, so the selected backend must match the SMP and CPU configuration.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 25 lines, 482 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/futex-irq.h -->
