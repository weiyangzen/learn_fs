# sources/distributed-fs/ceph-client/net/dsa/tag_rtl4_a.c

Purpose: Realtek 4-byte protocol A tag driver, currently for RTL8366RB-style tags with Realtek ethertype `0x8899` plus a 16-bit protocol/port word.

Important APIs/functions: `rtl4a_tag_xmit()` pads short frames, inserts the Realtek ethertype and RTL8366RB protocol bits, and encodes destination mask. `rtl4a_tag_rcv()` validates ethertype/protocol, decodes source port, strips the tag, and marks hardware-forwarded frames. `rtl4a_netdev_ops` registers `DSA_TAG_PROTO_RTL4_A`.

Control flow: TX adds an etype header after source MAC. RX passes through non-Realtek ethertype frames unchanged, rejects unknown Realtek protocols, maps source ports, and removes the tag for valid DSA frames.

State and persistence: stateless.

Dependencies and integration: uses Realtek ethertype constants, DSA tag helpers, padding helpers, and DSA conduit lookup.

Risks and test signals: pass-through behavior for non-Realtek frames is unusual and must match conduit filtering. Port extraction uses low 8 bits while the transmit side writes a mask; hardware interpretation should be tested. Tests should cover short packets, non-Realtek frames, unknown protocol, all supported ports, and bridge offload marking.
