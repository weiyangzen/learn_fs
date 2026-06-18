<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress-thread.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress-thread.S

Purpose: minimal assembly program used by `gcs-stress` to stress GCS context switching with recursion, syscalls, and signals.

Important APIs and symbols: `_start` enables GCS via raw prctl, installs signal handlers, prints "Running", and loops through generated `recurse1` and `recurse2`. Helpers implement raw `puts`, `putdec`, signal setup, and handlers for SIGTERM/SIGUSR1/SIGSEGV.

Control flow: enable shadow stack, install handlers, then repeatedly recurse to depth 5 through two different functions. Each return path issues a `getpid` syscall immediately before returning to provoke scheduling/migration near GCS updates. SIGSEGV handler disables GCS and reports `si_code`, identifying `SEGV_CPERR`.

State and persistence: no files; live GCS, call stack, and signal state are the test target.

Dependencies and integration: execed by `gcs-stress`; uses raw syscall numbers and GCS system registers/instructions.

Risks: intentionally sensitive to GCS faults and runtime environment. Offset constants for `siginfo_t` and ucontext are hard-coded.

Test signals: prints `Running` after setup; SIGTERM exits 0 with message; GCS violations print SIGSEGV code then exit 255.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress-thread.S -->
