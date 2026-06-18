# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tuntap_helpers.h

Purpose: Inline helper library for TUN/TAP selftests. It hides YNL-generated rtnetlink request construction and provides packet construction primitives for Ethernet, IPv4, IPv6, UDP, Geneve, checksums, and virtio-net tunnel headers.

Important APIs/types/functions: includes generated `rt-route-user.h`, `rt-addr-user.h`, `rt-neigh-user.h`, `rt-link-user.h` and `ynl.h`. Netlink helpers include `ip_addr_add`, `ip_neigh_add`, `ip_route_get`, `ip_link_add`, and `ip_link_del`. Packet helpers include `build_eth`, `add_csum`, `finish_ip_csum`, `build_ip_csum`, `build_ipv4_header`, `build_ipv6_header`, `build_geneve_header`, `build_udp_header`, `build_udp_packet_csum`, `build_udp_packet`, and `build_virtio_net_hdr_v1_hash_tunnel`.

Control flow: YNL helpers allocate a family socket, allocate a generated request, fill headers and attributes, submit the request, free request/response objects, and destroy the socket on all paths. Packet helpers write headers in-place into caller-provided buffers, returning byte lengths so callers can advance a cursor. The virtio helper calculates outer transport and inner network offsets from TAP/TUN mode and IP families, then sets checksum and GSO metadata.

State and persistence: all functions are `static inline` and hold no persistent state. They mutate kernel link/address/neighbor/route state through netlink or mutate caller-provided buffers.

Dependencies and integration: designed for `tun.c` and other local TUN/TAP tests that use generated YNL rtnetlink bindings. Requires libc networking headers, Linux virtio/packet headers, and `if_nametoindex`. Build integration depends on `ynl.mk` generating/including the rtnetlink family bindings.

Risks: checksum helpers assume packet layouts where IP addresses immediately precede the UDP header; that is true for these generated packets without extension headers but not general-purpose. The packet builders do not bounds-check caller buffers. Netlink helpers return only coarse `-1` errors, so diagnostics come from callers or YNL internals.

Test signals: no standalone tests; coverage comes from `tun.c`, where successful route checks, Geneve device setup, and packet parse/segmentation validate the helpers.
