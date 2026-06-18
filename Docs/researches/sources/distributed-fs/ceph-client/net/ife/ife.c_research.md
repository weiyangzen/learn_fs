# sources/distributed-fs/ceph-client/net/ife/ife.c

## Purpose
`ife.c` implements helpers for encoding and decoding Inter-FE metadata encapsulation. It manipulates skbuff layout to prepend an outer Ethernet header and IFE metadata block, then provides TLV helpers used by traffic-control actions or other IFE consumers.

## Important APIs, types, and functions
The file exports `ife_encode()`, `ife_decode()`, `ife_tlv_meta_decode()`, `ife_tlv_meta_next()`, and `ife_tlv_meta_encode()`. Internal wire structs are `struct ifeheadr` for total metadata length and `struct meta_tlvhdr` for per-metadata TLVs.

## Control flow
`ife_encode()` ensures enough headroom with `skb_cow_head()`, snapshots the existing Ethernet header, pushes space for outer header plus IFE metadata header, copies the original Ethernet header to the new front, resets the MAC header, writes total metadata length, and returns a pointer to TLV data. `ife_decode()` validates enough linear data, reads the metadata length after the hard header, validates length, pulls the hard header plus IFE metadata from the skb, updates the MAC header, stores metadata payload length, and returns the TLV data pointer. TLV decoding first runs `__ife_tlv_meta_valid()` to verify header presence, minimum netlink-attribute length, alignment overflow, and end bounds; encoding writes type/length in network order, zeros aligned padding, and copies the value.

## State and persistence
All state is carried in the skb data buffer. The helpers do not keep global or per-net state and do not persist metadata outside packet memory.

## Dependencies and integration points
The implementation depends on skbuff headroom/pull helpers, netdevice hard-header length, Ethernet headers, netlink attribute alignment (`NLA_HDRLEN`, `NLA_ALIGN`, `nla_total_size()`), and the public `<net/ife.h>` constants such as `IFE_METAHDRLEN`.

## Risks and invariants
The caller must provide coherent `metalen` values and enough skb context, including `skb->dev`. Decode returns a pointer into skb data after mutating the skb with `__skb_pull()`, so callers must consume metadata before further modifications invalidate it. TLV helpers rely on network byte order and reject malformed or overflowing lengths; bypassing them risks out-of-bounds reads.

## Test signals
Tests should round-trip an skb through encode/decode, verify hard header preservation, validate metadata length accounting, exercise malformed TLVs with short lengths and overlong aligned lengths, and confirm exported helpers work for multiple TLVs using `ife_tlv_meta_next()`.
