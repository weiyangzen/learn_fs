# sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack.c

## Purpose
Implements common x86 stack tracing, opcode/register display, and oops/die lifecycle handling.

## Important APIs, Types, And Functions
`in_task_stack()` and `in_entry_stack()` classify stacks. `show_opcodes()`, `show_ip()`, `show_iret_regs()`, `show_stack()`, `show_stack_regs()`, and `show_regs()` print diagnostic state. `oops_begin()`, `oops_end()`, `__die()`, `die()`, and `die_addr()` coordinate oops reporting, locking, tainting, crash-kexec, and task termination.

## Control Flow
Trace printing starts an unwind, then walks valid stack regions returned by arch-specific `get_stack_info()`, printing reliable unwinder return addresses and unreliable text-address hints. Oops handling enters verbose console mode under `die_lock`, prints headers/registers/modules, notifies die hooks, optionally crash-kexecs, taints the kernel, restores IRQ state, prints an executive summary, and either returns, panics, or rewinds the stack to kill the task.

## State, Persistence, And Dependencies
State includes `die_counter`, `exec_summary_regs`, `die_lock`, owner/nesting counters, kernel taint, and console spinlock state. It depends on unwinder, stacktrace helpers, ftrace graph return fixups, KASAN/KMSAN suppression, notifier chains, kexec, and trap regs.

## Integration Points
Used by exception, WARN/oops, sysrq stack dumps, crash paths, and architecture-specific stack classifiers in `dumpstack_32.c` and `dumpstack_64.c`.

## Risks
Stack walking may run from NMI/oops contexts and must avoid faults, sanitizer false positives, and recursion. Oops lock handling intentionally trades strictness for avoiding deadlock. User opcode copying is restricted to current.

## Test Signals
Fault injection should print code bytes, registers, stack sections, reliable markers, module list, oops count, and correct panic/crash behavior according to policy.
