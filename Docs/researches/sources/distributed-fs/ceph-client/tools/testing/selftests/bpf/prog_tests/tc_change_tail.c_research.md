# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tc_change_tail.c

Purpose: `tc_change_tail.c` is a focused TCX selftest for a BPF program that calls `bpf_skb_change_tail()` or equivalent skb tail adjustment logic from a TC classifier. It sends small UDP payloads over a local socket pair and checks the BPF-side return code for successful and invalid tail changes.

Important APIs/types/functions: `test_tc_change_tail()` is the only exported test. It uses `LIBBPF_OPTS(bpf_tcx_opts, tcx_opts)`, generated `test_tc_change_tail.skel.h`, `bpf_program__attach_tcx()`, `create_pair()`, `xsend()`, `recv()`, and the skeleton data variable `change_tail_ret`. `LO_IFINDEX` fixes the attach target to loopback ifindex 1.

Control flow: the test opens and loads the skeleton, attaches `skel->progs.change_tail` to loopback through a TCX link, creates an IPv4 UDP socket pair, then sends four payload patterns. `"Tr"` and `"G"` are expected to pass and leave `change_tail_ret` as 0. `"E"` and `"Z"` are expected to reach paths where the helper returns `-EINVAL`. Each send is paired with a receive to ensure traffic actually traversed the hook. File descriptors are closed after the packet checks, and skeleton destruction tears down the link.

State and persistence: runtime state is limited to the TCX link stored in `skel->links.change_tail`, socket pair descriptors, the transient packet buffers, and the skeleton data field updated by BPF. There is no filesystem persistence. A failure before skeleton destruction could briefly leave a TCX program attached to loopback until process teardown.

Dependencies: depends on generated `test_tc_change_tail.skel.h`, `socket_helpers.h`, libbpf TCX attach support, loopback TCX support, Linux UDP sockets, and the kernel BPF helper semantics for skb tail modification.

Integration points: the userspace test is paired with a BPF program in the selftest build and is invoked by the BPF test harness as `test_tc_change_tail`. It integrates socket-helper traffic generation with TCX attachment to validate data-plane helper behavior.

Risks: the test is compact but assumes loopback ifindex 1 and that local UDP traffic hits the TCX hook in the expected direction. It does not explicitly initialize `c1`/`p1` to invalid values before `create_pair()`, so cleanup after a failed pair creation relies on the current control path that skips `close()`. Exact expected helper errno values may change if kernel validation order changes.

Test signals: pass criteria are successful skeleton load/attach, successful socket-pair creation, exact send/receive byte counts for 2-byte and 1-byte payloads, and `change_tail_ret` equal to either 0 or `-EINVAL` for the intended payload classes.
