<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_ctx.c

Purpose: `skb_ctx.c` validates `bpf_prog_test_run_opts()` handling of `struct __sk_buff` context input/output for a `BPF_PROG_TYPE_SCHED_CLS` program. It checks that invalid context sizes and prohibited nonzero fields are rejected, then verifies that writable context fields are modified as expected.

Important APIs/types/functions: `test_skb_ctx()` constructs a `struct __sk_buff`, fills `LIBBPF_OPTS(bpf_test_run_opts)`, loads `test_skb_ctx.bpf.o` with `bpf_prog_test_load()`, runs `bpf_prog_test_run_opts()`, and validates returned context fields. It uses `pkt_v4` from `network_helpers.h` as packet data.

Control flow: the test first verifies that `ctx_in` with zero `ctx_size_in` and `ctx_out` with zero `ctx_size_out` both fail. It then sets nonzero `len`, `tc_index`, `hash`, and `sk` fields one by one and expects rejection. With a valid context, it runs the BPF program and checks `retval`, output context size, incremented `cb[]`, `priority`, `tstamp`, and `mark`, while stable fields such as `ifindex` and `ingress_ifindex` remain as expected.

State and persistence: state is entirely local to the loaded BPF object, the `__sk_buff` context buffer, and test-run options. There is no socket, namespace, or durable state.

Dependencies: requires `test_skb_ctx.bpf.o`, libbpf program test-run support for SCHED_CLS, `struct __sk_buff` context validation in the kernel, and IPv4 packet fixture data.

Integration points: this file bridges userspace BPF test-run APIs with the kernel's skb context validation and writable-field behavior for classifier programs.

Risks: the test encodes the exact set of context fields rejected by the kernel. If kernel policy changes for fields such as `tc_index`, `hash`, or `sk`, this test will need adjustment. It also assumes fixed output modifications performed by the paired BPF object.

Test signals: expected failures for zero context sizes and prohibited fields, followed by a successful run with `retval == 0`, full context output size, and expected incremented context fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/skb_ctx.c -->
