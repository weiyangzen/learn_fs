# sources/distributed-fs/ceph-client/net/dsa/tag_dsa.c

Purpose: implements regular Marvell DSA and Ethertype DSA packet formats used by mv88e6xxx-style switches. It converts between Ethernet/802.1Q frames and 4-byte DSA metadata, with an optional 4-byte EDSA prefix.

Important APIs/types: enums `dsa_cmd` and `dsa_code` describe switch commands and TO_CPU reasons. `dsa_xmit_ll()` and `dsa_rcv_ll()` contain shared encode/decode logic. Thin wrappers register `dsa_netdev_ops` for `DSA_TAG_PROTO_DSA` and `edsa_netdev_ops` for `DSA_TAG_PROTO_EDSA`.

Control flow: TX chooses `FROM_CPU` for direct port sends or `FORWARD` for bridge offload, encodes device/port, and either converts an existing 802.1Q tag into DSA metadata or inserts a new DSA header with standalone/bridged VID. EDSA additionally writes the ethertype prefix. RX parses command and reason, rejects unsupported/reserved cases, handles trunk/LAG source encoding, maps to the user device or LAG, marks hardware-forwarded frames except traps, and converts tagged DSA back into 802.1Q form.

State and persistence: stateless aside from packet transformation. It consults runtime DSA tree, bridge, and LAG state but does not own it.

Dependencies and integration: depends on mv88e6xxx VID constants, DSA tree/LAG helpers, bridge VLAN state, checksum helpers, and the generic DSA tag-driver framework.

Risks and test signals: risks include DSA-to-802.1Q checksum adjustment mistakes, trap vs forwarded classification errors, bridge offload source-device encoding, and LAG/trunk delivery to non-DSA upper devices. Tests should include tagged and untagged traffic, EDSA prefix handling, traps, mirrored frames, policy/reserved codes, and LAG offload RX.
