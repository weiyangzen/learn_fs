<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fentry.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fentry.c

Purpose: Fentry probe used to observe or validate the `subprog_tail` function from BPF-to-BPF tail-call tests.

Important APIs/types/functions: Defines a `fentry/subprog_tail` BPF program via `BPF_PROG`.

Control flow: The program runs on entry to the target subprogram and records/returns a simple value for the harness.

State and persistence: No maps; any state is through globals if present.

Dependencies and integration: Depends on fentry attachment to BPF subprogram symbols.

Risks: Attachment name must match the target subprog and coexist with tail-call tests.

Test signals: Test signal is successful fentry attach and expected invocation count/result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_fentry.c -->
