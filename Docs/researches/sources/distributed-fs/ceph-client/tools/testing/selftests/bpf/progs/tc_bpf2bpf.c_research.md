<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_bpf2bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_bpf2bpf.c

Purpose: Minimal tc BPF-to-BPF call test.

Important APIs/types/functions: Defines subprogram `subprog_tc` and tc entry `entry_tc`.

Control flow: Entry calls the subprogram and returns its result or transformed value.

State and persistence: No persistent maps or globals.

Dependencies and integration: Depends on tc program type and BPF subprogram call support.

Risks: Verifier/JIT must preserve context and return values across the call.

Test signals: Expected signal is successful load and deterministic return value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tc_bpf2bpf.c -->
