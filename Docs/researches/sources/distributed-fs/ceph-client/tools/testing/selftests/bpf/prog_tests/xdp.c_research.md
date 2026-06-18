# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp.c

## Purpose

Basic XDP tunnel rewrite test using shared IPv4/IPv6 packet fixtures. It verifies that `test_xdp.bpf.o` looks up VIP-to-tunnel map entries and rewrites packets for XDP_TX with the expected outer protocol. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_load()`, `bpf_find_map()`, `bpf_map_update_elem()` for `vip2tnl`, `bpf_prog_test_run_opts()`, `struct vip`, `struct iptnl_info`, packet fixtures `pkt_v4`/`pkt_v6`, and output header parsing via `struct iphdr`/`struct ipv6hdr`.

## Control Flow

The test loads `test_xdp.bpf.o`, populates the `vip2tnl` map with IPv4 and IPv6 TCP VIP keys, test-runs the program on an IPv4 packet and checks `XDP_TX`, output size 74, and `IPPROTO_IPIP`, then test-runs on an IPv6 packet and checks `XDP_TX`, output size 114, and `IPPROTO_IPV6`.

## State and Persistence Behavior

State is the loaded object, `vip2tnl` map entries, stack output buffer, and parsed output headers. The object close releases all test state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Coverage is intentionally small; regressions outside basic test-run behavior may be caught by the more specialized XDP files in this subset.

## Test Signals

Successful XDP program load and expected `bpf_prog_test_run_opts()` return/action values are the relevant signals.
