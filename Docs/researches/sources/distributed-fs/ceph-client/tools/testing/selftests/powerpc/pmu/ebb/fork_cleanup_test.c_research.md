<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/fork_cleanup_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/fork_cleanup_test.c

Purpose: Tests that EBB state is cleaned up correctly across fork. It ensures a child does not inherit usable stale EBB PMU state unexpectedly.

Important APIs and types: Defines global `event`, child function `child`, `fork_cleanup`, and `main()`.

Control flow: The parent configures EBB state, forks, the child probes inherited PMC/EBB access with SIGILL-catching behavior, and the parent waits/validates cleanup semantics.

State and persistence: Global event state exists only for the process lifetime and is closed before exit.

Dependencies and integration points: Depends on fork semantics, EBB state cleanup in the kernel, and `catch_sigill` helpers.

Risks: Fork inheritance rules are subtle; failure could indicate either kernel cleanup issues or test ordering mistakes.

Test signals: Pass means forked children do not retain unsafe EBB access/state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/fork_cleanup_test.c -->
