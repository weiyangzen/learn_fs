# sources/distributed-fs/ceph-client/arch/sh/kernel/stacktrace.c

Purpose: implements SH `save_stack_trace()` APIs using the architecture unwinder.

Important APIs and control flow: `save_stack_address()` stores only reliable addresses, honors `trace->skip`, and stops at `max_entries`. `save_stack_trace()` skips itself, unwinds the current task, and appends `ULONG_MAX` if space remains. `save_stack_trace_tsk()` handles current and other tasks, selects saved SP for blocked tasks, unwinds, and also appends `ULONG_MAX`.

State, dependencies, and risks: state is the caller-provided `struct stack_trace`. Dependencies include `unwind_stack()`, task stack access, pt_regs for current tasks, and reliable-frame tagging. Risks are incomplete traces when the unwinder is unavailable/unreliable and stale saved SP for running remote tasks. Test signals are stacktrace API users, lockdep/debug objects, and comparing traces from current versus sleeping tasks.
