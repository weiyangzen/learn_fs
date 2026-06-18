<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_helpers.c

Purpose: `skb_helpers.c` is a compact smoke test for skb helper behavior in a SCHED_CLS test-run context. It loads `test_skb_helpers.bpf.o` and runs it against a small IPv4 packet and a `struct __sk_buff` containing GSO and wire-length metadata.

Important APIs/types/functions: `test_skb_helpers()` creates `struct __sk_buff` with `wire_len`, `gso_segs`, and `gso_size`, prepares `bpf_test_run_opts`, calls `bpf_prog_test_load()` for `BPF_PROG_TYPE_SCHED_CLS`, executes `bpf_prog_test_run_opts()`, and closes the object.

Control flow: there is a single load/run/close path. Any helper-specific assertions are implemented inside the paired BPF object; the userspace side checks only that load and test-run succeed.

State and persistence: state is limited to the local skb context and BPF object FD. No maps, sockets, namespaces, or files are persisted.

Dependencies: depends on `test_skb_helpers.bpf.o`, libbpf test-run APIs, packet fixture `pkt_v4`, and kernel support for the skb helper set used by the BPF program.

Integration points: integrates the selftest runner with SCHED_CLS program loading and test-run execution for helpers that consume skb metadata such as GSO and wire length.

Risks: because the userspace side has no explicit result checks, regressions must be surfaced by the BPF program's return value or load/run failure. If helper behavior changes but the BPF program still returns success, this wrapper will not detect it.

Test signals: successful BPF object load and successful `bpf_prog_test_run_opts()` are the observable signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_helpers.c -->
