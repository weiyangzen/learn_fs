# sources/distributed-fs/ceph-client/net/tipc/udp_media.h

## Purpose
Declares UDP bearer netlink helpers and an MTU validation helper when `CONFIG_TIPC_MEDIA_UDP` is enabled.

## Important APIs, Types, And Functions
The header exposes `tipc_udp_nl_bearer_add`, `tipc_udp_nl_add_bearer_data`, and `tipc_udp_nl_dump_remoteip` for generic TIPC netlink code to manage UDP bearer-specific remote endpoints. `tipc_udp_mtu_bad` checks whether an MTU can carry minimum TIPC bearer data plus IPv4 and UDP headers, logging a warning on invalid values.

## Control Flow And State
No persistent state is declared here. The inline MTU helper returns `false` for acceptable MTUs and `true` for too-low values, so callers can reject bearer configuration before runtime packet loss.

## Dependencies And Integration Points
Includes IP and UDP header definitions and depends on TIPC bearer/netlink types from includers. It is conditionally compiled only for UDP media support, so generic code must guard use through the same config.

## Risks And Test Signals
The main risk is validating only IPv4+UDP overhead even though the UDP media implementation also supports IPv6, where overhead differs. Tests should include bearer configuration at boundary MTUs, IPv4/IPv6 UDP media builds, and netlink remote-IP add/dump calls with and without UDP media enabled.
