# sources/distributed-fs/ceph-client/net/dsa/tag_ocelot.c

Purpose: DSA tag driver for Ocelot/Seville switches using NPI injection/extraction frame headers plus a short prefix accepted by the conduit RX filter.

Important APIs/functions: `ocelot_xmit_common()` builds the injection header, populating bypass, source, QoS, VLAN TCI, tag type, and optional PTP rewrite operation. `ocelot_xmit()` and `seville_xmit()` write family-specific destination fields. `ocelot_rcv()` removes prefix/extraction headers, decodes source port, QoS, VLAN classification, and timestamp low bits. Ops register `DSA_TAG_PROTO_OCELOT` and `DSA_TAG_PROTO_SEVILLE`.

Control flow: TX derives VLAN/tag-type metadata through `ocelot_xmit_get_vlan_info()`, pushes `OCELOT_TAG_LEN` plus short prefix, then sets destination mask. RX repositions skb data from the conduit-consumed state, discards prefix and extraction header, updates checksum, maps the source port, marks offload-forwarded frames, restores priority, stores timestamp data in the skb control block, and may replace an in-frame VLAN tag with the classified VLAN from the extraction header.

State and persistence: stateless in the tagger; timestamp low bits live transiently in `OCELOT_SKB_CB`.

Dependencies and integration: depends on `linux/dsa/ocelot.h`, Ocelot IFH helpers, VLAN bridge state, PTP rewrite helpers, and DSA user mapping. The conduit is put in promiscuous mode.

Risks and test signals: skb pointer choreography is fragile. VLAN replacement must only happen for VLAN-filtering ports. Tests should cover Ocelot and Seville destinations, PTP rewrite, VLAN-unaware and VLAN-aware RX, reflected CPU-port frames, priority mapping, and checksum integrity.
