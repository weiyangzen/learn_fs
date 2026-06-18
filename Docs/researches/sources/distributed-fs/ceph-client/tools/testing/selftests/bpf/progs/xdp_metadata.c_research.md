<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata.c

## Purpose
This XDP metadata test redirects UDP port 8080 packets to AF_XDP after reserving custom metadata and populating RX timestamp, hash, and VLAN fields. It also provides a devmap redirect program.

## Important APIs, Types, and Functions
Maps are `xsk`, `prog_arr`, and `dev_map`. Kfuncs are `bpf_xdp_metadata_rx_timestamp`, `bpf_xdp_metadata_rx_hash`, and `bpf_xdp_metadata_rx_vlan_tag`. Entry points are `rx` and `redirect`.

## Control Flow
`rx` parses basic Ethernet IPv4/IPv6 UDP and passes non-UDP or non-8080 packets. For matches it calls `bpf_xdp_adjust_meta`, validates metadata space, writes metadata fields, substitutes timestamp 1 when veth returns zero, and redirects to `xsk[rx_queue_index]`. `redirect` redirects to `dev_map` by RX queue index.

## State and Persistence
Map state persists AF_XDP sockets, optional program-array entries, and devmap entries. Per-packet metadata is written transiently for userspace consumption.

## Dependencies and Integration Points
The program integrates with XDP metadata and AF_XDP tests. It depends on `xdp_metadata.h` layout shared with userspace and driver/kfunc support.

## Risks
Parser support is intentionally simple and does not handle VLANs here. Metadata kfunc return values are mostly ignored, so userspace must tolerate absent metadata except for the timestamp fallback behavior.

## Test Signals
Successful redirect to AF_XDP with a populated metadata prefix is the core signal; nonmatching packets pass and metadata adjustment failures drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata.c -->
