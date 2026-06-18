# sources/compression/xz/src/xz/signals.c

Purpose: implements process signal handling for the full `xz` command so long operations can be interrupted, incomplete output can be cleaned up, and the process can finally exit with the original terminating signal where the platform supports it.

Important APIs and functions: exports `user_abort`, `signals_init()`, `signals_block()`, `signals_unblock()`, and `signals_exit()` from `signals.h`. POSIX builds install `signal_handler()` for `SIGINT`, `SIGTERM`, optional `SIGHUP`, `SIGPIPE`, `SIGXCPU`, and `SIGXFSZ`; optional progress and `SIGTSTP` handlers are also folded into the blocked-signal mask. Native Windows uses `SetConsoleCtrlHandler()` instead of C signals.

Control flow: `signals_init()` builds `hooked_signals`, skips signals already ignored by the parent, installs handlers without `SA_RESTART`, and marks the subsystem initialized. The handler records `exit_signal`, sets `user_abort`, and notifies the user-abort pipe on non-DOS-like systems. `signals_block()` and `signals_unblock()` maintain a recursive block count around `mythread_sigmask()`. `signals_exit()` resets the original signal to default and re-raises it after cleanup.

State and persistence: process-local global state includes `user_abort`, `exit_signal`, `hooked_signals`, `signals_are_initialized`, and `signals_block_count`. No persistent files are written here, but this module directly affects cleanup decisions elsewhere by flipping `user_abort`.

Dependencies and integration: depends on `private.h`, message reporting, `io_write_to_user_abort_pipe()`, `mythread_sigmask()`, `set_exit_status()`, and optional `mytime_sigtstp_handler()`. It integrates with I/O loops that poll `user_abort` and with final process termination in `main()`.

Risks: async-signal-safety is central; the handler only updates atomics and writes to a pipe. The recursive signal block counter is not thread-safe by itself and assumes disciplined pairing. Platform branches change semantics: Windows cannot re-raise the original signal, while POSIX does. Calling block/unblock before initialization is intentionally a no-op.

Test signals: this file is not directly unit-tested in this subset. Coverage is indirect through command interruption behavior, I/O cleanup paths, and platform builds. Regression focus should include EINTR handling, nested block/unblock balance, ignored-parent-signal preservation, and exit status/signal propagation.
