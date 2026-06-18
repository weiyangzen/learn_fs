
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfree_skb.c

## Purpose

`kfree_skb.c` validates raw tracepoint and fentry/fexit access to skb data and control buffer around packet free paths.

## Important APIs, Types, and Functions

The test uses `kfree_skb.skel.h`, loads `test_pkt_access.bpf.o`, attaches raw tracepoint `kfree_skb` and fentry/fexit probes on `eth_type_trans`, creates a perf buffer, and runs a sched_cls packet program with a crafted `__sk_buff` context.

## Control Flow and Data Flow

It sets `skb.cb` to known bytes, runs the packet program on `pkt_v6`, polls the perf buffer, and the callback validates metadata (`ifindex`, cb bytes/words) and IPv6/TCP header fields. It then reads the skeleton BSS map and checks both fentry/fexit result flags.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes perf-buffer events, BSS flags, loaded packet program, and attached trace links. Dependencies are raw tracepoint, fentry/fexit, perf buffer, loopback ifindex assumptions, and packet test-run. Integration is skb memory access from tracing programs. Risks include spurious `kfree_skb` events, parallel instability noted by serial test comment, and loopback metadata assumptions. Test signals are callback `passed == true`, perf poll success, and both BSS test flags true.
