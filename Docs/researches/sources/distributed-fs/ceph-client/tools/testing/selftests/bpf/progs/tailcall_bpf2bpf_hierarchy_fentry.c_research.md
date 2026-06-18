<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy_fentry.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy_fentry.c

Purpose: Fentry-based hierarchy test that performs a tail call from a tracing program context.

Important APIs/types/functions: Defines initialized `jmp_table`, `subprog_tail`, and `fentry/dummy` program.

Control flow: The fentry program calls a subprogram that attempts a static tail call to a tc-like target in the prog-array.

State and persistence: Prog-array map persists target configuration.

Dependencies and integration: Depends on fentry program type, BPF-to-BPF calls, and tail-call compatibility rules.

Risks: Not all program-type combinations allow tail calls, so attach/load outcome is the key risk.

Test signals: Selftest checks expected load and invocation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy_fentry.c -->
