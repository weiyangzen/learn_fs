<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf3.c

Purpose: Tests nested BPF-to-BPF tail-call helpers and multiple classifier targets.

Important APIs/types/functions: Defines `subprog_tail2`, `subprog_tail`, classifiers 0/1, entry, and a prog-array.

Control flow: Entry enters subprograms that can tail-call into classifiers, with fallbacks on miss.

State and persistence: State is the prog-array map and any global counters.

Dependencies and integration: Depends on subprogram tail-call support in tc programs.

Risks: Nested call depth plus tail-call transfer must maintain verifier state.

Test signals: Tests exercise each map index and fallback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf3.c -->
