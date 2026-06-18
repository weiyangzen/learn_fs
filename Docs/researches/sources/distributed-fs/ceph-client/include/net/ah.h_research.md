# sources/distributed-fs/ceph-client/include/net/ah.h

## Purpose

`ah.h` provides the small shared IPsec Authentication Header support contract used by IPv4/IPv6 AH implementations. It defines AH transform data and a helper to locate the AH header in an skb.

## Important APIs, Types, and Functions

`struct ah_data` stores full and truncated Integrity Check Value lengths plus the `struct crypto_ahash *` transform used to compute or verify authentication data. `ip_auth_hdr()` casts `skb_transport_header(skb)` to `struct ip_auth_hdr *`, relying on callers to have already positioned the transport header at the AH header.

## Control Flow

This header has no independent control flow. AH input/output code prepares the skb transport offset, retrieves `ip_auth_hdr()`, and uses `ah_data` from xfrm state to authenticate packet bytes through the crypto ahash API.

## State and Persistence Behavior

No persistent state is defined here. `ah_data` is per-transform runtime state owned by the xfrm/IPsec stack and freed with the transform state.

## Dependencies and Integration Points

It depends on `linux/skbuff.h`, the crypto ahash forward declaration, and the UAPI/internal IP authentication header definition. It integrates with xfrm state, IPv4/IPv6 AH packet processing, and the crypto API.

## Risks and Edge Cases

`ip_auth_hdr()` performs a raw cast with no length validation; callers must ensure skb header offsets and linear access are valid. Incorrect ICV truncation lengths or ahash allocation failures are handled outside this header but are central to AH correctness.

## Test Signals

Validate AH packets with full/truncated ICVs, malformed short skbs, wrong transport header offsets, crypto transform allocation failures, and IPv4/IPv6 xfrm state setup with multiple algorithms.
