# sources/distributed-fs/ceph-client/tools/testing/selftests/signal/mangle_uc_sigmask.c

## Purpose
Tests signal mask semantics around delivered versus blocked signals and verifies that editing `ucontext_t.uc_sigmask` inside a handler updates the thread's blocked signal mask after handler return.

## Important APIs, types, and functions
Uses `sigaction()`, `raise()`, `sigismember()`, `sigaddset()`, `sigprocmask()`, and kselftest output helpers. Handlers are `handler_usr()`, `handler_segv()`, and `handler_verify_ucontext()`.

## Control flow
`main()` installs a `SIGUSR1` handler that blocks `SIGSEGV`, installs a `SIGSEGV` handler, raises `SIGUSR1`, and checks seven planned results. `handler_usr()` raises `SIGSEGV` and nested `SIGUSR1` signals while proving they are blocked until handler return, checks the interrupted-context mask is initially empty for those signals, then adds `SIGUSR2` to `uc_sigmask`. Later `handler_verify_ucontext()` confirms `SIGUSR2` is blocked in the saved context and cannot be delivered. `sigprocmask()` finally confirms `SIGUSR2` is in the live blocked set.

## State and persistence
Global `cnt` tracks recursive `SIGUSR1` delivery. Signal masks are process/thread state modified by kernel signal return from the mangled ucontext.

## Dependencies and integration points
Depends on POSIX signals, `ucontext_t`, and `kselftest.h`.

## Risks
Standard signals are not queued, which is intentionally tested and can be confusing when interpreting recursion count. Incorrect handler flags or masks can terminate the process.

## Test signals
Seven kselftest results cover SIGSEGV delivery, SIGUSR1 recursion count, ucontext mask contents, `SIGUSR2` blocking, and final blocked-mask verification.
