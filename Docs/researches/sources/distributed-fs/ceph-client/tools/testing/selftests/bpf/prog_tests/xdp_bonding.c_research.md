# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_bonding.c

## Purpose

Comprehensive XDP bonding integration test. It validates XDP attach rules for bond masters/slaves, packet balancing across bond modes and xmit policies, multi-redirect behavior, nested bond safety, feature aggregation, no-up round-robin redirect safety, and xmit policy compatibility with native XDP. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_program__attach_xdp()`, `bpf_xdp_attach/detach/query()`, BPF links, raw AF_PACKET `sendto()`, `/proc/net/dev` parsing, `setns()`, iproute2 bond/veth/netns commands, `xdp_dummy`, `xdp_tx`, and `xdp_redirect_multi_kern` skeletons.

## Control Flow

`serial_test_xdp_bonding()` opens root netns, loads skeletons, runs attach/nested/features subtests, iterates bond mode cases, then runs xmit-policy, redirect-multi, and no-up tests. Setup creates paired namespaces and bonds, enslaves veths, attaches XDP programs, sends synthetic UDP frames, reads rx counters, and tears down links/namespaces after each case.

## State and Persistence Behavior

Large transient network state is created: namespaces, bonds, veths, BPF links, bond feature state, and packet counters. `root_netns_fd` anchors namespace restoration; `struct skeletons` tracks links for cleanup.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires bonding driver support, veth native/generic XDP, netdev feature reporting, namespace privileges, and iproute2 support for bond options.

## Risks and Edge Cases

Environment-sensitive and cleanup-sensitive. Counter assertions can be affected by background traffic on test interfaces if names collide. Some modes/policies are intentionally selected; unsupported xmit policies are reported as unimplemented. Failing namespace restoration can cascade.

## Test Signals

Signals include expected attach accept/reject combinations, packet distribution by mode/policy, redirect-multi excluding ingress bond/slave, feature flag changes as slaves/programs change, no crash for inactive RR bond redirect, and rejection of `vlan+srcmac` while native XDP is attached.
