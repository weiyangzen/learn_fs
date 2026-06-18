# sources/distributed-fs/ceph-client/net/dsa/tag_qca.c

Purpose: DSA tag driver for Qualcomm Atheros QCA8K switches. It uses a QCA-specific etype header and also handles management/MIB packets delivered over Ethernet.

Important APIs/types: `qca_tag_xmit()` builds the transmit tag with version, from-CPU bit, and destination port mask. `qca_tag_rcv()` validates version, dispatches register-ack and MIB packet types to callbacks in `struct qca_tagger_data`, or maps normal source-port frames. `qca_tag_connect()`/`disconnect()` allocate/free tagger data. `qca_netdev_ops` registers `DSA_TAG_PROTO_QCA`.

Control flow: TX inserts `QCA_HDR_LEN` after source MAC. RX parses the header; management read/write ACKs and MIB autocast packets are consumed and not delivered to the network stack. Normal frames have the tag stripped and `skb->dev` assigned.

State and persistence: runtime callback state is held in `ds->tagger_data`; no persistent storage.

Dependencies and integration: depends on `linux/dsa/tag_qca.h`, QCA switch-driver callbacks, etype header helpers, and DSA conduit mapping. The conduit is promiscuous because special management frames may not target a user MAC.

Risks and test signals: management packet dispatch can accidentally consume data if type/version parsing is wrong. Tests should cover normal data RX/TX, register ACK callback, MIB autocast callback, malformed versions, unknown ports, and connect/disconnect cleanup.
