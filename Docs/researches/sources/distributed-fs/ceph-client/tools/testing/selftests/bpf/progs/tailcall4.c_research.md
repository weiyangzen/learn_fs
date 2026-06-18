<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall4.c

Purpose: Static tail-call edge-case test with a compact tc object and prog-array map.

Important APIs/types/functions: Defines a `jmp_table` and tc entry/classifier pair.

Control flow: Entry attempts a static tail call to a configured index and falls through on miss.

State and persistence: State is the prog-array map.

Dependencies and integration: Depends on static tail-call relocation and tc loading.

Risks: Map index or relocation mistakes change the observed return.

Test signals: Tests validate both populated and unpopulated prog-array behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall4.c -->
