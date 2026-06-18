# sources/distributed-fs/ceph-client/net/dsa/tag_gswip.c

Purpose: DSA PMAC tag driver for Intel/Lantiq GSWIP V2.0 switches. It uses a 4-byte TX header and an 8-byte RX header.

Important APIs/functions: `gswip_tag_xmit()` prepends the TX header, sets CPU source ID, ELAN destination group, and port-map fields. `gswip_tag_rcv()` reads the source physical port ID from the RX header and removes the tag. `gswip_netdev_ops` registers `DSA_TAG_PROTO_GSWIP`.

Control flow: TX writes a port map from `dsa_xmit_port_mask()` and enables DPID/port-map selection. RX ensures enough data, reads the tag relative to `skb->data - ETH_HLEN`, extracts source port, maps `skb->dev`, and pulls the RX header.

State and persistence: stateless; packet tags carry all routing metadata.

Dependencies and integration: uses bitfield macros, skb helpers, net/dsa, and the DSA conduit-to-user lookup. Needed headroom is set to the RX header length.

Risks and test signals: the unusual RX tag pointer offset is sensitive to conduit RX positioning. No offload forward mark is set, so bridge duplicate-forwarding behavior should be verified. Tests should cover all source ports, multicast/broadcast port masks, undersized RX packets, and expected skb data alignment.
