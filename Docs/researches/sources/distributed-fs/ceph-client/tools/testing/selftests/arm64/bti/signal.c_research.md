# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/signal.c

Purpose: minimal freestanding signal API wrappers for the BTI tests.

Important APIs/types/functions: `sigemptyset()`, `sigaddset()`, `sigaction()`, and `sigprocmask()` implemented using local signal structures and raw syscalls.

Control flow: set manipulation functions update bitsets; wrappers call `__NR_rt_sigaction` and `__NR_rt_sigprocmask`.

State and persistence: only caller-provided signal sets; no persistence.

Dependencies/integration: uses `system.h` syscall wrapper and Linux signal UAPI. Replaces libc in static freestanding BTI binaries.

Risks and test signals: signal-set sizing must match kernel ABI; wrong mask size would break SIGILL handling.
