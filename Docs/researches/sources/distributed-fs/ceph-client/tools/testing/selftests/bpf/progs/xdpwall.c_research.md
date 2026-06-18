<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdpwall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdpwall.c

## Purpose
This XDP firewall/parser test inspects IPv6 and IPv6/GUE-encapsulated traffic, consults multiple maps for source IP and transport-port matches, and enforces a simple policy that only passes ICMPv6 and non-SYN TCP after filtering.

## Important APIs, Types, and Functions
Maps include IPv6 and IPv4 exact-match hash maps, IPv4 LPM trie, TCP port array, and UDP port array. Important structs are `pkt_info`, `fw_match_info`, `v4_lpm_key`, and `v4_lpm_val`. Helpers parse Ethernet, IPv6/GUE, TCP, UDP, and map-backed filters.

## Control Flow
`edgewall` parses Ethernet and drops non-IPv6. `parse_ipv6_gue` initializes outer IPv6 state and, for UDP destination 6666, `parse_gue_v6` switches to inner IPv4 or IPv6 headers and marks `TUNNEL`. ICMPv6 passes. Non-TCP/UDP drops. The program then records IP match metadata, computes the transport header by bounded offset, parses TCP/UDP, records port matches, and finally passes only TCP packets that are not pure SYN; everything else drops.

## State and Persistence
Persistent state lives in filter maps configured by userspace. The program does not update maps or mutate packets. `fw_match_info` is local and currently affects only the final decision via TCP/SYN status.

## Dependencies and Integration Points
It integrates with XDP verifier/runtime selftests and uses Linux network header definitions plus BPF map lookups. The LPM trie requires `BPF_F_NO_PREALLOC`.

## Risks
The policy is intentionally narrow: non-IPv6, malformed GUE, UDP, TCP SYN, and most unmatched cases drop. Offset is capped at 255, limiting parser depth. GUE detection uses a simple first-byte IP-version heuristic.

## Test Signals
Packet outcomes are the signal: ICMPv6 passes, established-style TCP ACK/RST passes, TCP SYN drops, malformed/unsupported traffic drops, and map lookups exercise exact and LPM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdpwall.c -->
