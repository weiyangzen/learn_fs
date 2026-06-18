# sources/distributed-fs/ceph-client/net/dsa/tag_rzn1_a5psw.c

Purpose: DSA tag driver for Renesas RZ/N1 A5PSW switches. It inserts an 8-byte tag after the source MAC with a private `ETH_P_DSA_A5PSW` marker and control data.

Important APIs/types: `struct a5psw_tag` defines four big-endian 16-bit words. `a5psw_tag_xmit()` pads frames, inserts the marker, force-forward bit, and destination port mask. `a5psw_tag_rcv()` validates the marker, decodes source port, strips the tag, and marks hardware-forwarded frames. `a5psw_netdev_ops` registers `DSA_TAG_PROTO_RZN1_A5PSW`.

Control flow: TX ensures hardware minimum frame length, creates etype headroom, and fills the tag. RX bounds-checks, validates marker, maps source port, removes the etype header, and returns the skb.

State and persistence: stateless.

Dependencies and integration: uses Linux bitfield helpers, DSA etype helpers, padding, and conduit lookup. Bridge offload integration is via `dsa_default_offload_fwd_mark()`.

Risks and test signals: source-port decoding reads `ctrl_data` while TX writes destination data in `ctrl_data2_lo`; this reflects different RX/TX hardware semantics and needs hardware tests. Test marker rejection, padding, all source ports, and bridge forwarding behavior.
