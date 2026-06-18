# subset-b-006191 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_8021q.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_8021q.c

Purpose: provides shared primitives for DSA taggers that use synthetic 802.1Q VLAN IDs as the switch tag. It is not a complete tagger by itself; taggers such as SJA1105, Ocelot 802.1Q, and VSC73XX call it to encode target ports on TX and decode source ports, switch IDs, and virtual bridge IDs on RX.

Important APIs and types: `dsa_tag_8021q_bridge_vid()`, `dsa_tag_8021q_standalone_vid()`, `dsa_8021q_rx_switch_id()`, `dsa_8021q_rx_source_port()`, `vid_is_dsa_8021q()`, `dsa_tag_8021q_register()`, `dsa_tag_8021q_unregister()`, `dsa_8021q_xmit()`, `dsa_8021q_rcv()`, and `dsa_tag_8021q_find_user()` are exported. `struct dsa_8021q_context` stores the owning switch, installed VLAN list, and RX filter TPID. `struct dsa_tag_8021q_vlan` tracks CPU/DSA-port VLAN refcounts.

Control flow: TX calls `dsa_8021q_xmit()` to insert a VLAN tag. RX calls `dsa_8021q_rcv()`, which accepts either hardware-accelerated VLAN metadata or an in-frame VLAN header, validates the reserved VID bits, decodes source port, switch ID, VBID, strips the tag, and preserves packet priority. Registration allocates context, initializes per-user standalone VIDs, and adds conduit RX filters; unregister tears all of that down. Bridge join/leave replace standalone VIDs with bridge-domain VIDs for VLAN-unaware forwarding.

State and persistence: all state is in memory under `ds->tag_8021q_ctx`; CPU and DSA port VLANs are refcounted because many user ports can require the same shared-port programming. No on-disk persistence exists.

Dependencies and integration: depends on DSA port/switch helpers, notifier payload `dsa_notifier_tag_8021q_vlan_info`, switch driver callbacks `tag_8021q_vlan_add/del`, Linux VLAN helpers, and bridge state. It integrates with DSA broadcast notifier paths and with taggers that need an imprecise bridge-domain fallback.

Risks and test signals: main risks are incorrect VID bitfield encoding, refcount imbalance on shared ports, bridge VID replacement failures, and skb VLAN metadata/header handling regressions. Useful tests include VLAN-aware and VLAN-unaware bridge joins/leaves, standalone port RX source decoding, cascaded switch IDs, repeated add/delete of shared CPU VLANs, and packets with non-DSA 802.1Q tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_8021q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_8021q.h -->
# sources/distributed-fs/ceph-client/net/dsa/tag_8021q.h

Purpose: public local header for the tag_8021q helper module. It exposes the skb TX/RX helpers, source-device lookup helper, and switch-level VLAN add/delete hooks used by DSA taggers and core switch notifier code.

Important APIs/types: declares `dsa_8021q_xmit()`, `dsa_8021q_rcv()`, `dsa_tag_8021q_find_user()`, `dsa_switch_tag_8021q_vlan_add()`, and `dsa_switch_tag_8021q_vlan_del()`. It forward-declares `struct sk_buff`, `struct net_device`, `struct dsa_switch`, and `struct dsa_notifier_tag_8021q_vlan_info`.

Control flow: consumers include this header to insert or decode synthetic VLAN tags and to propagate VLAN programming requests across switches. The declarations separate generic tag_8021q behavior from hardware-specific tagger files.

State and persistence: the header owns no runtime state. State is created by `tag_8021q.c` and stored through DSA switch fields.

Dependencies and integration: integrates with local DSA headers and Linux skb/netdev types. It is a contract between tagger modules and the DSA core code that programs switch VLANs.

Risks and test signals: risks are API signature drift between the header and implementation, and callers misinitializing `source_port`, `switch_id`, `vbid`, or `vid` before RX decode. Compile coverage of all tag_8021q consumers and runtime tests with VLAN and non-VLAN frames are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_8021q.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_ar9331.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_ar9331.c

Purpose: DSA tag driver for the Atheros AR9331 built-in switch, using a 2-byte little-endian header placed at the front of the frame.

Important APIs/types: `ar9331_tag_xmit()` pushes `AR9331_HDR_LEN`, fills version, reserved bits, `FROM_CPU`, and destination port. `ar9331_tag_rcv()` validates version and rejects frames still marked from CPU, then maps the source port with `dsa_conduit_find_user()`. `ar9331_netdev_ops` registers protocol `DSA_TAG_PROTO_AR9331` with 2 bytes of headroom.

Control flow: TX derives the target port from `dsa_user_to_port(dev)` and writes bitfields with `FIELD_PREP`. RX pulls enough header, decodes fields, removes the header with `skb_pull_rcsum()`, assigns `skb->dev`, and returns the skb to DSA.

State and persistence: no private state or persistent data. All information is encoded in each packet.

Dependencies and integration: uses Linux bitfield helpers, ethernet helpers, `tag.h`, and DSA user/conduit mapping. Module aliasing makes it selectable by switch drivers declaring the AR9331 protocol.

Risks and test signals: header version and reserved-bit expectations are hardware-sensitive; wrong values drop all traffic. RX does not set `offload_fwd_mark`, so bridge behavior should be verified. Tests should cover malformed version, `FROM_CPU` reflection, all valid ports, and minimum-size frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_ar9331.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_brcm.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_brcm.c

Purpose: implements multiple Broadcom DSA tag formats: modern 4-byte in-frame tag, legacy 6-byte tag, legacy tag with transmitted FCS, and prepended 4-byte tag. The formats target Broadcom switch families with different CPU-port parsing rules.

Important APIs/functions: shared helpers `brcm_tag_xmit_ll()` and `brcm_tag_rcv_ll()` build/parse the modern tag at configurable offsets. Legacy paths are `brcm_leg_tag_xmit()`, `brcm_leg_fcs_tag_xmit()`, and `brcm_leg_tag_rcv()`. Prepend paths wrap the shared helpers. Registered ops include `brcm_netdev_ops`, `brcm_legacy_netdev_ops`, `brcm_legacy_fcs_netdev_ops`, and `brcm_prepend_netdev_ops`, conditionally compiled by Kconfig.

Control flow: TX pads frames to hardware minimum lengths, inserts tags either after source MAC or before the frame, encodes destination port masks and queue mappings, and optionally appends a calculated FCS. RX validates opcodes/reason codes, decodes source port, strips tags with checksum updates, handles legacy VID 0 stripping, maps the user port, and marks non-link-local frames as hardware-forwarded.

State and persistence: no module-owned state. Packet metadata is transient, with queue mapping rewritten for Broadcom port queues.

Dependencies and integration: depends on Broadcom tag definitions, skb padding/checksum helpers, `dsa_xmit_port_mask()`, `dsa_strip_etype_header()`, and DSA tag driver registration. It integrates with bridge offload by setting `dsa_default_offload_fwd_mark()` for non-link-local RX.

Risks and test signals: risks include unaligned tag access, wrong minimum padding, FCS calculation mistakes, incorrect legacy VLAN stripping, and reserved reason-code handling. Tests should cover each enabled protocol variant, short packets, VLAN-tagged legacy RX, link-local traps, and queue/port mask selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_brcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_dsa.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_dsa.c

Purpose: implements regular Marvell DSA and Ethertype DSA packet formats used by mv88e6xxx-style switches. It converts between Ethernet/802.1Q frames and 4-byte DSA metadata, with an optional 4-byte EDSA prefix.

Important APIs/types: enums `dsa_cmd` and `dsa_code` describe switch commands and TO_CPU reasons. `dsa_xmit_ll()` and `dsa_rcv_ll()` contain shared encode/decode logic. Thin wrappers register `dsa_netdev_ops` for `DSA_TAG_PROTO_DSA` and `edsa_netdev_ops` for `DSA_TAG_PROTO_EDSA`.

Control flow: TX chooses `FROM_CPU` for direct port sends or `FORWARD` for bridge offload, encodes device/port, and either converts an existing 802.1Q tag into DSA metadata or inserts a new DSA header with standalone/bridged VID. EDSA additionally writes the ethertype prefix. RX parses command and reason, rejects unsupported/reserved cases, handles trunk/LAG source encoding, maps to the user device or LAG, marks hardware-forwarded frames except traps, and converts tagged DSA back into 802.1Q form.

State and persistence: stateless aside from packet transformation. It consults runtime DSA tree, bridge, and LAG state but does not own it.

Dependencies and integration: depends on mv88e6xxx VID constants, DSA tree/LAG helpers, bridge VLAN state, checksum helpers, and the generic DSA tag-driver framework.

Risks and test signals: risks include DSA-to-802.1Q checksum adjustment mistakes, trap vs forwarded classification errors, bridge offload source-device encoding, and LAG/trunk delivery to non-DSA upper devices. Tests should include tagged and untagged traffic, EDSA prefix handling, traps, mirrored frames, policy/reserved codes, and LAG offload RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_dsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_gswip.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_gswip.c

Purpose: DSA PMAC tag driver for Intel/Lantiq GSWIP V2.0 switches. It uses a 4-byte TX header and an 8-byte RX header.

Important APIs/functions: `gswip_tag_xmit()` prepends the TX header, sets CPU source ID, ELAN destination group, and port-map fields. `gswip_tag_rcv()` reads the source physical port ID from the RX header and removes the tag. `gswip_netdev_ops` registers `DSA_TAG_PROTO_GSWIP`.

Control flow: TX writes a port map from `dsa_xmit_port_mask()` and enables DPID/port-map selection. RX ensures enough data, reads the tag relative to `skb->data - ETH_HLEN`, extracts source port, maps `skb->dev`, and pulls the RX header.

State and persistence: stateless; packet tags carry all routing metadata.

Dependencies and integration: uses bitfield macros, skb helpers, net/dsa, and the DSA conduit-to-user lookup. Needed headroom is set to the RX header length.

Risks and test signals: the unusual RX tag pointer offset is sensitive to conduit RX positioning. No offload forward mark is set, so bridge duplicate-forwarding behavior should be verified. Tests should cover all source ports, multicast/broadcast port masks, undersized RX packets, and expected skb data alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_gswip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_hellcreek.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_hellcreek.c

Purpose: tail-tag driver for Hirschmann Hellcreek TSN switches. It appends a 1-byte destination mask on TX and consumes a 1-byte source-port trailer on RX.

Important APIs/functions: `hellcreek_xmit()` computes pending checksums before appending the trailer. `hellcreek_rcv()` reads the trailer, maps the low two bits to a user port, trims the skb, and marks hardware-forwarded frames. `hellcreek_netdev_ops` advertises 1 byte of tailroom.

Control flow: TX must call `skb_checksum_help()` before modifying the tail because the switch strips the trailer before the packet reaches the wire. RX expects trailer bytes at `skb_tail_pointer() - 1`, then uses `pskb_trim_rcsum()` to remove them.

State and persistence: no private state.

Dependencies and integration: depends on `dsa_xmit_port_mask()`, `dsa_conduit_find_user()`, checksum helpers, and DSA tag registration. It integrates with bridge offload through `dsa_default_offload_fwd_mark()`.

Risks and test signals: risks are checksum corruption for offloaded checksums, invalid source-port decoding, and missing tailroom. Tests should cover CHECKSUM_PARTIAL traffic, all port masks, bridge forwarding, and short/truncated RX frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_hellcreek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_ksz.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_ksz.c

Purpose: DSA tag driver family for Microchip KSZ8795, KSZ9477, KSZ9893, and LAN937x switches. It implements tail tags, priority bits, optional PTP timestamp tags, and deferred transmit for timestamped packets.

Important APIs/types: `struct ksz_tagger_private` embeds exported `ksz_tagger_data`, a state bitset, and a kthread worker. `ksz_connect()`/`ksz_disconnect()` allocate worker state and export `hwtstamp_set_state`. Common RX is in `ksz_common_rcv()`. Family-specific TX/RX functions include `ksz8795_xmit/rcv`, `ksz9477_xmit/rcv`, `ksz9893_xmit`, and `lan937x_xmit`.

Control flow: TX computes pending checksums before appending tail tags, encodes destination port masks, priority, link-local override flags, and optional timestamp/correction fields. PTP-capable variants may queue deferred work when an skb clone awaits egress timestamp handling. RX linearizes, decodes tail source port, optionally extracts a PTP timestamp, trims the trailer, maps to a user port, and marks hardware-forwarded frames.

State and persistence: private state lives in `ds->tagger_data` for the life of the tagger connection. `KSZ_HWTS_EN` controls whether TX timestamp tags are emitted. No persistence beyond runtime memory.

Dependencies and integration: uses Linux PTP classification/correction helpers, Microchip DSA skb control blocks, DSA tagger-data callback contracts, kthread workers, and DSA conduit mapping. Switch drivers rely on the exported tagger-data function pointers.

Risks and test signals: high-risk areas are timestamp tag length accounting, deferred-xmit reference handling, checksum handling for trailing tags, and different family bit layouts. Tests should cover each registered protocol, PTP enabled/disabled paths, cloned timestamped skb deferral, link-local override, priority mapping, and RX timestamp extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_ksz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_lan9303.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_lan9303.c

Purpose: DSA tag driver for SMSC/Microchip LAN9303 switches, which use a normal 802.1Q tag field with special VID semantics to encode destination or source port and control bits.

Important APIs/functions: `lan9303_xmit_use_arl()` chooses ALR lookup for bridged unicast traffic. `lan9303_xmit()` inserts the special VLAN tag. `lan9303_rcv()` removes either hardware-accelerated VLAN metadata or an in-frame VLAN tag and decodes source/trap bits. `lan9303_netdev_ops` registers `DSA_TAG_PROTO_LAN9303`.

Control flow: TX inserts `ETH_P_8021Q` plus either the ALR bit or direct destination port with STP override. RX pulls the VLAN tag, extracts source port from low bits, maps the user device, and only marks offload-forwarded packets when they were not trapped for IGMP/STP.

State and persistence: no tagger-owned state; it reads `struct lan9303` from `ds->priv` to know whether ports are bridged.

Dependencies and integration: depends on LAN9303 driver-private bridge state, Linux VLAN helpers, DSA etype helpers, and switchdev bridge offload semantics.

Risks and test signals: risks include ALR/direct mode misselection, bad handling of VLAN hardware acceleration, and STP/IGMP trap classification. Tests should cover bridged unicast, multicast/flooding, VLAN hwaccel and in-frame RX, invalid source ports, and bridge learning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_lan9303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_mtk.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_mtk.c

Purpose: DSA tag driver for Mediatek switches using a 4-byte special tag after the source MAC. It supports combined handling with existing 802.1Q or 802.1ad headers.

Important APIs/functions: `mtk_tag_xmit()` selects tag type based on `skb->protocol`, encodes destination port mask, and maps the skb queue to the physical port. `mtk_tag_rcv()` strips the tag, extracts the source port, maps the user device, and marks hardware-forwarded frames. `mtk_netdev_ops` registers `DSA_TAG_PROTO_MTK`.

Control flow: untagged TX packets receive new headroom and an inserted tag; VLAN-tagged packets reuse the existing tag position so hardware can parse both special tag and VLAN table information. RX reads the tag from the etype-header position and strips it with checksum correction.

State and persistence: stateless.

Dependencies and integration: depends on VLAN ethertypes, DSA tag helpers, and queue/traffic-class integration. It integrates with bridge offload through `dsa_default_offload_fwd_mark()`.

Risks and test signals: VLAN-combined special tag handling is the main compatibility risk. Tests should cover untagged, 802.1Q, and 802.1ad TX, queue mapping, source port decode, and bridge flooding/forwarding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_mtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_mxl-gsw1xx.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_mxl-gsw1xx.c

Purpose: DSA tag driver for MaxLinear GSW1xx switches using an 8-byte special tag identified by `ETH_P_MXLGSW`.

Important APIs/functions: `gsw1xx_tag_xmit()` inserts the tag after source MAC, sets the MaxLinear ethertype, enables port map and learning disable bits, and writes destination mask. `gsw1xx_tag_rcv()` validates the ethertype, extracts source-port map bits, maps the user port, and strips the special tag. `gsw1xx_netdev_ops` registers `DSA_TAG_PROTO_MXL_GSW1XX`.

Control flow: TX creates headroom with `skb_push()` and `dsa_alloc_etype_header()`. RX checks `pskb_may_pull()`, rejects invalid marker/source port with rate-limited warnings, then removes the header and fixes checksums.

State and persistence: stateless; all route metadata is packet-local.

Dependencies and integration: depends on MaxLinear ethertype constants, Linux bitfield helpers, skb helpers, and the DSA tag framework.

Risks and test signals: risks include wrong RX bitfield interpretation, malformed tag logging floods, and missing offload-forward marking if hardware-forwarded traffic reaches a bridge. Tests should include valid/invalid ethertype, all source ports, port masks, short frames, and bridge duplicate-forwarding checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_mxl-gsw1xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_mxl862xx.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_mxl862xx.c

Purpose: DSA special-tag driver for MaxLinear MxL862xx switches, using an 8-byte `ETH_P_MXLGSW` tag that carries CPU-port and sub-interface information.

Important APIs/functions: `mxl862_tag_xmit()` computes the target sub-interface relative to the CPU port and writes the ingress/egress fields. `mxl862_tag_rcv()` validates the marker, decodes source port from the IGP/EGP field, maps the user device, marks non-link-local forwarded frames, and strips the tag. `mxl862_netdev_ops` registers `DSA_TAG_PROTO_MXL862`.

Control flow: TX obtains `dp` and `cpu_dp`, pushes headroom, inserts an etype header, and fills four 16-bit words. RX performs bounded parsing, rate-limited diagnostics, DSA user lookup, optional offload mark, then removes the header.

State and persistence: no private state.

Dependencies and integration: uses DSA port relationships, `dsa_strip_etype_header()`, link-local detection, and bitfield helpers. Integrates with hardware bridge offload via `dsa_default_offload_fwd_mark()`.

Risks and test signals: the sub-interface calculation depends on CPU port numbering and should be tested on non-default CPU ports. RX should be tested for invalid markers, unknown ports, link-local frames, and normal bridge-forwarded data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_mxl862xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_none.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_none.c

Purpose: no-op DSA tag driver for switches without hardware tagging support. The file explicitly warns new switch support should prefer tag_8021q where possible.

Important APIs/functions: `dsa_user_notag_xmit()` returns the original skb unchanged. `none_ops` registers `DSA_TAG_PROTO_NONE` with only an xmit callback and no RX parser.

Control flow: TX path passes packets directly to the conduit. RX source demultiplexing cannot be done by this tagger, so deployments rely on switch/hardware limitations that make no tag acceptable.

State and persistence: stateless.

Dependencies and integration: only depends on `tag.h` and the DSA tag driver framework.

Risks and test signals: no-tag mode cannot distinguish source ports in generic switched traffic and is unsuitable for new hardware. Tests should be limited to supported legacy configurations and should verify no unexpected multi-port ambiguity or bridge leakage occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_ocelot.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_ocelot.c

Purpose: DSA tag driver for Ocelot/Seville switches using NPI injection/extraction frame headers plus a short prefix accepted by the conduit RX filter.

Important APIs/functions: `ocelot_xmit_common()` builds the injection header, populating bypass, source, QoS, VLAN TCI, tag type, and optional PTP rewrite operation. `ocelot_xmit()` and `seville_xmit()` write family-specific destination fields. `ocelot_rcv()` removes prefix/extraction headers, decodes source port, QoS, VLAN classification, and timestamp low bits. Ops register `DSA_TAG_PROTO_OCELOT` and `DSA_TAG_PROTO_SEVILLE`.

Control flow: TX derives VLAN/tag-type metadata through `ocelot_xmit_get_vlan_info()`, pushes `OCELOT_TAG_LEN` plus short prefix, then sets destination mask. RX repositions skb data from the conduit-consumed state, discards prefix and extraction header, updates checksum, maps the source port, marks offload-forwarded frames, restores priority, stores timestamp data in the skb control block, and may replace an in-frame VLAN tag with the classified VLAN from the extraction header.

State and persistence: stateless in the tagger; timestamp low bits live transiently in `OCELOT_SKB_CB`.

Dependencies and integration: depends on `linux/dsa/ocelot.h`, Ocelot IFH helpers, VLAN bridge state, PTP rewrite helpers, and DSA user mapping. The conduit is put in promiscuous mode.

Risks and test signals: skb pointer choreography is fragile. VLAN replacement must only happen for VLAN-filtering ports. Tests should cover Ocelot and Seville destinations, PTP rewrite, VLAN-unaware and VLAN-aware RX, reflected CPU-port frames, priority mapping, and checksum integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_ocelot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_ocelot_8021q.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_ocelot_8021q.c

Purpose: Ocelot/Felix DSA tagger that uses the generic tag_8021q format and switch TCAM rules instead of NPI headers, preserving functionality under VLAN-filtering bridges.

Important APIs/types: `struct ocelot_8021q_tagger_private` embeds exported `ocelot_8021q_tagger_data` and a kthread worker. `ocelot_defer_xmit()` queues switch-driver deferred transmit work for PTP/link-local frames. `ocelot_xmit()` uses tag_8021q for normal data. `ocelot_rcv()` decodes tag_8021q and maps the user port. Connect/disconnect manage the worker.

Control flow: normal TX inserts an 802.1Q tag with PCP and standalone VID. PTP rewrite or link-local traffic is deferred to switch-driver work and has checksums completed in software if needed. RX calls `dsa_8021q_rcv()`, maps source switch/port, and marks hardware-forwarded frames.

State and persistence: per-switch runtime state in `ds->tagger_data`; no persistence. Worker lifetime follows tagger connect/disconnect.

Dependencies and integration: depends on generic tag_8021q helpers, Ocelot PTP helpers, DSA tagger-data contracts, kthread workers, and Felix driver callback setup.

Risks and test signals: deferred transmit reference ownership and checksum completion are the sensitive paths. Tests should cover normal data, PTP over IP, link-local control, worker setup failure, source decoding, and bridge/VLAN-aware operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_ocelot_8021q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_qca.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_qca.c

Purpose: DSA tag driver for Qualcomm Atheros QCA8K switches. It uses a QCA-specific etype header and also handles management/MIB packets delivered over Ethernet.

Important APIs/types: `qca_tag_xmit()` builds the transmit tag with version, from-CPU bit, and destination port mask. `qca_tag_rcv()` validates version, dispatches register-ack and MIB packet types to callbacks in `struct qca_tagger_data`, or maps normal source-port frames. `qca_tag_connect()`/`disconnect()` allocate/free tagger data. `qca_netdev_ops` registers `DSA_TAG_PROTO_QCA`.

Control flow: TX inserts `QCA_HDR_LEN` after source MAC. RX parses the header; management read/write ACKs and MIB autocast packets are consumed and not delivered to the network stack. Normal frames have the tag stripped and `skb->dev` assigned.

State and persistence: runtime callback state is held in `ds->tagger_data`; no persistent storage.

Dependencies and integration: depends on `linux/dsa/tag_qca.h`, QCA switch-driver callbacks, etype header helpers, and DSA conduit mapping. The conduit is promiscuous because special management frames may not target a user MAC.

Risks and test signals: management packet dispatch can accidentally consume data if type/version parsing is wrong. Tests should cover normal data RX/TX, register ACK callback, MIB autocast callback, malformed versions, unknown ports, and connect/disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_qca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_rtl4_a.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_rtl4_a.c

Purpose: Realtek 4-byte protocol A tag driver, currently for RTL8366RB-style tags with Realtek ethertype `0x8899` plus a 16-bit protocol/port word.

Important APIs/functions: `rtl4a_tag_xmit()` pads short frames, inserts the Realtek ethertype and RTL8366RB protocol bits, and encodes destination mask. `rtl4a_tag_rcv()` validates ethertype/protocol, decodes source port, strips the tag, and marks hardware-forwarded frames. `rtl4a_netdev_ops` registers `DSA_TAG_PROTO_RTL4_A`.

Control flow: TX adds an etype header after source MAC. RX passes through non-Realtek ethertype frames unchanged, rejects unknown Realtek protocols, maps source ports, and removes the tag for valid DSA frames.

State and persistence: stateless.

Dependencies and integration: uses Realtek ethertype constants, DSA tag helpers, padding helpers, and DSA conduit lookup.

Risks and test signals: pass-through behavior for non-Realtek frames is unusual and must match conduit filtering. Port extraction uses low 8 bits while the transmit side writes a mask; hardware interpretation should be tested. Tests should cover short packets, non-Realtek frames, unknown protocol, all supported ports, and bridge offload marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_rtl4_a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_rtl8_4.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_rtl8_4.c

Purpose: Realtek 8-byte protocol 4 tag driver for RTL8365MB-like switches, supporting both in-frame etype tag `rtl8_4` and trailing tag `rtl8_4t`.

Important APIs/functions: `rtl8_4_write_tag()` builds the shared tag with Realtek ethertype, protocol 4, KEEP, LEARN_DIS, and destination port mask. `rtl8_4_read_tag()` validates and decodes ethertype, protocol, reason, and source port. `rtl8_4_tag_xmit/rcv()` handle in-frame tags; `rtl8_4t_tag_xmit/rcv()` handle tail tags. Two `dsa_device_ops` instances register `DSA_TAG_PROTO_RTL8_4` and `DSA_TAG_PROTO_RTL8_4T`.

Control flow: in-frame TX inserts an etype header; tail TX completes pending checksums before appending the tag. RX validates the tag, maps `skb->dev`, marks frames offload-forwarded unless the reason is TRAP, then strips the header or trims the trailer.

State and persistence: stateless.

Dependencies and integration: depends on Realtek ethertype constants, Linux bitfield helpers, DSA tag helpers, skb checksum/trimming helpers, and bridge offload marking.

Risks and test signals: risk areas are the two physical layouts, checksum correctness for tail tags, reason-code trap handling, and the shared Realtek ethertype colliding with other formats. Tests should cover both protocols, invalid ethertype/protocol, trap vs forward reason, tail checksum offload, and all valid source ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_rtl8_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_rzn1_a5psw.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_rzn1_a5psw.c

Purpose: DSA tag driver for Renesas RZ/N1 A5PSW switches. It inserts an 8-byte tag after the source MAC with a private `ETH_P_DSA_A5PSW` marker and control data.

Important APIs/types: `struct a5psw_tag` defines four big-endian 16-bit words. `a5psw_tag_xmit()` pads frames, inserts the marker, force-forward bit, and destination port mask. `a5psw_tag_rcv()` validates the marker, decodes source port, strips the tag, and marks hardware-forwarded frames. `a5psw_netdev_ops` registers `DSA_TAG_PROTO_RZN1_A5PSW`.

Control flow: TX ensures hardware minimum frame length, creates etype headroom, and fills the tag. RX bounds-checks, validates marker, maps source port, removes the etype header, and returns the skb.

State and persistence: stateless.

Dependencies and integration: uses Linux bitfield helpers, DSA etype helpers, padding, and conduit lookup. Bridge offload integration is via `dsa_default_offload_fwd_mark()`.

Risks and test signals: source-port decoding reads `ctrl_data` while TX writes destination data in `ctrl_data2_lo`; this reflects different RX/TX hardware semantics and needs hardware tests. Test marker rejection, padding, all source ports, and bridge forwarding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_rzn1_a5psw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_sja1105.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_sja1105.c

Purpose: DSA tag driver for NXP SJA1105 and SJA1110 switches. SJA1105 primarily uses tag_8021q plus special handling for link-local management and metadata frames; SJA1110 adds in-band control extensions, metadata timestamp frames, and optional trailers.

Important APIs/types: `struct sja1105_tagger_private` embeds exported tagger data, a metadata spinlock, buffered timestampable skb, and xmit worker. Helpers include `sja1105_is_link_local()`, `sja1105_meta_unpack()`, `sja1105_defer_xmit()`, `sja1105_xmit_tpid()`, `sja1105_imprecise_xmit()`, `sja1105_pvid_tag_control_pkt()`, `sja1105_rcv_meta_state_machine()`, `sja1110_rcv_meta()`, and `sja1110_rcv_inband_control_extension()`. Ops register SJA1105 and SJA1110 variants.

Control flow: normal data TX inserts a tag_8021q VLAN with PCP and standalone VID. Bridge-offloaded traffic may use an imprecise bridge VID or pass VLAN-aware bridge traffic unchanged. Link-local control traffic is PVID-tagged and either deferred to driver work (SJA1105) or wrapped in an SJA1110 in-band control header/trailer. RX decodes management source info, tag_8021q VLANs, metadata follow-up frames, SJA1110 timestamp trailers, source device/port, and host-only state before marking offload-forwarded packets.

State and persistence: per-switch runtime state in `ds->tagger_data`; metadata pairing uses `stampable_skb` under `meta_lock`, and deferred TX uses a kthread worker. No disk persistence.

Dependencies and integration: depends on `linux/dsa/sja1105.h`, tag_8021q helpers, packing helpers, bridge VLAN APIs, PTP/timestamp control blocks, and switch-driver callbacks in tagger data.

Risks and test signals: this is high-risk because it contains a state machine pairing metadata with data frames without unique IDs. Risks include stale buffered skbs, wrong port on metadata, SJA1110 trailer position/trim errors, deferred-xmit reference leaks, and bridge VID imprecision. Tests should cover normal data, link-local management, TX/RX timestamps, metadata loss/reorder, VLAN-aware and VLAN-unaware bridges, SJA1110 host-only frames, and worker teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_sja1105.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_trailer.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_trailer.c

Purpose: legacy 4-byte trailer tag driver. It appends a fixed-format trailer carrying destination/source port information.

Important APIs/functions: `trailer_xmit()` appends bytes `0x80`, destination mask, `0x10`, `0x00`. `trailer_rcv()` linearizes the skb, validates the trailer signature, decodes source port, maps the user device, and trims the trailer. `trailer_netdev_ops` registers `DSA_TAG_PROTO_TRAILER`.

Control flow: TX simply appends tail bytes. RX checks exact bit patterns before trusting the source port, then removes the trailer with checksum adjustment.

State and persistence: stateless.

Dependencies and integration: uses DSA port-mask and conduit lookup helpers plus skb tail operations.

Risks and test signals: no offload-forward mark is set, so bridge behavior must match the hardware protocol. Trailer validation and linearization can drop fragmented/nonlinear frames. Tests should cover valid signature, invalid signature, all source ports, nonlinear skbs, and bridge forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_trailer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_vsc73xx_8021q.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_vsc73xx_8021q.c

Purpose: VLAN/tag_8021q-based DSA tagger for Vitesse VSC73XX switches.

Important APIs/functions: `vsc73xx_xmit()` chooses standalone or bridge-domain tag_8021q VID and inserts a VLAN tag. `vsc73xx_rcv()` decodes tag_8021q source information and maps the user device with fallback helpers. `vsc73xx_8021q_netdev_ops` registers `DSA_TAG_PROTO_VSC73XX_8021Q`.

Control flow: normal TX targets the precise standalone VID. Bridge-offloaded TX under VLAN-unaware bridges uses the bridge VID; under VLAN-aware bridges it returns the original skb because the bridge VLAN should carry the classification. RX initializes source fields to unknown, calls `dsa_8021q_rcv()`, finds the user device, warns on failure, and marks hardware-forwarded frames.

State and persistence: no tagger-owned state; it relies on tag_8021q registration by the switch driver.

Dependencies and integration: depends on generic tag_8021q helpers, bridge VLAN state, DSA user mapping, and promiscuous conduit mode.

Risks and test signals: bridge-mode decisions are the main risk. Tests should cover standalone, VLAN-unaware bridge, VLAN-aware bridge, VBID fallback, non-DSA VLAN RX, and unknown source decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_vsc73xx_8021q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_xrs700x.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_xrs700x.c

Purpose: DSA tail-tag driver for XRS700x switches using a 1-byte port mask trailer.

Important APIs/functions: `xrs700x_xmit()` appends destination mask. `xrs700x_rcv()` reads the trailer, uses `ffs()` to convert a one-hot mask to source port, trims the trailer, maps the user device, and marks hardware-forwarded frames. `xrs700x_netdev_ops` registers `DSA_TAG_PROTO_XRS700X`.

Control flow: TX appends one byte. RX trusts the last byte as source mask and rejects zero masks because `ffs(0) - 1` is negative.

State and persistence: stateless.

Dependencies and integration: depends on bit operations, DSA port-mask/conduit helpers, and skb trim helpers.

Risks and test signals: multi-bit source masks choose the lowest set bit; tests should verify hardware always emits one-hot masks. Also test zero masks, all ports, tailroom, and bridge offload marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_xrs700x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_yt921x.c -->
# sources/distributed-fs/ceph-client/net/dsa/tag_yt921x.c

Purpose: DSA tag driver for Motorcomm YT921x extended CPU-port tagging. The tag is 8 bytes and includes a configurable-looking ethertype, VLAN word, RX/TX port fields, priority, and packet code.

Important APIs/types: `enum yt921x_tag_code` documents known forwarding/copy/unknown-unicast/multicast codes. `yt921x_tag_xmit()` inserts `ETH_P_YT921X`, sets forward code, priority, destination port mask, and validity bits. `yt921x_tag_rcv()` validates ethertype and RX port validity, decodes source port and priority, classifies code for offload-forward marking, strips the tag, and returns the skb. `yt921x_netdev_ops` registers `DSA_TAG_PROTO_YT921X`.

Control flow: TX inserts an etype header and writes four 16-bit words. RX rejects malformed tags, maps source port, copies tag priority into `skb->priority`, marks forwarded/copy cases as hardware-forwarded, leaves unknown unicast/multicast unmarked for software switching, and warns on unknown codes.

State and persistence: stateless.

Dependencies and integration: uses DSA tag helpers, bitfield macros, Motorcomm ethertype, and bridge offload marking.

Risks and test signals: hardware code semantics are incomplete, and the comment notes unknown copy/trap distinction. Tests should cover known code values, unknown codes, priority propagation, invalid RX port validity, all source ports, and software bridge behavior for unknown unicast/multicast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/tag_yt921x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/trace.c -->
# sources/distributed-fs/ceph-client/net/dsa/trace.c

Purpose: implements helper functions used by DSA tracepoints defined in `trace.h`, and enables tracepoint generation by defining `CREATE_TRACE_POINTS`.

Important APIs/functions: `dsa_db_print()` formats a `struct dsa_db` as port, LAG, bridge, or unknown into a fixed buffer. `dsa_port_kind()` maps DSA port types to stable strings: user, cpu, dsa, or unused.

Control flow: tracepoint fast-assign code calls these helpers to produce printable database and port-kind fields. The file includes `trace.h` after `CREATE_TRACE_POINTS`, so the kernel trace infrastructure emits the tracepoint definitions here.

State and persistence: no runtime state is owned. Trace output is transient through ftrace/perf infrastructure.

Dependencies and integration: depends on DSA database and port structures from `trace.h` includes. It integrates with FDB, MDB, LAG, and VLAN trace events in the DSA core.

Risks and test signals: formatting uses `sprintf()` into `DSA_DB_BUFSIZ`, whose size is chosen in the header. Tests should compile with tracing enabled and exercise FDB/MDB/VLAN operations to ensure trace events print correct device, bridge, LAG, and port information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/trace.h -->
# sources/distributed-fs/ceph-client/net/dsa/trace.h

Purpose: defines the DSA tracepoint set for hardware programming of FDB, MDB, LAG FDB, and VLAN operations, including refcount bumps/drops and not-found diagnostics.

Important APIs/types: declares `dsa_db_print()` and `dsa_port_kind()`. Defines `DSA_DB_BUFSIZ`, event classes `dsa_port_addr_op_hw`, `dsa_port_addr_op_refcount`, `dsa_port_addr_del_not_found`, `dsa_vlan_op_hw`, and `dsa_vlan_op_refcount`, plus concrete events such as `dsa_fdb_add_hw`, `dsa_mdb_del_drop`, `dsa_lag_fdb_add_hw`, `dsa_vlan_add_bump`, and `dsa_vlan_del_not_found`.

Control flow: DSA code invokes trace events around switchdev programming. The trace macros capture device name, port kind/index, MAC address, VID, database string, errors, VLAN flags, changed state, and refcounts. The bottom overrides `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` and includes `<trace/define_trace.h>` outside the include guard, per kernel tracepoint convention.

State and persistence: tracepoints have no DSA data ownership. Captured data is emitted to runtime tracing buffers when enabled.

Dependencies and integration: includes DSA, switchdev, etherdevice, bridge, refcount, and tracepoint headers. It is consumed through `trace.c` and by DSA FDB/MDB/VLAN programming paths.

Risks and test signals: risks are trace macro signature drift, invalid pointer lifetime during fast assignment, missing fields in print formats, and buffer-size assumptions for database strings. Compile with tracepoints enabled and exercise add/delete/refcount/not-found cases for ports, LAGs, and bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/user.c -->
# sources/distributed-fs/ceph-client/net/dsa/user.c

Purpose: implements DSA user-facing network devices: creation/destruction, TX path, PHY/phylink setup, ethtool/DCB/netpoll/netdev operations, VLAN and MTU management, switchdev offloads, bridge/LAG/HSR upper handling, conduit migration, and notifier registration.

Important APIs/types: work structs `dsa_switchdev_event_work` and `dsa_standalone_event_work` defer FDB/MDB programming. Exported/core functions include `dsa_user_mii_bus_init()`, `dsa_user_sync_ha()`, `dsa_user_unsync_ha()`, `dsa_user_host_uc_install()`, `dsa_user_host_uc_uninstall()`, `dsa_enqueue_skb()`, `dsa_user_manage_vlan_filtering()`, `dsa_user_change_mtu()`, `dsa_port_phylink_mac_change()`, `dsa_user_setup_tagger()`, `dsa_user_create()`, `dsa_user_destroy()`, `dsa_user_change_conduit()`, `dsa_user_dev_check()`, `dsa_user_register_notifier()`, and `dsa_user_unregister_notifier()`.

Control flow: user netdev creation allocates `struct dsa_user_priv`, configures netdev/ethtool/DCB ops, inherits conduit MAC/features, sets tagger headroom/tailroom and xmit callback, creates phylink, normalizes MTU, registers the netdev, initializes DCB, and links it as a conduit upper. TX updates software stats, handles hardware timestamping, ensures writable head/tail, pads when needed, calls the selected tagger `xmit`, and queues the resulting skb to the conduit. Switchdev and netdevice notifiers translate bridge/VLAN/FDB/MDB/LAG events into DSA port operations, often via workqueue to avoid atomic-context hardware programming.

State and persistence: per-user state is in `struct dsa_user_priv`: cached tagger xmit, GRO cells, `dp`, optional netpoll, and matchall TC entries. Per-port VLAN RX filtering state is in `dp->user_vlans`. Deferred work items are heap allocated and freed after execution. No on-disk persistence.

Dependencies and integration: deeply integrated with DSA port/switch/conduit helpers, phylink/PHY/MDIO, switchdev, rtnetlink, bridge, LAG, HSR, tc flower/matchall, ethtool, DCB, netpoll, VLAN APIs, and DSA taggers through `cpu_dp->tag_ops`.

Risks and test signals: high-risk areas include rollback paths in create/change_conduit/change_mtu/VLAN filtering, notifier ordering, address/VLAN refcount synchronization, bridge/LAG upper sanity checks, deferred FDB/MDB work after device changes, and tagger headroom/tailroom feature masking. Tests should cover user netdev lifecycle, open/close, MAC change, multicast/unicast sync, VLAN upper add/remove, VLAN-aware bridge conflicts, bridge/LAG/HSR join/leave, conduit LAG migration, MTU rollback, tc offload add/delete, ethtool/DCB callbacks, hwtstamp, suspend/resume, and notifier unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/user.h -->
# sources/distributed-fs/ceph-client/net/dsa/user.h

Purpose: local interface for DSA user-device support. It defines the per-user private data layout and exposes lifecycle, notifier, VLAN, MTU, conduit, and tagger helpers to other DSA core files.

Important APIs/types: `struct dsa_user_priv` stores cached tagger xmit callback, GRO cells, owning `struct dsa_port *dp`, optional netpoll, and TC matchall state. Extern notifier blocks expose switchdev notifier instances. Function declarations cover MII init, create/destroy, suspend/resume, notifier registration, host unicast install/uninstall, host address sync/unsync, tagger setup, MTU changes, conduit changes, and VLAN filtering management. Inline helpers `dsa_user_to_port()` and `dsa_user_to_conduit()` translate netdevs to DSA state.

Control flow: other DSA modules include this header to interact with user netdevs without knowing the implementation details in `user.c`. The inline helpers are hot-path utilities used heavily by taggers and TX/RX code.

State and persistence: the header defines runtime netdev-private state but owns no persistent state.

Dependencies and integration: includes bridge, VLAN, list, netpoll, DSA, and GRO headers. It is a central contract between DSA user-device handling, taggers, switch code, and netdevice notifiers.

Risks and test signals: changing `struct dsa_user_priv` affects netdev private layout and tagger hot paths. Tests should compile all taggers and DSA core users, and runtime tests should verify `dsa_user_to_port()` assumptions for every DSA user netdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/dsa/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethernet/Makefile -->
# sources/distributed-fs/ceph-client/net/ethernet/Makefile

Purpose: Kbuild fragment for the Linux Ethernet layer under this source tree.

Important APIs/entries: declares `obj-y += eth.o`, so `eth.o` is always built into the Ethernet networking layer when this Makefile is reached.

Control flow: the kernel build system reads this Makefile and adds `eth.o` to the built-in object list for the directory. There are no conditionals or module entries here.

State and persistence: no runtime state. Its only effect is build graph configuration.

Dependencies and integration: depends on Kbuild semantics and the presence of `eth.c`/`eth.o` in the same directory. Integrates with parent networking Makefiles that descend into `net/ethernet`.

Risks and test signals: risk is low; accidental removal would break Ethernet helper linkage broadly. Test signal is a successful kernel/networking build and expected inclusion of `eth.o` in built-in objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethernet/Makefile -->
