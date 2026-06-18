# sources/distributed-fs/ceph-client/include/net/gso.h

Purpose: declares Generic Segmentation Offload helpers and per-skb GSO control metadata for splitting large skbs, including tunneled packets.

Important APIs/types: `struct skb_gso_cb` is stored at offset 32 in `skb->cb` and tracks MAC/data offset, encapsulation level, checksum accumulator, and checksum start. `skb_tnl_header_len()` computes tunnel header length from MAC offsets. `gso_pskb_expand_head()` expands headroom and adjusts stored offsets. `gso_reset_checksum()` records checksum state unless remote checksum offload is active. `gso_make_checksum()` builds a segment checksum from transport header to stored checksum start. Segmentation entry points include `__skb_gso_segment()`, `skb_gso_segment()`, Ethernet/MAC segment helpers, length validators, and `skb_gso_error_unwind()`.

Control flow and state: segmentation paths initialize control block state, possibly expand headroom, segment according to features, validate resulting lengths, and unwind skb headers on errors. State is transient in skb control block and checksum fields.

Dependencies and integration: depends on skbuff and netdev feature flags. It integrates with TCP/UDP segmentation, GRE/Geneve/GUE tunnels, checksum offload, and device transmit feature negotiation.

Risks: control-block offset overlap with other skb users, headroom expansion offset adjustment, and remote checksum exceptions are critical. Tests should cover tunnel and non-tunnel GSO, partial checksums, remcsum, segmentation failure unwind, MTU/mac-length validation, and devices with limited feature flags.
