# sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/Makefile

Purpose: builds membarrier syscall tests.

Important APIs/types/functions: sets debug CFLAGS with kernel header includes, links pthreads, and declares generated programs `membarrier_test_single_thread` and `membarrier_test_multi_thread`.

Control flow: standard kselftest `lib.mk` build; both C programs include the shared implementation header.

State and persistence: none.

Dependencies and integration points: membarrier uapi header, syscall availability, pthread library.

Risks: because implementation is in a header, changes there affect both runners.

Test signals: generated binaries are kselftest-discoverable.
