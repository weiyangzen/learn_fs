# sources/distributed-fs/ceph-client/net/dsa/tag_sja1105.c

Purpose: DSA tag driver for NXP SJA1105 and SJA1110 switches. SJA1105 primarily uses tag_8021q plus special handling for link-local management and metadata frames; SJA1110 adds in-band control extensions, metadata timestamp frames, and optional trailers.

Important APIs/types: `struct sja1105_tagger_private` embeds exported tagger data, a metadata spinlock, buffered timestampable skb, and xmit worker. Helpers include `sja1105_is_link_local()`, `sja1105_meta_unpack()`, `sja1105_defer_xmit()`, `sja1105_xmit_tpid()`, `sja1105_imprecise_xmit()`, `sja1105_pvid_tag_control_pkt()`, `sja1105_rcv_meta_state_machine()`, `sja1110_rcv_meta()`, and `sja1110_rcv_inband_control_extension()`. Ops register SJA1105 and SJA1110 variants.

Control flow: normal data TX inserts a tag_8021q VLAN with PCP and standalone VID. Bridge-offloaded traffic may use an imprecise bridge VID or pass VLAN-aware bridge traffic unchanged. Link-local control traffic is PVID-tagged and either deferred to driver work (SJA1105) or wrapped in an SJA1110 in-band control header/trailer. RX decodes management source info, tag_8021q VLANs, metadata follow-up frames, SJA1110 timestamp trailers, source device/port, and host-only state before marking offload-forwarded packets.

State and persistence: per-switch runtime state in `ds->tagger_data`; metadata pairing uses `stampable_skb` under `meta_lock`, and deferred TX uses a kthread worker. No disk persistence.

Dependencies and integration: depends on `linux/dsa/sja1105.h`, tag_8021q helpers, packing helpers, bridge VLAN APIs, PTP/timestamp control blocks, and switch-driver callbacks in tagger data.

Risks and test signals: this is high-risk because it contains a state machine pairing metadata with data frames without unique IDs. Risks include stale buffered skbs, wrong port on metadata, SJA1110 trailer position/trim errors, deferred-xmit reference leaks, and bridge VID imprecision. Tests should cover normal data, link-local management, TX/RX timestamps, metadata loss/reorder, VLAN-aware and VLAN-unaware bridges, SJA1110 host-only frames, and worker teardown.
