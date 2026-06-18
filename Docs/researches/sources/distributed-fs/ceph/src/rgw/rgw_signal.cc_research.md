# sources/distributed-fs/ceph/src/rgw/rgw_signal.cc

## Purpose
Implements RGW signal helpers for log reopening and graceful shutdown wakeups. The file bridges asynchronous process signals to synchronous server shutdown code with a socketpair and exposes handlers used by RGW main process setup.

## Important APIs, types, and functions
`signal_fd` is a static two-element socketpair descriptor array. `sig_handler_noop()` intentionally does nothing. `sighup_handler()` reopens the RGW ops log if present and then asks the global Ceph context to reopen logs. `signal_fd_init()` creates the socketpair, and `signal_fd_finalize()` closes both descriptors.

`signal_shutdown()` writes an integer token to `signal_fd[0]`. `wait_shutdown()` blocks reading the token from `signal_fd[1]` using `safe_read_exact()`. `handle_sigterm()` logs signal handling, calls `signal_shutdown()` for signals other than `SIGUSR1`, and arms an `alarm()` using `rgw_exit_timeout_secs` as a safety net for orderly shutdown.

## Control flow
Startup code calls `signal_fd_init()` before installing handlers. When a terminating signal arrives, `handle_sigterm()` writes to the socketpair to wake code waiting in `wait_shutdown()` or blocked in frontend accept loops. If shutdown stalls, the alarm provides a later forced wakeup/termination path. SIGHUP follows a separate control flow that reopens log files without initiating shutdown.

## State and persistence behavior
The only local state is the socketpair descriptors. Persistent effects are external: log files are reopened, shutdown waiters are woken, and process alarm state is modified. The code uses global `g_ceph_context` and `rgw::AppMain::ops_log_file`.

## Dependencies and integration points
The file includes Ceph signal handling, safe IO, errno formatting, RGW main/log headers, and optional `sys/prctl.h`. It uses `derr`, `dout`, and the RGW logging subsystem. It integrates with process-level signal registration and frontend shutdown loops.

## Risks and test signals
`signal_shutdown()` writes to `signal_fd[0]` and `wait_shutdown()` reads from `signal_fd[1]`; tests should confirm this direction matches the created socketpair usage. Calling shutdown before successful `signal_fd_init()` would write to descriptor `0`, so initialization ordering matters. Signal handlers perform operations such as logging, reopening logs, and writing through wrappers, which should be reviewed against async-signal-safety expectations for the actual registration path. Tests should cover socketpair init/finalize, a shutdown write waking a waiter, error handling when descriptors are invalid, SIGHUP log reopen behavior with and without an ops log, and `SIGUSR1` avoiding `signal_shutdown()`.
