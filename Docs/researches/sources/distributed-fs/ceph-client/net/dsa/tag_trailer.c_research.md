# sources/distributed-fs/ceph-client/net/dsa/tag_trailer.c

Purpose: legacy 4-byte trailer tag driver. It appends a fixed-format trailer carrying destination/source port information.

Important APIs/functions: `trailer_xmit()` appends bytes `0x80`, destination mask, `0x10`, `0x00`. `trailer_rcv()` linearizes the skb, validates the trailer signature, decodes source port, maps the user device, and trims the trailer. `trailer_netdev_ops` registers `DSA_TAG_PROTO_TRAILER`.

Control flow: TX simply appends tail bytes. RX checks exact bit patterns before trusting the source port, then removes the trailer with checksum adjustment.

State and persistence: stateless.

Dependencies and integration: uses DSA port-mask and conduit lookup helpers plus skb tail operations.

Risks and test signals: no offload-forward mark is set, so bridge behavior must match the hardware protocol. Trailer validation and linearization can drop fragmented/nonlinear frames. Tests should cover valid signature, invalid signature, all source ports, nonlinear skbs, and bridge forwarding.
