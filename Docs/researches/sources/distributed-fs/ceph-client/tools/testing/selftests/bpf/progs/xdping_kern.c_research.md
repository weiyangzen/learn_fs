<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdping_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdping_kern.c

## Purpose
This XDP ping implementation supports a kernel-space ping client/server test by converting ICMP echo replies into subsequent requests on the client side and converting requests into replies on the server side.

## Important APIs, Types, and Functions
It defines `ping_map`, keyed by remote IPv4 address with `struct pinginfo` values from `xdping.h`. Helpers include `bpf_ktime_get_ns` and `bpf_csum_diff`. Internal helpers swap MACs, fold checksums, compute IPv4/ICMP checksum, and validate ICMP packet shape in `icmp_check`.

## Control Flow
`icmp_check` validates minimum packet length, IPv4 EtherType, ICMP protocol, expected payload length, and ICMP type. `xdping_client` accepts echo replies, looks up ping state, records elapsed time in the first empty slot, stops if count is complete, rewrites the packet into the next echo request with swapped MAC/IP addresses and incremented sequence, updates checksum and start time, and returns XDP_TX. `xdping_server` rewrites echo requests into replies and returns XDP_TX.

## State and Persistence
`ping_map` persists per-peer sequence, start time, count, and timing samples. Packets are mutated in place for source/destination MACs, IPv4 addresses, ICMP type, sequence, and checksum.

## Dependencies and Integration Points
It integrates with userspace xdping selftests that seed `ping_map` and inspect timings. It depends on fixed ICMP echo length and definitions from `xdping.h` and `bpf_compiler.h`.

## Risks
Only simple IPv4 ICMP packets with exact payload length are handled. The unrolled loop over timing slots is verifier-friendly but capped by `XDPING_MAX_COUNT`.

## Test Signals
Client-side map timing entries and continuing XDP_TX requests confirm progress; server-side reflected echo replies validate packet rewrite and checksum logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdping_kern.c -->
