# sources/distributed-fs/ceph-client/include/net/transp_v6.h

## Purpose

`transp_v6.h` declares common IPv6 transport protocol initialization, control-message, and proc-format helpers. It is a shared contract for rawv6, udpv6, tcpv6, pingv6, IPv6 extension headers, and fragmentation setup.

## Important APIs, types, and functions

The header exports protocol objects `rawv6_prot`, `udpv6_prot`, `tcpv6_prot`, and `pingv6_prot`; init/exit functions for IPv6 extension headers, fragmentation, ping, raw, UDP, and TCP; control message helpers `ip6_datagram_recv_ctl()`, `ip6_datagram_recv_common_ctl()`, `ip6_datagram_recv_specific_ctl()`, and `ip6_datagram_send_ctl()`; and sequence-file helpers `__ip6_dgram_sock_seq_show()` plus `ip6_dgram_sock_seq_show()`. It also defines `LOOPBACK4_IPV6` and `IPV6_SEQ_DGRAM_HEADER`.

## Control flow

IPv6 stack initialization calls the init functions and unwinds with matching exit functions. Datagram receive paths populate ancillary data through common/specific control helpers. Send paths parse IPv6 cmsgs into `flowi6` and `ipcm6_cookie`. Proc seq readers call the wrapper to print socket state with current receive queue bytes.

## State and persistence behavior

The header owns no state. The declared protocol objects and module-level IPv6 transport registrations persist for the lifetime of the IPv6 stack. Proc display reflects live socket memory accounting.

## Dependencies and integration points

It depends on checksum and socket infrastructure and forward-declares IPv6 flow/control cookie types. It integrates with IPv6 datagram sockets, `/proc/net` sequence output, and transport module init/exit.

## Risks and test signals

Risks include init/exit ordering mismatches, cmsg parsing differences between common and protocol-specific paths, and proc output field drift. Tests should cover IPv6 UDP/TCP/raw/ping module init, send/recv control messages, proc socket listing, and builds without optional transports.
