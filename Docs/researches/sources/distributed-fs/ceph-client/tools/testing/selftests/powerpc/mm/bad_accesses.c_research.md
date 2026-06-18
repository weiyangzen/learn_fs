<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/bad_accesses.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/bad_accesses.c

Purpose: Tests that invalid user accesses to kernel and boundary addresses fault with the expected SIGSEGV metadata on 64-bit powerpc.

Important APIs and types: Defines `PAGE_OFFSET`, global fault tracking, `segv_handler`, `bad_access(char *p, bool write)`, `test()`, and `main()`.

Control flow: `bad_access` uses `setjmp`/`longjmp` around reads or writes to intentionally bad addresses. `test()` derives kernel virtual limits, installs a SIGSEGV handler, forks where needed, and checks access/error combinations near kernel and user address boundaries.

State and persistence: Fault code/address globals capture one fault at a time. No state persists after process exit.

Dependencies and integration points: Depends on signal info, 64-bit address layout, `utils.h`, and kernel address fault classification.

Risks: The test encodes assumptions about `PAGE_OFFSET` and address layout. It can be invalid on non-64-bit or changed virtual address split configurations.

Test signals: Pass means invalid accesses reliably fault without kernel oops and report expected si_code/address data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/bad_accesses.c -->
