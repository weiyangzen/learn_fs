<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_exec_prot.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_exec_prot.c

Purpose: Tests execute protection using powerpc memory protection keys. It verifies IAMR/AMR interactions for read, write, and execute faults.

Important APIs and types: Defines PPC instruction words, signal handlers, `test()`, and `main()`. Uses `sys_pkey_alloc`, `sys_pkey_mprotect`, `pkey_set_rights`, `next_pkey_rights`, and `siginfo_pkey` from `pkeys.h`.

Control flow: `test()` maps an instruction page, allocates pkeys with execute-disabled and other right combinations, performs read/write/branch attempts, and expects either access faults or `SEGV_PKUERR`. The SIGSEGV handler restores rights or remaps execute-only pages so testing can continue.

State and persistence: Global fault metadata records expected pkey, fault type, code, and address. Pkeys are allocated/freed during each case.

Dependencies and integration points: Depends on kernel pkey support, powerpc IAMR behavior, POSIX signals, and executable anonymous mappings.

Risks: Subtle risk is distinguishing ordinary access faults from pkey faults when PROT bits and pkey rights both deny access. Handler recovery depends on pkey semantics that userspace cannot fully control for IAMR.

Test signals: Pass confirms correct pkey signal metadata and execute restriction behavior across valid rights combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_exec_prot.c -->
