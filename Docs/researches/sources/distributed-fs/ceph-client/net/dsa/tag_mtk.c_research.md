# sources/distributed-fs/ceph-client/net/dsa/tag_mtk.c

Purpose: DSA tag driver for Mediatek switches using a 4-byte special tag after the source MAC. It supports combined handling with existing 802.1Q or 802.1ad headers.

Important APIs/functions: `mtk_tag_xmit()` selects tag type based on `skb->protocol`, encodes destination port mask, and maps the skb queue to the physical port. `mtk_tag_rcv()` strips the tag, extracts the source port, maps the user device, and marks hardware-forwarded frames. `mtk_netdev_ops` registers `DSA_TAG_PROTO_MTK`.

Control flow: untagged TX packets receive new headroom and an inserted tag; VLAN-tagged packets reuse the existing tag position so hardware can parse both special tag and VLAN table information. RX reads the tag from the etype-header position and strips it with checksum correction.

State and persistence: stateless.

Dependencies and integration: depends on VLAN ethertypes, DSA tag helpers, and queue/traffic-class integration. It integrates with bridge offload through `dsa_default_offload_fwd_mark()`.

Risks and test signals: VLAN-combined special tag handling is the main compatibility risk. Tests should cover untagged, 802.1Q, and 802.1ad TX, queue mapping, source port decode, and bridge flooding/forwarding behavior.
