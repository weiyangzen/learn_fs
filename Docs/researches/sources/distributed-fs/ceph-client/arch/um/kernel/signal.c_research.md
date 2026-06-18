# sources/distributed-fs/ceph-client/arch/um/kernel/signal.c

## Purpose
Implements UML signal delivery and signal-related IRQ tracing. It builds user signal frames, handles syscall restart rules, and keeps lockdep IRQ trace state aligned with UML signal blocking.

## Important APIs, Types, and Functions
`block_signals_trace()`, `unblock_signals_trace()`, `um_trace_signals_on()`, and `um_trace_signals_off()` wrap host signal masking with hardirq tracing. `handle_signal()` prepares signal frames using `setup_signal_stack_si()` or compat `setup_signal_stack_sc()`. `do_signal()` loops over `get_signal()`, handles syscall restart return codes, and restores saved masks when no signal is delivered.

## Control Flow, State, and Persistence
State is per-thread signal masks, ptrace single-step state, saved sigmask, and pt_regs syscall fields. On signal delivery it may rewrite syscall return/original-number fields to restart or convert interrupted syscalls to `-EINTR`. No persistent storage is used.

## Dependencies and Integration Points
Integrates generic signal core, UML frame setup, ptrace flags, syscall register macros, and host signal block/unblock functions from `os-Linux/signal.c`. It is reached from trap/fatal paths and the SKAS userspace loop.

## Risks and Test Signals
Risks include wrong syscall restart semantics, bad alternate-stack selection, and mismatched hardirq trace state. Test POSIX signal handlers, `SA_RESTART`, ptraced single-step signal delivery, altstack, and lockdep IRQ tracing under signal-heavy workloads.
