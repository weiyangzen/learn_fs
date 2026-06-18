# subset-b-004660 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-nuss.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-nuss.c

## Purpose
Implements the TI K3 AM65 CPSW NUSS Ethernet platform driver. It owns platform probe/remove, device-tree parsing, netdev allocation and registration, ALE setup, devlink switch-mode control, phylink MAC callbacks, K3 UDMA TX/RX channel management, NAPI/IRQ handling, XDP, hardware timestamp configuration, runtime PM, and suspend/resume context restore for AM65/J721E/AM64/J7200/J784S4 CPSW2G/CPSWxG variants.

## Important APIs, Types, and Functions
The main externally visible functions are `am65_cpsw_nuss_set_p0_ptype`, `am65_cpsw_nuss_update_tx_rx_chns`, and `am65_cpsw_port_dev_check`. Platform entry points are `am65_cpsw_nuss_probe`, `am65_cpsw_nuss_remove`, `am65_cpsw_nuss_suspend`, and `am65_cpsw_nuss_resume`. Netdev operations are collected in `am65_cpsw_nuss_netdev_ops`: open/stop, `ndo_start_xmit`, RX mode, stats, VLAN add/kill, ioctl, TC setup, maxrate, BPF/XDP, XDP xmit, and hwtstamp get/set. The file relies on `struct am65_cpsw_common`, `struct am65_cpsw_port`, `struct am65_cpsw_tx_chn`, `struct am65_cpsw_rx_flow`, and descriptor-side software data from `am65-cpsw-nuss.h`.

## Control Flow
Probe maps the `cpsw_nuss` resource, derives switch id, counts `ethernet-ports`, initializes clocks/runtime PM, parses ports and MAC/PHY data, creates ALE and optional CPTS, allocates phylink-backed netdevs, initializes DMA channels, registers devlink ports and netdevs, then registers bridge/switchdev notifiers. Opening a slave netdev resumes PM, resets the MAC slave, sets queue counts and TX queue rate state, starts shared CPSW resources when the first port opens, configures DSCP and ALE entries, connects phylink, restores VLANs, and starts phylink. Stopping reverses phylink and queues, and tears down shared ALE/DMA only when the last port closes.

TX maps the skb linear area and fragments into CPPI5 host descriptors, stores skb/xdp metadata in descriptor swdata, sets packet tags to the egress port id, programs checksum/timestamp metadata, pushes to K3 UDMA, and uses BQL plus descriptor-pool thresholds to stop/wake queues. RX pre-posts page-pool buffers to flows, pops descriptors in NAPI, resolves ingress port from descriptor tags, optionally runs XDP, builds skbs, applies switchdev offload-forward marks, CPTS RX timestamping, checksum status, GRO, and recycles or replenishes pages. IRQ handlers disable IRQs and schedule NAPI; hrtimers optionally pace re-enable.

## State and Persistence
Runtime state is mostly in `am65_cpsw_common`: open-port `usage_count`, DMA channel arrays, ALE pointer/context, rx flow base, switch/emac mode, bridge members, default VLAN, devlink, CPTS, and PM/suspend context. Per-port state includes netdev, MAC/phylink state, timestamp enable/filter, QoS, XDP program, devlink port, and saved VLAN register. Persistent hardware state lives in CPSW registers, ALE tables, CPPI/UDMA rings, descriptor pools, page pools, phylink PHY state, and CPTS. Suspend dumps ALE and VLAN registers, stops running netdevs, suspends CPTS, removes DMA channels, then resume recreates DMA, restores CPTS, reopens running ports, restores VLAN registers, and restores ALE entries.

## Dependencies and Integration Points
Depends on Linux netdev, phylink, runtime PM, platform/OF, PHY/SerDes, devlink, switchdev, DSA tag detection, XDP/BPF, page_pool, NAPI, K3 UDMA glue, CPPI5 descriptors, TI `cpsw_ale`, `cpsw_sl`, `k3-cppi-desc-pool`, `am65-cpts`, `am65-cpsw-qos`, and `am65-cpsw-switchdev`. It integrates with `am65-cpsw-qos.c` through `ndo_setup_tc`, link up/down callbacks, and host rate initialization; with `am65-cpts.c` through PHC/timestamp helpers; and with `am65-cpsw-switchdev.c` through notifier registration and offload forwarding marks.

## Risks and Test Signals
High-risk areas are DMA teardown/completion ordering, descriptor ownership and DMA unmapping on TX/RX error paths, multi-port TX channel locking, XDP page recycling, runtime PM reference balancing, switch-mode transitions while ports are running, CPTS absence/config mismatches, and suspend/resume context loss. Test signals include boot/probe on each compatible, `ip link` up/down loops on every port, bridge switch-mode toggles via devlink, VLAN add/remove, multicast/promisc/allmulti, phylink speed/duplex/pause changes, XDP PASS/DROP/TX/REDIRECT, PTP hwtstamp with `ptp4l`, TX timeout recovery, suspend/resume with active traffic, and DMA teardown timeout diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-nuss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-nuss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-nuss.h

## Purpose
Defines the shared data model and public interface for the AM65 CPSW NUSS driver cluster. The header is the contract between the main platform/netdev driver, QoS offload code, switchdev offload code, ethtool support, and CPTS timestamp integration.

## Important APIs, Types, and Functions
Key types are `struct am65_cpsw_common`, `struct am65_cpsw_port`, `struct am65_cpsw_host`, `struct am65_cpsw_slave_data`, `struct am65_cpsw_tx_chn`, `struct am65_cpsw_rx_chn`, `struct am65_cpsw_rx_flow`, `struct am65_cpsw_tx_swdata`, `struct am65_cpsw_swdata`, `struct am65_cpsw_pdata`, `struct am65_cpsw_devlink`, and `struct am65_cpsw_ndev_priv`. Public helpers/macros include netdev-to-private conversions, common port accessors, NAPI container helpers, `AM65_CPSW_IS_CPSW2G`, `am65_cpsw_nuss_set_p0_ptype`, `am65_cpsw_nuss_update_tx_rx_chns`, and `am65_cpsw_port_dev_check`.

## Control Flow
There is no executable control flow beyond macros and declarations. The file shapes runtime flow by defining ownership boundaries: `am65_cpsw_common` is shared platform state, `am65_cpsw_port` is per-external-port netdev/MAC state, `am65_cpsw_tx_chn` and `am65_cpsw_rx_chn` are DMA resources, and `am65_cpsw_ndev_priv` is the per-netdev bridge between Linux netdev callbacks and driver internals.

## State and Persistence
The header identifies which state survives across callbacks and suspend/resume. `am65_cpsw_common` persists port count, base addresses, ALE, DMA channels, CPTS pointer, EST/IET enable flags, switch/emac mode, bridge membership, default VLAN, switch id, and ALE context. `am65_cpsw_port` persists timestamp filter bits, QoS state, devlink port, XDP program, and VLAN context. Descriptor software data persists only while a DMA descriptor is owned by hardware or completion cleanup.

## Dependencies and Integration Points
Includes kernel netdevice/phylink/platform/devlink/XDP/K3 ring headers and `am65-cpsw-qos.h`, and forward-declares `struct am65_cpts`. It is consumed by `am65-cpsw-nuss.c`, `am65-cpsw-qos.c`, `am65-cpsw-switchdev.c`, ethtool code, and optional switchdev/CPTS modules.

## Risks and Test Signals
ABI drift in this header affects every module in the cluster. Risks include descriptor swdata size exceeding CPPI software-data limits, queue count assumptions exceeding `AM65_CPSW_MAX_QUEUES`, stale suspend context fields, and conditional feature fields being accessed when support is disabled. Test signals are all config combinations for QoS/CPTS/switchdev, `BUILD_BUG_ON` checks in the main file, sparse/smatch structure-use warnings, and runtime queue/XDP/timestamp exercises.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-nuss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-qos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-qos.c

## Purpose
Implements traffic-control and time-sensitive networking offloads for AM65 CPSW: MQPRIO queue/priority mapping and shapers, TAPRIO/EST schedule programming, IET/MAC Merge preemption configuration, host TX queue maxrate programming, and simple flower policer offload for broadcast/multicast ALE rate limits.

## Important APIs, Types, and Functions
The public entry points are `am65_cpsw_qos_ndo_setup_tc`, `am65_cpsw_qos_link_up`, `am65_cpsw_qos_link_down`, `am65_cpsw_qos_ndo_tx_p0_set_maxrate`, `am65_cpsw_qos_tx_p0_rate_init`, `am65_cpsw_iet_commit_preemptible_tcs`, and `am65_cpsw_iet_common_enable`. Internal flows center on `am65_cpsw_setup_mqprio`, `am65_cpsw_taprio_replace`, `am65_cpsw_taprio_destroy`, `am65_cpsw_est_set_sched_list`, `am65_cpsw_timer_set`, `am65_cpsw_qos_setup_tc_block`, and clsflower policer helpers.

## Control Flow
`ndo_setup_tc` dispatches query caps, TAPRIO, MQPRIO, and TC block requests. MQPRIO copies qdisc offload state, resumes PM, validates shaper rates, configures Linux traffic classes, writes queue-to-priority mapping into the port TX priority map, applies per-priority CIR/EIR shapers if link bandwidth allows, and updates IET preemptible traffic classes. TAPRIO requires a running link, rejects round-robin P0 RX priority mode and unsupported cycle extensions, applies MQPRIO, allocates a variable-sized EST schedule object, validates fetch RAM command count, selects a free double buffer, writes fetch commands into port fetch RAM, adjusts past base times into the future, enables EST at port/common level, and programs a CPTS ESTF periodic output when needed.

IET flow stores requested preemptible TCs, serializes with `mm_lock`, enables common IET if any port has IET RX enabled, programs verification timeout based on PHY mode and link speed, optionally runs MAC Merge verify polling, and commits the preemption mask only after link and verification. Flower offload only accepts chain-0 policer actions using packet-per-second rate with drop-on-exceed and destination MAC matches for broadcast or multicast, translating those into `cpsw_ale_rx_ratelimit_bc/mc`.

## State and Persistence
QoS state persists in `port->qos`: admin/oper EST schedules, link speed/down time, MQPRIO copy and shaper state, IET preemptible TCs/original max blocks/verify timeout, and ALE rate-limit cookies. Hardware state persists in CPSW global EST/IET enable bits, per-port EST/IET control/status/verify registers, per-priority CIR/EIR shaper registers, priority maps, fetch RAM buffers, CPTS ESTF outputs, and ALE rate-limit entries.

## Dependencies and Integration Points
Depends on `am65-cpsw-nuss.h`, `am65-cpsw-qos.h`, `am65-cpts.h`, `cpsw_ale.h`, runtime PM, TC qdisc/offload APIs, flow block/flower APIs, netlink extack, and phylink link-speed callbacks from the main driver. TAPRIO timing is tied to CPTS through `am65_cpts_ns_gettime`, `am65_cpts_estf_enable`, and `am65_cpts_estf_disable`.

## Risks and Test Signals
Risks include incorrect unit conversion between bytes/sec, Mbps, bus-frequency shaper units, nanoseconds, link-speed fetch counts, and CPTS cycles; touching EST RAM while a buffer transition is in flight; losing TAS after long link-down intervals; sequential high-to-low rate-mask validation surprising users; IET verification timeout miscomputed for PHY modes; and stale policer cookies. Test signals include `tc mqprio` with min/max rates, `tc taprio` base-time/cycle edge cases, `tc filter flower ... police` for broadcast/multicast, link down/up while EST/IET is enabled, PTP/CPTS clock adjustment while schedules run, and register dumps of shaper, EST, IET, and ALE policer state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-qos.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-qos.h

## Purpose
Declares AM65 CPSW QoS state structures, register offsets, bit fields, and optional build stubs. It is the shared contract for TSN/TC support used by the NUSS driver and QoS implementation.

## Important APIs, Types, and Functions
State structs include `am65_cpsw_est`, `am65_cpsw_mqprio`, `am65_cpsw_iet`, `am65_cpsw_ale_ratelimit`, and `am65_cpsw_qos`. Public APIs are conditionally declared or stubbed: `am65_cpsw_qos_ndo_setup_tc`, `am65_cpsw_qos_link_up`, `am65_cpsw_qos_link_down`, `am65_cpsw_qos_ndo_tx_p0_set_maxrate`, `am65_cpsw_qos_tx_p0_rate_init`, `am65_cpsw_iet_commit_preemptible_tcs`, and `am65_cpsw_iet_common_enable`. The file also defines CPSW global/port QoS registers, EST fetch RAM fields, IET MAC Merge fields, FIFO status bits, and IET statistics offsets.

## Control Flow
Runtime control is selected at compile time with `CONFIG_TI_AM65_CPSW_QOS`. When enabled, callers bind to the real implementation. When disabled, TC setup returns `-EOPNOTSUPP`, link callbacks and IET enable/commit are no-ops, and maxrate returns success without hardware programming.

## State and Persistence
The declared QoS structures are embedded per port and keep admin/oper schedules, link information, mqprio shaper copies, IET requested state, and ALE policer cookies across netdev and phylink callbacks. The register macros describe persistent hardware state in CPSW global control, port control, priority maps, shaper registers, EST fetch RAM, MAC Merge control/status/verify, FIFO status, and IET statistics.

## Dependencies and Integration Points
Includes `linux/netdevice.h` and `net/pkt_sched.h`, forward-declares `am65_cpsw_common` and `am65_cpsw_port`, and is included by `am65-cpsw-nuss.h` and `am65-cpsw-qos.c`. It integrates TC qdisc APIs with the main driver's netdev ops and phylink link-state notifications.

## Risks and Test Signals
Risks are mostly hardware ABI and config-stub drift: duplicated register definitions must remain consistent, masks must match hardware, and disabled-QoS stubs must preserve caller expectations. Test signals are enabled/disabled QoS builds, compile coverage of TAPRIO/MQPRIO/flower paths, and hardware tests proving EST/IET/shaper bits land in expected registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-switchdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-switchdev.c

## Purpose
Implements switchdev offload translation for AM65 CPSW switch mode. It maps bridge attributes, VLAN objects, MDB objects, and FDB add/delete notifications into CPSW ALE operations, and registers the switchdev notifier blocks used by the main NUSS driver.

## Important APIs, Types, and Functions
The exported APIs are `am65_cpsw_switchdev_register_notifiers` and `am65_cpsw_switchdev_unregister_notifiers`. Internal functions include `am65_cpsw_port_stp_state_set`, bridge-flag validators/setters, `am65_cpsw_port_vlan_add/del`, `am65_cpsw_port_mdb_add/del`, `am65_cpsw_port_obj_add/del`, `am65_cpsw_switchdev_event`, `am65_cpsw_switchdev_blocking_event`, and asynchronous `am65_cpsw_switchdev_event_work`. `struct am65_cpsw_switchdev_event_work` carries deferred FDB events plus a held netdev reference.

## Control Flow
Blocking notifier events handle bridge object add/delete and attribute set synchronously through switchdev helper dispatch, first filtering devices with `am65_cpsw_port_dev_check`. STP bridge states are converted to ALE port states. Bridge flags currently validate only learning and multicast flood masks, and implement multicast flood through ALE unregistered multicast control. VLAN add determines whether the object is for the CPU/bridge master or a front-panel port, computes ALE membership/untag/mcast masks, adds/modifies the ALE VLAN, optionally installs the CPU unicast entry, and updates PVID. VLAN delete removes the ALE VLAN membership, optional CPU unicast, PVID, and broadcast multicast entry. MDB add/delete programs ALE multicast entries for CPU or physical port masks.

Non-blocking FDB notifications are copied under RCU into `am65_cpsw_switchdev_event_work`, including a private address copy and `dev_hold`. The work item runs under RTNL, ignores non-user/local entries, maps the port's own MAC to host port when needed, adds or deletes ALE unicast entries, emits an offloaded notification on add, then frees the address, work, and netdev reference.

## State and Persistence
The module has no durable software table of its own. Persistent offload state is in the CPSW ALE: port states, VLAN memberships, PVID registers, multicast entries, unregistered multicast flood settings, and FDB unicast entries. Temporary FDB state lives in queued work until processed.

## Dependencies and Integration Points
Depends on Linux bridge/switchdev notifier APIs, workqueues, RTNL, `am65-cpsw-nuss.h`, `am65-cpsw-switchdev.h`, and `cpsw_ale.h`. It is registered/unregistered by `am65-cpsw-nuss.c` only for multi-port switch-capable builds, while bridge membership and switch-mode eligibility are tracked in the main driver.

## Risks and Test Signals
Risks include notifier lifetime races, missed `dev_put`/address free on uncommon paths, stale ALE entries when bridge objects are removed in unusual order, unsupported bridge flags being accepted or rejected incorrectly, CPU-port VLAN semantics, and duplicate FDB offload notifications. Test signals include Linux bridge VLAN filtering, PVID/untagged changes, MDB joins/leaves, STP state transitions, multicast flood toggles, static FDB add/delete, port enslave/release, and module unload/remove while FDB work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-switchdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-switchdev.h

## Purpose
Provides the optional switchdev interface for the AM65 CPSW NUSS driver. It lets the main driver set skb offload-forward marks and register/unregister switchdev notifiers while compiling cleanly when switchdev support is disabled.

## Important APIs, Types, and Functions
When `CONFIG_TI_K3_AM65_CPSW_SWITCHDEV` is enabled, it declares `am65_cpsw_switchdev_register_notifiers`, `am65_cpsw_switchdev_unregister_notifiers`, and defines `am65_cpsw_nuss_set_offload_fwd_mark` to set `skb->offload_fwd_mark`. When disabled, notifier registration returns `-EOPNOTSUPP`, unregister is a no-op, and the skb mark helper is a no-op.

## Control Flow
The only runtime logic is compile-time selected inline behavior. The enabled mark helper is called from the RX path before GRO so packets forwarded by hardware can be marked for bridge/switchdev semantics. The notifier functions are called by the main driver's registration and remove paths.

## State and Persistence
No state is stored in the header. The enabled skb helper mutates transient packet metadata. Switchdev persistent state is created in `am65-cpsw-switchdev.c` through ALE programming.

## Dependencies and Integration Points
Includes `linux/skbuff.h` and relies on `struct am65_cpsw_common` from includers. It is included by `am65-cpsw-nuss.c` and implemented by `am65-cpsw-switchdev.c`.

## Risks and Test Signals
Risks are configuration mismatches: the main driver should not fail single-port or non-switchdev systems because registration is unavailable, and skb marking must only be meaningful in switch mode. Test signals are switchdev-enabled and disabled builds, RX bridge forwarding tests that inspect `offload_fwd_mark`, and probe/remove on configurations where switchdev is not reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-switchdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpts.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpts.c

## Purpose
Implements the TI K3 AM65 Common Platform Time Sync driver. It provides a PTP hardware clock, timestamp FIFO handling, RX/TX PTP packet timestamp matching, external timestamp and periodic output support, PPS generation, ESTF outputs for TAPRIO schedules, refclk mux setup, platform probe, and suspend/resume context save/restore.

## Important APIs, Types, and Functions
Exported APIs are `am65_cpts_create`, `am65_cpts_release`, `am65_cpts_phc_index`, `am65_cpts_rx_timestamp`, `am65_cpts_tx_timestamp`, `am65_cpts_prep_tx_timestamp`, `am65_cpts_ns_gettime`, `am65_cpts_estf_enable`, `am65_cpts_estf_disable`, `am65_cpts_suspend`, and `am65_cpts_resume`. Key internal types are register-layout structs `am65_cpts_regs` and `am65_genf_regs`, `struct am65_cpts_event`, `struct am65_cpts`, and skb control block `am65_cpts_skb_cb_data`. The PTP ops are in `am65_ptp_info`.

## Control Flow
Creation allocates state, obtains the `cpts` IRQ, parses DT for external timestamp inputs, periodic outputs, PPS indexes, and optional refclk mux, initializes event pools/lists/locks/txq, gets and enables the refclk, configures add value and control/int registers, initializes PHC time to realtime, registers the PTP clock, and requests a threaded IRQ. Interrupts and explicit reads drain the hardware event FIFO into a small software pool, classifying events as push, RX, TX, hardware timestamp, host, rollover, half rollover, or compare. RX/TX events are queued with timeouts; hardware events are emitted to the PTP core as EXTS or PPS events.

PTP gettime temporarily disables interrupts, triggers a timestamp push, records system pre/post timestamps, drains FIFO, then re-enables interrupts. Adjfine computes PPM adjustment periods from scaled ppm and refclk, updates CPTS and active GenF/ESTF compensation registers under mutex plus spinlock. RX timestamping parses the skb PTP header before `eth_type_trans`, adds port and RX event bits, searches queued RX events, and writes skb hwtstamp. TX preparation parses PTP metadata and marks `SKBTX_IN_PROGRESS`; TX completion queues a referenced skb; auxiliary work matches queued TX events against skbs by message type/sequence/port or expires them.

## State and Persistence
Persistent software state includes PHC registration, refclk frequency/add value, event pool and TX/RX event lists, skb TX timestamp queue, ext-ts/genf/pps/estf enable bitmaps, last pushed timestamp, and saved suspend context. Persistent hardware state includes CPTS control, interrupt enable, refclk select, PPM registers, GenF/ESTF compare/length/control/PPM registers, and timestamp counter value. Suspend saves control, interrupt, refclk, ppm, current CPTS time plus realtime anchor, and GenF/ESTF register blocks, then disables CPTS/refclk. Resume restores clock selection, add value, controls, time advanced by suspend duration, PPM, and GenF/ESTF blocks using the documented length-zero sequence.

## Dependencies and Integration Points
Depends on Linux PTP clock APIs, PTP packet parsing/classification, net timestamping, IRQ/platform/OF/clk APIs, clock provider mux registration, PM runtime consumers, skbuff queues, and kernel timekeeping. It integrates with `am65-cpsw-nuss.c` for hwtstamp get/set, RX/TX timestamp hooks, PHC index, and PM; with `am65-cpsw-qos.c` for ESTF periodic outputs; and can also probe standalone as `ti,am65-cpts`/`ti,j721e-cpts`.

## Risks and Test Signals
Risks include FIFO pool exhaustion, timestamp event/skb matching ambiguity, event timeout tuning, lock ordering between FIFO spinlock, txq lock, and PTP mutex, PHC adjfine divide-by-zero style edge cases for zero ppb, PPS index validation, refclk mux lifetime, double clock disable on failed create/release paths, and context drift across suspend. Test signals include PHC registration and `phc_ctl`, `ptp4l`/`phc2sys`, hardware TX/RX timestamp accuracy, PPS/EXTTS/PEROUT requests, TAPRIO ESTF enable/disable, high timestamp load to stress FIFO pool, suspend/resume with active PHC, and IRQ/error-path injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpts.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpts.h

## Purpose
Declares the public interface for the TI K3 AM65 CPTS time-sync driver and provides no-op or error stubs when CPTS support is disabled.

## Important APIs, Types, and Functions
Defines opaque `struct am65_cpts` and `struct am65_cpts_estf_cfg` with `ns_period` and `ns_start`. Enabled builds declare lifecycle, PHC, timestamp, time read, ESTF, and suspend/resume helpers: `am65_cpts_create`, `am65_cpts_release`, `am65_cpts_phc_index`, `am65_cpts_rx_timestamp`, `am65_cpts_tx_timestamp`, `am65_cpts_prep_tx_timestamp`, `am65_cpts_ns_gettime`, `am65_cpts_estf_enable`, `am65_cpts_estf_disable`, `am65_cpts_suspend`, and `am65_cpts_resume`.

## Control Flow
Compile-time selection through `CONFIG_TI_K3_AM65_CPTS` either binds callers to the implementation or uses inline stubs. Disabled builds return `ERR_PTR(-EOPNOTSUPP)` for create, `-1` for PHC index, zero/no-op behavior for timestamp and ESTF helpers, and no-op suspend/resume.

## State and Persistence
The header stores no state directly. It defines the ESTF timing contract used by QoS/TAPRIO to request a periodic CPTS output and exposes an opaque handle whose implementation persists PHC and event state in `am65-cpts.c`.

## Dependencies and Integration Points
Includes device and OF declarations and is included by the NUSS main driver and QoS module. It bridges optional CPTS support to netdev hwtstamp, RX/TX timestamping, and EST schedule timing without forcing those callers to know CPTS internals.

## Risks and Test Signals
Risks include type/signature drift between stubs and real implementation and callers assuming CPTS is present despite `ERR_PTR(-EOPNOTSUPP)`. Test signals are CPTS-enabled and disabled kernel builds, probe paths with missing `cpts` child nodes, hwtstamp requests returning clear errors when disabled, and TAPRIO behavior when ESTF helpers are stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw-common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw-common.c

## Purpose
Provides common TI CPSW MAC-address extraction helpers for older TI platforms where factory MAC IDs are stored in control-module/syscon registers rather than directly in the Ethernet node.

## Important APIs, Types, and Functions
The exported API is `ti_cm_get_macid(struct device *dev, int slave, u8 *mac_addr)`. Internal helpers are `davinci_emac_3517_get_macid` and `cpsw_am33xx_cm_get_macid`, both using `syscon_regmap_lookup_by_phandle` and `regmap_read` against offsets generated by `CTRL_MAC_LO_REG` and `CTRL_MAC_HI_REG`.

## Control Flow
`ti_cm_get_macid` selects register layout and base offset by machine or device compatibility: dm8148/am33xx/am43 use the AM33xx layout at offset `0x630`, AM3517 uses the DaVinci/3517 layout at `0x110`, DM816 uses AM33xx layout at `0x30`, and DRA7 uses DaVinci/3517 layout at `0x514`. If no match is found, it logs an incompatible type and returns `-ENOENT`. Each layout helper tolerates missing `syscon` phandle by returning 0, but propagates other lookup errors.

## State and Persistence
No software state is persisted. The only persistent data read is factory-programmed MAC ID register content in a syscon/control-module regmap. The output buffer is populated in the byte order required by the platform-specific register layout.

## Dependencies and Integration Points
Depends on OF compatibility checks, MFD syscon/regmap APIs, kernel module support, and `cpsw.h` for declaration context. It is exported for CPSW/DaVinci/related Ethernet drivers that need fallback MAC retrieval during probe.

## Risks and Test Signals
Risks include platform-specific byte-order mistakes, returning success with an unchanged buffer when syscon is absent, compatibility checks that miss newer DTs, and offset drift from SoC reference manuals. Test signals include probe on each compatible family, comparison against efuse/control-module MAC values, invalid/missing syscon phandle behavior, and fallback to random or DT-provided MAC in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw-phy-sel.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw-phy-sel.c

## Purpose
Implements the built-in TI CPSW PHY interface selection helper for AM335x/AM43xx/DRA7-style control-module `gmii-sel` registers. It lets CPSW Ethernet drivers program MII/RMII/RGMII mode bits for each slave port based on the requested PHY interface.

## Important APIs, Types, and Functions
The exported API is `cpsw_phy_sel(struct device *dev, phy_interface_t phy_mode, int slave)`. The private state is `struct cpsw_phy_sel_priv`, containing the device, mapped `gmii_sel` register, `rmii_clock_external`, and SoC-specific selector callback. Implementation callbacks are `cpsw_gmii_sel_am3352` and `cpsw_gmii_sel_dra7xx`; platform probing is in `cpsw_phy_sel_probe`.

## Control Flow
Probe matches one of `ti,am3352-cpsw-phy-sel`, `ti,dra7xx-cpsw-phy-sel`, or `ti,am43xx-cpsw-phy-sel`, allocates private state, maps the `gmii-sel` resource, records the optional `rmii-clock-ext` flag, and stores the SoC-specific callback. `cpsw_phy_sel` finds the selector node either through a `cpsw-phy-sel` phandle or child node, locates the bound platform device on the platform bus, retrieves private state, invokes the selector callback, releases the device, and drops the node reference.

The AM335x/AM43xx selector maps RMII/RGMII/RGMII-ID/MII into two-bit mode fields, handles per-slave RMII external clock enable bits, and RGMII internal-delay bits. The DRA7 selector supports slaves 0 and 1 with different bit positions, rejects invalid slave numbers, warns that external RMII clock is unsupported, and otherwise writes the selected mode.

## State and Persistence
Software state is static after probe: register mapping, external clock flag, and callback. Persistent hardware state is the `gmii-sel` register bitfield controlling port interface mode and optional clock/delay bits. No restore logic is present in this file; callers or system PM must ensure control-module state is valid after resets if needed.

## Dependencies and Integration Points
Depends on platform bus/device lookup, OF phandles/child nodes, PHY interface enums, MMIO accessors, and `cpsw.h`. It is built in with `builtin_platform_driver`, and legacy CPSW drivers call the exported `cpsw_phy_sel` during interface setup.

## Risks and Test Signals
Risks include a likely confusing error path where `dev_err(dev, ...)` is used after `bus_find_device` returns NULL, unsupported PHY modes silently defaulting to MII after warning, invalid slave indexes on AM335x not explicitly bounded, missing PM restore, and DTs that use neither phandle nor child node. Test signals include mode register reads for MII/RMII/RGMII/RGMII-ID on each compatible, RMII external-clock behavior, invalid slave tests, probe deferral/order tests where Ethernet calls before selector device exists, and link-up verification after mode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw-phy-sel.c -->
