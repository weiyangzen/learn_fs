# Research: sources/distributed-fs/ceph-client/net/ceph/decode.c

## Purpose

`decode.c` centralizes Ceph entity address decoding and encoding for the kernel client. It handles both legacy address encodings and versioned `entity_addr_t` / `entity_addrvec_t` encodings used by msgr2-aware peers. The key job is to safely decode wire-format monitor and peer addresses into `struct ceph_entity_addr`, select the address type appropriate for msgr1 or msgr2, and encode the client's own address back into the modern versioned form.

## Important APIs, Types, and Functions

Public functions:

- `ceph_decode_entity_addr(void **p, void *end, struct ceph_entity_addr *addr)` reads a marker byte and dispatches to versioned marker `1` or legacy marker `0` decoding.
- `ceph_decode_entity_addrvec(void **p, void *end, bool msgr2, struct ceph_entity_addr *addr)` decodes marker `2`, walks all embedded addresses, and selects exactly one address matching either `CEPH_ENTITY_ADDR_TYPE_MSGR2` or `CEPH_ENTITY_ADDR_TYPE_LEGACY`.
- `ceph_entity_addr_encoding_len(const struct ceph_entity_addr *addr)` computes the modern encoded size for the address family.
- `ceph_encode_entity_addr(void **p, const struct ceph_entity_addr *addr)` emits marker `1`, an encoding block, address type, nonce, sockaddr length, family, and sockaddr data.

Private helpers:

- `ceph_decode_entity_addr_versioned()` uses `ceph_start_decoding()` to respect a bounded structured block and skips unknown tail fields by advancing to `struct_end`.
- `ceph_decode_entity_addr_legacy()` handles the old layout, maps old clients' `TYPE_NONE` style to `CEPH_ENTITY_ADDR_TYPE_LEGACY`, and converts sockaddr family from big-endian legacy wire order.
- `get_sockaddr_encoding_len()` selects IPv4, IPv6, or generic sockaddr storage size for encoding.

## Control Flow

The decode paths all advance a caller-owned buffer pointer and validate against an end pointer through Ceph safe-decode macros. For a single address, `ceph_decode_entity_addr()` consumes the marker, then either decodes a structured block or the legacy fields. The versioned path validates `addr_len` against the storage size, zeroes the destination sockaddr, copies only the encoded length, fixes the sockaddr family endian, and skips any future fields in the encoding block.

For an address vector, `ceph_decode_entity_addrvec()` requires marker `2`, decodes the count, then decodes each member using the single-address routine. It picks the type required by the caller's messenger mode and rejects duplicate matches. A vector with no entries, or a single all-zero decoded address, is treated as an empty address slot and succeeds without filling a meaningful target. A non-empty vector with no matching address returns `-ENOENT`.

Encoding is the inverse modern path: determine sockaddr length from the address family, write the marker and block header, copy `type` and `nonce`, write `addr_len`, encode the family as little-endian, and copy the remainder of `sockaddr_storage.__data`.

## State and Persistence Behavior

There is no persistent state and no allocation. The functions mutate only the passed buffer pointer and destination address. Error handling returns negative errno values and leaves the buffer pointer wherever the safe-decode macro stopped; callers should treat failure as fatal for the current message or map decode.

## Dependencies and Integration Points

The file depends on Ceph decode helpers from `linux/ceph/decode.h`, address structures from `linux/ceph/messenger.h`, and kernel sockaddr definitions. `ceph_decode_entity_addrvec()` is used by monitor map decoding in `mon_client.c` and by msgr2 session identity processing in `messenger_v2.c`. `ceph_encode_entity_addr()` is used by msgr2 hello/client-ident/reconnect frame preparation.

## Risks and Edge Cases

Address selection is strict: duplicate matching address types are rejected to avoid ambiguous peer endpoints. Empty vectors are tolerated for unused OSD slots, and a weird single zeroed address is also treated as empty. The legacy path intentionally rewrites type to `LEGACY` for forward compatibility, which is important for clients that never supported address type metadata. Versioned decode validates `addr_len`, but encoding uses the current sockaddr family, so callers must ensure the address family is set consistently before encoding. Endian handling differs between legacy and modern layouts, making regression tests around family conversion valuable.

## Test Signals

Good test signals include decoding legacy IPv4/IPv6 addresses, versioned IPv4/IPv6 addresses, msgr2 and legacy address vectors, duplicate matching vector entries, no-match vectors, zero-entry vectors, truncated buffers at each field, oversized `addr_len`, and encode/decode round trips. Integration tests should cover monmap decoding in both msgr1 and msgr2 modes and msgr2 handshake identity validation with an address vector containing both legacy and msgr2 addresses.
