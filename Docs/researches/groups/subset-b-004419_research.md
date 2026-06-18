# subset-b-004419 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc-cmd.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc-cmd.h

Purpose: Defines the Management Complex command ABI for DPAA2 Data Path Real Time Counter objects. It is not a driver by itself; it is the private command layout consumed by `dprtc.c` when sending MC portal commands.

Important APIs, types, and constants: `DPRTC_CMD()` and `DPRTC_CMD_V2()` encode command IDs with base or v2 command versions. The command IDs cover open/close plus IRQ enable, mask, status, and clear operations. Packed structures such as `dprtc_cmd_open`, `dprtc_cmd_set_irq_enable`, `dprtc_cmd_set_irq_mask`, `dprtc_cmd_get_irq_status`, and response structures define exact little-endian payload layout for `struct fsl_mc_command.params`.

Control flow and state: The header contains no executable flow and no persistent state. Runtime state lives in MC firmware and is addressed by DPRTC object ID, token, IRQ index, event mask, and W1C status bits passed in these payloads.

Dependencies and integration points: Depends on kernel fixed-width little-endian types and on `linux/fsl/mc.h` conventions through its consumers. The `#pragma pack(push, 1)` section is an integration contract with the MC firmware ABI; field order, sizes, and endianness must match firmware exactly.

Risks: ABI drift is the main risk. `DPRTC_CMDID_SET_IRQ_MASK` uses command version 2 while related getters use base version, so changing versions without firmware coordination can break interrupt control. Missing endian conversion in consumers would corrupt object IDs, masks, or status.

Test signals: Useful signals are successful `dprtc_open()` token retrieval, IRQ enable/mask round trips, PPS/ETS event delivery, and sparse/build coverage that catches packed-structure or endian type misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc.c

Purpose: Implements the DPAA2 DPRTC object API as thin wrappers around Management Complex commands. It opens and closes control sessions and manages the single DPRTC interrupt line's enable state, cause mask, pending status, and status clearing.

Important APIs and functions: `dprtc_open()` encodes `DPRTC_CMDID_OPEN`, passes a DPRTC object ID, sends the command, and extracts the returned token. `dprtc_close()` invalidates that control session. `dprtc_set_irq_enable()` and `dprtc_get_irq_enable()` control the whole interrupt. `dprtc_set_irq_mask()`/`dprtc_get_irq_mask()` configure which causes assert the interrupt. `dprtc_get_irq_status()` reads pending bits using the caller-supplied status filter, and `dprtc_clear_irq_status()` clears W1C bits.

Control flow: Every exported function builds a zeroed `struct fsl_mc_command`, fills the encoded header with command ID, flags, and token, casts `cmd.params` to the command-specific packed structure, writes parameters with CPU-to-little-endian conversions when needed, calls `mc_send_command()`, and decodes response fields on success. There is no retry, caching, locking, or asynchronous behavior.

State and persistence: The only local state is stack command storage. Persistent state is in the MC-managed DPRTC object: the open token, interrupt enable bit, interrupt mask, and pending event bits. After close, all later operations require a fresh token.

Dependencies and integration points: Uses `linux/fsl/mc.h`, `mc_encode_cmd_header()`, `mc_send_command()`, and `mc_cmd_hdr_read_token()`. It integrates with callers that know DPRTC event bits from `dprtc.h`, such as PPS and external timestamp events.

Risks: Callers must pass valid output pointers; the wrapper does not defensively check them. IRQ status read writes the input `*status` into the request, so uninitialized caller status can change firmware-side filtering semantics. ABI packing and command versions are inherited from `dprtc-cmd.h`.

Test signals: MC command success/error propagation, open/close token validity, IRQ mask get-after-set, event status read/clear behavior, and interrupt delivery under PPS/ETS events are the key runtime tests. Static tests should verify endian conversions and no unchecked command response use after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc.h

Purpose: Public local header for the DPAA2 Data Path Real Time Counter API. It exposes the DPRTC interrupt constants and the MC command wrapper prototypes implemented in `dprtc.c`.

Important APIs and types: Defines `DPRTC_MAX_IRQ_NUM` as one IRQ and `DPRTC_IRQ_INDEX` as index zero. Event bit definitions include `DPRTC_EVENT_PPS`, `DPRTC_EVENT_ETS1`, and `DPRTC_EVENT_ETS2`. Function declarations cover session lifecycle and IRQ enable/mask/status/clear operations, all parameterized by `struct fsl_mc_io`, command flags, token, and IRQ index.

Control flow and state: The header has no executable control flow. It defines the contract that consumers follow: open an object to get a token, perform interrupt operations using that token, then close the session.

Dependencies and integration points: Forward-declares `struct fsl_mc_io` and expects Linux integer typedefs to be available from includers. It is included by `dprtc.c` and by DPAA2 drivers that need access to RTC/PPS/ETS events through the MC.

Risks: There is only one IRQ index; callers using arbitrary indexes may receive firmware errors. Event bit constants must match firmware event causes. Since the header exposes raw `u32` masks rather than typed flags, accidental mixing with other DPAA2 event masks is possible.

Test signals: Compile-time coverage for users of the prototypes, runtime validation of event masks against actual PPS/ETS interrupt generation, and negative tests for invalid tokens or IRQ indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw-cmd.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw-cmd.h

Purpose: Defines the packed DPAA2 Management Complex ABI for Data Path Switch commands. It is the private wire-format layer used by `dpsw.c` to configure switch objects, interfaces, VLANs, FDBs, ACLs, control queues, flooding, learning, and reflection.

Important APIs, types, and constants: Command version macros encode base and v2 IDs. Command IDs cover object lifecycle, IRQs, attributes, link configuration, TCI/STP, counters, VLAN membership, FDB creation and entries, FDB dump, ACL management, control-interface attributes/pools/queues, port MAC lookup, egress flood, learning mode, and reflection. Bitfield helpers `dpsw_set_field()`, `dpsw_get_field()`, and `dpsw_get_bit()` pack sub-byte fields. Packed structs include `dpsw_rsp_get_attr`, `dpsw_rsp_if_get_attr`, `dpsw_cmd_vlan_add_if`, `dpsw_cmd_fdb_unicast_op`, `dpsw_cmd_fdb_multicast_op`, `dpsw_prep_acl_entry`, and `dpsw_cmd_acl_entry`.

Control flow and state: This header has no executable flow, but its structure layout determines how `dpsw.c` populates command buffers. State represented in payloads includes object attributes, interface bitmaps, FDB IDs, VLAN IDs, ACL IDs, DMA IOVA pointers, control queue destination configuration, and event masks.

Dependencies and integration points: Includes `dpsw.h` for public constants such as `DPSW_MAX_IF` and `DPSW_MAX_DPBP`. The packed ABI integrates directly with MC firmware. `__le16`, `__le32`, and `__le64` fields require consumers to do explicit endian conversion.

Risks: The command ABI is dense and version-sensitive. Interface sets are represented by bitmaps in `__le64 if_id`; callers must cap IDs at `DPSW_MAX_IF`. MAC addresses are stored in firmware byte order expected by `dpsw.c`, which reverses bytes during command construction and decoding. ACL entry preparation requires a caller-provided DMA-able 256-byte buffer, so layout mismatches or non-zero stale padding can affect rule matching.

Test signals: Build coverage for all command structs, firmware API version checks, VLAN/FDB/ACL round trips, FDB dump into DMA memory, and packet-level validation of ACL, learning, flooding, and reflection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw.c

Purpose: Implements the DPAA2 Data Path Switch API as Management Complex command wrappers. It exposes switch lifecycle, interface, VLAN, FDB, ACL, control-interface, learning, flooding, and mirroring operations to higher-level DPAA2 Ethernet/switch code.

Important functions: Lifecycle calls include `dpsw_open()`, `dpsw_close()`, `dpsw_enable()`, `dpsw_disable()`, and `dpsw_reset()`. Attribute and link APIs include `dpsw_get_attributes()`, `dpsw_if_get_attributes()`, `dpsw_if_set_link_cfg()`, `dpsw_if_get_link_state()`, and `dpsw_if_get_port_mac_addr()`. VLAN APIs add/remove VLANs and tagged/untagged interface membership. FDB APIs create/remove FDBs, add/remove unicast and multicast MAC entries, dump FDB content into caller-provided IOVA memory, and configure learning/flooding. ACL APIs create ACL tables, associate interfaces, prepare match/mask entries, and add/remove entries. Control-interface APIs expose queue FQIDs, buffer pools, queue destinations, and enable/disable control traffic.

Control flow: Most calls follow a uniform command path: zero a command, encode header, fill `cmd.params`, call `mc_send_command()`, and decode response fields. `build_if_id_bitmap()` converts arrays of interface IDs into a little-endian bitmap while ignoring IDs outside `DPSW_MAX_IF`. Multi-field encoders use `dpsw_set_field()` for compact firmware bitfields. MAC address commands reverse byte order when copying to/from firmware payloads. ACL preparation is split: `dpsw_acl_prepare_entry_cfg()` formats match/mask fields into caller-owned DMA memory, then add/remove entry commands pass `key_iova` to firmware.

State and persistence: The file keeps no persistent driver-owned switch state. Persistent state is owned by MC firmware: object tokens, enabled state, interface attributes, VLAN membership, FDB tables, ACL rules, buffer pools, queues, learning mode, flooding lists, and reflection rules. Local state is transient command payloads and decoded outputs.

Dependencies and integration points: Relies on `linux/fsl/mc.h`, `dpsw.h`, and `dpsw-cmd.h`. It integrates with DPAA2 switch and Ethernet management code, MC portals, DMA memory supplied by callers for FDB dumps and ACL keys, and Linux networking concepts such as MAC addresses, VLAN IDs, link state, and counters.

Risks: There is little validation; firmware is expected to reject invalid VLANs, FDB IDs, ACL IDs, interface lists, or queue destinations. Interface bitmap truncation can silently ignore IDs >= 64. FDB dump depends on zero-initialized DMA memory and sufficient `iova_size`. ACL preparation assumes the provided buffer is large, zeroed, and DMA-mapped later by the caller. The enum spelling `DPSW_FDB_ENTRY_DINAMIC` is part of the exposed API and should not be casually renamed.

Test signals: MC command error propagation, get-after-set for link, TCI, VLAN membership, and learning mode; packet forwarding tests for FDB unicast/multicast, flooding, and ACL actions; FDB dump parsing; control-interface queue traffic; IRQ link-change delivery; and endian-sensitive tests on big-endian/little-endian systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw.h

Purpose: Public local API header for DPAA2 Data Path Switch management. It defines switch capabilities, option bits, public configuration structures, enums, event masks, and prototypes implemented by `dpsw.c`.

Important APIs and types: Defines limits such as `DPSW_MAX_PRIORITIES`, `DPSW_MAX_IF`, and `DPSW_MAX_DPBP`. Public structs model switch attributes, control-interface attributes and queue configuration, link configuration/state, TCI/STP, interface attributes, VLAN membership, FDB unicast/multicast entries, FDB dump entries, egress flooding, ACL keys/results/entries, and reflection rules. Enums cover component type, flooding/broadcast mode, queue type, destination type, accepted frames, counters, learning mode, ACL actions, and reflection filters.

Control flow and state: The header defines the intended call sequence: open a switch object, query attributes, configure interfaces/link/VLAN/FDB/ACL/control queues, enable the object or interfaces as needed, then close. It does not store state; all actual switch state lives in the MC object and is accessed through tokens.

Dependencies and integration points: Forward-declares `struct fsl_mc_io` and relies on Linux network and integer types from includers. It is consumed by DPAA2 Ethernet/switch management code and by `dpsw-cmd.h` for command ABI sizing.

Risks: Many structures contain arrays sized for `DPSW_MAX_IF`; callers must set `num_ifs` consistently. ACL entry usage requires a prepared DMA buffer and stable `key_iova`. Counter and learning mode enums map directly to firmware values, so value changes would be ABI-breaking. `DPSW_STP_STATE_DISABLED` and `DPSW_STP_STATE_BLOCKING` both map to zero in this snapshot, which may be intentional firmware encoding but is a semantic hazard for callers.

Test signals: Compile coverage across all consumers, firmware API compatibility checks, and integration tests that exercise public structures through `dpsw.c`: VLAN add/remove, FDB add/remove/dump, ACL redirect/drop/accept, link state, counters, control-interface RX/TX error queues, and reflection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpsw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/Kconfig

Purpose: Declares Kconfig symbols for the NXP/Freescale ENETC and NETC Ethernet driver family. It controls which common libraries, PF/VF drivers, MDIO/PTP/QoS helpers, ENETC4 support, and NETC block-control modules can be built.

Important symbols: `FSL_ENETC_CORE` builds shared ENETC core functionality. `NXP_ENETC_PF_COMMON` builds shared PF code across controller versions. `NXP_NETC_LIB` provides NTMP, tc flower, and debugfs support selected by `NXP_NTMP`. `FSL_ENETC` selects the original ENETC PF driver and dependencies such as PCI MSI, phylink, PCS Lynx, MDIO, IERB, DIMLIB, and core code. `NXP_ENETC4` selects ENETC revision 4 PF support and NTMP. `FSL_ENETC_VF`, `FSL_ENETC_IERB`, `FSL_ENETC_MDIO`, `FSL_ENETC_PTP_CLOCK`, `FSL_ENETC_QOS`, and `NXP_NETC_BLK_CTRL` gate the VF, IERB, MDIO, PTP clock, TSN QoS, and NETC block control modules.

Control flow and state: Kconfig has no runtime flow. Its state is build-time configuration, which determines object inclusion and whether runtime code has PTP, QoS, NTMP, debugfs, phylink, or MDIO support.

Dependencies and integration points: Integrates with kernel networking, PCI MSI, PTP, phylink, PHYLIB, MDIO, DIMLIB, traffic control schedulers, and NETC timer support. Selected symbols align with object lists in the ENETC `Makefile`.

Risks: Missing dependencies cause link failures or unavailable runtime features. `FSL_ENETC_PTP_CLOCK` defaults to y when ENETC PF or VF and QorIQ PTP are available, so timestamp behavior can vary by kernel config. `FSL_ENETC_QOS` is bool and depends on selected qdisc support, so TSN code may compile out even when hardware supports it.

Test signals: `olddefconfig`/`allyesconfig` build coverage, module build checks for each advertised module name, and runtime smoke tests for PF, VF, ENETC4, MDIO, PTP, QoS, and block-control combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/Makefile

Purpose: Maps ENETC/NETC Kconfig symbols to kernel modules and object files. It defines the build composition for shared core, PF/VF, ENETC4, MDIO, PTP, QoS, IERB, NTMP, and NETC block-control code.

Important targets: `fsl-enetc-core.o` includes `enetc.o`, `enetc_cbdr.o`, and `enetc_ethtool.o`. `nxp-enetc-pf-common.o` includes `enetc_pf_common.o`. `nxp-netc-lib.o` includes `ntmp.o`. `fsl-enetc.o` includes `enetc_pf.o` and conditionally `enetc_msg.o` and `enetc_qos.o`. `nxp-enetc4.o` includes `enetc4_pf.o` and conditionally `enetc4_debugfs.o` under `CONFIG_DEBUG_FS`. Separate modules are declared for VF, IERB, MDIO, PTP, and NETC block control.

Control flow and state: The Makefile has build-time flow only. It persists no runtime state, but its conditional object selection determines whether runtime features such as SR-IOV messaging, QoS, and debugfs exist in the compiled module.

Dependencies and integration points: Directly implements the module layout implied by `Kconfig`. It integrates with Kbuild's `obj-$(CONFIG_...)` and per-module `foo-y`/`foo-$(CONFIG_...)` mechanisms.

Risks: Object composition must match symbol exports and Kconfig dependencies. If `enetc4_debugfs.o` references functions or types not present when `CONFIG_DEBUG_FS` is enabled, `nxp-enetc4.o` link fails. Conditional QoS and PCI IOV objects mean feature tests must use matching configs.

Test signals: Build matrix coverage across PF, VF, ENETC4, MDIO, PTP, QoS, PCI_IOV, and DEBUG_FS configurations. Module load tests should verify the module names advertised by Kconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc.c

Purpose: Core shared ENETC Ethernet driver implementation used by PF/VF variants. It handles MAC register access helpers, TX/RX descriptor processing, DMA resource management, NAPI/MSI-X interrupt flow, XDP, timestamping, VLAN/RSS feature toggles, tc mqprio setup, SI capability discovery/configuration, and generic PCI probe/remove support.

Important APIs and functions: Exported entry points include `enetc_xmit()`, `enetc_xdp_xmit()`, `enetc_open()`, `enetc_close()`, `enetc_start()`, `enetc_stop()`, `enetc_get_stats()`, `enetc_set_features()`, `enetc_ioctl()`, `enetc_setup_tc_mqprio()`, `enetc_reset_tc_mqprio()`, `enetc_setup_bpf()`, timestamp get/set helpers, MSI allocation/free, SI resource allocation/configuration, PCI probe/remove, and driver-data lookup. Internal TX helpers map skb, TSO, LSO, VLAN, checksum, and PTP timestamp descriptors. RX helpers refill page-backed buffers, build SKBs, run XDP, recycle pages, and parse hardware offloads.

Control flow: TX starts at `enetc_xmit()`, marks requested timestamp mode, validates one-step PTP Sync packets, then `enetc_start_xmit()` selects a TX ring, checks descriptor space, and maps either normal skb fragments, software TSO segments, or hardware LSO descriptors before ringing the producer index. TX completion is handled in NAPI by `enetc_clean_tx_ring()`, which reads completion indexes, unmaps DMA, frees SKBs or XDP frames, recycles XDP_TX pages, collects timestamps, updates stats, and wakes stopped queues. RX is driven from `enetc_poll()` after MSI-X disables interrupts and schedules NAPI. Non-XDP RX refills descriptors, builds SKBs from page halves, applies checksum/VLAN/timestamp offloads, and hands packets to GRO. XDP RX builds `xdp_buff`, runs the BPF program, and handles DROP, PASS, TX, and REDIRECT paths with page ownership updates. Open allocates IRQs, connects phylink, allocates rings, sets up descriptors, and starts queues; close stops queues, disconnects PHY, frees rings, IRQs, and clocks.

State and persistence: Persistent runtime state is in `struct enetc_ndev_priv`, `struct enetc_si`, interrupt vectors, TX/RX rings, software buffer descriptors, XDP RX queue info, active offload flags, class rules, timestamp workqueue state, and hardware registers. DMA-coherent descriptor rings and TSO header buffers persist while the interface is open. Hardware state includes SI enable, RSS table, interrupt coalescing, BDR base/length/index registers, VLAN offload enable, timestamp mode, and MAC/port registers.

Dependencies and integration points: Integrates with PCI, DMA mapping, netdev/NAPI, GRO, phylink, XDP/BPF, DIM interrupt moderation, skb timestamping, PTP classification, tc mqprio, VLAN features, RSS, and ENETC register definitions in `enetc_hw.h`/`enetc4_hw.h`. Uses exported helper hooks from variant-specific PF/VF code for ethtool ops and RSS table access.

Risks: High-risk areas include DMA mapping unwind on multi-BD TX/TSO/LSO failures, XDP page ownership transitions, RX page reuse under memory pressure, descriptor index wraparound, one-step timestamp serialization, RX timestamp reconfiguration requiring extended descriptors, and lock ordering around `enetc_lock_mdio()` plus NAPI/GRO handoff. `enetc_alloc_msix()` returns `-EPERM` without freeing vectors if `pci_alloc_irq_vectors()` returns a nonmatching positive count, though the exact API behavior for fixed min=max normally avoids partial success. Feature changes while running rely on `enetc_reconfigure()` to preserve callback correctness and restart safely.

Test signals: Packet TX/RX under checksum, VLAN, GSO/TSO/LSO, and MTU stress; XDP DROP/PASS/TX/REDIRECT with fragmented frames; PTP TX/RX timestamping including one-step Sync serialization; NAPI interrupt moderation/DIM behavior; ring exhaustion and queue wake tests; phylink up/down and phy-less mode; runtime feature toggles for RSS and VLAN; mqprio traffic-class mapping; suspend-like open/close loops with DMA leak checking; and builds for rev1, ENETC4 PF, PPM, and VF driver data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc.h

Purpose: Shared internal header for ENETC drivers. It defines core data structures, ring helpers, feature flags, SI/private state, active offloads, exported function prototypes, CBDR helpers, and conditional QoS stubs used by PF, VF, ENETC4, ethtool, QoS, and PTP code.

Important types and APIs: Defines TX/RX software buffer descriptors, skb private control block, LSO metadata, ring statistics, XDP data, descriptor-ring resources, `struct enetc_bdr`, `struct enetc_cbdr`, `struct enetc_si`, `struct enetc_int_vector`, `struct enetc_ndev_priv`, classifier rule storage, PSFP capabilities, active offload flags, and interrupt coalescing modes. Inline helpers handle ring index wraparound, unused descriptor counts, RX descriptor addressing with optional extension descriptors, SI private-data alignment, PF detection, pseudo-MAC detection, CBDR DMA data allocation, and conditional PTP clock selection.

Control flow and state: The header encodes ring lifecycle assumptions used by `enetc.c`: `next_to_use`, `next_to_clean`, and `next_to_alloc` track producer/consumer and page reuse state; active offload flags drive timestamping, Qbv/Qci/Qbu, checksum, and LSO behavior; XDP reserves TX rings from the same TX ring array; `ENETC_TX_DOWN` and one-step timestamp bits coordinate queue state and serialized timestamp work.

Dependencies and integration points: Pulls in PCI, netdevice, DMA mapping, skb, ethtool, NTMP, VLAN, phylink, DIM, XDP, and ENETC hardware headers. The prototypes link the common core to variant-specific PF/VF/ENETC4 modules, ethtool code, CBDR/NTMP code, and optional QoS implementation.

Risks: Structure fields define ownership and cacheline-sensitive state, so changes can affect performance and concurrency. Descriptor count helpers assume one slot remains unused. XDP TX queue reservation reduces stack-visible TX queues and must stay consistent with `enetc_num_stack_tx_queues()`. Conditional QoS stubs return success for PSFP enable/disable when QoS is disabled, which callers must interpret carefully.

Test signals: Compile matrix for QoS enabled/disabled, PTP timer variants, PF/VF/ENETC4; ring index wrap tests; XDP queue reservation tests; descriptor extended-mode RX timestamp tests; and ABI/build checks for all exported prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_debugfs.c

Purpose: Provides ENETC4 debugfs visibility into MAC filtering state. It creates a per-netdev debugfs directory with a `mac_filter` file that dumps promiscuous mode bits, unicast/multicast hash filters, and optional MAC address filter table entries.

Important functions: `enetc_create_debugfs()` creates the root directory named after the netdevice and adds `mac_filter`. `enetc_remove_debugfs()` removes it. `enetc_mac_filter_show()` is the seq_file show callback. `enetc_show_si_mac_hash_filter()` reads per-SI hash filter registers. The show path queries NTMP MAFT entries through `ntmp_maft_query_entry()` when `pf->num_mfe` is nonzero.

Control flow: Opening the debugfs file invokes the generated `DEFINE_SHOW_ATTRIBUTE` path, with `struct enetc_si` in `s->private`. The show function derives PF private state via `enetc_si_priv(si)`, computes the SI count as PF plus VSIs, reads promiscuous and hash registers, then optionally walks all MAC filter table entries and prints MAC plus SI bitmap.

State and persistence: Debugfs dentries persist while the ENETC4 device is registered. It does not mutate hardware state; it reads registers and NTMP table entries. `si->debugfs_root` stores the created directory pointer for removal.

Dependencies and integration points: Depends on debugfs, seq_file, `string_choices.h`, ENETC PF private structures, ENETC4 register macros, and the NTMP MAFT query API. Built only into `nxp-enetc4.o` when `CONFIG_DEBUG_FS` is enabled.

Risks: Debugfs reads can return NTMP query errors mid-dump. The directory is created at debugfs root using the netdev name, so duplicate names or rename timing need normal debugfs handling. Register reads assume ENETC4 PF register layout and valid `pf->caps.num_vsi`/`pf->num_mfe`.

Test signals: With DEBUG_FS enabled, verify `/sys/kernel/debug/<netdev>/mac_filter` appears and disappears with device lifetime, reports SI promiscuous and hash bits accurately, handles zero `num_mfe`, and reports MAFT entries that match configured MAC filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_debugfs.h

Purpose: Declares ENETC4 debugfs creation/removal helpers and provides no-op inline stubs when debugfs is disabled.

Important APIs: `enetc_create_debugfs(struct enetc_si *si)` and `enetc_remove_debugfs(struct enetc_si *si)` are real functions under `CONFIG_DEBUG_FS`; otherwise they compile to empty inline functions.

Control flow and state: The header itself has no runtime state. It lets ENETC4 PF code call debugfs setup/teardown unconditionally without sprinkling `#ifdef CONFIG_DEBUG_FS` through caller code.

Dependencies and integration points: Expects `struct enetc_si` to be visible or at least forward-declared by includers. Integrates with `enetc4_debugfs.c` and the ENETC4 PF lifecycle.

Risks: If included before `struct enetc_si` is declared in a context that needs prototype checking, build errors are possible; current local include ordering should avoid that. The disabled-debugfs stubs intentionally hide missing debugfs behavior, so tests must run with `CONFIG_DEBUG_FS=y` to exercise the real path.

Test signals: Build with DEBUG_FS enabled and disabled, and ENETC4 PF probe/remove tests that call the helpers in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_hw.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_hw.h

Purpose: Defines ENETC revision 4 hardware register offsets, device IDs, and bit fields that are not already covered by the original ENETC hardware header. It is a register contract used by ENETC4 PF, PPM, ethtool, debugfs, and common core code.

Important constants and macros: Identifies NXP ENETC vendor/PF/PPM device IDs. Station-interface macros cover LSO segmentation flag masks and capability registers. Port macros cover SI enable, pause thresholds, discard counters, promiscuous MAC/VLAN modes, RSS keys, MAC/VLAN filtering capabilities, SI primary MAC and anti-spoofing registers, hash filters, port/MAC capabilities, speed configuration, MAC command configuration, maximum frame length, internal/external MDIO bases, interrupt events, pause quanta, single-step timestamp configuration, extensive MAC RX/TX counters, interface mode, and pseudo-MAC counters. Field helpers use `BIT`, `GENMASK`, and `FIELD_PREP`.

Control flow and state: No executable flow. The macros represent hardware state addressed by MMIO reads/writes elsewhere. For example, `ENETC4_PM_SINGLE_STEP()` fields are written by the one-step PTP timestamp path, hash filter registers are read by debugfs, and LSO flag masks are set during SI configuration.

Dependencies and integration points: Included by `enetc.h` and code that needs ENETC4-specific registers. Complements `enetc_hw.h`; comments state that shared ENETC v1 registers remain defined there. Integrates with PCI ID matching through driver-data selection in `enetc.c`.

Risks: Register offset mistakes cause silent hardware misconfiguration. Some macros take a MAC or SI index and compute offsets; callers must pass indexes within hardware-supported ranges. ENETC4 pseudo-MAC has a distinct counter block, so normal MAC register helpers must respect `ENETC_SI_F_PPM`. Speed and interface mode bitfield macros must match hardware units and encoding.

Test signals: ENETC4 PF/PPM probe with correct PCI IDs, ethtool counter reads, debugfs hash/promiscuous reads, one-step timestamp operation through `PM_SINGLE_STEP`, LSO behavior after `SILSOSFMR` programming, MDIO access through ENETC4 bases, and register readback tests for MAC command/configuration fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_hw.h -->
