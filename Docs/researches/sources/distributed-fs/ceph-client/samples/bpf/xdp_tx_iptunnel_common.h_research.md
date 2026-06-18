<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_common.h -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_common.h

## Purpose
`xdp_tx_iptunnel_common.h` defines shared key/value structures for the XDP IP-in-IP tunnel transmit sample.

## Important APIs, Types, And Functions
It defines `MAX_IPTNL_ENTRIES`, `struct vip` for matching service destination address/port/family/protocol, and `struct iptnl_info` for tunnel source/destination addresses, family, and destination MAC.

## Control Flow
There is no executable control flow.

## State And Persistence
Instances of `struct vip` and `struct iptnl_info` persist as keys and values in the `vip2tnl` BPF map populated by userspace and read by the XDP program.

## Dependencies And Integration Points
The header is included by both kernel and userspace halves, making it the ABI for tunnel map population and lookup.

## Risks And Edge Cases
Any layout or byte-order mismatch between userspace population and BPF lookup breaks encapsulation selection. The maximum entries constant limits accepted port-range size.

## Test Signals
Successful map lookups in the XDP program for user-configured VIP/port/protocol entries validate the shared layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_common.h -->
