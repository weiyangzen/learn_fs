<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_siginfo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_siginfo.c

Purpose: Concurrency test for pkey signal metadata. It checks that faults report the restrictive pkey when two threads race to protect the same page with permissive and restrictive keys.

Important APIs and types: Defines `struct region`, SIGSEGV handler, thread functions `protect` and `protect_access`, `reset_pkeys`, `test()`, and `main()`. Uses pthread barriers and pkey syscalls.

Control flow: `test()` prepares an executable page, clears pkey restrictions, then runs three thread pairs for read, write, and execute restrictions. One thread repeatedly applies a permissive pkey while the other applies a restrictive pkey and accesses a random instruction word, expecting `SEGV_PKUERR` to name the restrictive key.

State and persistence: Global volatile fields hold the current permissive/restrictive pkeys, rights, fault count, and fault address. The barrier synchronizes each iteration across one million loops.

Dependencies and integration points: Depends on pthreads, `pkeys.h`, signal metadata, and powerpc AMR/IAMR pkey implementation.

Risks: The test is race-oriented and long-running. Random fault addresses and competing `pkey_mprotect` calls are intentional, so failures require distinguishing real kernel metadata bugs from unsupported pkey setups.

Test signals: Pass means `siginfo` pkey reporting remains accurate under concurrent protection changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/pkey_siginfo.c -->
