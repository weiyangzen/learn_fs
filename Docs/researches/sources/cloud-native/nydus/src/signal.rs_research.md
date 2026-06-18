# sources/cloud-native/nydus/src/signal.rs

## Purpose
`signal.rs` provides a tiny wrapper for registering Unix signal handlers through `nix`.

## Important APIs, Types, And Functions
`register_signal_handler` takes a `nix::sys::signal::Signal` and an extern "C" handler function pointer, builds a `SigAction` with empty flags and mask, and calls `sigaction`.

## Control Flow
Callers provide the signal and handler. The function constructs the action and installs it in an unsafe block. Registration failure panics via `unwrap`, based on the assumption that daemon binaries cannot operate correctly without signal handling.

## State And Persistence
It mutates process-global signal disposition. There is no file or durable persistence.

## Dependencies And Integration Points
It depends on `nix::sys::signal` and `libc` handler ABI. `lib.rs` re-exports it. `nydusd/main.rs` uses it to register SIGINT and SIGTERM handlers that notify `DAEMON_CONTROLLER`.

## Risks
The wrapper does not expose flags, masks, or error handling. Handlers run in async signal context, so the caller-provided function must be signal-safe or accept the risk. Panicking during registration aborts startup.

## Test Signals
There are no tests. Practical validation is daemon startup and graceful shutdown via SIGINT/SIGTERM.
