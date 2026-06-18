# sources/distributed-fs/ceph-client/net/dsa/tag_yt921x.c

Purpose: DSA tag driver for Motorcomm YT921x extended CPU-port tagging. The tag is 8 bytes and includes a configurable-looking ethertype, VLAN word, RX/TX port fields, priority, and packet code.

Important APIs/types: `enum yt921x_tag_code` documents known forwarding/copy/unknown-unicast/multicast codes. `yt921x_tag_xmit()` inserts `ETH_P_YT921X`, sets forward code, priority, destination port mask, and validity bits. `yt921x_tag_rcv()` validates ethertype and RX port validity, decodes source port and priority, classifies code for offload-forward marking, strips the tag, and returns the skb. `yt921x_netdev_ops` registers `DSA_TAG_PROTO_YT921X`.

Control flow: TX inserts an etype header and writes four 16-bit words. RX rejects malformed tags, maps source port, copies tag priority into `skb->priority`, marks forwarded/copy cases as hardware-forwarded, leaves unknown unicast/multicast unmarked for software switching, and warns on unknown codes.

State and persistence: stateless.

Dependencies and integration: uses DSA tag helpers, bitfield macros, Motorcomm ethertype, and bridge offload marking.

Risks and test signals: hardware code semantics are incomplete, and the comment notes unknown copy/trap distinction. Tests should cover known code values, unknown codes, priority propagation, invalid RX port validity, all source ports, and software bridge behavior for unknown unicast/multicast.
