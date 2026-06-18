# sources/distributed-fs/ceph-client/net/dsa/tag_hellcreek.c

Purpose: tail-tag driver for Hirschmann Hellcreek TSN switches. It appends a 1-byte destination mask on TX and consumes a 1-byte source-port trailer on RX.

Important APIs/functions: `hellcreek_xmit()` computes pending checksums before appending the trailer. `hellcreek_rcv()` reads the trailer, maps the low two bits to a user port, trims the skb, and marks hardware-forwarded frames. `hellcreek_netdev_ops` advertises 1 byte of tailroom.

Control flow: TX must call `skb_checksum_help()` before modifying the tail because the switch strips the trailer before the packet reaches the wire. RX expects trailer bytes at `skb_tail_pointer() - 1`, then uses `pskb_trim_rcsum()` to remove them.

State and persistence: no private state.

Dependencies and integration: depends on `dsa_xmit_port_mask()`, `dsa_conduit_find_user()`, checksum helpers, and DSA tag registration. It integrates with bridge offload through `dsa_default_offload_fwd_mark()`.

Risks and test signals: risks are checksum corruption for offloaded checksums, invalid source-port decoding, and missing tailroom. Tests should cover CHECKSUM_PARTIAL traffic, all port masks, bridge forwarding, and short/truncated RX frames.
