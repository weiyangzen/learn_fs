<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall2.c

Purpose: Exercises chained static tail calls, multi-program updates, and tail-call limit behavior.

Important APIs/types/functions: Defines five classifiers and a five-entry `jmp_table`; classifiers 0/1 chain to 1/2 and 3/4 loop between each other.

Control flow: `entry` starts at index 0, then has fallback checks for index 2 and a 3/4 loop intended to hit limits.

State and persistence: State is the prog-array map only.

Dependencies and integration: Depends on static tail-call chaining and runtime tail-call count enforcement.

Risks: Improper call-limit handling can loop indefinitely or return wrong fallback.

Test signals: Tests update prog-array entries and check returns for chain and limit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall2.c -->
