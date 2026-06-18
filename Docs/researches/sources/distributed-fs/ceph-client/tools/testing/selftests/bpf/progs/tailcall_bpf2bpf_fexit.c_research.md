<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fexit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fexit.c

Purpose: Fexit companion for observing `subprog_tail` return behavior in BPF-to-BPF tail-call tests.

Important APIs/types/functions: Defines `fexit/subprog_tail` using `BPF_PROG`.

Control flow: Runs after the target subprogram when the subprogram returns normally rather than tail-calling away.

State and persistence: No persistent maps.

Dependencies and integration: Depends on fexit attachment to BPF subprograms.

Risks: Tail calls can bypass normal returns, so expected invocation semantics are delicate.

Test signals: Tests verify fexit fires only on appropriate fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fexit.c -->
