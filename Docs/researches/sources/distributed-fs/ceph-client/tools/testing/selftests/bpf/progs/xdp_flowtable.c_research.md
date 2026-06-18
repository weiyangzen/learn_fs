<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_flowtable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_flowtable.c

## Purpose
This XDP fragments program tests `bpf_xdp_flow_lookup` kfunc integration by parsing IPv4/IPv6 TCP/UDP packets into a `bpf_fib_lookup` tuple and counting successful flowtable lookups.

## Important APIs, Types, and Functions
It declares local kfunc prototype `bpf_xdp_flow_lookup`, local options type `bpf_flowtable_opts___local`, and `stats` array map. Helpers validate IPv4 fragmentation/options/TTL and TCP FIN/RST state. Entry point is `xdp_flowtable_do_lookup`.

## Control Flow
The entry point parses Ethernet, dispatches IPv4 or IPv6, validates transport header bounds, filters out unsupported fragments, options, TTL/hop-limit exhaustion, and TCP FIN/RST. It fills `struct bpf_fib_lookup` fields including family, L4 protocol, addresses, ports, lengths, and ifindex, calls the kfunc, and increments `stats[0]` on a non-null result.

## State and Persistence
Persistent state is a single stats counter updated atomically. Packet data is read-only; no packet mutation or redirect occurs.

## Dependencies and Integration Points
It depends on BTF kfunc availability for flowtable lookup, XDP frags support, and kernel networking structs from `vmlinux.h`. Selftests populate flowtable state externally.

## Risks
The parser intentionally handles only direct transport headers and simple IPv4/IPv6. Unsupported extension headers, fragmentation, or TCP teardown packets are passed without lookup. Kfunc availability depends on kernel configuration.

## Test Signals
Successful flowtable hits increment `stats[0]`; all unsupported or miss cases return `XDP_PASS` without increment, while malformed Ethernet returns `XDP_DROP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_flowtable.c -->
