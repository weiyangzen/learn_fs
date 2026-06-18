# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_metadata.bpf.c

## Purpose
This XDP BPF program tests receive metadata support by reading the hardware/kernel RSS hash and hash type for selected packets.

## Important APIs and Maps
`map_xdp_setup` is an array map keyed by `XDP_PORT` and `XDP_PROTO` to filter destination port and L4 protocol. `map_rss` stores `RSS_KEY_HASH`, `RSS_KEY_TYPE`, packet count, and error count. `xdp_rss_hash` parses Ethernet, IPv4/IPv6, and TCP/UDP headers; `get_dest_port` safely extracts TCP/UDP destination ports. The program calls kfunc `bpf_xdp_metadata_rx_hash`.

## Control Flow and State
On each packet, the program validates header bounds, applies optional protocol and port filters from `map_xdp_setup`, calls `bpf_xdp_metadata_rx_hash`, increments error count on failure, or updates hash/type and increments packet count on success. It always returns `XDP_PASS`.

## Dependencies and Integration
It depends on XDP metadata kfunc availability, BPF map support, libbpf section loading, and userspace configuration through bpftool or `lib/py/bpf.py`. It is built as a BPF object by the helper Makefile.

## Risks and Test Signals
Unsupported metadata kfuncs or drivers without RX hash support increment error count or fail load depending on kernel support. The parser does not walk IPv6 extension headers. Test signals are `map_rss` packet count/error count and observed hash/type values while traffic continues to pass.
