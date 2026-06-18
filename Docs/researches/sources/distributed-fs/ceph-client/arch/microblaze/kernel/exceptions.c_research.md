# sources/distributed-fs/ceph-client/arch/microblaze/kernel/exceptions.c

Purpose: maps MicroBlaze hardware and software exceptions from low-level assembly into Linux signals or kernel oops handling.

Important APIs and state: `die()` prints registers under `die_lock` and terminates via `make_task_dead()`. `sw_exception()` handles debug `brki` traps. `_exception()` delivers a signal to user mode or oopses kernel mode. `full_exception()` decodes ESR exception types and chooses SIGILL, SIGBUS, or SIGFPE with architecture-specific si codes.

Control flow: assembly entry passes saved `pt_regs`, ESR/FSR/address context. User-mode faults become `force_sig_fault()`; kernel faults call `die()` except for FPU and privileged cases that still funnel through `_exception()`.

State and persistence: no persistent state beyond the spinlock. It mutates user signal state and may terminate tasks.

Dependencies and integration: called by `entry.S` and `hw_exception_handler.S`; relies on `kernel_mode()`/`user_mode()` and cache flushes for software breakpoints.

Risks and test signals: unexpected exceptions only log without forced termination in the default case. FPU code remaps FSR bits destructively into si_code. Test illegal instruction, divide-by-zero, bus error, FPU exception, user breakpoint, and kernel oops paths.
