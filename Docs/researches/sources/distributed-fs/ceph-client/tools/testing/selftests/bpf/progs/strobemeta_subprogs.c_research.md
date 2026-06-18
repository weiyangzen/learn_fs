<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_subprogs.c

Purpose: Builds strobemeta with no-unroll loops and selected helpers emitted as BPF subprograms to exercise call-stack and subprog verification.

Important APIs/types/functions: Defines the nounroll constants plus `SUBPROGS`, causing `calc_location`, `read_int_var`, and `read_strobe_meta` to be `__noinline`.

Control flow: Runtime flow is the common strobemeta path, but metadata collection crosses BPF-to-BPF calls instead of being fully inlined.

State and persistence: Common strobemeta maps and sample state only.

Dependencies and integration: Depends on BPF subprogram support and the shared header.

Risks: Private stack usage, pointer/refinement preservation across calls, and loop bounds across subprograms are the important verifier risks.

Test signals: Successful program load with metadata enabled validates call-boundary tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_subprogs.c -->
