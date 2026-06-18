# sources/distributed-fs/ceph-client/net/dsa/tag_ar9331.c

Purpose: DSA tag driver for the Atheros AR9331 built-in switch, using a 2-byte little-endian header placed at the front of the frame.

Important APIs/types: `ar9331_tag_xmit()` pushes `AR9331_HDR_LEN`, fills version, reserved bits, `FROM_CPU`, and destination port. `ar9331_tag_rcv()` validates version and rejects frames still marked from CPU, then maps the source port with `dsa_conduit_find_user()`. `ar9331_netdev_ops` registers protocol `DSA_TAG_PROTO_AR9331` with 2 bytes of headroom.

Control flow: TX derives the target port from `dsa_user_to_port(dev)` and writes bitfields with `FIELD_PREP`. RX pulls enough header, decodes fields, removes the header with `skb_pull_rcsum()`, assigns `skb->dev`, and returns the skb to DSA.

State and persistence: no private state or persistent data. All information is encoded in each packet.

Dependencies and integration: uses Linux bitfield helpers, ethernet helpers, `tag.h`, and DSA user/conduit mapping. Module aliasing makes it selectable by switch drivers declaring the AR9331 protocol.

Risks and test signals: header version and reserved-bit expectations are hardware-sensitive; wrong values drop all traffic. RX does not set `offload_fwd_mark`, so bridge behavior should be verified. Tests should cover malformed version, `FROM_CPU` reflection, all valid ports, and minimum-size frames.
