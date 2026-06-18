<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf_fail.c

Purpose: Negative conntrack kfunc verifier suite covering illegal insert/lookup combinations, field writes, and post-insert mutation.

Important APIs/types/functions: Defines failing optional XDP/TC programs with expected messages and local ct option/conn structs.

Control flow: Each program violates a specific rule: double insert, lookup-to-insert, writing disallowed fields, setting timeout/status after insert, or changing status/timeout before insert incorrectly.

State and persistence: No successful runtime state expected.

Dependencies and integration: Depends on conntrack kfunc verifier annotations and `bpf_misc.h` failure metadata.

Risks: Verifier must enforce ownership and mutation windows for `nf_conn`.

Test signals: Expected annotated verifier errors are the pass condition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf_fail.c -->
