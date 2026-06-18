# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/signal.h

Purpose: header for freestanding signal wrappers used by BTI tests.

Important APIs/types/functions: includes Linux signal definitions, aliases `sighandler_t`, and declares `sigemptyset()`, `sigaddset()`, `sigaction()`, `sigprocmask()`.

Control flow: no direct flow.

State and persistence: none.

Dependencies/integration: included by `test.c` and implemented by `signal.c`.

Risks and test signals: depends on `system.h` and kernel UAPI definitions matching the running architecture.
