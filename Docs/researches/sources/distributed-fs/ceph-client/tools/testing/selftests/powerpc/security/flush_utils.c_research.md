# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/flush_utils.c

Purpose: common cache-miss workload and DSCR-control support for the powerpc flush mitigation tests.

Important APIs/types/functions: defines inline `load()`, `syscall_loop()`, `syscall_loop_uaccess()`, `sigill_handler()`, and `set_dscr()`.

Control flow: the syscall loops repeatedly touch one cacheline per `CACHELINE_SIZE` across the supplied buffer, then issue either `getppid()` or `uname()` to trigger kernel entry/uaccess paths. `set_dscr()` installs a SIGILL handler once, then attempts `mtspr(SPRN_DSCR, val)`; the handler skips unavailable DSCR writes.

State and persistence behavior: static `init` ensures signal handler registration once, and static `warned` limits DSCR warning noise. DSCR changes affect the running thread's prefetch behavior until reset by callers.

Dependencies and integration points: depends on `reg.h`, `utils.h`, and `flush_utils.h`. Used by `rfi_flush.c`, `entry_flush.c`, and `uaccess_flush.c`.

Risks and test signals: signal-handler PC patching assumes instruction encoding for DSCR writes. If an unrelated SIGILL occurs, the handler aborts the process.
