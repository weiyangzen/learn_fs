# sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_single_thread.c

Purpose: runs membarrier syscall tests in a single-threaded process.

Important APIs/types/functions: includes `membarrier_test_impl.h` and calls `test_membarrier_get_registrations()`, `test_membarrier_query()`, `test_membarrier_fail()`, and `test_membarrier_success()`.

Control flow: prints kselftest header, sets plan `18`, checks initial registrations with command `0`, verifies query/support, runs negative and positive suites, checks registrations again, and exits pass.

State and persistence: only process-local membarrier registration state.

Dependencies and integration points: membarrier syscall and kselftest framework.

Risks: test count depends on query-supported optional commands and helper behavior; stale assumptions can desynchronize plan output.

Test signals: expected kselftest pass lines and registration bitmask consistency.
