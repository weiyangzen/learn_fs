<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_fail.c

Purpose: Negative verifier suite for invalid task-work scheduling patterns.

Important APIs/types/functions: Defines hash/array maps, `process_work`, and perf_event programs annotated for expected failures.

Control flow: Programs try disallowed contexts, duplicate scheduling, or invalid object lifetime transitions around task work.

State and persistence: No successful runtime state expected for failing sections.

Dependencies and integration: Depends on task-work verifier rules and map value lifetime tracking.

Risks: Accepting invalid scheduling can lead to use-after-free or duplicate callbacks.

Test signals: Expected verifier messages are the pass criteria.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/task_work_fail.c -->
