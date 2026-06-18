# Research: subset-b-004661

Grouped source research for the TI CPSW Ethernet driver files in `sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw.c

## Purpose
`cpsw.c` is the legacy platform netdev driver for TI CPSW Ethernet controllers. It binds `ti,cpsw`, `ti,am335x-cpsw`, `ti,am4372-cpsw`, and `ti,dra7-cpsw` device-tree nodes, creates one or two net devices depending on dual-EMAC configuration, wires CPDMA RX/TX channels, ALE filtering, CPGMAC sliver configuration, PHY links, CPTS timestamping, NAPI, runtime PM, VLAN filtering, XDP transmit, and ethtool operations.

## Important APIs, Types, And Functions
The main exported surface is the platform driver `cpsw_driver` and its `cpsw_probe()`, `cpsw_remove()`, suspend, and resume callbacks. Netdev behavior is collected in `cpsw_netdev_ops`: `cpsw_ndo_open()`, `cpsw_ndo_stop()`, `cpsw_ndo_start_xmit()`, MAC address changes, PHY ioctl, VLAN add/kill, traffic-control setup, BPF/XDP setup, XDP xmit, and hardware timestamp get/set. `cpsw_ethtool_ops` delegates most common ethtool logic to `cpsw_ethtool.c` and provides legacy-driver-specific driver info, pause, and channel setters. Internal helpers split by role: multicast/ALE sync (`cpsw_set_promiscious()`, `cpsw_set_mc()`, `cpsw_ndo_set_rx_mode_work()`), RX data path (`cpsw_rx_handler()`), link/PHY programming (`_cpsw_adjust_link()`, `cpsw_adjust_link()`), host/slave initialization (`cpsw_init_host_port()`, `cpsw_slave_open()`), and DT parsing (`cpsw_probe_dt()`).

## Control Flow
Probe allocates `struct cpsw_common`, maps subsystem and wrapper registers, obtains RX/TX/misc IRQs, enables runtime PM, parses legacy CPSW DT properties and child `slave` nodes, initializes common resources with `cpsw_init_common()`, creates initial CPDMA channels, allocates the first netdev, registers NAPI, registers the netdev, optionally creates the second dual-EMAC netdev, and requests IRQs. Open resumes runtime PM, configures queue counts, initializes the host port once per shared hardware use, opens the selected slave port(s), installs default or reserved VLAN ALE entries, enables NAPI and IRQs, creates XDP RX queues/page pools, fills RX descriptors, registers CPTS when present, restores VLAN/QoS state, starts CPDMA, and increments `usage_count`. RX callbacks consume CPDMA page tokens, switch `ndev` by source port in dual EMAC, run XDP when attached, build SKBs, restore VLAN tags from CPDMA encapsulation status, timestamp RX packets, submit to the stack, and requeue a fresh page. TX pads packets, marks CPTS timestamp requests, submits the skb on a selected CPDMA TX channel, and stops/wakes queues based on descriptor availability. Stop tears down multicast ALE entries, queues, NAPI, CPTS, interrupts, CPDMA, ALE, XDP RX queues, PHYs, and runtime PM when the last user closes.

## State And Persistence
Persistent runtime state is in `struct cpsw_common`, `struct cpsw_priv`, `struct cpsw_slave`, ALE table contents, hardware registers, CPDMA descriptor state, PHY state, CPTS state, VLAN filters, multicast lists, QoS settings, XDP attachments, and runtime PM usage. Module parameters (`debug_level`, `ale_ageout`, `rx_packet_max`, `descs_pool_size`) shape driver behavior at load time. `usage_count` is critical because the CPSW host port, CPDMA, IRQs, ALE, and page pools are shared across dual netdevs. MAC addresses and reserved dual-EMAC VLAN IDs originate from DT, TI control-module fallback, or random generation.

## Dependencies And Integration Points
This file depends on Linux netdev, phylib/of_mdio, runtime PM, GPIO mode selection, CPDMA (`davinci_cpdma`), ALE (`cpsw_ale`), CPGMAC sliver (`cpsw_sl`), CPTS (`cpts`), XDP/page_pool, VLAN core, traffic control, and device-tree platform population. It integrates with userspace through netdev registration, ethtool, VLAN devices, `SIOCGMII*` PHY ioctls, XDP, and hardware timestamping.

## Risks
The shared-resource model is sensitive to `usage_count` ordering: disabling CPDMA, NAPI, page pools, or ALE while the other dual-EMAC netdev is still active would drop traffic or corrupt RX refill. Promiscuous mode and multicast sync deliberately affect shared ALE hardware, so one interface can constrain another. VLAN reserved IDs must not be accepted for user VLAN devices in dual-EMAC mode because they provide port separation. RX page requeue paths must recycle or resubmit every page exactly once. `cpsw_probe_dt()` has many DT legacy compatibility branches; missing `of_node_put()` or fixed-link cleanup regressions are likely failure modes. The probe error path destroys CPDMA/CPTS and removes DT resources, so any new allocation must be added to cleanup.

## Test Signals
Useful signals include successful probe logs with CPSW version and descriptor pool size, both single-port and dual-EMAC netdev registration, link up/down transitions, `ip link` open/close cycles on one and both ports, VLAN add/remove rejection of reserved IDs, multicast and promiscuous mode changes, XDP pass/drop/tx/redirect tests, ethtool stats/register dump, PTP hardware timestamp enablement, suspend/resume with running interfaces, and TX timeout recovery. DT variants should cover `phy-handle`, fixed-link, legacy `phy_id`, missing optional mode GPIOs, and dual-EMAC reserved VLAN properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw.h

## Purpose
`cpsw.h` is the small public header shared by TI CPSW driver pieces. It provides MAC address packing helpers and declarations for external platform helpers used by the CPSW drivers.

## Important APIs, Types, And Functions
`mac_hi(mac)` and `mac_lo(mac)` pack a six-byte Ethernet address into the two register values used by CPGMAC slave source-address registers. `cpsw_phy_sel()` is declared when `CONFIG_TI_CPSW_PHY_SEL` is enabled and replaced by an empty inline otherwise, allowing callers to configure legacy GMII selection without conditional call sites. `ti_cm_get_macid()` is declared as a TI control-module MAC address fallback.

## Control Flow
This header has no independent control flow. Its macros are used by `cpsw_set_slave_mac()` in `cpsw_priv.c`, while `cpsw_phy_sel()` and `ti_cm_get_macid()` are called during DT/probe and slave open paths in `cpsw.c` and `cpsw_new.c`.

## State And Persistence
The header owns no mutable state. The packed MAC values are transient register-write inputs. The optional `cpsw_phy_sel()` stub preserves build-time behavior by turning absent PHY select support into a no-op rather than a runtime branch.

## Dependencies And Integration Points
It includes `linux/if_ether.h` and `linux/phy.h`, and integrates CPSW with optional TI PHY select code and TI control-module MAC ID lookup.

## Risks
The `mac_hi()`/`mac_lo()` byte order must match CPSW register layout; changing it would silently break programmed source MACs. The no-op `cpsw_phy_sel()` path means boards without the PHY select driver must rely on an alternative PHY interface configuration path.

## Test Signals
Test by verifying slave `SA_HI`/`SA_LO` register values match the netdev MAC, booting configurations with and without `CONFIG_TI_CPSW_PHY_SEL`, and confirming MAC fallback through `ti_cm_get_macid()` when DT lacks a valid address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ale.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ale.c

## Purpose
`cpsw_ale.c` implements the CPSW Address Lookup Engine abstraction. It hides ALE register and table layout differences across legacy CPSW, NetCP NU switch, AM65, J721E, and AM64 variants, and provides APIs for unicast, multicast, VLAN, port control, rate limiting, aging, table dump/restore, and default classifier setup.

## Important APIs, Types, And Functions
The key constructor is `cpsw_ale_create()`, which matches `dev_id`, creates a regmap over ALE MMIO, allocates regmap fields and VLAN untag tracking, reads hardware version/table sizes, and initializes variant-specific field metadata. Table APIs include `cpsw_ale_add_ucast()`, `cpsw_ale_del_ucast()`, `cpsw_ale_add_mcast()`, `cpsw_ale_del_mcast()`, `cpsw_ale_flush_multicast()`, `cpsw_ale_add_vlan()`, `cpsw_ale_del_vlan()`, `cpsw_ale_vlan_add_modify()`, and `cpsw_ale_vlan_del_modify()`. Control APIs are `cpsw_ale_control_set()` and `cpsw_ale_control_get()`, backed by `ale_controls[]`. Lifecycle APIs are `cpsw_ale_start()` and `cpsw_ale_stop()`. Diagnostics and restore paths use `cpsw_ale_dump()`, `cpsw_ale_restore()`, and `cpsw_ale_get_num_entries()`.

## Control Flow
Table operations scan the hardware table for matching address/VLAN/free/ageable entries, construct 68-bit entries through bitfield helpers, and write them through `ALE_TABLE` plus `ALE_TABLE_CONTROL`. VLAN functions merge port membership, registered/unregistered multicast masks, and untag masks, with special handling for NU switch VLAN mask mux registers. Start programs the ALE prescale for 1000 pps granularity, enables global rate limiting, enables and clears ALE, then starts either software aging timer or hardware aging timer. Stop reverses aging and disables/clears ALE. Default classifier setup resets policer/thread mappings and maps PCP priorities to RX channels through ALE policer entries.

## State And Persistence
The ALE table, port controls, policer registers, VLAN mask mux registers, aging timer, and `p0_untag_vid_mask` are persistent runtime hardware/software state. `cpsw_ale_create()` mutates global `ale_controls[]` offsets and widths for NU switch variants, which affects all ALE users in the module. Entry allocation prefers existing matching entries, then free entries, then ageable unicast entries. `p0_untag_vid_mask` mirrors host-port untag VLANs so RX VLAN encapsulation handling can decide whether to restore tags.

## Dependencies And Integration Points
The file depends on MMIO, regmap/regmap_field, Linux timers, bitmaps, Ethernet helpers, VLAN constants, and module/platform infrastructure. It is consumed by `cpsw.c`, `cpsw_new.c`, `cpsw_priv.c`, `cpsw_ethtool.c`, and `cpsw_switchdev.c` for filtering, switch mode, bridge VLANs/MDB/FDBs, multicast state, timestamp-aware RX VLAN processing, ethtool register dumps, and TC policer offload.

## Risks
ALE entry bit positions differ by SoC, so incorrect `vlan_entry_tbl` or dynamic port bit width corrupts VLAN membership. The global mutation of `ale_controls[]` for NU variants could be unsafe if multiple ALE hardware types coexist in one kernel instance. Table scans are linear in ALE entries and happen under caller context, so large ALE tables can make control operations expensive. Rate limits round down to 1000 pps granularity. `WARN_ON(idx > ale_entries)` accepts `idx == ale_entries`; callers should not pass an out-of-range index. Aging may evict non-persistent unicast entries when tables are full.

## Test Signals
Exercise add/delete of VLAN, unicast, multicast, allmulti, unknown VLAN controls, ALE bypass, rate limits below and above 1000 pps, and ethtool register dumps. Test legacy CPSW and NU/K3 variants for correct table size detection, VLAN mask mux behavior, host-port untag RX handling, software and hardware aging, and classifier thread mapping for 1-8 RX channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ale.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ale.h

## Purpose
`cpsw_ale.h` defines the public CPSW ALE interface and state structures used by CPSW Ethernet and switchdev code.

## Important APIs, Types, And Functions
`struct cpsw_ale_params` passes MMIO base, device, ageout, table size, policer count, port count, SoC `dev_id`, reg fields, and bus frequency into `cpsw_ale_create()`. `struct cpsw_ale` stores the resolved parameters, timer, regmap fields, version/features, dynamic field widths, host untag bitmap, and VLAN field table. Enumerations define regmap fields (`enum ale_fields`), control selectors (`enum cpsw_ale_control`), and port states (`enum cpsw_ale_port_state`). Flags such as `ALE_SECURE`, `ALE_BLOCKED`, `ALE_SUPER`, and `ALE_VLAN` select entry semantics.

## Control Flow
The header declares ALE lifecycle, table manipulation, VLAN modification, multicast/allmulti, rate limiting, control get/set, dump/restore, table size query, host untag query, and classifier setup APIs. Callers create an ALE object once during CPSW common initialization, start/stop it during netdev open/close, and then mutate entries from netdev, VLAN, switchdev, and TC paths.

## State And Persistence
The declared `struct cpsw_ale` persists across the lifetime of `struct cpsw_common`; individual ALE entries persist in hardware until cleared, aged, or explicitly removed. `p0_untag_vid_mask` is software state tied to VLAN entry updates and used by RX VLAN restoration.

## Dependencies And Integration Points
The header forward-declares regmap and field metadata and exposes ALE to CPSW legacy, switchdev, ethtool, private helper, and K3-related drivers. It assumes Linux bit macros and VLAN constants from included kernel headers through users.

## Risks
Because the header exposes internals of `struct cpsw_ale`, external code can rely on fields that should remain implementation details. Callers must pass valid port masks matching `ale_ports`; stale masks can create unreachable VLAN or multicast entries. `cpsw_ale_get_vlan_p0_untag()` assumes `ale` and its bitmap are initialized.

## Test Signals
Build coverage should include all users of the declarations. Runtime signals include correct open/close ALE lifecycle, VLAN add/delete behavior, ethtool ALE dumps, bridge MDB/FDB offload, TC policer offload, and RX VLAN tag restoration for host-untagged versus tagged VLANs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ale.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ethtool.c

## Purpose
`cpsw_ethtool.c` implements the shared ethtool helper functions used by the legacy and switchdev CPSW drivers. It exposes hardware statistics, CPDMA channel statistics, interrupt coalescing, pause/WOL/link settings through PHYs, ALE register dumps, queue/channel configuration, ring sizing, and timestamping capabilities.

## Important APIs, Types, And Functions
Statistics are described by `struct cpsw_hw_stats`, `struct cpsw_stats`, `cpsw_gstrings_stats[]`, and `cpsw_gstrings_ch_stats[]`. Public helpers include `cpsw_get_msglevel()`, `cpsw_set_msglevel()`, `cpsw_get_coalesce()`, `cpsw_set_coalesce()`, `cpsw_get_sset_count()`, `cpsw_get_strings()`, `cpsw_get_ethtool_stats()`, `cpsw_get_pauseparam()`, `cpsw_get_wol()`, `cpsw_set_wol()`, `cpsw_get_regs_len()`, `cpsw_get_regs()`, `cpsw_ethtool_op_begin()`, `cpsw_ethtool_op_complete()`, channel/ring getters and setters, PHY ksettings/EEE/nway helpers, and `cpsw_get_ts_info()`.

## Control Flow
Stats collection reads fixed CPSW hardware statistic offsets and then CPDMA RX/TX channel stats for each configured channel. Coalescing computes wrapper interrupt pacing prescale and interrupt counts from requested RX usecs, clamps to hardware limits, writes RX/TX `*_imax`, updates `int_control`, and stores `coal_intvl`. Channel changes suspend data passing by disabling interrupts, stopping TX queues, and stopping CPDMA; create/destroy CPDMA channels; update real queue counts on running netdevs; rebalance NAPI budgets; recreate XDP RX queues/page pools if RX count changes; and resume DMA/interrupts. Ring changes similarly suspend data, adjust RX descriptor count, recreate pools, and resume. Ettool begin/complete pair runtime-PM get/put around operations needing register access.

## State And Persistence
The file mutates `cpsw->coal_intvl`, wrapper interrupt registers, CPDMA channel objects, `rx_ch_num`, `tx_ch_num`, TX queue maxrate defaults, NAPI budgets, page pools, XDP RXQ registrations, and CPDMA RX descriptor count. It reads but does not reset hardware stats. Channel/ring changes affect all CPSW slave netdevs because CPDMA is shared.

## Dependencies And Integration Points
It depends on `cpsw_priv.h`, `cpsw_ale.h`, `davinci_cpdma`, phylib ethtool helpers, runtime PM, CPTS, and netdev queue APIs. Legacy and switchdev drivers plug these helpers into their ethtool ops tables.

## Risks
Channel and ring updates are disruptive and close all CPSW netdevs on failure through `cpsw_fail()`. Multi-queue changes must stay synchronized with page pools and XDP RX queues; otherwise RX callbacks can reference freed or missing pools. Coalescing uses only RX usecs but programs both RX and TX pacing. `cpsw_get_regs()` dumps ALE entries only, not all CPSW registers, so users may misinterpret the register dump scope. PHY-dependent helpers must handle absent PHYs, especially during down or partially probed states.

## Test Signals
Use `ethtool -S`, `--show-coalesce`, `--coalesce`, `-l`, `-L`, `-g`, `-G`, `-d`, `--show-eee`, `--set-eee`, WOL, link ksettings, and timestamp info on both legacy and switchdev netdevs. Exercise channel/ring changes while interfaces are up, while XDP is attached, and with both dual-EMAC ports running; verify data resumes or devices close cleanly on injected CPDMA allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_new.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_new.c

## Purpose
`cpsw_new.c` is the newer CPSW switchdev-capable platform driver. It supports `ti,*-cpsw-switch` compatibles, creates per-port netdevs from `ethernet-ports`, can operate in dual-MAC or switch mode, registers switchdev and netdevice notifiers, and exposes devlink runtime parameters for `switch_mode` and `ale_bypass`.

## Important APIs, Types, And Functions
The platform driver is `cpsw_driver` named `cpsw-switch`. Netdev operations mirror the legacy driver but add `ndo_get_phys_port_name`, `ndo_get_port_parent_id`, immutable netns, and hardware TC feature advertising. `struct cpsw_devlink` binds devlink to `struct cpsw_common`. Devlink handlers `cpsw_dl_switch_mode_get/set()` and `cpsw_dl_ale_ctrl_get/set()` manage switch mode and ALE bypass. Notifier helpers `cpsw_register_notifiers()`, `cpsw_netdevice_event()`, `cpsw_netdevice_port_link()`, and `cpsw_netdevice_port_unlink()` connect bridge membership to switchdev offload tracking. Port setup flows through `cpsw_create_ports()`, `cpsw_register_ports()`, and `cpsw_slave_open()`.

## Control Flow
Probe allocates common state and two slave slots, maps subsystem registers, gets named IRQs, enables runtime PM, parses `ethernet-ports`, initializes common CPSW resources, creates base CPDMA channels, creates per-port netdevs, requests IRQs, registers switchdev/netdevice notifiers, registers devlink params, then registers netdevs. Opening a port resumes PM, configures queues, initializes the host port once, opens that slave, creates/fills shared RX pools if first user, registers CPTS, enables NAPI/IRQs, restores VLAN/QoS/clsflower offload, starts CPDMA, and increments usage. Switch mode changes under RTNL either update stored mode/port VLANs while all ports are down or, while running, temporarily enables ALE bypass, clears ALE, reinitializes host mode, rebuilds per-port ALE entries, updates `tx_packet_min`, and disables bypass. Bridge upper events record a single hardware bridge device and update `offload_fwd_mark` when both ports are offloaded.

## State And Persistence
The core mode bit is still `cpsw->data.dual_emac`; `cpsw_is_switch_en()` returns its inverse. Per-port state includes `emac_port` values 1 and 2, `tx_packet_min`, offload forward mark, reserved dual-EMAC VLANs, and bridge membership. Device-wide state includes devlink pointer, ALE bypass flag, base MAC for parent ID, `br_members`, and `hw_bridge_dev`. Runtime switch transitions persist by rewriting ALE entries and port VLANs rather than rebooting the driver.

## Dependencies And Integration Points
This file integrates CPSW with devlink, switchdev, bridge upper-device notifiers, phylib, of_platform population, CPDMA, ALE, CPGMAC sliver, CPTS, XDP/page_pool, ethtool shared helpers, and Linux netdevice APIs. It depends on `cpsw_switchdev.c` for VLAN/MDB/FDB/STP object handling.

## Risks
Runtime switch-mode transitions are complex: a bad ordering around ALE bypass, table clear, `dual_emac` flip, port VLAN rewrite, or `tx_packet_min` update can leak traffic across ports or break bridge forwarding. `cpsw_dl_ale_ctrl_set()` returns 0 even when `cpsw_ale_control_set()` fails after assigning `ret`, which hides errors. `cpsw_port_offload_fwd_mark_update()` assumes every slave has an `ndev` before calling `netdev_priv()`. Only one hardware bridge is supported. New DT parsing requires exactly two port children and valid PHY nodes for enabled ports, unlike older legacy binding flexibility.

## Test Signals
Test probe with `ti,cpsw-switch` DT, disabled port nodes, named IRQs, fixed-link and PHY-handle ports, netdev registration order, devlink `switch_mode` toggles with ports down and up, bridge enslave/release of one and both ports, rejection of second bridge, `ale_bypass` toggles, VLAN and multicast behavior in switch versus dual-MAC mode, XDP, PTP timestamping, suspend/resume, and offload forward mark behavior with bridge traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_new.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_priv.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_priv.c

## Purpose
`cpsw_priv.c` contains shared CPSW implementation used by both driver front ends: interrupt control, NAPI polling, TX completion, RX VLAN reconstruction, common hardware initialization, hardware timestamp programming, CPDMA resource splitting, TX rate limiting, traffic-control offloads, XDP/page_pool management, and clsflower policer offload.

## Important APIs, Types, And Functions
It defines exported function pointer `cpsw_slave_index`, set by the active front-end driver. Interrupt/data path exports include `cpsw_intr_enable()`, `cpsw_intr_disable()`, `cpsw_tx_handler()`, `cpsw_tx_interrupt()`, `cpsw_rx_interrupt()`, `cpsw_misc_interrupt()`, `cpsw_tx_mq_poll()`, `cpsw_tx_poll()`, `cpsw_rx_mq_poll()`, and `cpsw_rx_poll()`. Initialization and recovery include `cpsw_init_common()`, `cpsw_soft_reset()`, `cpsw_set_slave_mac()`, `cpsw_ndo_tx_timeout()`, `cpsw_need_resplit()`, and `cpsw_split_res()`. Offload and data features include hardware timestamp get/set, `cpsw_ndo_set_tx_maxrate()`, `cpsw_ndo_setup_tc()`, CBS/MQPRIO/clsflower resume helpers, XDP RXQ creation/destruction, `cpsw_ndo_bpf()`, `cpsw_xdp_tx_frame()`, and `cpsw_run_xdp()`.

## Control Flow
Interrupt handlers mask wrapper interrupts, acknowledge CPDMA EOI, optionally disable broken AM33xx IRQ lines, and schedule NAPI. NAPI polls either a single channel or all active CPDMA channels and reenables wrapper IRQ bits when under budget. TX completion distinguishes skb tokens from tagged XDP frame tokens, timestamps skb TX completions, frees resources, wakes stopped queues, and updates stats. Common init reads CPSW version, chooses register offsets, initializes slave register/sliver objects, creates ALE, configures CPDMA parameters, and creates CPTS. XDP setup creates shared page pools per RX channel, registers each netdev RXQ with page_pool memory model, runs BPF programs in RX callbacks, handles PASS/TX/REDIRECT/DROP/ABORTED, and transmits XDP frames through CPDMA.

## State And Persistence
Shared state includes CPDMA controller/channels, NAPI budgets and channel weights, page pools, per-netdev XDP programs and RXQ registrations, CPTS flags, QoS shaper configuration, MQPRIO state, clsflower broadcast/multicast rate-limit cookies, and hardware registers. `cpsw_split_res()` persists TX/RX budgets and CPDMA channel weights based on link speed and configured channel rates. Timestamp enablement persists in per-port flags and slave registers.

## Dependencies And Integration Points
This file binds CPSW to `davinci_cpdma`, `cpsw_ale`, `cpsw_sl`, `cpts`, phylib, runtime PM, page_pool, XDP/BPF, TC qdisc and clsflower APIs, netdev queues, VLAN RX helpers, and kernel tracing for XDP exceptions. Front-end drivers call these routines from netdev operations, probe, open/stop, ethtool, and switchdev restore paths.

## Risks
`cpsw_slave_index` must be initialized before helpers that index slaves; wrong semantics between legacy and switchdev drivers would target the wrong port. CPDMA/page_pool/XDP lifetimes are tightly coupled to interface open/close and channel/ring changes. XDP redirect is flushed per packet because RX queue ownership can change by source port; batching would be wrong here. Rate and shaper calculations depend on current link speed and can reject or misproportion budgets if speed is unknown or changes. Hardware timestamp support excludes version 4, and source filtering expects MAC timestamping in switch mode. TC clsflower only supports broadcast or multicast destination policers in packets per second, not byte-rate policers.

## Test Signals
Test IRQ/NAPI behavior on normal and AM33xx quirk platforms, TX timeout recovery, multi-channel RX/TX, ethtool channel/ring changes, XDP attach/detach/pass/drop/tx/redirect, PTP timestamp configuration and packet stamping, CBS/MQPRIO offload and resume after link reset, TX maxrate distribution, clsflower broadcast/multicast policer add/delete/resume, and suspend/resume with active offloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_priv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_priv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_priv.h

## Purpose
`cpsw_priv.h` is the central private interface for CPSW drivers. It defines hardware offsets, feature bits, constants, register layouts, platform data, slave/common/private state structures, logging macros, XDP metadata helpers, and prototypes shared between legacy, switchdev, ethtool, ALE, and helper implementation files.

## Important APIs, Types, And Functions
Important structures are `struct cpsw_platform_data`, `struct cpsw_slave_data`, `struct cpsw_slave`, `struct cpsw_vector`, `struct cpsw_common`, `struct cpsw_priv`, `struct cpsw_ale_ratelimit`, `struct addr_sync_ctx`, and `struct cpsw_meta_xdp`. It defines CPSW version constants, register offsets for v1/v2 layouts, CPDMA offsets, VLAN and FIFO constants, timestamp-control masks, queue limits, descriptor defaults, and XDP handle tagging helpers (`cpsw_is_xdpf_handle()`, `cpsw_xdpf_to_handle()`, `cpsw_handle_to_xdpf()`). It declares all shared helper APIs implemented in `cpsw_priv.c` and `cpsw_ethtool.c`.

## Control Flow
The header has no runtime control flow, but its macros and inline helpers drive key flows: `ndev_to_cpsw()` and `napi_to_cpsw()` convert kernel callback objects to driver common state; `slave_read()`/`slave_write()` centralize slave MMIO access; XDP handle tagging lets TX completion choose skb or XDP cleanup path.

## State And Persistence
`struct cpsw_common` persists device-wide state: mapped registers, version, DMA, ALE, CPTS, IRQs, page pools, queues, bridge/devlink state, and resource counts. `struct cpsw_priv` persists per-netdev state: MAC, pause flags, QoS settings, timestamp flags, XDP program/RXQs, port id, offload mark, packet minimum, rate-limit cookies, and rx-mode work. `struct cpsw_slave` persists per-port register base, PHY/sliver, MAC control, netdev, and VLAN.

## Dependencies And Integration Points
It includes XDP/BPF UAPI and `davinci_cpdma.h`, and is included by almost every CPSW source in this subset. It provides the contract between Linux netdev callbacks, CPDMA callbacks, ALE programming, phylib, CPTS, TC, XDP, and ethtool.

## Risks
Because this header exposes many hardware constants and shared structures, changes have broad blast radius. Field ownership is split across files; for example, `usage_count`, page pools, and queue counts are modified from open/stop and ethtool paths. Inline XDP pointer tagging relies on alignment and low-bit availability. Register offsets must remain correct for CPSW v1/v2 layouts. `cpsw_slave_index` is an external function pointer rather than a fixed helper, so callers depend on front-end driver initialization.

## Test Signals
Compile coverage across both `cpsw` and `cpsw-switch` drivers is essential. Runtime tests should cover state transitions that touch shared fields: dual-port open/close, channel changes, XDP attach/detach, switchdev bridge offload, hardware timestamping, QoS restore, and register writes for v1 and v2 CPSW versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_sl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_sl.c

## Purpose
`cpsw_sl.c` implements the CPGMAC_SL, or MAC sliver, abstraction used by CPSW and related TI Ethernet devices. It maps logical sliver registers and supported MAC control bits across device variants and provides reset, register access, MAC control set/clear, and idle wait helpers.

## Important APIs, Types, And Functions
`struct cpsw_sl` stores device, MMIO base, selected register map, supported control feature mask, and idle mask. `struct cpsw_sl_dev_id` describes per-device register maps, offset adjustment, supported control bits, and idle mask. Public exported APIs are `cpsw_sl_get()`, `cpsw_sl_reg_read()`, `cpsw_sl_reg_write()`, `cpsw_sl_reset()`, `cpsw_sl_ctl_set()`, `cpsw_sl_ctl_clr()`, `cpsw_sl_ctl_reset()`, and `cpsw_sl_wait_for_idle()`.

## Control Flow
`cpsw_sl_get()` allocates a managed sliver object, matches `device_id`, assigns the register map and feature masks, and applies per-device base offset. Register read/write reject unsupported logical registers. Reset writes the soft-reset bit and polls until it clears or times out. Control set/clear validates requested bits against `control_features`, reads MACCONTROL, modifies bits, and writes back. Idle wait polls MACSTATUS until the configured idle mask is set.

## State And Persistence
The sliver object persists as devm-managed per-slave state under `struct cpsw_slave`. Hardware state persists in MACCONTROL, MACSTATUS, reset, maxlen, pause, priority map, and other sliver registers. `control_features` prevents unsupported controls from being written for a selected SoC.

## Dependencies And Integration Points
It depends on MMIO, kernel delay/jiffies, and `cpsw_sl.h`. CPSW open/link paths use it to reset ports, set RX max length, priority maps, GMII/gigabit/full-duplex/flow-control bits, and wait for idle on link down.

## Risks
Unsupported logical register reads return 0 after logging, which may hide configuration errors if callers do not check device capabilities. `cpsw_sl_ctl_set()` and `_clr()` return `u32` but can return negative errno values, so caller typing is awkward. Timeout loops rely on correct idle/reset bit definitions per SoC. Wrong `device_id` mapping or `regs_offset` will direct all MAC programming to the wrong MMIO locations.

## Test Signals
Test sliver reset and idle wait on each supported `device_id`, verify unsupported register logging, validate MACCONTROL bits during link speed/duplex/pause transitions, and check that AM65/K3 idle mask requirements work on link down and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_sl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_sl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_sl.h

## Purpose
`cpsw_sl.h` declares the CPGMAC_SL abstraction used to configure TI Ethernet MAC sliver blocks independently from CPSW front-end details.

## Important APIs, Types, And Functions
`enum cpsw_sl_regs` defines logical sliver registers such as IDVER, MACCONTROL, MACSTATUS, SOFT_RESET, RX_MAXLEN, pause, EMCONTROL, priority map, and TX gap. The control-bit enum defines MACCONTROL functions including full duplex, loopback, flow control, GMII, gigabit, XGMII, command idle, interface control, external control, CRC options, and error-frame copy controls. The public API declares object creation, reset, control set/clear/reset, idle wait, and logical register read/write.

## Control Flow
The header has no runtime logic, but its enum values are used by `cpsw_sl.c` to index per-SoC register maps and by CPSW open/link code to program port behavior.

## State And Persistence
It forward-declares opaque `struct cpsw_sl`, preserving implementation-private mapping state. Hardware register contents persist in the sliver block until reset or reprogrammed.

## Dependencies And Integration Points
It includes `linux/device.h` and is consumed by CPSW common initialization and port/link setup. It decouples CPSW drivers from SoC-specific sliver MMIO offsets.

## Risks
Adding enum members requires updating every register map in `cpsw_sl.c`; otherwise new logical registers may index uninitialized data. Control bits must match hardware MACCONTROL definitions across variants, and unsupported bits must be captured in feature masks.

## Test Signals
Build and runtime tests should verify all declared logical registers map correctly for supported SoCs, and that link changes produce expected MACCONTROL bits through `cpsw_sl_ctl_set()`/`clr()` without unsupported-bit errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_sl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_switchdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_switchdev.c

## Purpose
`cpsw_switchdev.c` implements switchdev notifier handling for the CPSW switch-mode driver. It translates bridge STP state, bridge flags, VLAN objects, MDB objects, and FDB events into ALE port state and table updates.

## Important APIs, Types, And Functions
The file exposes `cpsw_switchdev_register_notifiers()` and `cpsw_switchdev_unregister_notifiers()`. Internal helpers include `cpsw_port_stp_state_set()`, `cpsw_port_attr_br_flags_set/pre_set()`, `cpsw_port_attr_set()`, PVID helpers, `cpsw_port_vlan_add()`, `cpsw_port_vlan_del()`, `cpsw_port_mdb_add()`, `cpsw_port_mdb_del()`, `cpsw_port_obj_add()`, `cpsw_port_obj_del()`, `cpsw_fdb_offload_notify()`, async `cpsw_switchdev_event_work()`, and notifier callbacks for atomic and blocking switchdev chains.

## Control Flow
Blocking notifier events handle port VLAN/MDB object add/delete and port attributes synchronously through switchdev helper dispatch filtered by `cpsw_port_dev_check()`. Atomic switchdev events either dispatch port attributes or allocate work for FDB add/delete, copy the FDB address, hold the netdev, and queue work on `system_long_wq`. The work item takes RTNL, ignores non-user or local FDB entries, maps local MAC entries to host port, programs ALE unicast add/delete with optional VLAN flag, notifies switchdev of offload on add, releases copied address and netdev reference, and frees work state.

## State And Persistence
Persistent state is mostly ALE hardware state: port STP state, VLAN member/untag/multicast masks, port PVID registers, multicast database entries, and static FDB unicast entries. No long-lived private state exists beyond queued work items. Bridge multicast-flood flags modify unregistered multicast masks across ALE VLAN entries.

## Dependencies And Integration Points
It depends on Linux bridge and switchdev APIs, workqueues, netdevice references, `cpsw_ale`, `cpsw_priv`, and `cpsw_switchdev.h`. It is registered by `cpsw_new.c` after common device setup and unregistered during remove.

## Risks
FDB events are asynchronous, so object lifetime is protected by copying the MAC address and holding the netdev; any new FDB fields would need similar handling. VLAN/PVID handling must distinguish CPU bridge master objects from physical port objects. `cpsw_port_attr_br_flags_pre_set()` accepts only learning and multicast flood masks, but learning is not acted on in the set path; this may rely on hardware learning defaults elsewhere. ALE errors from some cleanup operations are intentionally ignored. Queued work must be drained indirectly by notifier unregister and device teardown ordering.

## Test Signals
Test bridge enslave in switch mode, STP state transitions, `bridge vlan add/del` including PVID and untagged flags on ports and bridge master, `bridge mdb add/del`, static FDB add/delete with and without VID, offload notifications, multicast flood flag changes, rapid port unregister while FDB work is pending, and non-CPSW devices passing through notifiers untouched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_switchdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_switchdev.h

## Purpose
`cpsw_switchdev.h` declares the CPSW switchdev integration API used by the switch-mode CPSW driver.

## Important APIs, Types, And Functions
It includes `<net/switchdev.h>` and declares `cpsw_port_dev_check()`, `cpsw_switchdev_register_notifiers()`, and `cpsw_switchdev_unregister_notifiers()`.

## Control Flow
There is no implementation in the header. `cpsw_new.c` calls register/unregister during probe/remove, and switchdev notifier helpers use `cpsw_port_dev_check()` as their filter predicate.

## State And Persistence
No state is stored in this header. The functions it declares operate on `struct cpsw_common` and `struct net_device` state owned by `cpsw_new.c` and `cpsw_priv.h`.

## Dependencies And Integration Points
The header is the narrow contract between the switchdev implementation file and the `cpsw-switch` front end. It depends on `struct cpsw_common` being visible to includers through `cpsw_priv.h`.

## Risks
The prototypes expose global notifier registration, so probe/remove ordering must avoid double registration or unregistering without prior registration. `cpsw_port_dev_check()` is security-sensitive in the sense that it gates which netdevs receive CPSW hardware offload operations.

## Test Signals
Compile with switchdev enabled, probe/remove `cpsw-switch`, confirm only CPSW switch-mode ports pass the device check, and verify bridge/switchdev operations do not affect legacy `cpsw` or unrelated netdevs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_switchdev.h -->
