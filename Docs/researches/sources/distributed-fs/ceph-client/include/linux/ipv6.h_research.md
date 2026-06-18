# sources/distributed-fs/ceph-client/include/linux/ipv6.h

## Purpose
`ipv6.h` defines kernel IPv6 configuration, skb control-block metadata, socket private storage, and inline helpers for IPv6 header and payload length handling.

## Important APIs, types, and functions
Key items include `ipv6_optlen`, `ipv6_authlen`, `struct ipv6_devconf`, `struct ipv6_params`, `ipv6_hdr`, `inner_ipv6_hdr`, `ipipv6_hdr`, `ipv6_transport_len`, `ipv6_payload_len`, `ipv6_set_payload_len`, `struct inet6_skb_parm`, `IP6CB`, `inet6_iif`, `inet6_is_jumbogram`, `inet6_sdif`, `struct ipv6_pinfo`, raw/UDP/TCP IPv6 socket wrappers, and `inet6_sk` helpers.

## Control flow
Receive and transmit paths populate `IP6CB(skb)` with parsed extension-header offsets and flags, then socket and routing code reads per-device and per-socket IPv6 configuration. Payload helpers infer jumbo/GSO payload length when the 16-bit field is zero.

## State and persistence
State is runtime sysctl/device/socket/skb metadata: devconf knobs, stable secret, multicast lists, sticky packet info, pktoptions, PMTU notifications, and IPv6 module enable state.

## Dependencies and integration points
It depends on UAPI IPv6, cacheline grouping, TCP/UDP/inet socket types, skbuff GSO helpers, RCU socket options, sysctl, and optional IPv6 features such as MROUTE, SEG6, HMAC, optimistic DAD, and L3 master devices.

## Risks and test signals
Risks include layout changes to protocol socket wrappers, stale skb control blocks after TCP parsing, GSO/jumbogram length mistakes, per-netdev sysctl races, and optional-config stub misuse. Tests should cover extension-header parsing flags, L3 master ingress, jumbograms, IPv6-disabled builds, DAD/autoconf sysctls, and raw/UDP/TCP socket layout assumptions.
