## sources/distributed-fs/ceph-client/net/ieee802154/header_ops.c

Purpose: IEEE 802.15.4 MAC header serialization, parsing, peeking, and payload-size calculation. It is shared by mac802154, 6LoWPAN, socket, and management paths needing to build or inspect frame control/address/security headers.

Important APIs/types/functions: exported functions include `ieee802154_hdr_push()`, `ieee802154_mac_cmd_push()`, `ieee802154_beacon_push()`, `ieee802154_hdr_pull()`, `ieee802154_mac_cmd_pl_pull()`, `ieee802154_hdr_peek_addrs()`, `ieee802154_hdr_peek()`, and `ieee802154_max_payload()`. Internal helpers push/pull addresses and security headers, compute address lengths, minimum header length, security header length, and intra-PAN source PAN elision.

Control flow and state: push builds a temporary header buffer from frame control, sequence, destination, source, and optional security header, then prepends it to the skb. Pull validates minimum data with `pskb_may_pull()`, copies frame control/seq, parses addresses, optionally parses security header, and advances skb data. Peek variants inspect from `skb_mac_header()` without pulling. `ieee802154_max_payload()` subtracts header, auth tag, and FCS sizes from `IEEE802154_MTU`.

Dependencies and integration points: depends on `linux/ieee802154.h`, mac802154, IEEE 802.15.4 netdev types, skb APIs, and security-control helpers. 6LoWPAN uses `peek_addrs()` for decompression and `max_payload()` for fragmentation.

Risks: packed bitfield/frame-control layout and memcpy use must match on-wire endian expectations. Security header indexing trusts key-id modes after validation; out-of-range modes could index length arrays if callers bypass normal parsing. Beacon push does not support pending address lists and returns `-EOPNOTSUPP` after appending the fixed beacon header.

Test signals: round-trip push/pull for short/long/no addresses, intra-PAN elision, all security key-id modes, truncated skb rejection, peek without pull, max-payload calculations with security auth tags, MAC command and beacon construction.
