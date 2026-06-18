## sources/distributed-fs/ceph-client/arch/s390/kernel/unwind_bc.c

Purpose: Implements s390 backchain-based kernel unwinding for stacktrace, perf, livepatch reliability checks, and diagnostics.

Important APIs and functions: `unwind_get_return_address()`, `unwind_next_frame()`, and `__unwind_start()` are exported. Helpers validate stack bounds, move between stack types with `get_stack_info()`, identify final `pt_regs`, and recover return addresses.

Control flow: Start initializes the state from supplied kernel `pt_regs`, current frame address, or saved task kernel stack pointer; user-mode regs are rejected. Each next-frame step either consumes a pending `pt_regs` frame, follows a nonzero backchain, or interprets no-backchain as a possible `pt_regs` structure. It checks stack range transitions, 8-byte alignment, kernel text return addresses, final user/kernel-thread regs, and marks errors before stopping.

State and persistence: State is all in `struct unwind_state`: task, current stack info, mask, SP, IP, regs pointer, reliability flag, and error flag. No global state is modified.

Dependencies and integration: Depends on s390 stack-frame ABI, `get_stack_info()`, `task_pt_regs()`, kernel text address validation, scheduler task stacks, and stacktrace consumers in `stacktrace.c`.

Risks and test signals: Risks include interpreting corrupted backchains, false reliability on interrupt stacks, and KMSAN false positives from uninitialized frame reads. Test signals include reliable stacktrace validation, stack dumps across IRQ and task stacks, corrupted-stack detection, and unwinding stopped cleanly at user-mode `pt_regs`.
