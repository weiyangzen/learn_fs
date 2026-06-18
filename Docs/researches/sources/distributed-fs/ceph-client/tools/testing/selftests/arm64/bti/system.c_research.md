# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/system.c

Purpose: tiny freestanding system-call based runtime helpers for BTI tests.

Important APIs/types/functions: `exit()` calls `__NR_exit` and then `unreachable()`; `write()` calls `__NR_write`.

Control flow: wrappers delegate directly to assembly `syscall`.

State and persistence: no internal state; `write()` emits to file descriptors.

Dependencies/integration: included in static BTI binaries with `system.h` and `syscall.S`.

Risks and test signals: no errno handling; callers inspect behavior directly or terminate.
