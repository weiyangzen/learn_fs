# subset-b-004577 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_mirror.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_mirror.c

### Purpose
`sparx5_mirror.c` implements TC matchall mirroring support for Microchip Sparx5-family switch ports. It maps a source port, monitor port, and ingress/egress direction onto the chip's small set of ANA mirror probes and QFWD frame-copy monitor-port registers.

### Important APIs, Types, And Functions
The exported entry points are `sparx5_mirror_add()`, `sparx5_mirror_del()`, and `sparx5_mirror_stats()`, all operating on `struct sparx5_mall_entry`. Internal helpers read/write probe membership (`sparx5_mirror_port_get/add/del()`), direction (`sparx5_mirror_dir_get/set()`), and monitor port (`sparx5_mirror_monitor_get/set()`). `SPX5_MIRROR_PROBE_MAX` limits hardware probes to three, and the QFWD monitor register index is offset by `SPX5_QFWD_MP_OFFSET`.

### Control Flow
Adding a mirror rejects self-mirroring, checks that the source port is not already used as a monitor port, tries to reuse an existing probe with the same direction and monitor port, then falls back to an empty probe. It sets the source port bit in `ANA_AC_PROBE_PORT_CFG{,1}`, writes probe direction, writes the monitor port, and stores the selected probe index in the mall entry. Deletion removes the source port from the probe and only disables direction and resets monitor port when the probe becomes empty.

### State, Persistence, And Dependencies
Persistent state is split between hardware registers and `entry->mirror.idx`. Statistics baselining is kept in `entry->port->mirror_stats` and updated from `sparx5_get_stats64()`. The file depends on `sparx5_main.h`, generated register macros, TC mall entry definitions, `is_sparx5()` for 64-bit port masks, and Linux flow stats helpers.

### Integration Points
This is called from `sparx5_tc_matchall.c` for `FLOW_ACTION_MIRRED` matchall filters and reports hardware stats back through `TC_CLSMATCHALL_STATS`. It shares port statistics with the normal netdev stats path and uses switch hardware probes rather than VCAP rules.

### Risks
Only three probes exist, so multi-user mirror programming can return `-ENOENT`. Monitor-port exclusion is checked against the source port only, so callers must ensure action devices are valid Sparx5 ports. Probe state is hardware-resident; inconsistent `entry->mirror.idx` would delete the wrong probe membership. `do_div()` mutates the local `reg` variable intentionally, but this is easy to misread.

### Test Signals
Test ingress and egress mirror add/delete, duplicate source detection, source equal monitor rejection, monitor-port reuse, exhaustion after three distinct probe configurations, stats deltas across repeated reads, and delete behavior when multiple source ports share one probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_mirror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_netdev.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_netdev.c

### Purpose
`sparx5_netdev.c` creates, registers, opens, stops, and exposes Linux `net_device` instances for Sparx5 front-panel ports. It bridges Linux netdev operations to phylink, SerDes power management, IFH construction, MACT programming, TC offload, and PTP timestamp configuration.

### Important APIs, Types, And Functions
The file exports `sparx5_create_netdev()`, `sparx5_register_netdevs()`, `sparx5_destroy_netdevs()`, `sparx5_unregister_netdevs()`, and `sparx5_netdevice_check()`. The `sparx5_port_netdev_ops` table wires `ndo_open`, `ndo_stop`, `ndo_start_xmit`, multicast sync, stats, parent ID, TC setup, and hwtstamp get/set callbacks. IFH builders include `sparx5_set_port_ifh()`, `sparx5_set_port_ifh_rew_op()`, `sparx5_set_port_ifh_pdu_type()`, `sparx5_set_port_ifh_pdu_w16_offset()`, and `sparx5_set_port_ifh_timestamp()`.

### Control Flow
Open enables the hardware port, connects phylink to the PHY, starts phylink, and powers up SerDes for fixed-link or in-band modes without `ndev->phydev`. Stop disables the port, stops/disconnects phylink, and powers SerDes down. Netdev creation allocates per-port private storage with TX queues equal to `SPX5_PRIOS`, marks TC offload feature support, attaches ethtool/netdev ops, and generates a MAC from the switch base MAC. Registration iterates existing ports and starts each injection timeout timer.

### State, Persistence, And Dependencies
State lives in `struct sparx5_port` private data, `port->conf`, phylink objects, SerDes PHY state, netdev feature flags, and MACT entries for local MAC addresses. IFH encoding writes a 36-byte header used by the packet injection path. The file depends on `sparx5_port.c`, `sparx5_packet.c`, `sparx5_ptp.c`, `sparx5_tc.c`, ethtool support, MACT helpers, and generated IFH bit positions.

### Integration Points
This file is the Linux networking face of the driver. It integrates with phylink for link negotiation, `sparx5_port_xmit_impl()` for TX, switchdev/bridge code through `sparx5_netdevice_check()`, TC through `ndo_setup_tc`, and PTP through netdev hwtstamp operations.

### Risks
Open error unwinding must leave the port disabled and phylink disconnected. Destroy calls `sparx5_port_stop()` under RTNL and then disconnects phy again, so lifecycle assumptions should be checked around phylink state. IFH bitfield encoding is endian/position-sensitive and allows widths only up to 40 bits. MAC address changes forget and learn entries using the current PVID, so bridge/VLAN state affects host reachability.

### Test Signals
Test netdev register/unregister cycles, open/stop with external PHY and SerDes-only ports, failed `phylink_of_phy_connect()` unwind, MAC address change programming, hwtstamp unsupported when PTP is disabled, TC setup dispatch, parent ID stability, and packet TX IFH fields by hardware or register-level tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_packet.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_packet.c

### Purpose
`sparx5_packet.c` implements manual CPU-port packet extraction and injection for Sparx5 when FDMA is not used or for common packet handling support. It parses extraction IFHs, builds receive SKBs, injects transmit SKBs with IFHs, and handles TX queue recovery after injection watermark backpressure.

### Important APIs, Types, And Functions
Exports are `sparx5_xtr_flush()`, `sparx5_ifh_parse()`, `sparx5_port_xmit_impl()`, `sparx5_manual_injection_mode()`, `sparx5_xtr_handler()`, and `sparx5_port_inj_timer_setup()`. `sparx5_xtr_grp()` reads one frame from `QS_XTR_RD()`, `sparx5_inject()` writes SOF, IFH, payload, padding, EOF, and dummy CRC to `QS_INJ_WR()`, and `sparx5_injection_timeout()` clears watermark counters and wakes the TX queue.

### Control Flow
RX interrupt handling polls up to 64 frames while extraction data is present. Each frame starts with an IFH, which yields source port and timestamp. The body loop reads words until EOF, PRUNED, or ABORT escape words; good frames are trimmed by FCS length, optionally marked `offload_fwd_mark`, receive timestamped, protocol-decoded, counted, and delivered via `netif_rx()`. TX builds an IFH, optionally requests PTP timestamp state and adds rewrite metadata, then sends through FDMA if available or manual injection under `tx_lock`. Successful Sparx5 manual TX consumes the skb except for two-step PTP frames, which are held until timestamp completion.

### State, Persistence, And Dependencies
RX/TX state is mostly hardware FIFO state plus per-netdev stats and `sparx5->tx` counters. PTP TX state is stored in skb control block fields and per-port PTP queues. Backpressure state uses the netdev queue and per-port hrtimer. Dependencies include generated QS/DSM register macros, IFH helpers from `sparx5_netdev.c`, PTP helpers, FDMA ops, and `sparx5_get_internal_port()`.

### Integration Points
This file is used by netdev `ndo_start_xmit`, RX IRQ setup, manual injection initialization during driver bring-up, and PTP timestamp paths. It also cooperates with bridge offload by marking already-forwarded SKBs.

### Risks
RX allocation uses `mtu + ETH_HLEN`; oversized frames or malformed extraction could overrun expectations if hardware delivers unexpected lengths. EOF byte accounting and byte-swap handling are delicate. Manual TX returns `-EBUSY` from `sparx5_inject()` but the public xmit path treats negative non-busy values as drops. Two-step PTP skb ownership differs from normal TX and must match timestamp IRQ release.

### Test Signals
Exercise extraction of normal, abort, pruned, and inactive-port frames; IFH timestamp parsing; bridge offload mark; manual injection queue-not-ready and watermark recovery; FDMA and manual TX paths; small frames requiring padding; and PTP two-step busy/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_pgid.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_pgid.c

### Purpose
`sparx5_pgid.c` manages allocation of packet group IDs used for flood, CPU, and multicast forwarding masks in the Sparx5 analyzer block.

### Important APIs, Types, And Functions
The exported functions are `sparx5_pgid_init()`, `sparx5_pgid_alloc_mcast()`, `sparx5_pgid_free()`, and `sparx5_get_pgid()`. They operate on `sparx5->pgid_map[]`, whose entries use states such as `SPX5_PGID_FREE`, `SPX5_PGID_RESERVED`, and `SPX5_PGID_MULTICAST`.

### Control Flow
Initialization marks every PGID free, then reserves the fixed PGIDs through the CPU PGID. Multicast allocation scans from `PGID_MCAST_START` translated through `sparx5_get_pgid()` to the chip-specific absolute PGID space. Freeing rejects fixed PGIDs, out-of-range IDs, and already-free entries before returning the slot to the free state.

### State, Persistence, And Dependencies
State is in-memory only in `sparx5->pgid_map`; hardware PGID masks are updated by other files after an ID is allocated. `sparx5_get_pgid()` maps logical PGID constants after the physical front-port range by adding `n_ports`.

### Integration Points
Switchdev MDB handling allocates multicast PGIDs here, bridge flood programming uses fixed PGIDs, and MACT entries can target allocated PGIDs. The file relies on `sparx5_main.h` constants and the runtime `sparx5->data->consts` table.

### Risks
The allocator is linear and has no lock of its own; callers must serialize if concurrent MDB changes are possible. Freeing an ID does not clear hardware masks; callers must clear them first. Logical-to-absolute PGID mapping depends on chip constants matching register layout.

### Test Signals
Validate initialization reservations, allocation exhaustion, rejection of CPU/flood PGID free attempts, reuse after free, and correct interaction with MDB add/delete hardware mask clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_pgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_phylink.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_phylink.c

### Purpose
`sparx5_phylink.c` adapts Linux phylink MAC/PCS callbacks to Sparx5 port and PCS configuration. It selects the per-port PCS, translates phylink negotiation state into `struct sparx5_port_config`, and reports PCS link state back to phylink.

### Important APIs, Types, And Functions
It exports `sparx5_phylink_mac_ops` and `sparx5_phylink_pcs_ops`. Key helpers are `port_conf_has_changed()`, `sparx5_phylink_mac_select_pcs()`, `sparx5_phylink_mac_link_up()`, `sparx5_pcs_get_state()`, and `sparx5_pcs_config()`.

### Control Flow
MAC PCS selection returns `port->phylink_pcs` for SGMII, QSGMII, 1000BASE-X, 2500BASE-X, and Base-R modes; other modes do not use a PCS. Link-up copies current port config, applies resolved speed/duplex/pause, and calls `sparx5_port_config()`. PCS config builds a config from interface, in-band negotiation mode, advertised pause bits, and Base-R media type, skips programming if unchanged, and otherwise calls `sparx5_port_pcs_set()`. PCS state reads hardware via `sparx5_get_port_status()`.

### State, Persistence, And Dependencies
Persistent state is `port->conf`, the phylink PCS object embedded in `struct sparx5_port`, and hardware PCS/MAC registers programmed by `sparx5_port.c`. The file depends on Linux phylink, SFP/PHY interface mode enums, and Sparx5 port helpers.

### Integration Points
Netdev open starts phylink, and phylink invokes these callbacks during negotiation, link-up, and state polling. The PCS callbacks are a key integration point for SerDes, in-band autonegotiation, pause advertisement, and MAC configuration.

### Risks
The expression setting `conf.inband` is true for both disabled and enabled PCS negotiation modes, so interpretation depends on phylink semantics and port code. `mac_link_down()` and PCS autoneg restart are no-ops, making disable/restart behavior rely on later config changes. Base-R media is inferred only from advertised `FIBRE`.

### Test Signals
Test PCS selection for each supported interface, link-up speed/pause propagation, no-op config when unchanged, in-band pause advertisement, Base-R media selection, link state reporting after sticky link-down, and unsupported interface handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_phylink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_police.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_police.c

### Purpose
`sparx5_police.c` programs Sparx5 service policer hardware for PSFP flow meters. It converts software rate/burst parameters into SDLB token and threshold registers.

### Important APIs, Types, And Functions
The public function is `sparx5_policer_conf_set()`, dispatching on `struct sparx5_policer::type`. The implemented type is `SPX5_POL_SERVICE`, handled by `sparx5_policer_service_conf_set()`. It uses `sparx5_sdlb_pup_token_get()` and `ops->get_sdlb_group()`.

### Control Flow
For service policers, the code retrieves the SDLB group metadata, converts kbit rate to bit/s, computes current and maximum PUP tokens for the group interval, derives burst threshold in group minimum-burst units, and writes token, max-token, and threshold fields in `ANA_AC_SDLB_*` registers. Unknown policer types currently return success without programming.

### State, Persistence, And Dependencies
Policer state persists in hardware SDLB registers indexed by `pol->idx` and group zero subindex. Software state is carried by `struct sparx5_policer`. Dependencies include SDLB group definitions, generated ANA_AC register macros, and chip ops.

### Integration Points
`sparx5_psfp.c` uses this file when adding or deleting flow meters from TC flower police actions. The programmed policer is linked into SDLB groups by `sparx5_sdlb_group_add()` or removed by `sparx5_sdlb_group_del()`.

### Risks
Unsupported policer types silently succeed, which can hide caller mistakes. Rate/burst unit conversions must remain aligned with TC flower parsing and SDLB group initialization. Register programming assumes the caller has selected an appropriate group and index.

### Test Signals
Test police add with representative rates/bursts, zero rate deletion path via PSFP, group max-token calculation, threshold rounding, maximum rate rejection in TC flower, and unknown type behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_police.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_pool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_pool.c

### Purpose
`sparx5_pool.c` provides a small reference-counted ID pool used by PSFP stream filters, stream gates, and flow meters. It maps one-based external IDs to zero-based array entries.

### Important APIs, Types, And Functions
The file exports `sparx5_pool_idx_to_id()`, `sparx5_pool_put()`, `sparx5_pool_get()`, and `sparx5_pool_get_with_idx()`. It operates on arrays of `struct sparx5_pool_entry`, whose fields include `ref_cnt` and a caller-defined `idx`.

### Control Flow
`sparx5_pool_get()` returns the first unused entry and increments its reference count. `sparx5_pool_get_with_idx()` prefers an existing entry with matching `idx` and positive reference count, otherwise remembers the first free entry, stores `idx`, and increments its reference count. `sparx5_pool_put()` rejects zero references and decrements the count.

### State, Persistence, And Dependencies
Pool state is in static arrays owned by users such as `sparx5_psfp.c`; this file only manipulates counters and indices. There is no locking, persistence, or hardware access.

### Integration Points
PSFP uses the generic pool to share stream gates and flow meters for identical TC hardware indices and to allocate unique stream filters. One-based IDs match hardware conventions used by PSFP lookup helpers.

### Risks
The `size` argument is not bounds-checked against an incoming ID in `sparx5_pool_put()`, so callers must pass valid IDs. No lock protects shared static pools. `idx` remains stale after refcount reaches zero until reused, which is fine for current matching because refcount must be positive.

### Test Signals
Test first-free allocation, one-based ID conversion, reference increments for repeated `idx`, decrement-to-zero behavior, invalid put on free entries, and exhaustion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_port.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_port.c

### Purpose
`sparx5_port.c` is the main port hardware programming file. It handles link status decoding, speed/interface validation, safe port disable/flush, SerDes setup, PCS and MAC configuration for low-speed and Base-R devices, muxing, flow control, VLAN tag awareness, forwarding urgency, and per-port QoS classification/rewrite programming.

### Important APIs, Types, And Functions
Exports include `sparx5_get_port_status()`, `sparx5_serdes_set()`, `sparx5_port_mux_set()`, `sparx5_port_fwd_urg()`, `sparx5_port_pcs_set()`, `sparx5_port_config()`, `sparx5_port_init()`, `sparx5_port_enable()`, `sparx5_port_qos_set()` and its PCP/DSCP helpers, and `sparx5_get_internal_port()`. Internal control helpers include `sparx5_port_disable()`, `sparx5_port_flush_poll()`, `sparx5_dev_switch()`, `sparx5_port_pcs_low_set()`, `sparx5_port_pcs_high_set()`, and `sparx5_port_config_low_set()`.

### Control Flow
Status reads dispatch on current `port->conf.portmode`: 1G/2.5G PCS paths decode SGMII or Clause 37 words, while Base-R paths inspect high-speed MAC sticky status. Reconfiguration first validates speed and interface compatibility, optionally configures RGMII through chip ops, programs MAC speed/duplex registers for low-speed modes, applies flow control, sets DSM watermarks, and enables QFWD forwarding with a speed-derived urgency. PCS reconfiguration safely disables the active hardware device, switches between low/high-speed device mappings when necessary, programs SerDes and PCS, toggles counter collection, and saves `port->conf`.

### State, Persistence, And Dependencies
State is both hardware-resident and cached in `struct sparx5_port` (`conf`, VLAN tag settings, signal-detect settings, QoS config inputs). Disable/flush manipulates QFWD, HSCH, QSYS, DSM, DEV2G5, DEV10G, PCS10G, and DEV25G registers. Dependencies include Linux PHY/SerDes APIs, DCB constants, generated register macros, chip ops for port capabilities and RGMII, and global constants in `sparx5_main.h`.

### Integration Points
Phylink uses this file for PCS config, link-up MAC config, and link status. Netdev open/stop uses `sparx5_port_enable()` and SerDes power state. VLAN, QoS, PTP, and switchdev behavior depend on the tag, timestamp, and forwarding settings programmed here.

### Risks
The disable sequence is long and hardware-order-sensitive; missed flush completion can leave queues or MAC domains inconsistent. Speed validation has chip-family-specific capability assumptions. Multiple functions save `port->conf`, so callers must understand whether PCS-only or MAC config is being updated. QoS DSCP/PCP maps are global or per-port depending on register block, so per-port APIs may affect broader state.

### Test Signals
Use hardware/register tests for every supported interface and speed, link-down sticky clearing, PCS low/high transitions, QSGMII muxing, SerDes reset/power sequencing, queue flush timeout, pause TX/RX behavior, VLAN tag awareness, port enable/disable, and PCP/DSCP classification and rewrite tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_port.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_port.h

### Purpose
`sparx5_port.h` declares the public port configuration, status, and QoS programming interface for Sparx5 ports and provides inline helpers that classify port numbers and map them to hardware target instances.

### Important APIs, Types, And Functions
It defines PCP/DSCP rewrite mode constants, inline capability helpers (`sparx5_port_is_2g5()`, `sparx5_port_is_5g()`, `sparx5_port_is_10g()`, `sparx5_port_is_25g()`, `sparx5_port_is_rgmii()`), target mapping helpers, `struct sparx5_port_status`, and QoS map structs for PCP, PCP rewrite, DSCP, DSCP rewrite, and defaults. It declares port init/config/PCS/SerDes/status/enable and QoS functions implemented in `sparx5_port.c`.

### Control Flow
There is no runtime control flow beyond inline mapping. Port classes determine whether callers use DEV2G5, DEV5G, DEV10G, or DEV25G blocks and which PCS target applies. QoS structs encode the data passed down to register programming functions.

### State, Persistence, And Dependencies
The header has no storage but defines the shape of state consumed by the driver. It depends on `sparx5_main.h` for `struct sparx5`, `struct sparx5_port`, and `SPX5_PRIOS`.

### Integration Points
Included by netdev, phylink, and port implementation files. It is the contract between link-management code and hardware programming, and between QoS/DCB/TC code and per-port classifier/rewrite registers.

### Risks
Inline port-number ranges encode Sparx5 topology directly; variant support depends on `sparx5_ops` wrappers where available. `sparx5_port_is_rgmii()` returns false in this variant, so LAN969x or future chips must override through ops rather than this inline. QoS map array dimensions must match hardware register tables.

### Test Signals
Compile coverage across all users, unit-style validation of port-number mapping for boundary ports, and integration tests confirming chip ops override behavior for non-Sparx5 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_psfp.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_psfp.c

### Purpose
`sparx5_psfp.c` implements IEEE 802.1Qci-style PSFP resources: stream filters, stream gates, flow meters, ISDX mappings, and initialization of service dual leaky bucket groups. It is primarily driven by TC flower gate and police actions.

### Important APIs, Types, And Functions
Exports include resource lookup helpers `sparx5_psfp_isdx_get_sf()`, `sparx5_psfp_isdx_get_fm()`, `sparx5_psfp_sf_get_sg()`, `sparx5_isdx_conf_set()`, add/delete functions for stream filters, gates, and flow meters, and `sparx5_psfp_init()`. Static pools `sparx5_psfp_sf_pool`, `sparx5_psfp_sg_pool`, and `sparx5_psfp_fm_pool` track software resource references.

### Control Flow
Adding a stream gate obtains or shares a gate by TC index, computes a future base time using `sparx5_new_base_time()`, writes admin gate parameters and cumulative gate-control intervals, then triggers a hardware config-change copy to operational state. Flow meter add obtains or shares a meter, selects an SDLB group by rate/burst, programs policer registers, and links the meter into the group. Stream filter add allocates a filter and writes gate/max-SDU/block settings. TC flower maps ISDX to stream filter and optional flow meter.

### State, Persistence, And Dependencies
State spans static software pools, hardware ANA_AC TSN stream filter/gate registers, ANA_L2 ISDX mapping registers, and SDLB policer/list registers. Dependencies include pool helpers, SDLB helpers, policer programming, PTP time via QoS base-time calculation, generated register macros, and chip constants for resource counts.

### Integration Points
`sparx5_tc_flower.c` creates and frees PSFP resources for `FLOW_ACTION_GATE` and `FLOW_ACTION_POLICE`. `sparx5_qos_init()` calls `sparx5_psfp_init()` to initialize SDLB groups, enable SG cycle-time updates, and enable ISDX lookup.

### Risks
Resource pools are static and unprotected; concurrent TC changes need external serialization. Delete paths respect reference counts, so wrong IDs can leak or prematurely reset shared resources. Hardware gate intervals are cumulative, which differs from TC input intervals. Timeout in config-change wait is logged only with `pr_debug()`.

### Test Signals
Test gate add/delete with shared TC indices, flow meter add/delete with shared police indices, always-open gate fallback for police-only filters, ISDX mapping cleanup, max-SDU programming, invalid gate parameters from TC, and SDLB group selection under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_psfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_ptp.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_ptp.c

### Purpose
`sparx5_ptp.c` implements hardware timestamping and PHC support for Sparx5. It registers PTP clocks, programs TOD increments for the switch core clock, handles hwtstamp configuration, classifies PTP packets for one-step/two-step rewrite, manages pending TX timestamp SKBs, and reconstructs RX/TX timestamps.

### Important APIs, Types, And Functions
Exports include `sparx5_ptp_hwtstamp_set/get()`, `sparx5_ptp_txtstamp_request()`, `sparx5_ptp_txtstamp_release()`, `sparx5_get_hwtimestamp()`, `sparx5_ptp_irq_handler()`, `sparx5_ptp_gettime64()`, `sparx5_ptp_init()`, `sparx5_ptp_deinit()`, and `sparx5_ptp_rxtstamp()`. PHC operations are `sparx5_ptp_adjfine()`, `sparx5_ptp_settime64()`, `sparx5_ptp_gettime64()`, and `sparx5_ptp_adjtime()`.

### Control Flow
Initialization requests the PTP IRQ when supported, registers three PHCs, initializes locks and per-port TX queues, programs nominal TOD increments for each domain, and enables master counters. TX hwtstamp configuration sets a per-port rewrite command and normalizes RX filters to `HWTSTAMP_FILTER_ALL`. TX timestamp request classifies the skb, stores IFH rewrite metadata, queues two-step PTP SKBs with a rolling timestamp ID, and marks `SKBTX_IN_PROGRESS`. The IRQ drains hardware timestamp FIFO entries, matches IDs to queued SKBs, reconstructs time using current TOD seconds plus hardware nanoseconds, reports timestamps, and frees SKBs.

### State, Persistence, And Dependencies
State lives in `sparx5->phc[]`, locks, `sparx5->ptp_skbs`, per-port `tx_skbs` and `ts_id`, per-port `ptp_cmd`, and PTP/TOD hardware registers. Dependencies include Linux PTP clock APIs, `ptp_classify_raw()`, `ptp_parse_header()`, skb timestamp APIs, generated PTP/REW registers, core clock constants, and netdev bridge masks.

### Integration Points
Netdev hwtstamp ops call set/get, packet TX calls txtstamp request and writes IFH fields, packet RX calls `sparx5_ptp_rxtstamp()`, and QoS/PSFP base-time calculation reads PHC time.

### Risks
PTP is rejected for bridged ports to avoid duplicate forwarded transparent-clock frames. Two-step skb ownership is subtle and bounded by `SPARX5_MAX_PTP_ID`; leaks or double frees can occur if busy/error paths diverge. `sparx5_ptp_txtstamp_release()` decrements `port->ts_id`, which can underflow around zero. Clock adjustment math is core-clock-specific and split to avoid overflow.

### Test Signals
Test hwtstamp filter normalization, bridge-port rejection, one-step and two-step Sync/Delay packet classification, timestamp ID wrap, pending queue timeout cleanup, IRQ matching and overflow warning, PHC get/set/adjfine/adjtime for each core clock, RX timestamp seconds rollover, and deinit queue purging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_qos.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_qos.c

### Purpose
`sparx5_qos.c` implements scheduling, shaping, DWRR, MQPRIO, TBF, ETS, PSFP initialization, and base-time calculation for Sparx5 QoS offload. It programs HSCH leak groups and scheduler elements used by TC qdiscs.

### Important APIs, Types, And Functions
Public functions include `sparx5_new_base_time()`, `sparx5_get_hsch_max_group_rate()`, `sparx5_qos_init()`, `sparx5_tc_mqprio_add/del()`, `sparx5_tc_tbf_add/del()`, and `sparx5_tc_ets_add/del()`. Internal leak-group operations maintain circular linked lists in hardware using `sparx5_lg_add()`, `sparx5_lg_del()`, and `sparx5_lg_conf_set()`. Shaper and DWRR programming are done by `sparx5_shaper_conf_set()` and `sparx5_dwrr_conf_set()`.

### Control Flow
QoS initialization derives leak group timing and resolution from `HSCH_SYS_CLK_PER`, disables all groups to mark them empty, initializes DCB, then initializes PSFP. TBF add converts bytes/s to kbit/s, selects a leak group by rate, validates min/max rate and burst, scales to hardware resolution and 4096-byte burst units, writes scheduler element mode/rate/burst, and links the element into the chosen group. ETS add validates bands in the TC layer, computes minimum weight, reverses priority bands to match hardware preference, converts weights to DWRR costs, and writes DWRR entries.

### State, Persistence, And Dependencies
Leak group metadata is cached in a static `layers[]` array, while active group membership persists in HSCH registers. Netdev TC state is reflected in Linux netdev TC queues. The file depends on PTP time for future base-time calculation, DCB initialization, PSFP initialization, generated HSCH registers, and qdisc offload structs.

### Integration Points
`sparx5_tc.c` dispatches MQPRIO, TBF, and ETS qdisc offloads here. `sparx5_psfp.c` uses `sparx5_new_base_time()` for stream gate basetimes. DCB support is initialized as part of QoS.

### Risks
Static `layers[]` is global, not per device, so multi-device assumptions should be reviewed. `sparx5_tc_tbf_del()` does not check failure from group lookup before using `group`. Leak group linked-list manipulation is hardware-state-dependent and uses warnings rather than graceful recovery for missing members. Base-time math assumes cycle time is nonzero.

### Test Signals
Test leak group init on each core clock, TBF add/delete across root and queue parents, rate/burst boundary rejection, moving a scheduler element between leak groups, MQPRIO exactly eight traffic classes, ETS strict/DWRR combinations and reverse priority mapping, and PSFP initialization side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_qos.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_qos.h

### Purpose
`sparx5_qos.h` defines scheduler-layer constants, hardware shaper limits, leak-group metadata, DWRR state, and the public TC/QoS offload function prototypes.

### Important APIs, Types, And Functions
The header defines three HSCH layers, scheduler element counts, `SPX5_HSCH_L0_GET_IDX()`, four leak groups, scheduler modes, rate/burst hardware limits, and `SPX5_DWRR_COST_MAX`. Structs include `sparx5_shaper`, `sparx5_lg`, `sparx5_layer`, and `sparx5_dwrr`. It declares QoS init and TC mqprio/tbf/ets add/delete functions plus `sparx5_get_hsch_max_group_rate()`.

### Control Flow
No runtime control flow exists in the header. The L0 index macro maps a port and queue to a hardware scheduler element with 64 elements per port and eight queues.

### State, Persistence, And Dependencies
The header itself has no state. Its structs define the in-memory metadata used by `sparx5_qos.c`, and constants must match HSCH hardware limits.

### Integration Points
Included by `sparx5_qos.c` and `sparx5_tc.c`. It is the interface between Linux qdisc offload handling and hardware scheduler programming.

### Risks
Hardware limits are compiled in; mismatches with chip variants can cause accepted TC configs to fail or be misprogrammed. The L0 index formula is central to queue shaping correctness.

### Test Signals
Compile-time coverage plus qdisc tests that validate root and queue parent mapping, rate/burst limit enforcement, and DWRR cost array dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_regs.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_regs.c

### Purpose
`sparx5_regs.c` is an autogenerated register metadata table for the Sparx5 platform. It supplies target sizes, register addresses/counts, group addresses/counts/sizes, and field positions/sizes used by register accessor macros.

### Important APIs, Types, And Functions
The file defines constant arrays declared in `sparx5_regs.h`: `sparx5_tsize`, `sparx5_raddr`, `sparx5_rcnt`, `sparx5_gaddr`, `sparx5_gcnt`, `sparx5_gsize`, `sparx5_fpos`, and `sparx5_fsize`. It contains no functions.

### Control Flow
There is no control flow. The compiled arrays are indexed by enum values generated in the matching header.

### State, Persistence, And Dependencies
The arrays are immutable runtime metadata. They depend on `sparx5_regs.h` enum ordering and on the cml-utils generation source noted in the file header. Driver register macros depend on these values for correct MMIO offsets and bitfield extraction.

### Integration Points
This file is linked into the driver and used throughout generated `sparx5_main_regs.h` accessors and chip data structures. Port, QoS, PTP, PSFP, switchdev, and packet code all indirectly rely on these offsets.

### Risks
Because it is generated, manual edits are high risk. Any enum/table ordering mismatch corrupts register accesses. The tables are Sparx5-specific and must not be reused blindly for LAN969x or other variants.

### Test Signals
Build-time enum/table size checks, smoke tests reading known chip registers, register dump comparison against vendor data, and hardware bring-up tests for each block represented in the tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_regs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_regs.h

### Purpose
`sparx5_regs.h` declares the autogenerated enum indices and external metadata arrays for Sparx5 register access.

### Important APIs, Types, And Functions
It defines enums for target counts (`sparx5_tsize_enum`), register addresses/counts, group addresses/counts/sizes, field positions, and field sizes. It declares the corresponding `extern const unsigned int` arrays implemented by `sparx5_regs.c`.

### Control Flow
No control flow is present. The header is purely a typed index contract for generated register access code.

### State, Persistence, And Dependencies
There is no mutable state. The header must stay synchronized with `sparx5_regs.c` and generated register macros that use these enum names.

### Integration Points
Included by low-level register accessor code and chip data. Any source file using generated register macros depends on these enums through the register model.

### Risks
Enum order and array order are a hard ABI inside the driver. Adding, removing, or reordering enum members without regenerating arrays will silently misaddress hardware. The file is generated from a specific cml-utils commit and timestamp, so regeneration provenance matters.

### Test Signals
Compile all generated accessors, compare array lengths with `*_LAST`, validate selected offsets against vendor register data, and run hardware init paths that touch every major target block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_sdlb.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_sdlb.c

### Purpose
`sparx5_sdlb.c` manages service dual leaky bucket groups used by PSFP flow meters and policers. It defines rate classes, computes token update intervals, and maintains per-group linked lists of active leaky buckets in hardware.

### Important APIs, Types, And Functions
Exports include `sdlb_groups`, `sparx5_get_sdlb_group()`, `sparx5_sdlb_clk_hz_get()`, `sparx5_sdlb_pup_token_get()`, `sparx5_sdlb_group_get_by_rate()`, `sparx5_sdlb_group_get_by_index()`, `sparx5_sdlb_group_add()`, `sparx5_sdlb_group_del()`, and `sparx5_sdlb_group_init()`. Internal helpers read first/next list links, detect empty/singular/first/last entries, and enable/disable PUP.

### Control Flow
Initialization computes each group's PUP interval from core clock, max token, and max rate, writes frame-rate tokens and threshold shift, and leaves groups ready for use. Group selection scans from low-rate groups upward in reverse index order, rejects full groups based on `pup_interval / 4 - 1`, and selects a group whose max rate exceeds requested rate. Add inserts an LB index at the head of the hardware list and enables the group; delete relinks around first, last, middle, or singular entries and disables the group if empty.

### State, Persistence, And Dependencies
Group metadata is stored in global `sdlb_groups[]` and augmented with computed `pup_interval` and `frame_size`. Active membership persists in ANA_AC_SDLB registers. Dependencies include core clock period helpers, generated SDLB register macros, chip ops, and constants in `sparx5_main.h`.

### Integration Points
PSFP flow meters use this file for group selection and list membership. Policer programming uses group intervals to compute PUP tokens. QoS initialization calls `sparx5_sdlb_group_init()` for each group.

### Risks
`sparx5_sdlb_group_get_count()` appears to return zero for a single-element group because it checks `itr == next` before incrementing; verify this against intended fullness logic. Linked-list operations depend on valid hardware state and can fail delete if membership is inconsistent. Global `sdlb_groups[]` is shared across devices.

### Test Signals
Test group initialization per core clock, token calculation for zero/nonzero rates, selection for boundary rates and full groups, add/delete head/middle/tail/singular cases, lookup by index, and PSFP police add/delete integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_sdlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_switchdev.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_switchdev.c

### Purpose
`sparx5_switchdev.c` implements Linux switchdev and netdevice notifier integration for bridge offload, FDB programming, VLAN objects, MDB multicast groups, bridge flags, STP state, ageing, and mrouter behavior.

### Important APIs, Types, And Functions
Exports are `sparx5_register_notifier_blocks()` and `sparx5_unregister_notifier_blocks()`. Important internals include bridge join/leave, `sparx5_port_attr_set()`, `sparx5_netdevice_event()`, asynchronous FDB work handling, VLAN add/delete handlers, MDB allocation/free/get, `sparx5_handle_port_mdb_add/del()`, and switchdev blocking/nonblocking notifier callbacks.

### Control Flow
Bridge join enforces a single hardware bridge, marks the port bridged, offloads bridge port, removes standalone host MACT entry, unsyncs multicast list, and enables UC/MC/BC flooding. Leave reverses those changes, restores standalone CPU copy, resets VLAN state, syncs multicast, and disables flooding. Switchdev FDB events are copied under atomic context into ordered workqueue items, then applied under RTNL. Blocking object events program VLAN membership and MDB PGID masks synchronously. MDB add allocates a PGID on first group, applies mrouter ports, optionally enables CPU copy for host entries, updates port masks, and learns MACT to the multicast PGID.

### State, Persistence, And Dependencies
State lives in bridge masks (`bridge_mask`, `bridge_fwd_mask`, `bridge_lrn_mask`), `hw_bridge_dev`, per-port VLAN/mrouter flags, `mdb_entries` list protected by `mdb_lock`, PGID map, MACT hardware, VLAN hardware, and flood PGID masks. Dependencies include Linux bridge/switchdev notifier APIs, MACT, VLAN, PGID helpers, and ordered workqueues.

### Integration Points
This file is the main bridge offload path for the driver. It cooperates with netdev RX marking, multicast sync, VLAN programming, ageing timer programming, and PGID/MACT hardware updates.

### Risks
MDB lookup returns a pointer after dropping `mdb_lock`, then callers lock again, which can be safe only if switchdev serialization prevents concurrent free. Workqueue allocation and `dev_hold()`/`dev_put()` pairing must be correct for FDB events. The driver supports only one hardware bridge. VLAN-unaware mode maps vid 0 to 1, which must remain consistent across FDB/MDB/VLAN paths.

### Test Signals
Test bridge join/leave, rejection of second bridge, STP state transitions and forwarding masks, flood flag toggles, VLAN-aware/unaware adds and deletes, FDB add/delete for host and port entries, MDB host/port/mrouter combinations, ageing updates, notifier registration unwind, and ordered workqueue shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc.c

### Purpose
`sparx5_tc.c` is the TC offload dispatcher for Sparx5 netdevices. It connects Linux block, classifier, and qdisc setup callbacks to matchall, flower, MQPRIO, TBF, and ETS implementations.

### Important APIs, Types, And Functions
The exported function is `sparx5_port_setup_tc()`. Internal callbacks include `sparx5_tc_block_cb()`, ingress/egress wrappers, `sparx5_tc_setup_block()`, `sparx5_tc_get_layer_and_idx()`, and qdisc setup handlers for MQPRIO, TBF, and ETS. A static `sparx5_block_cb_list` tracks flow block callbacks.

### Control Flow
Block setup selects ingress or egress callback based on binder type and registers with `flow_block_cb_setup_simple()`. Classifier callbacks dispatch `TC_SETUP_CLSMATCHALL` to `sparx5_tc_matchall()` and `TC_SETUP_CLSFLOWER` to `sparx5_tc_flower()`. Qdisc handling maps root TBF to HSCH layer 2 and per-queue TBF to layer 0 using `SPX5_HSCH_L0_GET_IDX()`, delegates MQPRIO directly, and accepts ETS only at root with eight bands and reversed priority map.

### State, Persistence, And Dependencies
State is mostly in kernel TC flow block lists and netdev TC configuration; hardware state is programmed by downstream QoS and classifier files. Dependencies include Linux `pkt_cls`, `pkt_sched`, Sparx5 QoS helpers, and classifier implementations.

### Integration Points
Netdev ops call this through `ndo_setup_tc`. It is the central TC entry for qdiscs and clsact filters, tying Linux configuration to VCAP, mirror, PSFP, and HSCH programming.

### Risks
Unsupported binder types and qdisc commands return `-EOPNOTSUPP`, so user-visible TC features are intentionally narrow. ETS validation assumes a strict reversed priority map. Parent-to-layer mapping must match the hardware scheduling hierarchy.

### Test Signals
Test ingress/egress clsact block binding, matchall and flower dispatch, MQPRIO add/delete, root and queue TBF parent mapping, ETS invalid bands/priomap/weights, and unsupported command returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc.h

### Purpose
`sparx5_tc.h` defines TC action encoding constants for Sparx5 VCAP actions and declares the TC dispatcher and classifier handlers.

### Important APIs, Types, And Functions
It defines enums for port mask modes, ES0 forwarding selection, outer tag selection, TPID A/B selection, VID/PCP/DEI selectors, and inner tag selection. It declares `sparx5_port_setup_tc()`, `sparx5_tc_matchall()`, and `sparx5_tc_flower()`.

### Control Flow
No runtime control flow is present. The enum values are passed directly to VCAP action fields by `sparx5_tc_flower.c` and `sparx5_tc_matchall.c`.

### State, Persistence, And Dependencies
There is no state. The header depends on Linux flow offload and netdevice headers and must match hardware VCAP action encodings.

### Integration Points
Used by TC dispatcher, matchall mirror/goto handling, flower VCAP action construction, and mirror support.

### Risks
Wrong enum values would program valid-looking but incorrect VCAP actions. The header is a narrow contract; adding TC actions requires synchronized changes in flower/matchall parsing and hardware validation.

### Test Signals
Compile coverage plus VCAP action tests for mirror/redirect/trap/VLAN push/pop/mangle to confirm the encoded values produce expected hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc_flower.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc_flower.c

### Purpose
`sparx5_tc_flower.c` translates TC flower filters into Sparx5 VCAP rules. It parses supported dissector keys, validates action combinations and chain progression, selects VCAP keysets, programs actions for trap/mirror/redirect/VLAN/goto/accept, manages PSFP resources for gate and police actions, supports template keyset changes, and reports counters.

### Important APIs, Types, And Functions
The public entry is `sparx5_tc_flower()`. Major internal structures are `sparx5_wildcard_rule`, `sparx5_multiple_rules`, and `sparx5_tc_flower_template`. Important functions include dissector handlers, `sparx5_tc_flower_action_check()`, `sparx5_tc_select_protocol_keyset()`, extra rule copy helpers, chain link helpers, PSFP parse/setup/free helpers, action builders, `sparx5_tc_flower_replace()`, destroy/stats handlers, and template create/destroy handlers.

### Control Flow
Replace validates actions, allocates a VCAP rule for the TC chain, parses supported flower keys, adds a counter and any chain target key, then walks actions. Gate and police actions are parsed into PSFP structures and later allocate stream gate, flow meter, stream filter, and ISDX action if the chip supports PSFP. Other actions immediately add VCAP action fields. The rule then uses a stored template keyset if present; otherwise it intersects rule-required keysets with port-supported keysets, possibly producing multiple wildcarded rules for `ETH_P_ALL`. The rule is validated and added, with extra rules added for remaining keysets.

### State, Persistence, And Dependencies
State persists in VCAP rule storage, per-port `tc_templates`, hardware counters, PSFP pools/hardware, and ISDX mappings. The destroy path repeatedly deletes all VCAP rules with the same cookie and frees PSFP resources from the first rule. Dependencies include VCAP API/client helpers, `vcap_tc` generic flower parsers, `sparx5_vcap_impl`, PSFP helpers, TC gate/police action formats, and netlink extack reporting.

### Integration Points
`sparx5_tc.c` dispatches clsflower setup here. Matchall goto rules can enable VCAP lookups that flower chains then populate. PSFP integrates with `sparx5_psfp.c`, policer/SDLB code, and QoS time. VCAP templates alter port keyset configuration through `sparx5_vcap_set_port_keyset()`.

### Risks
Action ordering and chain validation are strict: non-last chains must end in goto. PSFP allocation is not fully transactional; failures after partial gate/meter allocation can leak until destroy unless VCAP/TC cleanup runs. Template destroy initializes `err = -ENOENT` and never sets it to success after removing a template. Multiple rules for one cookie rely on insertion/order assumptions for resource cleanup.

### Test Signals
Test every supported dissector key, unsupported key detection, fragment flag mapping, action conflict rejection, goto chain validation, trap/mirror/redirect/VLAN actions per VCAP type, PSFP gate/police add and destroy, ETH_P_ALL multi-keyset expansion, counter stats, template create/destroy, and cleanup after mid-replace errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc_flower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc_matchall.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc_matchall.c

### Purpose
`sparx5_tc_matchall.c` implements TC matchall offload for two coarse actions: port mirroring through mirror probes and goto-chain lookup enablement through the VCAP framework.

### Important APIs, Types, And Functions
The public handler is `sparx5_tc_matchall()`. Internals include `sparx5_tc_matchall_entry_find()`, action parsing helpers, `sparx5_tc_matchall_replace()`, `sparx5_tc_matchall_destroy()`, and `sparx5_tc_matchall_stats()`. Entries are stored as `struct sparx5_mall_entry` on `sparx5->mall_entries`.

### Control Flow
Replace requires exactly one action. For `FLOW_ACTION_MIRRED`, it records source port, monitor port, direction, cookie, calls `sparx5_mirror_add()`, and initializes baseline stats. For `FLOW_ACTION_GOTO`, it calls `vcap_enable_lookups()` from the current chain to the target chain and translates common errors into extack messages. Successful entries are appended to the mall list. Destroy finds by cookie, deletes mirror state or disables VCAP lookup, removes the list entry, and returns the result. Stats are supported only for mirror entries.

### State, Persistence, And Dependencies
State is retained in allocated mall entries and hardware mirror/VCAP lookup state. Mirror stats baseline is stored per port through `sparx5_mirror_stats()`. Dependencies include TC matchall structures, flow action helpers, mirror APIs, VCAP API, and `sparx5_main.h`.

### Integration Points
`sparx5_tc.c` dispatches `TC_SETUP_CLSMATCHALL` here for ingress or egress clsact blocks. Mirror actions are implemented by `sparx5_mirror.c`; goto actions prepare VCAP chains used by flower rules.

### Risks
Error paths after allocating `mall_entry` do not free it before returning in several cases, which should be checked for leaks. The action parser does not validate that mirrored device is a Sparx5 netdev before `netdev_priv()`. Destroy removes entries but does not free the `mall_entry` allocation. Stats for goto are unsupported.

### Test Signals
Test one-action enforcement, mirror add/delete/stat paths, mirror error extacks, goto enable/disable with invalid and duplicate chains, unsupported actions, invalid mirror device handling, and memory/resource cleanup on replace failure and destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc_matchall.c -->
