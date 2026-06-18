# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/connect_ping.c

## Purpose
Tests cgroup connect programs for IPv4 and IPv6 ping sockets, including optional bind behavior that changes the local address.

## Important APIs, types, and functions
Uses `connect_ping.skel.h`, `unshare(CLONE_NEWNET | CLONE_NEWNS)`, sysfs/bpffs mounts, loopback address setup, `write_sysctl()` for ping group range, and cgroup attach helpers. `subtest()` creates datagram ICMP/ICMPv6 sockets, connects to loopback, validates invocation counters and local bound address through `getsockname()`.

## Control flow and state
The top-level function creates isolated network and mount namespaces, remounts `/sys`, mounts bpffs, configures loopback IPv4/IPv6 addresses, joins `/connect_ping`, loads and attaches IPv4/IPv6 connect programs, then runs four subtests: v4, v4-bind, v6, v6-bind. State is namespace-local network config, cgroup FD, skeleton links, and BSS fields `do_bind`, `invocations_v4`, `invocations_v6`, `has_error`.

## Dependencies and integration points
Requires privilege to unshare/mount/configure networking, ping socket permissions, cgroup hooks, and generated skeleton. Integrated into selftests as `test_connect_ping()`.

## Risks and test signals
Environmental setup is the primary risk. Passing signals are exactly one family-specific invocation, no BPF error, and expected local address: loopback when not binding, `1.1.1.1` or `2001:db8::1` when binding.
