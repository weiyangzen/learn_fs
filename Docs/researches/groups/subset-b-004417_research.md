# subset-b-004417 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth.c

## Purpose
`dpaa2-eth.c` is the primary Linux netdev driver for NXP/Freescale DPAA2 DPNI Ethernet interfaces. It bridges a Management Complex DPNI object to the kernel networking stack by allocating MC resources, configuring DPNI buffer layouts and queues, driving QBMan enqueue/dequeue operations, translating DPAA2 frame descriptors into SKBs or XDP actions, and exposing runtime controls through `net_device_ops`. It also coordinates MAC/phylink connection, hardware timestamping, devlink trap hooks, traffic-class setup, RX hashing/flow steering, and probe/remove lifecycle.

## Important APIs, types, and functions
The central state object is `struct dpaa2_eth_priv` from `dpaa2-eth.h`; this file initializes and mutates its DPNI token, MC portal, queue array, channel array, buffer pools, per-CPU statistics, XDP program pointers, timestamping state, MAC pointer, and devlink state. `dpaa2_eth_probe()` is the full constructor; `dpaa2_eth_remove()` is the destructor. `dpaa2_eth_open()` seeds RX buffer pools, enables NAPI, enables the DPNI, and starts phylink when the endpoint is PHY-backed. `dpaa2_eth_stop()` stops MAC or queues, waits for egress/ingress drain, disables DPNI/NAPI, drains pools, and flushes the per-CPU SGT cache.

Packet ingress starts in `dpaa2_eth_poll()`, which pulls a channel store with `dpaa2_io_service_pull_channel()`, consumes descriptors through `dpaa2_eth_consume_frames()`, and dispatches by FQ callback to `dpaa2_eth_rx()`, `dpaa2_eth_rx_err()`, or `dpaa2_eth_tx_conf()`. `dpaa2_eth_rx()` handles single-buffer and SG descriptors, DMA sync/unmap, XDP execution, copybreak, SKB construction, checksum/timestamp annotation, and batched `netif_receive_skb_list()`. Transmit is `dpaa2_eth_tx()` and `__dpaa2_eth_tx()`, backed by descriptor builders `dpaa2_eth_build_single_fd()`, `dpaa2_eth_build_sg_fd()`, `dpaa2_eth_build_sg_fd_single_buf()`, and `dpaa2_eth_build_gso_fd()`. `dpaa2_eth_free_tx_fd()` is the common TX-confirmation and TX-error cleanup routine.

Resource setup is split across `dpaa2_eth_setup_dpni()`, `dpaa2_eth_setup_dpio()`, `dpaa2_eth_setup_fqs()`, `dpaa2_eth_setup_default_dpbp()`, `dpaa2_eth_bind_dpni()`, and `dpaa2_eth_alloc_rings()`. Distribution and classifier support is implemented by `dpaa2_eth_set_hash()`, `dpaa2_eth_set_cls()`, `dpaa2_eth_set_dist_key()`, `dpaa2_eth_cls_key_size()`, `dpaa2_eth_cls_fld_off()`, and `dpaa2_eth_cls_trim_rule()`. `dpaa2_eth_setup_tc()` offloads mqprio and root TBF shaping. `dpaa2_eth_setup_xdp()` and `dpaa2_eth_xdp_xmit()` provide XDP and redirect/ndo-xmit support.

## Control flow
Probe allocates a multiqueue netdev, obtains an atomic MC portal, opens/resets DPNI, reads API and DPNI attributes, programs buffer layouts, allocates DPCON-backed channels on affine CPUs, builds FQ descriptors, allocates a DPBP buffer pool, binds DPNI pools and queues, registers XDP RXQ metadata, allocates per-CPU stats/FD/SGT caches, initializes netdev features and queues, configures checksum offloads, creates dequeue stores, connects DPMAC/phylink if present, configures link interrupts or starts a polling thread, registers devlink hooks/traps/port, and finally registers the netdev.

Runtime RX is interrupt-to-NAPI. CDAN notifications call `dpaa2_eth_cdan_cb()`, which schedules the channel NAPI instance. NAPI pulls descriptors until RX budget, TX-confirmation threshold, empty store, or portal error. RX FDs are converted to SKBs or consumed by XDP. TX confirmations free DMA mappings/SKBs/XDP frames and account completed netdev queue bytes. If the poll did not consume its budget, it updates DIM statistics, completes NAPI, rearms CDAN, flushes XDP redirects/TX bulks, completes AF_XDP TX credits, and submits the built RX list to the stack.

TX builds one or more hardware descriptors based on SKB layout: normal linear, nonlinear SG, linear-with-insufficient-headroom SG, or software TSO split into multiple SG descriptors. It then chooses the FQ from queue mapping and optional traffic class, calls the selected enqueue method, and relies on TX-confirmation descriptors for final resource release. PTP one-step Sync packets are serialized through a workqueue and `onestep_tstamp_lock` so the shared hardware correction offset is not changed while a one-step packet is in flight.

## State and persistence behavior
Driver state lives in kernel memory and MC object configuration; nothing is persisted to disk. DPNI/DPCON/DPBP state is programmed through MC commands and reset/closed on remove. RX pool state is tracked by per-channel `buf_count`, recycled address batches, and DPBP hardware counts. Per-CPU stats and SGT caches persist while the netdev exists. Flow steering rules are held in `priv->cls_rules`; hardware classifier keys and entries are programmed through DPNI and rebuilt by ethtool operations, not persisted across driver reload. Link state is mirrored in `priv->link_state`. Global PTP state comes from `dpaa2_ptp` and `dpaa2_phc_index`, exported by the DPRTC driver.

## Dependencies and integration points
This file depends on fsl-mc bus APIs, DPNI/DPCON/DPBP commands, DPAA2 IO/QBMan services, DMA/IOMMU translation, phylink through `dpaa2-mac.c`, PTP through `ptp_qoriq` and `dpaa2-ptp.c`, netdev/NAPI/ethtool/XDP/AF_XDP APIs, devlink helpers declared in the header, and optional DCB/debugfs support. It integrates with `dpaa2-ethtool.c` through exported hash/classifier helpers and `dpaa2_ethtool_ops`, with XSK helpers from other DPAA2 source files, and with `dpaa2-mac.c` for physical link management.

## Risks and edge cases
The highest-risk areas are descriptor ownership and DMA lifetime. `dpaa2_eth_free_tx_fd()` has to correctly distinguish SWA types for SKB, SG, XDP, XSK, and software TSO descriptors. Error paths in SG/TSO construction must unmap partially built entries without double-freeing shared SKBs. RX XDP redirect failure remaps or frees the original page and updates `buf_count`, which is sensitive to DMA mapping errors. The DPNI version gates for enqueue mode, pause support, classifier APIs, pending TX stats, and one-step register access must match firmware behavior. Link endpoint changes can disconnect/reconnect MAC at runtime, so `mac_lock` and comments about IRQ serialization are important. Taildrop behavior changes with pause/PFC and can affect loss under congestion. `dpaa2_eth_stop()` depends on bounded hardware drain waits and still continues if DPNI disable retries are exceeded.

## Test signals
Useful signals include successful probe/remove under DPNI endpoint changes; `ip link set up/down` with no buffer leaks; traffic through linear, SG, GSO/TSO, XDP_PASS, XDP_DROP, XDP_TX, XDP_REDIRECT, and AF_XDP zero-copy paths; ethtool stats showing RX/TX confirmations and buffer counts; classifier/hash changes through `ethtool -N/-n` and `ethtool -X` style flows; mqprio/TBF offload behavior; hardware timestamp TX/RX including one-step Sync; link IRQ and polling fallback; and fault injection around DMA mapping, portal busy retries, depleted DPBP buffers, and DPNI firmware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth.h

## Purpose
`dpaa2-eth.h` is the shared contract for the DPAA2 Ethernet driver. It defines queue, buffer, annotation, timestamp, classifier, statistics, XDP, and private-driver data structures used by the core driver, ethtool support, MAC support, devlink support, XSK support, DCB support, and debugfs code.

## Important APIs, types, and constants
The header sets hardware sizing and policy constants such as `DPAA2_ETH_STORE_SIZE`, `DPAA2_ETH_MFL`, `DPAA2_ETH_MAX_MTU`, RX/TX hardware annotation sizes, buffer-pool quota/refill thresholds, taildrop/congestion thresholds, queue limits, DPCON limits, SGT cache size, and enqueue retry bounds. `struct dpaa2_eth_swa` is the critical software annotation area stored in TX buffers; its union records ownership for linear SKB, SG SKB, XDP frame, XSK buffer, or software TSO descriptor. `struct dpaa2_fas`, `struct dpaa2_fapr`, and `struct dpaa2_faead` model hardware annotation status, parse results, and egress action descriptors.

Core runtime objects are `struct dpaa2_eth_fq`, `struct dpaa2_eth_channel`, `struct dpaa2_eth_bp`, and `struct dpaa2_eth_priv`. `dpaa2_eth_priv` aggregates the netdev, queue arrays, enqueue callback, channels, DPNI attributes/version/token, MC IO portal, buffer pools, per-CPU statistics, link and classifier state, XDP program, MAC pointer, timestamping workqueue, devlink data, and per-CPU descriptor array. Inline helpers include annotation accessors `dpaa2_get_fas()`, `dpaa2_get_ts()`, `dpaa2_get_fapr()`, `dpaa2_get_faead()`, version comparator `dpaa2_eth_cmp_dpni_ver()`, queue/TC/FS capability macros, pause-state helpers, `dpaa2_eth_needed_headroom()`, and lock-asserting MAC helpers.

## Control flow and integration
This header is included by `dpaa2-eth.c`, `dpaa2-ethtool.c`, `dpaa2-mac.c`, and adjacent feature files. It declares externally used functions for hash/classifier setup, devlink, buffer-pool allocation, RX processing helpers, IOVA translation, buffer recycling, XDP enqueue, XSK setup/wakeup/TX, TX FD cleanup, and SGT cache handling. It also exposes `dpaa2_ethtool_ops`, optional `dpaa2_eth_dcbnl_ops`, and global PTP objects.

## State and persistence behavior
The structures here describe volatile kernel and hardware-programmed state, not durable state. Hardware annotation layout must remain compatible with the DPNI buffer layout programmed at probe time. `DPAA2_ETH_SWA_SIZE` is a fixed 64-byte contract with `struct dpaa2_eth_swa`; adding fields risks corrupting TX cleanup. Capability macros encode MC firmware version gates that persist only as runtime decisions.

## Dependencies
The header depends on Linux netdev, VLAN, timestamping, devlink, XDP, DPAA2 IO/FD, DPNI/DPNI command headers, trace/debugfs headers, and `dpaa2-mac.h`. It exposes DPAA2 concepts to multiple compilation units, so changes here have broad build and ABI-like implications inside the driver.

## Risks and edge cases
The largest risks are layout and arithmetic mistakes. `DPAA2_ETH_MAX_SG_ENTRIES` depends on RX buffer size; headroom calculations interact with XDP and PTP TX annotation; queue-count macros assume one RX and TX-conf queue per channel; `dpaa2_eth_is_type_phy()` and `dpaa2_eth_has_mac()` require `mac_lock` held. `DPAA2_FAPR_SIZE` uses `sizeof((struct dpaa2_fapr))`, which is unusual but accepted by the compiler; any cleanup should be careful. Duplicated prototypes for DPBP allocation/free appear in the file and could be simplified, but they are harmless.

## Test signals
Compile coverage is the first signal because this header fans out widely. Runtime signals include correct `netdev->needed_headroom`, successful TX timestamping for SKBs with annotation headroom, XDP attach/detach with correct RX headroom, ethtool stats alignment with `DPAA2_ETH_CH_STATS`, classifier field offsets matching hardware keys, and no `WARN_ONCE` from unsupported classification fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ethtool.c

## Purpose
`dpaa2-ethtool.c` implements ethtool operations for DPAA2 DPNI netdevs. It reports driver/firmware identity, link settings, pause settings, hardware and software statistics, RX flow classification rules, RX hash fields, timestamping capabilities, RX copybreak tunable, DPIO interrupt coalescing, channel counts, and MAC-level standardized statistics.

## Important APIs and functions
`dpaa2_ethtool_ops` is the exported operation table consumed by `dpaa2_eth_netdev_init()`. Link and pause operations route to phylink when a DPMAC PHY/backplane is connected, otherwise they use cached DPNI link state and `dpni_set_link_cfg()`. Stats are assembled by `dpaa2_eth_get_ethtool_stats()` from DPNI statistic pages, per-CPU extra stats, channel stats, instantaneous FQ counts, buffer-pool counts, and optional DPMAC stats.

Classifier support is built around ethtool RX NFC. `dpaa2_eth_prep_eth_rule()`, `dpaa2_eth_prep_uip_rule()`, `dpaa2_eth_prep_l4_rule()`, `dpaa2_eth_prep_ext_rule()`, and `dpaa2_eth_prep_mac_ext_rule()` translate ethtool flow specs into the driver classifier key/mask layout. `dpaa2_eth_do_cls_rule()` DMA maps the key/mask pair and calls `dpni_add_fs_entry()` or `dpni_remove_fs_entry()`. `dpaa2_eth_update_cls_rule()` updates the software `priv->cls_rules` table and handles the no-mask firmware case by constraining all active rules to the same extracted field set. `dpaa2_eth_get_rxnfc()` and `dpaa2_eth_set_rxnfc()` expose rule listing, lookup, insertion, and deletion. `dpaa2_eth_get_rxfh_fields()` and `dpaa2_eth_set_rxfh_fields()` expose the single global RX hash key field mask.

## Control flow
Etntool calls enter through the kernel ethtool core. Read operations aggregate existing driver or MC state and return immediately. Mutating operations call into DPNI or phylink: pause settings check firmware support and reject autoneg for fixed/non-phylink DPNIs; RX hash changes rebuild the DPNI hash key through core helpers; RX class rule insertion removes any existing rule at that location, programs hardware, and then records the new software copy; coalescing updates every channel's affine DPIO and rolls back previous channels if a later update fails.

## State and persistence behavior
The file persists ethtool-installed classifier rules in `priv->cls_rules` for the life of the netdev. RX hash fields are cached in `priv->rx_hash_fields`. RX copybreak writes `priv->rx_copybreak`. Pause settings update `priv->link_state.options` after a successful DPNI configuration. Coalescing writes DPIO service state. None of this survives driver unload or DPNI reset except whatever the MC firmware naturally retains during the object lifetime.

## Dependencies and integration points
This file depends on `dpaa2-eth.h` helpers for classification key offsets/sizes, feature gates, pause helpers, queue counts, and MAC locking helpers. It calls DPNI MC APIs, DPAA2 IO query/coalescing APIs, phylink ethtool helpers, MAC stats functions from `dpaa2-mac.c`, and the global PTP state exported by `dpaa2-ptp.c`.

## Risks and edge cases
The stats array must stay synchronized with DPNI statistic pages; missing firmware pages are treated as zero only for `-EINVAL`. Classifier rules are limited: unsupported flow types, IPv4 TOS in several paths, VLAN ethertype extension, multiple field sets on no-mask firmware, out-of-range ring cookies, and unsupported hash bits are rejected. `array_index_nospec()` is correctly used for rule lookup. Coalescing rollback only restores channels already modified. MAC statistics are protected by `mac_lock`, but DPNI and per-CPU stats are read locklessly and can be approximate.

## Test signals
Use `ethtool -i`, `ethtool -S`, `ethtool -k`, `ethtool -c/-C`, `ethtool -l`, `ethtool -a/-A`, `ethtool -n/-N`, and timestamp capability queries. Validate rule insertion/deletion for ETHER, IP_USER, TCP/UDP/SCTP IPv4, VLAN extension, discard, and queue steering. Test no-mask firmware behavior by adding two rules with different field sets and expecting rejection. Verify MAC stats appear only when a MAC endpoint is connected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-mac.c

## Purpose
`dpaa2-mac.c` is the DPAA2 DPMAC support library used by DPNI Ethernet and switch ports. It opens DPMAC MC objects, discovers firmware/node/PHY interface details, creates phylink and optional Lynx PCS/SerDes integration, propagates phylink state into DPMAC link state, and fetches DPMAC hardware statistics for ethtool.

## Important APIs and functions
Public exports include `dpaa2_mac_open()`, `dpaa2_mac_close()`, `dpaa2_mac_connect()`, `dpaa2_mac_disconnect()`, `dpaa2_mac_start()`, `dpaa2_mac_stop()`, `dpaa2_mac_get_strings()`, `dpaa2_mac_get_ethtool_stats()`, and standardized RMON/pause/control/MAC stat getters. Feature detection is handled by `dpaa2_mac_detect_features()` based on DPMAC API versions for protocol change, bundled stats, and standard stats. `dpaa2_mac_get_node()` maps DPMAC IDs to OF or ACPI firmware nodes. `phy_mode()` and `dpmac_eth_if_mode()` translate DPMAC protocol enums to Linux `phy_interface_t` and back.

Phylink callbacks are `dpaa2_mac_select_pcs()`, `dpaa2_mac_config()`, `dpaa2_mac_link_up()`, and `dpaa2_mac_link_down()`. PCS and SerDes helpers include `dpaa2_pcs_create()`, `dpaa2_pcs_destroy()`, and `dpaa2_mac_set_supported_interfaces()`. Statistics use arrays of `struct dpmac_counter` mapping DPMAC counter IDs to either ethtool string names or offsets in standard ethtool stats structures. Newer firmware uses DMA-backed bundled reads prepared by `dpaa2_mac_setup_stats()` and consumed by `dpaa2_mac_get_standard_stats()` or `dpaa2_mac_get_ethtool_stats()`, while older firmware falls back to `dpmac_get_counter()` per counter.

## Control flow
`dpaa2_mac_open()` opens the DPMAC object, reads attributes and API version, detects features, finds the firmware node, links the netdev OF node, and allocates DMA buffers for supported stats bundles. `dpaa2_mac_connect()` validates interface mode, optionally obtains a SerDes PHY when protocol changes are supported, rejects fixed-link RGMII delay modes that the MAC cannot provide, creates PCS for non-RGMII PHY/backplane modes, initializes phylink capabilities and supported interfaces, creates phylink, and connects the firmware PHY. `dpaa2_mac_start()` powers SerDes and starts phylink under RTNL; `dpaa2_mac_stop()` stops phylink and powers SerDes off. Disconnect reverses phylink, PCS, and SerDes references. Close releases stats DMA buffers, closes DPMAC, and drops the firmware-node reference.

## State and persistence behavior
State lives in `struct dpaa2_mac`: MC device/handle, DPMAC attributes, API version, feature bits, current `dpmac_link_state`, phylink objects, selected interface mode, optional PCS, firmware node, optional SerDes PHY, and DMA buffers for stats. Link state is pushed into MC firmware by phylink callbacks but is not durable across object reset. Stats buffers are noncoherent DMA allocations and must be synchronized before and after MC statistics calls.

## Dependencies and integration points
This file depends on fsl-mc DPMAC commands, Linux phylink, PHY/SerDes APIs, Lynx PCS, OF/ACPI firmware properties, and ethtool standard stats structures. It is used by `dpaa2-eth.c` and switch support to manage physical endpoints and gather MAC counters.

## Risks and edge cases
Firmware-node discovery can defer probe if the parent DPRC fwnode is not ready. PCS lookup permits old DTs without `pcs-handle` but treats unavailable or failed PCS nodes differently. SerDes PHY is only attempted for OF nodes and non-RGMII modes when protocol change is supported. `dpaa2_mac_config()` changes both DPMAC protocol and SerDes mode at runtime, so ordering and error reporting matter. Stats paths must handle missing DMA buffers or unsupported feature bits and fall back cleanly. `dpaa2_mac_disconnect()` uses RTNL while disconnecting the PHY, so callers must avoid lock inversions.

## Test signals
Probe DPMAC endpoints with OF and ACPI descriptions, fixed link, external PHY, backplane, PCS-backed SGMII/1000BASE-X, and SerDes protocol-change-capable hardware. Exercise link up/down, pause negotiation, ethtool link settings, module unload/reload, endpoint hot changes, and both bundled and fallback stats retrieval. Fault injection around missing `pcs-handle`, deferred PCS/SerDes, and `dpmac_get_statistics()` should not leak DMA buffers or firmware-node references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-mac.h

## Purpose
`dpaa2-mac.h` declares the DPAA2 DPMAC helper interface and state structures shared between Ethernet and switch drivers. It provides the minimal abstraction for opening/closing MC DPMAC objects, connecting them to phylink, starting/stopping link management, and retrieving MAC statistics.

## Important APIs and types
`struct dpaa2_mac_stats` stores DMA memory and IOVA addresses for bundled counter index/value arrays. `struct dpaa2_mac` stores the MC device, DPMAC link state, netdev, MC portal, attributes, API version, feature bits, phylink config and instance, interface mode, link type, optional PCS, firmware node, optional SerDes PHY, and five stats bundles. `dpaa2_mac_is_type_phy()` returns true for PHY and backplane DPMAC link types and is used by DPNI and switch code to decide whether phylink owns link settings.

The header declares lifecycle calls `dpaa2_mac_open()`, `dpaa2_mac_close()`, `dpaa2_mac_connect()`, `dpaa2_mac_disconnect()`, `dpaa2_mac_start()`, and `dpaa2_mac_stop()`. It also declares ethtool string/count/stat helpers and standard RMON, pause, control, and MAC stat getters.

## Control flow and integration
Callers allocate `struct dpaa2_mac`, fill `mc_dev`, `mc_io`, and `net_dev`, call `dpaa2_mac_open()`, optionally call `dpaa2_mac_connect()` for PHY/backplane endpoints, then start/stop around netdev open/close and disconnect/close on teardown. Switch and DPNI ethtool code call the stat helpers under their own MAC locks.

## State and persistence behavior
The structures model runtime-only MC/phylink state and DMA buffers. They do not persist settings across driver reload. `fw_node` reference ownership is held by the `dpaa2_mac` instance after open and released during close.

## Dependencies
The header depends on OF, MDIO/OF net helpers, phylink, and DPMAC MC command headers. Users must also include locking discipline around their pointer to `struct dpaa2_mac`; this header does not provide synchronization primitives.

## Risks and edge cases
`dpaa2_mac_is_type_phy(NULL)` returns false, allowing callers to safely check absent endpoints. Any future expansion of `struct dpaa2_mac_stats` must preserve DMA sync/free expectations in `dpaa2-mac.c`. Start/stop require RTNL as enforced by the implementation, so callers must invoke them from netdev-open/stop contexts.

## Test signals
Build coverage across Ethernet and switch users is important. Runtime signals include successful phylink start/stop, no use-after-free when endpoint changes clear the MAC pointer, stable ethtool MAC stat counts/strings, and correct handling of ports without a DPMAC endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ptp.c

## Purpose
`dpaa2-ptp.c` registers the DPAA2 DPRTC real-time counter as a Linux PTP hardware clock using the shared `ptp_qoriq` engine. It provides the PHC and global pointer consumed by the Ethernet driver for RX/TX hardware timestamping and one-step PTP Sync support.

## Important APIs and functions
The driver matches fsl-mc objects of type `dprtc`. `dpaa2_ptp_caps` supplies the `ptp_clock_info` operations, mostly delegated to `ptp_qoriq` (`adjfine`, `adjtime`, `gettime64`, `settime64`) with local `dpaa2_ptp_enable()` for external timestamp/PPS interrupt masking. `dpaa2_ptp_irq_handler_thread()` converts DPRTC PPS and external timestamp events into PTP clock events or `extts_clean_up()` calls. `dpaa2_ptp_probe()` allocates `struct ptp_qoriq`, opens the DPRTC MC object, maps the `"fsl,dpaa2-ptp"` register range, allocates/request IRQs, enables DPRTC IRQs, initializes the qoriq PHC, and sets global `dpaa2_phc_index` and `dpaa2_ptp`. `dpaa2_ptp_remove()` unregisters/free the PHC and MC resources.

## Control flow
On probe, the MC portal and DPRTC handle are acquired first, then the OF node and MMIO base are found, then IRQ resources are allocated and enabled, and finally `ptp_qoriq_init()` publishes the PHC. IRQ handling reads status, reports PPS, cleans external timestamp channels 0/1, and clears handled bits. Enable/disable operations read the current DPRTC IRQ mask, set or clear the requested event bit, and write it back.

## State and persistence behavior
`dpaa2_ptp` and `dpaa2_phc_index` are global exported state shared with `dpaa2-eth.c` and `dpaa2-ethtool.c`. PHC time and adjustment state live in hardware through `ptp_qoriq`. IRQ masks are MC state. The driver does not persist configuration to disk. Remove resets the exported PHC index to `-1`, frees the PTP clock, closes the DPRTC handle, frees IRQs, and releases the MC portal.

## Dependencies and integration points
The file depends on fsl-mc DPRTC APIs, OF address lookup, threaded IRQ support, and `linux/fsl/ptp_qoriq.h`. Ethernet timestamping checks `dpaa2_ptp` before advertising and using timestamp features; ethtool timestamp info reports `dpaa2_phc_index`.

## Risks and edge cases
The compatible node lookup is global (`of_find_compatible_node(NULL, NULL, "fsl,dpaa2-ptp")`), so multiple DPRTC/PTP nodes would need careful review. Error paths must unmap MMIO and release OF node references; remove relies on `ptp_qoriq_free()` to release resources initialized by `ptp_qoriq_init()`. IRQ status errors return `IRQ_NONE`, while enable errors propagate to PTP core. Ethernet code must tolerate `dpaa2_ptp` being absent or removed.

## Test signals
Validate `/dev/ptp*` registration, `ethtool -T` PHC index on DPAA2 Ethernet, `phc2sys`/`ptp4l` adjustment behavior, PPS and external timestamp enable/disable, IRQ delivery and clear behavior, module remove/reload, and Ethernet TX/RX timestamping when the DPRTC driver is loaded before and after the DPNI driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ptp.h

## Purpose
`dpaa2-ptp.h` is the small shared declaration header for the DPAA2 DPRTC PTP clock driver. It exposes DPRTC command headers and the global PHC state used by DPAA2 Ethernet timestamping.

## Important APIs and types
The header includes `linux/fsl/ptp_qoriq.h`, `dprtc.h`, and `dprtc-cmd.h`. It declares `extern int dpaa2_phc_index` and `extern struct ptp_qoriq *dpaa2_ptp`, both defined/exported by `dpaa2-ptp.c` and also declared in `dpaa2-eth.h` for Ethernet users.

## Control flow and integration
There is no executable logic in this file. It exists so the PTP driver can use DPRTC APIs and so other DPAA2 files can refer to the shared PHC pointer/index. Ethernet code checks `dpaa2_ptp` before enabling timestamping and uses the pointer's `caps.gettime64()` path for one-step timestamp updates.

## State and persistence behavior
The state declared here is global in-kernel runtime state. `dpaa2_phc_index` is set to the registered PHC index or `-1`; `dpaa2_ptp` points at the live qoriq clock object while the DPRTC driver is bound.

## Dependencies
Consumers depend on the qoriq PTP core and DPRTC MC command definitions. The include guard is named `__RTC_H`, which is generic and could collide with another header guard in a larger include context.

## Risks and edge cases
Because the globals are shared without explicit locking in this header, users must handle `NULL` and driver ordering. A future change that supports multiple DPRTC clocks would need to replace these singletons with per-device association.

## Test signals
Build with Ethernet timestamping users, load/unload the DPRTC driver around active DPNI interfaces, and verify timestamp-capability reporting falls back cleanly when `dpaa2_ptp` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch-ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch-ethtool.c

## Purpose
`dpaa2-switch-ethtool.c` implements ethtool support for DPAA2 Ethernet switch port netdevs. It reports driver and firmware identity, link settings, DPSW per-port counters, and optional DPMAC statistics for switch ports.

## Important APIs and functions
`dpaa2_switch_port_ethtool_ops` is the exported ethtool operation table. `dpaa2_switch_get_drvinfo()` reads the DPSW API version and bus name. `dpaa2_switch_get_link_ksettings()` delegates to phylink for PHY/backplane ports, otherwise reads DPSW link state with `dpsw_if_get_link_state()`. `dpaa2_switch_set_link_ksettings()` similarly delegates to phylink for PHY-backed ports, or disables the switch interface, applies a `dpsw_link_cfg`, and re-enables the interface for fixed/non-phylink ports. Stats functions expose `dpaa2_switch_ethtool_counters` plus MAC-library counters and standard MAC stats.

## Control flow
Etntool stats requests copy counter names, then `dpaa2_switch_ethtool_get_stats()` iterates DPSW counter IDs and calls `dpsw_if_get_counter()` for the target port. After hardware switch counters, it takes `port_priv->mac_lock` and appends DPMAC stats if the port has a MAC. Link settings take the same MAC lock to decide whether phylink owns the port.

## State and persistence behavior
This file does not own long-lived state. It reads `struct ethsw_port_priv` and `struct ethsw_core` created by switch core code. Link setting changes are written to DPSW MC state and may require the interface to be temporarily disabled. Stats are read from hardware.

## Dependencies and integration points
The file depends on `dpaa2-switch.h`, DPSW MC APIs, phylink ethtool helpers, and the shared MAC stats library from `dpaa2-mac.c`. It is separate from DPNI Ethernet ethtool support and operates on switch-port private data.

## Risks and edge cases
If re-enabling a port after a fixed-link setting change fails, the function returns that error and the port may remain disabled. `get_drvinfo()` reports `"N/A"` firmware version if API version read fails. MAC stats are conditional on a connected MAC and protected by `mac_lock`. The file does not expose pause stats unlike the DPNI ethtool path.

## Test signals
Use `ethtool -i`, `ethtool -S`, and link settings on switch ports with and without PHY-backed DPMAC endpoints. Validate interface disable/re-enable around fixed-port setting changes, firmware-version failure handling, and MAC stat string/count alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch-flower.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch-flower.c

## Purpose
`dpaa2-switch-flower.c` translates Linux traffic-control flower and matchall offloads for DPAA2 switch ports into DPSW ACL entries or reflection/mirroring rules. It supports drop, trap, redirect, and mirred actions with a constrained set of match keys.

## Important APIs and functions
The public entry points are `dpaa2_switch_cls_flower_replace()`, `dpaa2_switch_cls_flower_destroy()`, `dpaa2_switch_cls_matchall_replace()`, `dpaa2_switch_cls_matchall_destroy()`, `dpaa2_switch_block_offload_mirror()`, `dpaa2_switch_block_unoffload_mirror()`, and `dpaa2_switch_acl_entry_add()`. `dpaa2_switch_flower_parse_key()` maps supported flower keys into `struct dpsw_acl_key`: basic EtherType/IP protocol, Ethernet addresses, VLAN ID/TPID/PCP/DEI, IPv4 addresses, L4 ports, and DSCP. `dpaa2_switch_tc_parse_action_acl()` maps trap/redirect/drop actions to DPSW ACL results. Mirror parsing is split into `dpaa2_switch_flower_parse_mirror_key()` for per-VLAN flower mirroring and matchall mirroring for ingress-all reflection.

ACL table helpers maintain `block->acl_entries` ordered by tc priority and translate list order into DPSW precedence values. Adding an entry may reprogram higher-priority existing entries to make space. Removing an entry deletes it from hardware/list and shifts preceding entries down. Mirror helpers maintain `block->mirror_entries`, configure a single switch-wide reflection destination, and add/remove `dpsw_if_add_reflection()` filters on every port represented by the filter block.

## Control flow
For flower replace, the code first enforces exactly one action. Drop/trap/redirect allocate an ACL entry, parse keys, parse action, assign priority/cookie, insert into the ordered ACL table, and program hardware. Mirred validates the destination as another DPAA2 switch port, enforces the single mirror-port hardware limitation, parses a VLAN-only key, rejects duplicate VLAN mirror filters, allocates a mirror entry, and applies reflection to all ports in the block. Destroy finds the cookie in ACL entries first, then mirror entries, and removes the matching hardware state.

For matchall replace, the same single-action rule applies. Drop/trap/redirect create an ACL entry with no key match, while mirred creates an ingress-all reflection entry. Block offload/unoffload mirror functions apply or remove all existing mirror rules when a port joins or leaves a shared block, with unwind logic on partial failure.

## State and persistence behavior
Software state is held in per-filter-block linked lists: `acl_entries`, `mirror_entries`, rule counts, cookies, priorities, and mirror configs. Hardware state is programmed into DPSW ACL tables and reflection filters. It is runtime-only and must be rebuilt by tc if the driver or switch object is reset. `ethsw->mirror_port` tracks the one active mirror destination or `num_ifs` as the sentinel for none.

## Dependencies and integration points
The file depends on Linux flow offload dissector/action APIs and `dpaa2-switch.h` data structures/helpers. It calls DPSW MC APIs `dpsw_acl_prepare_entry_cfg()`, `dpsw_acl_add_entry()`, `dpsw_acl_remove_entry()`, `dpsw_set_reflection_if()`, `dpsw_if_add_reflection()`, and `dpsw_if_remove_reflection()`. It uses netlink extack messages to explain unsupported keys/actions.

## Risks and edge cases
Supported keys are intentionally narrow. IPv6 address key is listed as accepted in the top-level mask but is not populated into the DPSW ACL key, which should be reviewed because it could silently ignore IPv6 address matches. TTL and ECN matching are rejected; DSCP is supported by shifting TOS. Mirroring supports only one destination port and only VLAN ID or matchall filters. Per-VLAN mirroring requires the VLAN to already be installed on every block port. ACL precedence reprogramming can leave hardware partially changed if a mid-sequence MC call fails; callers receive an error, but list/hardware reconciliation should be tested. `list_add(&entry->list, pos->prev)` depends on list-head semantics and priority iteration correctness.

## Test signals
Exercise tc flower drop/trap/redirect with Ethernet, VLAN, IPv4, ports, and DSCP keys; unsupported TTL/ECN/extra keys; duplicate cookies and priority ordering; ACL table full behavior; destroy by cookie; matchall drop/trap/redirect; mirred VLAN and matchall reflection to a DPAA2 switch port; rejection of non-switch destinations, multiple mirror destinations, duplicate mirror filters, and VLAN-not-installed cases. Validate hardware counters and packet behavior after partial add/remove failures and when ports join/leave shared blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch-flower.c -->
