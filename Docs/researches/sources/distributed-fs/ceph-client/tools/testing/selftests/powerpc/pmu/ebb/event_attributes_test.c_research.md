<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/event_attributes_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/event_attributes_test.c

Purpose: Validates perf event attribute requirements for EBB events. It checks accepted/rejected combinations of pinned, exclusive, config bits, and grouping.

Important APIs and types: Defines `event_attributes()` and `main()` using event initialization helpers from `ebb.h`/`event.h`.

Control flow: The test constructs several perf event attributes, opens them, and expects success or failure depending on EBB constraints such as leader/pinned/exclusive configuration.

State and persistence: Perf fds are opened/closed per case; no persistence.

Dependencies and integration points: Depends on perf_event_open validation in the kernel and local event wrappers.

Risks: Kernel policy changes to EBB attribute validation require updating expected outcomes.

Test signals: Pass means userspace receives stable success/error behavior for EBB perf attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/event_attributes_test.c -->
