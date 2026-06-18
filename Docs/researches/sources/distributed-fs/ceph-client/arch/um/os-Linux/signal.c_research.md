# sources/distributed-fs/ceph-client/arch/um/os-Linux/signal.c

## Purpose
Implements host signal handling and signal masking for UML threads. It converts host signals into UML IRQs, traps, faults, child reaping, timers, and time-travel pending events.

## Important APIs, Types, and Functions
Global `sig_info[]` dispatches kernel-level signal handlers. `sig_handler_common()`, `sig_handler()`, and `timer_alarm_handler()` handle host signals. `set_handler()`, `set_sigstack()`, `timer_set_signal_handler()`, `deliver_alarm()`, `send_sigio_to_self()`, `change_sig()`, `block_signals()`, `unblock_signals()`, `um_set_signals()`, and time-travel hard block helpers form the API.

## Control Flow, State, and Persistence
Thread-local `signals_enabled`, `signals_pending`, and `signals_active` implement UML interrupt masking on top of host signals. With time-travel support, `signals_blocked` and atomic `signals_blocked_pending` prevent nested external-scheduler SIGIO handling until safe.

## Dependencies and Integration Points
Integrated with `trap.c`, `time.c`, SIGIO, SIGCHLD tracking, SMP IPI masking, and lockdep trace wrappers in `kernel/signal.c`. Handlers use alternate stacks and preserve errno.

## Risks and Test Signals
Risks are lost pending signals, reentrant timer handling, hard-block underflow, SIGIO/time-travel ACK ordering bugs, and wrong masks in seccomp mode. Test signal storms, timer interrupts while blocked, external time travel, seccomp child death, and SMP IPIs.
