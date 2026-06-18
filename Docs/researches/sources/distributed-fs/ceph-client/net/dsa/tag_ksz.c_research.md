# sources/distributed-fs/ceph-client/net/dsa/tag_ksz.c

Purpose: DSA tag driver family for Microchip KSZ8795, KSZ9477, KSZ9893, and LAN937x switches. It implements tail tags, priority bits, optional PTP timestamp tags, and deferred transmit for timestamped packets.

Important APIs/types: `struct ksz_tagger_private` embeds exported `ksz_tagger_data`, a state bitset, and a kthread worker. `ksz_connect()`/`ksz_disconnect()` allocate worker state and export `hwtstamp_set_state`. Common RX is in `ksz_common_rcv()`. Family-specific TX/RX functions include `ksz8795_xmit/rcv`, `ksz9477_xmit/rcv`, `ksz9893_xmit`, and `lan937x_xmit`.

Control flow: TX computes pending checksums before appending tail tags, encodes destination port masks, priority, link-local override flags, and optional timestamp/correction fields. PTP-capable variants may queue deferred work when an skb clone awaits egress timestamp handling. RX linearizes, decodes tail source port, optionally extracts a PTP timestamp, trims the trailer, maps to a user port, and marks hardware-forwarded frames.

State and persistence: private state lives in `ds->tagger_data` for the life of the tagger connection. `KSZ_HWTS_EN` controls whether TX timestamp tags are emitted. No persistence beyond runtime memory.

Dependencies and integration: uses Linux PTP classification/correction helpers, Microchip DSA skb control blocks, DSA tagger-data callback contracts, kthread workers, and DSA conduit mapping. Switch drivers rely on the exported tagger-data function pointers.

Risks and test signals: high-risk areas are timestamp tag length accounting, deferred-xmit reference handling, checksum handling for trailing tags, and different family bit layouts. Tests should cover each registered protocol, PTP enabled/disabled paths, cloned timestamped skb deferral, link-local override, priority mapping, and RX timestamp extraction.
