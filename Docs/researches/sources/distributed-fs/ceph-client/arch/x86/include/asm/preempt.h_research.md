# sources/distributed-fs/ceph-client/arch/x86/include/asm/preempt.h

Purpose: implements x86 per-CPU preemption count handling, folding an inverted need-resched bit into `__preempt_count` so `preempt_enable()` can decrement and test for rescheduling efficiently.

Important APIs, types, and functions: declares per-CPU `__preempt_count`, defines `PREEMPT_NEED_RESCHED` and `PREEMPT_ENABLED`, and provides `preempt_count()`, `preempt_count_set()`, `init_task_preempt_count()`, `init_idle_preempt_count()`, `set_preempt_need_resched()`, `clear_preempt_need_resched()`, `test_preempt_need_resched()`, `__preempt_count_add()`, `__preempt_count_sub()`, `__preempt_count_dec_and_test()`, and `should_resched()`. Under preemption it declares schedule thunks and dynamic/static-call wrappers for `__preempt_schedule()` and `__preempt_schedule_notrace()`.

Control flow: preempt count reads mask off the inverted need-resched bit. Setting need-resched clears the MSB; clearing need-resched sets it. `__preempt_count_dec_and_test()` uses an x86 decrement-and-condition-code helper to detect zero. Dynamic preemption can call schedule thunks through static-call trampolines.

State and persistence: `__preempt_count` is per-CPU scheduler state. No external persistence exists.

Dependencies and integration points: depends on x86 per-CPU ops, RMW condition-code helpers, scheduler/preemption code, static calls, and dynamic preemption.

Risks: the inverted bit convention is subtle; treating raw `__preempt_count` as a plain count gives wrong results. Atomic cmpxchg in `preempt_count_set()` preserves need-resched across count writes. Schedule thunk calls must satisfy calling constraints.

Test signals: preemption selftests, voluntary/full/dynamic preemption modes, scheduler stress, interrupt/softirq nesting, idle task initialization, objtool validation, and tracing/notrace preemption paths.
