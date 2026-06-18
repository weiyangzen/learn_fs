# sources/distributed-fs/ceph-client/net/dsa/tag_xrs700x.c

Purpose: DSA tail-tag driver for XRS700x switches using a 1-byte port mask trailer.

Important APIs/functions: `xrs700x_xmit()` appends destination mask. `xrs700x_rcv()` reads the trailer, uses `ffs()` to convert a one-hot mask to source port, trims the trailer, maps the user device, and marks hardware-forwarded frames. `xrs700x_netdev_ops` registers `DSA_TAG_PROTO_XRS700X`.

Control flow: TX appends one byte. RX trusts the last byte as source mask and rejects zero masks because `ffs(0) - 1` is negative.

State and persistence: stateless.

Dependencies and integration: depends on bit operations, DSA port-mask/conduit helpers, and skb trim helpers.

Risks and test signals: multi-bit source masks choose the lowest set bit; tests should verify hardware always emits one-hot masks. Also test zero masks, all ports, tailroom, and bridge offload marking.
