<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/segv_errors.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/segv_errors.c

Purpose: Validates SIGSEGV `si_code` values for mapping and permission errors. It focuses on distinguishing map errors from access errors.

Important APIs and types: Defines `segv_handler`, `test_segv_errors()`, and `main()`, with global `faulted` and `si_code` state.

Control flow: The test installs a handler, triggers faults for unmapped memory and protected mappings, and checks the kernel reports expected `SEGV_MAPERR` or `SEGV_ACCERR` semantics.

State and persistence: Fault status is process-local global state reset per case.

Dependencies and integration points: Depends on POSIX signals, `mmap`/`mprotect`, ucontext availability, and `utils.h`.

Risks: Signal-code expectations can vary for architecture-specific fault classes; this file is intentionally narrow to common SEGV cases.

Test signals: Passing confirms basic powerpc fault classification visible to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/segv_errors.c -->
