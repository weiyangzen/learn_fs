# sources/distributed-fs/ceph-client/net/ipv4/ip_sockglue.c

## Purpose
Provides IPv4 socket API glue: SOL_IP control-message send/receive handling, router-alert registration, ICMP/local error queue delivery, programmatic socket option setters, multicast membership/source-filter option handling, generic IP setsockopt/getsockopt dispatch, and packet-info preparation for receive side ancillary data.

## APIs, Types, and Functions
Exported APIs are `ip_cmsg_recv_offset()`, `ip_icmp_error()`, `ip_sock_set_tos()`, `ip_sock_set_freebind()`, `ip_sock_set_recverr()`, `ip_sock_set_mtu_discover()`, `ip_sock_set_pktinfo()`, `ip_setsockopt()`, and `ip_getsockopt()`. Key internal functions include `ip_cmsg_send()`, `ip_ra_control()`, `ip_local_error()`, `ip_recv_error()`, `do_ip_setsockopt()`, `do_ip_getsockopt()`, multicast helpers for `ip_msfilter`, `group_filter`, source membership, compat structures, and `ipv4_pktinfo_prepare()`. The file defines the `ip4_min_ttl` static key.

## Control Flow
Receive ancillary data is gated by `inet_cmsg_flags()` and emitted in likely-use order: packet info, TTL, TOS, received/return options, security label, original destination, checksum, and fragment size. Send control messages parse SOL_SOCKET, SOL_IP, and optional v4-mapped IPv6 pktinfo into `ipcm_cookie` fields before transport send. Error handling clones or allocates skbs, fills `sock_extended_err`, queues them to `sk_error_queue`, and `ip_recv_error()` later copies payload, offender address, timestamps, ancillary data, and `IP_RECVERR`.

`do_ip_setsockopt()` first handles options that can be toggled without the socket lock, then locks RTNL when multicast table state requires it and locks the socket for options that mutate IPv4 options, checksum conversion, multicast interfaces/memberships/source filters, and XFRM policy. `do_ip_getsockopt()` mirrors this by returning lockless scalar state when safe and locking for multicast filter queries. Netfilter gets a fallback chance for unknown non-excluded options.

## State and Persistence
State lives primarily in `inet_sock` bits and fields: TOS, TTL, multicast TTL/interface/address, pmtudisc, min TTL, local port range, receive flags, `inet_opt` RCU pointer, and unicast interface. Router alert state persists in `net->ipv4.ra_chain` under `ra_mutex` and is removed with RCU-delayed socket put. Error queues persist until read or purged. Multicast membership and source-filter state is delegated to IGMP helpers. The `ip4_min_ttl` static key is enabled when any socket sets a nonzero minimum TTL and is not disabled here.

## Dependencies and Integration
Integrates with the BSD socket API, cmsg helpers, user/compat copy helpers, IGMP multicast state, route/FIB lookup for pktinfo, security/LSM secctx conversion, timestamping error queues, XFRM policy sockets, multicast routing socket options, netfilter socket options, IPv6 compatibility for v4-mapped pktinfo and receive info, RTNL locking, and RCU-managed IP options.

## Risks
Risks include optlen compatibility mistakes, integer overflow in variable-size source-filter allocations, stale or incorrectly locked `inet_opt` changes affecting TCP MSS, inconsistent multicast interface validation with L3 master devices, error queue address offsets for short payloads, static key lifetime for `IP_MINTTL`, and security/capability checks around transparent bind and XFRM policy. Router-alert cleanup depends on RCU ordering and destructor behavior.

## Test Signals
Good tests exercise `setsockopt()` and `getsockopt()` for every scalar option with int and byte optlen forms, multicast join/leave and source-filter compat paths, `IP_PKTINFO`/`IP_RECVTTL`/`IP_RECVTOS` cmsgs, raw `IP_HDRINCL`, `IP_RECVERR` local and ICMP errors, `IP_RECVERR_RFC4884`, `IP_UNICAST_IF` with L3 masters, netfilter fallback options, and socket lock/RTNL lockdep coverage.
