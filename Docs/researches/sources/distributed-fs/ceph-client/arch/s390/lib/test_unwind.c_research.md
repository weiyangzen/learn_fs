# sources/distributed-fs/ceph-client/arch/s390/lib/test_unwind.c

## Purpose
Large KUnit suite validating s390 stack unwinding across normal calls, explicit stack pointer/regs inputs, alternate stacks, separate tasks, IRQ context, program-check/kprobe/ftrace paths, kretprobe paths, and rethook handling.

## Important APIs, Types, And Functions
`test_unwind()` runs `unwind_for_each_frame()`, formats a backtrace, requires `unwindme_func2` followed by `unwindme_func1`, rejects unwind errors and `arch_rethook_trampoline+0x0`, and can print backtraces via the `backtrace` module parameter. `struct unwindme` carries flags, task state, completion/wait queues, stack pointer, and result. Helpers synthesize regs (`fake_pt_regs()`), install kprobes/kretprobes/ftrace handlers, run timer IRQ tests, spawn kthreads, and form a call chain through `unwindme_func1..4`. `param_list` enumerates many flag combinations and feeds `KUNIT_ARRAY_PARAM`.

## Control Flow And State
Each parameterized test sets `current_test`, initializes flags, then chooses task, IRQ, or direct execution. Direct paths may call into kprobe, kretprobe, ftrace, or fake-regs unwinding. IRQ tests use a timer callback; task tests park a kthread after it reaches a known stack point. Global `unwindme` coordinates asynchronous callback contexts, and `current_test` supports logging.

## Dependencies And Integration
Depends on s390 unwind APIs, KUnit, kallsyms, kthreads, ftrace, timers, kprobes, wait queues, lowcore alternate stack, and module parameters. Built with sibling-call optimization disabled.

## Risks And Test Signals
Risks include fragile symbol-name prefix checks, async global-state races, configuration-dependent skips, ftrace/kprobe cleanup on failure, backtrace buffer truncation, and optimizer effects. The suite itself is a primary signal for unwinder reliability across important s390 contexts.
