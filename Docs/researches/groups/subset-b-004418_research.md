# Research: subset-b-004418

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch.c

Purpose: Implements the Linux DPAA2 Ethernet switch (`dpsw`) driver. It binds FSL MC switch objects to one net_device per switch port, configures VLAN-aware switching, per-bridge FDB domains, switchdev bridge offloads, tc flower/matchall ingress offloads, the control-interface RX/TX-confirm path, IRQ handling, buffer pools, and DPIO notification/NAPI plumbing.

Important APIs, types, and functions: Probe/lifecycle is centered on `dpaa2_switch_probe()`, `dpaa2_switch_init()`, `dpaa2_switch_probe_port()`, `dpaa2_switch_port_init()`, `dpaa2_switch_remove()`, and `dpaa2_switch_teardown()`. Port netdev behavior is exposed through `dpaa2_switch_port_ops`, including open/stop, MTU, stats, VLAN RX add/kill, FDB dump, TX, port parent ID, physical name, and tc setup. Switchdev handling is split across netdevice notifier callbacks, switchdev atomic callbacks, blocking object callbacks, and queued `dpaa2_switch_event_work()`. Data path functions include `dpaa2_switch_port_tx()`, `dpaa2_switch_build_single_fd()`, `dpaa2_switch_rx()`, `dpaa2_switch_build_linear_skb()`, `dpaa2_switch_tx_conf()`, and `dpaa2_switch_poll()`. Hardware resource setup uses `dpsw_*`, `dpbp_*`, and `dpaa2_io_service_*` APIs.

Control flow: Probe allocates `ethsw_core`, gets an atomic MC portal, opens the DPSW object, validates firmware/API capabilities, resets the switch, clears the default VLAN 1 programming, creates the ordered switchdev workqueue, removes default FDB 0, and brings up the shared control interface. It then allocates per-port arrays, creates a private FDB and ACL table per port, installs standalone VLAN 1 as untagged PVID, traps STP MAC frames to the control interface, connects any DPMAC endpoint, adds NAPI instances on the first port, configures MC IRQs, and finally registers all netdevs. Opening a port enables the hardware interface, starts shared NAPI once for the first user, and starts phylink-backed MACs when present. Closing reverses the per-port hardware interface and shared-NAPI reference count. TX linearizes/skb-headroom-adjusts frames, creates a single FD with skb backpointer in software annotation space, and enqueues to the port QDID. RX pulls control-interface frames, maps the ingress if_id from FLC, builds an skb from the buffer-pool page, strips the PVID VLAN header, sets `offload_fwd_mark` when bridged, and injects the skb into the stack.

State and persistence behavior: Runtime state lives in `struct ethsw_core` and `struct ethsw_port_priv`: MC portal and DPSW handle, switch attributes/version/features, port table, per-port VLAN bitmaps and PVIDs, FDB/bridge-domain assignment, flood/learning flags, ACL/mirror filter blocks, MAC endpoint pointer, DPIO notification contexts, DPBP buffer count, buffer pool ID, and shared NAPI user count. No durable state is written; all switch, VLAN, ACL, FDB, buffer-pool, queue, and IRQ state is reconstructed during probe and port events. FDB IDs and ACL table IDs are hardware resources tracked in memory until driver removal.

Dependencies and integration points: The file integrates Linux netdev, switchdev bridge and FDB notifications, bridge VLAN/STP flags, tc block offload (`FLOW_BLOCK_BIND`, flower, matchall), FSL MC bus/portal services, DPSW/DPBP command APIs, DPAA2 IO stores and notifications, IOMMU translation, DMA mapping, phylink/MAC support via `dpaa2-mac.h`, and the companion ACL/mirror implementation declared in `dpaa2-switch.h`.

Risks: The driver depends on VLAN-aware bridge operation and rejects VLAN-unaware bridges; incorrect bridge event ordering can strand VLANs in the wrong FDB domain. `dpaa2_switch_port_vlans_add()` performs duplicate DPSW attribute capacity checks, which is redundant and could hide future edits if one copy changes. `dpaa2_switch_prechangeupper_sanity_checks()` sets an extack for VLAN uppers but returns `0` after `-EOPNOTSUPP`, which appears to allow the operation despite the message. RX assumes frames mirrored to the control interface carry a VLAN header and uses PVID stripping; malformed/non-VLAN frames can hit error paths. Buffer-pool refill/acquire/release loops rely on bounded busy retries, and depletion can temporarily drop traffic. The IRQ endpoint-changed path toggles MAC connection based on current `port_priv->mac`; ordering regressions could race link handling. Cleanup paths free netdevs and hardware resources through several staged labels, so partial-probe failure coverage matters.

Test signals: Probe/remove on supported DPSW firmware >= 8.9; error probe against unsupported API, disabled control interface, non-per-FDB flooding/broadcast, too few FDBs, and no interfaces. Exercise standalone port VLAN 1 behavior, bridge join/leave with VLAN filtering, multiple ports in one bridge, cross-DPSW bridge rejection, VLAN uppers before bridge join, STP state transitions, learning on/off and fast age, broadcast/unicast/multicast flood flags, static FDB/MDB add/delete/dump, tc flower and matchall bind/unbind, MAC endpoint add/remove IRQs, link changed IRQs, MTU updates, buffer-pool refill under RX load, TX confirmation skb freeing, and NAPI enable/disable with multiple open ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch.h

Purpose: Defines the private data model, constants, and cross-file interfaces for the DPAA2 Ethernet switch driver. It describes switch-wide state, per-port state, control-interface queues, FDB and ACL/mirror bookkeeping, buffer sizing, and exported helpers used by the main switch, ethtool, ACL, and mirror code.

Important APIs, types, and functions: Key constants include `DPSW_IRQ_NUM`, VLAN state bits (`ETHSW_VLAN_MEMBER`, `ETHSW_VLAN_UNTAGGED`, `ETHSW_VLAN_PVID`, `ETHSW_VLAN_GLOBAL`), frame-size/headroom/buffer-pool sizing, store depth, ACL limits, and `ETHSW_FEATURE_MAC_ADDR`. Core structs are `dpaa2_switch_fq`, `dpaa2_switch_fdb`, `dpaa2_switch_acl_entry`, `dpaa2_switch_mirror_entry`, `dpaa2_switch_filter_block`, `ethsw_port_priv`, and `ethsw_core`. Inline helpers include `dpaa2_switch_acl_tbl_is_full()`, `dpaa2_switch_get_index()`, `dpaa2_switch_supports_cpu_traffic()`, `dpaa2_switch_port_is_type_phy()`, and `dpaa2_switch_port_has_mac()`. Declarations export port detection, VLAN add/delete, FDB iteration callback type, tc flower/matchall hooks, ACL entry add, and mirror offload/unoffload helpers.

Control flow: The header has no standalone execution, but it shapes how the C files cooperate. `ethsw_core` is allocated once per DPSW object and owns MC/DPIO/DPBP resources and arrays of per-port objects. Each `ethsw_port_priv` is embedded in a netdev and points back to the core. Filter blocks can be private per port or shared by tc block binding; ACL entries and mirror entries are list-managed inside the block.

State and persistence behavior: The declared state is volatile driver state only. VLAN bitmaps mirror hardware VLAN programming, `fdbs` and `filter_blocks` mirror hardware table allocation and sharing, `napi_users` gates shared control-interface NAPI, and `mac_lock` protects runtime updates to `port_priv->mac`. Nothing in the header defines persistent on-disk state.

Dependencies and integration points: Includes Linux netdevice, bridge, VLAN, switchdev, packet classifier, FSL MC, DPAA2 IO, `dpaa2-mac.h`, and `dpsw.h`. It is the contract between `dpaa2-switch.c`, switch ethtool support, and tc ACL/mirror source files in the same directory.

Risks: The per-port VLAN bitmap is sized to all VLAN IDs, so memory use scales with port count. `dpaa2_switch_supports_cpu_traffic()` enforces strict DPSW capabilities; newer firmware feature variants must continue to satisfy per-FDB flooding/broadcast and adequate FDB counts. `dpaa2_switch_port_is_type_phy()` calls into MAC helpers and assumes `port_priv->mac` is valid, so callers must respect setup/locking conditions. ACL capacity reserves `DPAA2_ETHSW_PORT_DEFAULT_TRAPS`; tc code must keep this reservation in sync with default trap installation.

Test signals: Compile coverage across switch, ethtool, ACL, and mirror objects; probe with `DPSW_OPT_CTRL_IF_DIS`, non-per-FDB flooding/broadcast, and low `max_fdbs`; tc block sharing across ports; ACL table full behavior including default trap reservation; and runtime endpoint change while open/closed ports access `port_priv->mac`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-xsk.c

Purpose: Adds AF_XDP zero-copy support to the DPAA2 Ethernet driver. It binds an XSK buffer pool to a receive queue/channel, switches that channel to an XSK-specific RX consumer, runs XDP programs on UMEM-backed RX frames, supports wakeups from AF_XDP sockets, and transmits XSK TX descriptors through DPAA2 scatter-gather frame descriptors.

Important APIs, types, and functions: `dpaa2_xsk_setup_pool()` is the public setup entry that enables or disables a pool per queue ID. `dpaa2_xsk_wakeup()` schedules channel NAPI when an XSK socket needs TX progress. RX handling is in `dpaa2_xsk_rx()` and `dpaa2_xsk_run_xdp()`. Pool binding logic is in `dpaa2_xsk_enable_pool()`, `dpaa2_xsk_disable_pool()`, `dpaa2_xsk_set_bp_per_qdbin()`, and `dpaa2_eth_setup_consume_func()`. TX is handled by `dpaa2_xsk_tx_build_fd()` and `dpaa2_xsk_tx()`.

Control flow: Enabling checks WRIOP and queue-count support, closes the device if it is running, DMA maps the XSK pool, changes the channel RXQ memory model to `MEM_TYPE_XSK_BUFF_POOL`, allocates a dedicated DPBP buffer pool, points the channel to that pool, switches the channel's RX FQ consumer to `dpaa2_xsk_rx()`, updates DPNI pool association by qdbin, and reopens the device if needed. Disabling closes the device if running, unmaps DMA, restores page-order RXQ memory model, frees the channel DPBP, restores the default buffer pool and normal RX consumer, updates DPNI pools, and reopens. RX obtains the buffer VA from the FD address, rejects non-single FDs, runs any channel XDP program, handles redirect/TX/drop/recycle outcomes, or builds an skb on `XDP_PASS`. TX peeks an XSK descriptor batch, builds SG FDs using UMEM DMA addresses plus a separately DMA-mapped SGT buffer, enqueues with retries, updates stats, and frees non-enqueued FDs.

State and persistence behavior: Runtime state is per channel: `xsk_pool`, `xsk_zc`, channel buffer pool pointer, `xsk_tx_pkts_sent`, RXQ memory model, and per-channel XDP result/statistics. `priv->bp` and `priv->num_bps` grow when a channel gets a dedicated pool. No persistent state exists; pool mappings and channel mode are reconstructed by userspace AF_XDP setup.

Dependencies and integration points: Integrates AF_XDP (`xsk_buff_pool`, `xsk_tx_peek_release_desc_batch`, DMA map/unmap helpers), XDP/BPF core (`bpf_prog_run_xdp`, redirect, exception tracing), DPAA2 Ethernet core (`dpaa2-eth.h`, channel/FQ/buffer-pool helpers, enqueue/free paths, stats), DPNI pool configuration, DMA API, NAPI, and netdev open/close lifecycle.

Risks: Enabling/disabling temporarily closes the netdev, so failures must restore memory model, DMA mapping, pools, consumer callbacks, and link state. `priv->num_bps` is incremented on enable and not visibly decremented in this file on disable, so repeated pool churn depends on the broader DPAA2 buffer-pool management semantics. Only single-buffer RX FDs are supported; unexpected formats are dropped. XDP redirect success decrements `ch->buf_count`, so mismatched recycle/accounting can starve RX. TX uses separately mapped SGT buffers for UMEM payloads; partial enqueue failures must free each built FD correctly. Queue ID is directly indexed into `priv->channel[qid]`, so callers must provide valid queue IDs.

Test signals: AF_XDP bind/unbind on each queue while device is down and up, unsupported WRIOP <= 3.0.0, DPNI with more than 8 queues, DMA map failure, RXQ memory model failure, DPBP allocation failure, `dpni_set_pools()` failure rollback, XDP `PASS`, `DROP`, `ABORTED`, `TX`, and `REDIRECT`, invalid XDP action, non-single RX FD drop, wakeup with link down/no XDP/no zero-copy, TX batch partial enqueue and portal busy retries, and repeated enable/disable leak/accounting checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpkg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpkg.h

Purpose: Defines the DPAA2 Data Path Key Generator profile language used to build classification, hashing, QoS, and flow-steering keys. It is a declarative header: callers describe protocol fields or byte ranges to extract, and DPNI command code serializes those profiles into MC/DMA command buffers.

Important APIs, types, and functions: Core limits are `DPKG_NUM_OF_MASKS` and `DPKG_MAX_NUM_OF_EXTRACTS`. Extraction selectors include `enum dpkg_extract_from_hdr_type`, `enum dpkg_extract_type`, `struct dpkg_mask`, `struct dpkg_extract`, and `struct dpkg_profile_cfg`. `enum net_prot` lists parser protocols such as Ethernet, VLAN, IPv4/IPv6, IP, TCP, UDP, SCTP, PPPoE, MPLS, IPsec, GRE, ARP, GTP, and user-defined layers. The many `NH_FLD_*` masks describe selectable fields within those protocols.

Control flow: There is no executable flow in this file. A driver constructs `struct dpkg_profile_cfg`, fills up to ten extracts with header/data/parser selections and optional byte masks, then passes it to `dpni_prepare_key_cfg()` in `dpni.c`, which serializes the profile into the 256-byte command extension consumed by DPNI distribution/QoS commands.

State and persistence behavior: The structs are transient configuration containers. The effective key profile persists only inside MC hardware/firmware after the relevant DPNI command succeeds; this header itself stores no state.

Dependencies and integration points: Includes `<linux/types.h>` and uses Linux `BIT()` masks through the including environment. It is included by `dpni.h`, consumed by `dpni_prepare_key_cfg()`, and indirectly used by DPAA2 Ethernet RSS/hash/flow-steering and switch tc offload code that needs hardware parser keys.

Risks: Field masks and `enum net_prot` values are an ABI with MC firmware/parser expectations; changing numeric values or mask meanings would break hardware classification. Callers must respect the maximum extract and mask counts, valid `hdr_index` semantics, and protocol-field combinations. Several protocol masks are very broad, increasing the chance of invalid combinations that only firmware can reject. Typographical issues in comments/names, such as `BEGGINING`, should not be renamed if firmware-facing values depend on them.

Test signals: Build key profiles for common RSS and flow-steering keys: Ethernet DA/SA, VLAN TCI, IPv4/IPv6 5-tuple, TCP/UDP ports, payload bytes, parser-result extracts, masked extracts, outer/last VLAN/MPLS/IP header indexes, maximum ten extracts, invalid extract type rejection in `dpni_prepare_key_cfg()`, and firmware rejection paths for unsupported protocol/field combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpkg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac-cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac-cmd.h

Purpose: Defines MC command IDs, bitfield helpers, and packed command/response payload layouts for the DPAA2 Data Path MAC API.

Important APIs, types, and functions: Version macros are `DPMAC_VER_MAJOR`, `DPMAC_VER_MINOR`, command versions, `DPMAC_CMD_ID_OFFSET`, `DPMAC_CMD()`, and `DPMAC_CMD_V2()`. Command IDs cover open/close, API version, attributes, link state, counters, protocol, and bulk statistics. Bitfield helpers are `DPMAC_MASK()`, `dpmac_set_field()`, and `dpmac_get_field()`. Payload structs include `dpmac_cmd_open`, `dpmac_rsp_get_attributes`, `dpmac_cmd_set_link_state`, `dpmac_cmd_get_counter`, `dpmac_rsp_get_counter`, `dpmac_rsp_get_api_version`, `dpmac_cmd_set_protocol`, and `dpmac_cmd_get_statistics`.

Control flow: No direct execution occurs. `dpmac.c` casts `fsl_mc_command.params` to these structs, fills little-endian fields and compact bitfields, sends the command through `mc_send_command()`, then interprets response layouts from the same buffer.

State and persistence behavior: The header encodes transient MC command payloads. Link state, protocol, counters, and statistics live in MC firmware/hardware; this file stores no driver state.

Dependencies and integration points: Depends on Linux endian/fixed-width types through including context and the FSL MC command ABI. It is private to the DPMAC wrapper implementation and must match MC firmware command layouts exactly.

Risks: Struct layout, padding, command version, and bit shifts are firmware ABI. `DPMAC_CMDID_SET_LINK_STATE` uses command version 2 while most commands use base version; changing that would break newer link-state fields such as supported/advertising. `dpmac_set_field()` ORs into the existing variable, so callers must start from zeroed command buffers or clear target bits first.

Test signals: Compile and runtime smoke tests for every `dpmac.c` wrapper, firmware API version query, link-state set with `up` and `state_valid`, counter reads across all IDs, protocol changes, and bulk statistics DMA commands. Static layout checks are useful if MC ABI headers evolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac.c

Purpose: Implements thin Linux-side wrappers for the DPAA2 DPMAC Management Complex commands. It opens/closes DPMAC sessions and exposes attributes, link state, counters, API version, protocol selection, and bulk statistics to MAC/phylink-facing DPAA2 code.

Important APIs, types, and functions: Exported functions are `dpmac_open()`, `dpmac_close()`, `dpmac_get_attributes()`, `dpmac_set_link_state()`, `dpmac_get_counter()`, `dpmac_get_api_version()`, `dpmac_set_protocol()`, and `dpmac_get_statistics()`. All use `struct fsl_mc_command`, `mc_encode_cmd_header()`, `mc_send_command()`, and payload definitions from `dpmac-cmd.h`.

Control flow: Each function zero-initializes an MC command, encodes the command ID, flags, and token into the header, fills command parameters where needed, sends the command, and unpacks response fields if the call succeeds. Open returns the session token from the response header. Attribute, counter, version, and statistics reads convert little-endian response fields into CPU values. Link-state set packs options, rate, `up`, `state_valid`, supported, and advertising fields.

State and persistence behavior: This file keeps no persistent state; the session token is returned to callers and used externally. Any effective state change, such as link state or protocol, is stored by MC firmware/hardware. Counter/statistic values are snapshots.

Dependencies and integration points: Depends on `linux/fsl/mc.h`, `dpmac.h`, and `dpmac-cmd.h`. It is consumed by DPAA2 MAC support, switch port endpoint connection, and Ethernet drivers that need to synchronize phylink/MAC state with DPMAC objects.

Risks: MAC addresses are not handled here, but all other fields depend on exact MC ABI layout and endian conversion. `dpmac_get_counter()` writes `dpmac_cmd->id = id` without explicit width conversion because the field is one byte; enum expansion would matter if IDs exceed u8. Bulk statistics requires caller-provided DMA IOVAs for counter IDs and output values; invalid mapping/lifetime is a caller risk not checked here. Link-state bitfields rely on a zeroed command buffer because setters OR bits into `state`.

Test signals: DPMAC open/close token lifecycle, attribute read against known DPMAC IDs, link up/down and advertised capability propagation through phylink, individual counter reads, API version query, protocol reconfiguration on supported links, bulk statistics with valid and invalid DMA buffers, and MC error propagation for stale tokens or removed endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac.h

Purpose: Public in-driver DPMAC API declaration header. It defines DPMAC link/interface enums, link options, advertised speeds, attributes, link-state configuration, counter IDs, and prototypes for the command wrappers in `dpmac.c`.

Important APIs, types, and functions: Core types include `enum dpmac_link_type`, `enum dpmac_eth_if`, `struct dpmac_attr`, `struct dpmac_link_state`, and `enum dpmac_counter_id`. Link option macros cover autonegotiation, half duplex, pause, and asymmetric pause. Advertised-speed masks cover common 10/100/1000/2500/10000 full-duplex and autoneg. Prototypes expose open/close, attribute read, link-state set, counter read, API version, protocol set, and bulk statistics.

Control flow: No direct flow. Callers open a DPMAC object to get a token, read attributes to learn link type/interface/rate, push link state as PHY/phylink changes, query counters/statistics, optionally change MAC protocol, and close the token when done.

State and persistence behavior: The header declares transient request/response structs and enum IDs. Link configuration/state is persisted only in MC/DPMAC hardware. Counter IDs describe hardware-maintained counters; reads are snapshots.

Dependencies and integration points: Forward-declares `struct fsl_mc_io` and is included by DPMAC wrapper code and higher-level DPAA2 MAC/switch code. It is part of the internal contract between DPMAC MC objects and netdev/phylink integration.

Risks: `enum dpmac_counter_id` numeric order is a firmware ABI used in single and bulk statistics commands; reordering breaks counter reads. Link and advertised option bit positions must match MC firmware. `struct dpmac_link_state` uses `int` for boolean-like fields but command packing stores one-bit values; callers should pass normalized 0/1 values. Comment typos do not affect ABI but can obscure counter semantics.

Test signals: Build coverage for all users, phylink mode mapping for each `dpmac_eth_if`, fixed/PHY/backplane link types, link option translation, all counter IDs including PFC counters, bulk statistics counter-list construction, and unsupported protocol/link combinations from firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni-cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni-cmd.h

Purpose: Defines the MC command ABI for DPAA2 Data Path Network Interface objects. It maps high-level DPNI operations to command IDs, command versions, compact bitfields, and little-endian command/response structs consumed by `dpni.c`.

Important APIs, types, and functions: Version and ID helpers include `DPNI_VER_MAJOR`, `DPNI_VER_MINOR`, `DPNI_CMD()`, `DPNI_CMD_V2()`, and `DPNI_CMD_V3()`. Command IDs cover object lifecycle, enable/reset, IRQs, pools, error behavior, QDID/data offsets, link/frame length, promiscuous/MAC/VLAN filters, distribution, QoS/FS rules, statistics, queues, taildrop, buffer layout, congestion notification, offloads, link config, and single-step PTP. Bitfield helpers are `DPNI_MASK()`, `dpni_set_field()`, and `dpni_get_field()`. Structs define every command and response payload, including the external 256-byte RX distribution key extension (`dpni_ext_set_rx_tc_dist`).

Control flow: No direct execution. `dpni.c` writes these layouts into `struct fsl_mc_command.params`, sets command headers and tokens, calls `mc_send_command()`, and decodes response payloads using these structs and bitfield macros.

State and persistence behavior: The header defines transient command wire formats only. Persistent hardware/firmware state is affected by the commands sent by callers, such as queues, filters, distribution, taildrop, congestion, shaping, offloads, and PTP configuration.

Dependencies and integration points: Includes `dpni.h` for shared public enums and limits, which makes it tightly coupled to the public DPNI type definitions. It is private to the DPNI command wrapper implementation and must track MC firmware ABI exactly.

Risks: This file is almost entirely ABI-sensitive. Command-version mismatches are particularly important: `SET_POOLS` uses V3, `ADD_VLAN_ID` and `SET_TX_SHAPING` use V2, and `GET_SINGLE_STEP_CFG` uses V2. Reused bitfield names such as `DPNI_DEST_TYPE_*` appear for multiple structs with compatible shifts; future divergent layouts would need separate names. `dpni_set_field()` ORs into the destination, so callers need zeroed command buffers or explicit clearing. MAC address payloads are stored reversed by `dpni.c`, so command structs must not be interpreted as normal byte order. The key-extension struct size/ordering must fit the 256-byte DMA buffer expected by MC.

Test signals: ABI smoke tests for each wrapper in `dpni.c`, command version compatibility against target firmware, IRQ get/mask/clear, pool association including backup mask and qdbin mode, queue get/set round-trip, MAC add/remove byte ordering, VLAN filter/action commands, RSS/FS/QoS key extension serialization, congestion/taildrop threshold programming, offload get/set, single-step PTP flags, and static checks for struct sizes if the MC ABI changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni.c

Purpose: Implements the DPAA2 DPNI Management Complex command wrapper layer. It translates kernel driver requests for network-interface configuration into MC commands covering object lifecycle, buffer pools, IRQs, attributes, buffer layout, offloads, link state, filters, queues, statistics, distribution, QoS/flow steering, congestion/taildrop, shaping, VLAN filters, and one-step PTP.

Important APIs, types, and functions: `dpni_prepare_key_cfg()` serializes `dpkg_profile_cfg` into the 256-byte key extraction extension used by distribution and QoS commands. Object and base control wrappers include `dpni_open()`, `dpni_close()`, `dpni_enable()`, `dpni_disable()`, `dpni_is_enabled()`, `dpni_reset()`, and `dpni_get_attributes()`. Configuration families include pool setup, IRQ enable/mask/status/clear, error behavior, buffer layout, offload get/set, QDID/TX data offset, link config/state, max frame length, promiscuous mode, MAC filters, VLAN filters, RX distribution/hash/FS, queue get/set, statistics, congestion notification, taildrop, QoS/FS rule management, TX shaping, and single-step PTP config.

Control flow: Each wrapper zeroes `struct fsl_mc_command`, encodes the command header with command flags and token, fills the appropriate payload struct from `dpni-cmd.h`, sends it with `mc_send_command()`, and unpacks response fields on success. `dpni_prepare_key_cfg()` is local serialization rather than an MC send: it validates extract count, iterates requested extracts, maps header/data/parser extract variants into `dpni_dist_extract`, writes masks, and returns `-EINVAL` for invalid extract types or too many extracts. MAC address setters/getters reverse the six bytes to match MC payload convention. Queue and congestion wrappers pack compact destination/stash/hold-active fields, while statistics copies seven counters from the selected page.

State and persistence behavior: This file keeps no global state. Session tokens, DMA buffers, and configuration structs are caller-owned. Successful commands mutate DPNI object state in MC firmware/hardware: enabled state, pools, filters, layout, queues, congestion, distribution tables, QoS/FS tables, shaping, and PTP settings. Statistics/counter getters return snapshots.

Dependencies and integration points: Depends on Linux kernel/errno, FSL MC command infrastructure, `dpni.h`, `dpni-cmd.h`, and `dpkg.h`. It is a common support layer for the DPAA2 Ethernet netdev driver, AF_XDP pool setup, RSS/flow-steering configuration, ethtool statistics/offloads, DPIO queue setup, and MAC/link integration.

Risks: Because wrappers are thin, most bugs are ABI, endian, and field-packing errors. `dpni_prepare_key_cfg()` assumes `key_cfg_buf` is zeroed by the caller; stale bytes could leak into firmware-visible extraction fields. It copies all `DPKG_NUM_OF_MASKS` masks regardless of `num_of_byte_masks`, so unused masks must be zeroed by callers. Several commands are documented as allowed only while DPNI is disabled; this layer does not enforce those lifecycle rules. DMA IOVA parameters for key, mask, congestion messages, and rule buffers are not validated here. MAC byte reversal must remain consistent across set/get/add/remove. `dpni_set_single_step_cfg()` reads flags from an uninitialized command field after zero-initialization; this is currently safe only because the command struct starts zeroed.

Test signals: MC command success/error propagation with stale tokens; key extraction serialization for every `dpkg_extract_type`, max extract count, masks, and invalid types; pool association by priority and qdbin; enable/disable/reset sequencing; IRQ mask/status clear; attributes decoding; buffer layout/offload round-trips; MAC address set/get/add/remove byte order; VLAN add/remove with queue action fields; RX hash and flow-steering setup with DMA key buffers; queue get/set including FQID/qdbin; statistics page reads 0-6; congestion/taildrop programming; QoS and FS add/remove with mask IOVAs; shaping; and one-step PTP enable/checksum-update/peer-delay fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni.h

Purpose: Declares the public in-driver DPNI API and data model used by DPAA2 Ethernet code. It defines DPNI limits, creation/options flags, pool configuration, IRQ events, attributes, error behavior, buffer layout, offloads, statistics, link state, filtering, distribution, QoS/flow steering, queue destination/control, congestion/taildrop, shaping, one-step PTP, VLAN filters, and function prototypes implemented in `dpni.c`.

Important APIs, types, and functions: Major constants include `DPNI_MAX_TC`, `DPNI_MAX_DPBP`, all-TC/all-flow sentinels, DPNI option flags, IRQ event bits, error masks, buffer-layout option bits, statistics page count, link options, queue option flags, congestion options, FS action flags, and VLAN/filter sentinels. Key structs/enums include `dpni_pools_cfg`, `dpni_attr`, `dpni_error_cfg`, `dpni_buffer_layout`, `dpni_queue_type`, `dpni_offload`, `union dpni_statistics`, `dpni_link_cfg`, `dpni_link_state`, `dpni_dist_mode`, `dpni_fs_tbl_cfg`, `dpni_rx_tc_dist_cfg`, `dpni_rx_dist_cfg`, `dpni_qos_tbl_cfg`, `dpni_dest`, `dpni_queue`, `dpni_queue_id`, `dpni_congestion_notification_cfg`, `dpni_taildrop`, `dpni_rule_cfg`, `dpni_fs_action_cfg`, `dpni_tx_shaping_cfg`, and `dpni_single_step_cfg`. Prototypes mirror the DPNI command wrapper surface.

Control flow: This header is declarative. Typical caller flow is open a DPNI token, query attributes/API, configure pools and buffer layout while disabled, configure queues/offloads/filters/distribution/QoS/congestion as appropriate, enable the object, then react to link/endpoint IRQs and statistics while running. Some commands, such as key-based distribution and QoS, require callers to prepare a DMA-able key profile with `dpni_prepare_key_cfg()` first.

State and persistence behavior: The structs are request/response containers. Actual DPNI state persists in MC firmware/hardware across successful commands for the lifetime of the object or until reset/reconfiguration. Driver memory owns tokens, DMA buffers, and cached attributes; this header itself stores no state.

Dependencies and integration points: Includes `dpkg.h` for key extraction profiles and forward-declares `struct fsl_mc_io`. It is included by `dpni.c`, `dpni-cmd.h`, DPAA2 Ethernet, AF_XDP, ethtool/statistics/offload code, and queue/DPIO setup paths.

Risks: Numeric enum values and flag bits are firmware ABI. Many functions have lifecycle constraints documented in comments but not encoded in types, especially pool and buffer-layout programming while disabled. Several DMA IOVA fields require caller-managed coherent or DMA-mapped memory and alignment. Distribution sizes support a discrete firmware set; callers must validate values. `DPNI_FS_OPT_DISCARD` has a leading space before the preprocessor directive in the source but remains valid after whitespace; style-only edits should avoid altering ABI. `DPNI_ERROR_L4CE` comment incorrectly says L3 checksum, which can mislead diagnostics. `struct dpni_queue.destination.id` is `u16` while some command payloads use 32-bit destination IDs, so range expectations must match hardware.

Test signals: Compile coverage for all prototypes and structs, lifecycle tests for disabled-only commands, attribute decoding on DPNI variants with different options, queue destination modes `NONE`/`DPIO`/`DPCON`, RSS/hash distribution sizes, FS/QoS exact match and TCAM masking, MAC/VLAN filter capacity, all statistics pages, congestion/taildrop units and thresholds, link option mapping, offload flags, one-step PTP configuration, and ABI compatibility against firmware command versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpni.h -->
