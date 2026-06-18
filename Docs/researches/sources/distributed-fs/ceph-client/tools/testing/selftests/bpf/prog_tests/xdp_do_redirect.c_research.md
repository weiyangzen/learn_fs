# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_do_redirect.c

## Purpose

XDP redirect integration tests. It validates live-frame XDP test-run interactions with XDP_PASS/TX/REDIRECT, veth feature flags, TC counting, maximum packet size limits, and index-based XDP forwarding across namespaces. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_run_opts()` with `BPF_F_TEST_XDP_LIVE_FRAMES`, `bpf_xdp_query()`, `bpf_program__attach_xdp()`, TC hook APIs, veth/netns/ip/sysctl/ethtool commands, `kern_sync_rcu()`, and `test_xdp_do_redirect`/`xdp_dummy` skeletons.

## Control Flow

The first test creates a veth namespace, enables IPv6 forwarding/GRO, queries XDP feature flags before and after GRO, loads a redirect skeleton, attaches an XDP counter and TC counter, runs `NUM_PKTS` live-frame test-run iterations, waits for flush, asserts XDP/TC counts, then checks max packet size. `test_xdp_index_redirect()` builds three namespaces and two fixed-index veths, attaches redirect programs on both sides, and verifies ping through noflag, drv, and skb modes.

## State and Persistence Behavior

Transient namespaces, veths, TC hooks, XDP attachments, BSS packet counters, neighbor entries, and sysctl/GRO state inside the namespace.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires veth feature reporting, ethtool, IPv6 forwarding, TC, and live-frame XDP test-run support.

## Risks and Edge Cases

Feature flags vary by kernel/device; GRO changes alter expected flags. Batch/live-frame paths can deadlock if kernel regressions reappear. Fixed ifindexes 111/222 are assumed free in NS0.

## Test Signals

Expected feature flag masks, `pkts_seen_xdp == 2`, `pkts_seen_zero == 2`, `pkts_seen_tc == NUM_PKTS - 2`, max-size success/too-big `-EINVAL`, and successful ping for each attach mode.
