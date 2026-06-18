<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy3.c

Purpose: Hierarchy test using two prog-array maps to validate cross-map tail-call chains.

Important APIs/types/functions: Defines `jmp_table0`, `jmp_table1`, subprogram tail path, auxiliary classifiers, counters, and expected retval annotations.

Control flow: Control alternates through two maps/classes to exercise hierarchical tail-call accounting.

State and persistence: Persistent state is both prog arrays and counters.

Dependencies and integration: Depends on static map value initialization and tc tail-call semantics.

Risks: Cross-map chains must still honor global tail-call limits.

Test signals: Expected retval and counter assertions are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy3.c -->
