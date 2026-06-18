<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/subpage_prot.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/subpage_prot.c

Purpose: Exercises the powerpc `subpage_prot` syscall for 64 KiB pages split into smaller protected subpages. It covers anonymous and file-backed mappings.

Important APIs and types: Defines signal handler `segv`, access helpers, `check_faulted`, `run_test`, `syscall_available`, `test_anon`, `test_file`, and `main()`.

Control flow: `run_test()` applies a subpage protection bitmap, performs read/write probes across subpages, and checks which accesses fault. `test_anon` maps anonymous memory; `test_file` maps a generated tempfile. `main` handles optional filename input and syscall availability.

State and persistence: Global `file_name`, `in_test`, `errors`, and signal context track the active probe. File-backed test uses the Makefile-generated tempfile.

Dependencies and integration points: Depends on powerpc-specific `subpage_prot` syscall, signal/ucontext reporting, `mmap`, ptrace/syscall headers, and `utils.h`.

Risks: The syscall is powerpc-specific and page-size dependent. Fault address handling must align with subpage granularity or the test can misattribute failures.

Test signals: Pass demonstrates correct read/write blocking for protected subpages in anonymous and file mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/subpage_prot.c -->
