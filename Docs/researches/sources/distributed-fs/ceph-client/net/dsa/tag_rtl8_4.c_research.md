# sources/distributed-fs/ceph-client/net/dsa/tag_rtl8_4.c

Purpose: Realtek 8-byte protocol 4 tag driver for RTL8365MB-like switches, supporting both in-frame etype tag `rtl8_4` and trailing tag `rtl8_4t`.

Important APIs/functions: `rtl8_4_write_tag()` builds the shared tag with Realtek ethertype, protocol 4, KEEP, LEARN_DIS, and destination port mask. `rtl8_4_read_tag()` validates and decodes ethertype, protocol, reason, and source port. `rtl8_4_tag_xmit/rcv()` handle in-frame tags; `rtl8_4t_tag_xmit/rcv()` handle tail tags. Two `dsa_device_ops` instances register `DSA_TAG_PROTO_RTL8_4` and `DSA_TAG_PROTO_RTL8_4T`.

Control flow: in-frame TX inserts an etype header; tail TX completes pending checksums before appending the tag. RX validates the tag, maps `skb->dev`, marks frames offload-forwarded unless the reason is TRAP, then strips the header or trims the trailer.

State and persistence: stateless.

Dependencies and integration: depends on Realtek ethertype constants, Linux bitfield helpers, DSA tag helpers, skb checksum/trimming helpers, and bridge offload marking.

Risks and test signals: risk areas are the two physical layouts, checksum correctness for tail tags, reason-code trap handling, and the shared Realtek ethertype colliding with other formats. Tests should cover both protocols, invalid ethertype/protocol, trap vs forward reason, tail checksum offload, and all valid source ports.
