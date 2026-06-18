# sources/distributed-fs/ceph-client/include/linux/virtio_net.h

## Purpose
This header provides kernel helpers for translating between virtio-net headers and Linux `sk_buff` checksum/GSO/tunnel metadata.

## Important APIs, types, and functions
Important helpers include `virtio_net_hdr_match_proto()`, `virtio_net_hdr_set_proto()`, `virtio_net_hdr_to_skb()`, internal `__virtio_net_hdr_to_skb()`, `virtio_net_hdr_from_skb()`, header-length setters, `virtio_l3min()`, tunnel-aware `virtio_net_hdr_tnl_to_skb()`, checksum validation `virtio_net_handle_csum_offload()`, and tunnel-aware `virtio_net_hdr_tnl_from_skb()`.

## Control flow, state, and persistence
RX paths parse virtio header flags, GSO type, checksum start/offset, optional tunnel offsets, and set skb protocol, transport headers, checksum state, GSO metadata, and encapsulation. TX paths derive virtio header fields from skb GSO/checksum/tunnel metadata and negotiated features. State is per-packet skb metadata and header contents; no persistence is involved.

## Dependencies and integration points
It depends on VLAN/IP/IPv6/UDP/TCP and virtio-net UAPI headers plus skbuff helpers. It integrates virtio-net, vhost-net, tap/macvtap-like paths, and packet validation for offloads.

## Risks and test signals
Risks include accepting invalid checksum offsets, GSO size zero or `GSO_BY_FRAGS`, unsupported tunnel metadata without negotiated features, protocol misclassification, and modifying skb GSO type during header creation. Tests should cover TCPv4/v6, UDP/UFO/USO, tunnel GSO with and without checksum, DATA_VALID handling, malformed offsets, endian variants, and VLAN header lengths.
