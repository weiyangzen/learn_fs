<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/lost_exception_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/lost_exception_test.c

Purpose: Regression test for lost EBB exceptions around scheduling and signal/mmap activity. It tries to expose pending EBBs that fail to deliver.

Important APIs and types: Defines `test_body`, wrapper `lost_exception`, and `main()`.

Control flow: `test_body()` configures EBBs, runs busy loops and scheduler activity, may use mappings/signals, and checks that expected EBB counts arrive rather than being silently lost.

State and persistence: Uses process-global EBB state and transient mappings.

Dependencies and integration points: Depends on `ebb.h`, scheduler behavior, and PMU exception delivery.

Risks: Race/timing-sensitive by design; failures can be hard to reproduce without the same CPU load.

Test signals: Pass indicates no lost EBB delivery under the tested stress pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/lost_exception_test.c -->
