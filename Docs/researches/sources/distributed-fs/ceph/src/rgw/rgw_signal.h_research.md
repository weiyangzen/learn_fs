# sources/distributed-fs/ceph/src/rgw/rgw_signal.h

## Purpose
Declares the RGW signal helper interface implemented by `rgw_signal.cc`. It gives RGW startup and signal-registration code a small API for no-op handling, log reopening, shutdown notification, and socketpair lifecycle.

## Important APIs, types, and functions
The namespace `rgw::signal` declares `sig_handler_noop(int)`, `sighup_handler(int)`, `signal_shutdown()`, `wait_shutdown()`, `signal_fd_init()`, `signal_fd_finalize()`, and `handle_sigterm(int)`. `handle_sigterm(int)` is declared twice, which is harmless for matching declarations but indicates header cleanup is needed.

## Control flow
Consumers initialize the signal fd pair, install handlers, then use `wait_shutdown()` on the synchronous side and `signal_shutdown()`/`handle_sigterm()` on the signal side. SIGHUP is routed to `sighup_handler()` for log reopen rather than shutdown.

## State and persistence behavior
The header owns no state. It exposes functions that manipulate static state in the implementation file and external process/logging state.

## Dependencies and integration points
The header has no includes beyond `#pragma once`, keeping it lightweight for RGW main-process code. It integrates with Ceph's global signal handling setup and RGW frontend shutdown coordination.

## Risks and test signals
The duplicate `handle_sigterm()` declaration should be removed to reduce noise. Build coverage validates declaration/definition agreement. Runtime tests should include code that includes only this header and links against `rgw_signal.cc`, then verifies init, shutdown wakeup, finalize, SIGHUP, and SIGTERM handler behavior through the public API.
