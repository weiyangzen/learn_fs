<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.c

## Purpose

`skf_net_off.c` tests classic socket BPF access through `SKF_NET_OFF` when packets arrive from a TAP device, including fragmented/NAPI-frags skb layout. It verifies that a raw IPv6 UDP socket can receive a packet and that an attached filter can inspect network-header-relative fields.

## Important APIs, Types, and Functions

Key functions are `tun_open`, `sk_set_filter`, `raw_open`, `tun_write`, `raw_read`, `parse_opts`, and `main`. The test uses `/dev/net/tun`, `ioctl(TUNSETIFF)`, `IFF_TAP`, optional `IFF_NAPI | IFF_NAPI_FRAGS`, `socket(PF_INET6, SOCK_RAW, IPPROTO_UDP)`, `SO_ATTACH_FILTER`, classic BPF instructions, `writev`, `recvmsg`, and `SO_RCVTIMEO`.

## Control Flow

Options select a TAP interface (`-i`), attach the BPF filter (`-f`), and request NAPI frags mode (`-F`). `main` opens the raw socket, opens the TAP, writes an Ethernet + IPv6 + UDP + payload frame to the TAP fd, then reads the UDP header and payload from the raw socket. The filter accepts only host packets with IPv6 next-header UDP and destination port `cfg_dst_port`.

## State and Persistence Behavior

The program attaches per-socket classic BPF state and opens a TAP file descriptor for an already configured interface. It does not create the interface itself. Packet data is transient; all descriptors close before exit.

## Dependencies and Integration Points

It depends on a prepared TAP interface with IPv6 peer addressing, disabled GRO, and early-demux configuration supplied by `skf_net_off.sh`. It integrates with kernel skb header offset handling, raw IPv6 sockets, TUN/TAP, and classic BPF ancillary offsets `SKF_AD_OFF` and `SKF_NET_OFF`.

## Risks and Edge Cases

The IPv6 UDP checksum is set to zero, which is normally invalid for IPv6 UDP but accepted in this controlled raw-path scenario only if the stack path permits it. Filter offsets assume no IPv6 extension headers. The test is sensitive to GRO/early-demux because those can linearize or pull headers before the targeted code path.

## Test Signals

Success prints the received payload and `OK`. Failures appear as `error(3)` exits for TUN open/configuration, filter attach, frame write, raw receive timeout, or unexpected received length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/skf_net_off.c -->
