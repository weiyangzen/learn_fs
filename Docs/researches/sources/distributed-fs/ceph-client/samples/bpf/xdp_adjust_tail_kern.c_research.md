<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_kern.c

## Purpose
`xdp_adjust_tail_kern.c` demonstrates `bpf_xdp_adjust_tail()` and `bpf_xdp_adjust_head()` by turning oversized IPv4 packets into ICMP "fragmentation needed" responses sent with `XDP_TX`.

## Important APIs, Types, And Functions
The `icmpcnt` array map counts generated ICMP packets. Helpers include `count_icmp()`, `swap_mac()`, `csum_fold_helper()`, `ipv4_csum()`, `send_icmp4_too_big()`, and `handle_ipv4()`. Entry point `_xdp_icmp()` is in section `xdp_icmp`.

## Control Flow
The XDP program parses Ethernet, handles IPv4 packets, and if packet size exceeds the configured maximum and ICMP response size, trims the tail to preserve the quoted payload, grows the head for a new IP+ICMP header, swaps MAC/IP addresses, fills ICMP frag-needed fields and checksums, increments `icmpcnt`, and transmits back out the ingress device.

## State And Persistence
`icmpcnt` persists generated response count. `max_pcktsz` is a global data variable that userspace can update through the `.data` map before attach.

## Dependencies And Integration Points
It depends on XDP helper support for head/tail adjustment, IPv4/ICMP header layout, and the userspace loader that sets max packet size and polls `icmpcnt`.

## Risks And Edge Cases
Only simple IPv4 Ethernet packets are handled; VLAN, IPv6, fragments, and IP options are not covered. Incorrect size constants can corrupt response construction. `XDP_DROP` is used for malformed or failed adjustment paths.

## Test Signals
Oversized IPv4 ingress packets should cause ICMP packet-too-big responses and increment `icmpcnt`; smaller packets should pass unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_kern.c -->
