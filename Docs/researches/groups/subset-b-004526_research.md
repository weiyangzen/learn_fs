# subset-b-004526 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_ethtool.c

## Purpose
Implements the `ethtool_ops` surface for the mlx4 Ethernet driver. It exposes driver and firmware identity, Wake-on-LAN, statistics strings and values, self-tests, link mode query/set, interrupt coalescing, pause/PFC configuration, ring sizes, RSS hash settings, ntuple flow steering, channel counts, timestamp capabilities, private flags, TX copybreak, module EEPROM access, and physical identify/beacon control.

## Important APIs, Types, and Functions
The exported integration point is `mlx4_en_ethtool_ops`; `mlx4_en_moderation_update` is also used by netdev reconfiguration paths. Link support centers on `mlx4_en_get_link_ksettings`, `mlx4_en_set_link_ksettings`, `mlx4_en_init_ptys2ethtool_map`, `ptys2ethtool_update_link_modes`, and `ethtool2ptys_link_modes`. Stats use `main_strings`, `mlx4_en_get_sset_count`, `mlx4_en_get_strings`, `mlx4_en_get_ethtool_stats`, and the local `bitmap_iterator` over `priv->stats_bitmap`. Flow steering uses `mlx4_en_validate_flow`, `mlx4_en_ethtool_to_net_trans_rule`, `mlx4_en_flow_replace`, `mlx4_en_flow_detach`, and cached `priv->ethtool_rules`. Reconfiguration APIs include coalesce, pause, ringparam, RXFH, channels, private flags, tunables, and module EEPROM helpers.

## Control Flow
Simple getters read cached state from `mlx4_en_priv`, `mlx4_en_dev`, and hardware capability fields. Link getters first call `mlx4_en_QUERY_PORT`, then prefer the PTYS register path when firmware supports Ethernet protocol control, falling back to a default transceiver mapping. Link setting queries PTYS, validates duplex/autoneg/speed/advertisement, writes the new admin protocol mask, then restarts the port under `state_lock` if it is up. Ring, channel, RXFH, and selected feature changes allocate a temporary profile through netdev helpers, stop the port if active, replace resources, restart, and refresh moderation. Ntuple insertion converts ethtool flow specs into mlx4 flow specs, detaches any prior rule at the same location, attaches the new rule, and stores the firmware registration id.

## State and Persistence Behavior
Most settings are runtime state in `struct mlx4_en_priv`: message level, coalescing thresholds, adaptive RX moderation parameters, RSS key/hash function/ring count, profile ring sizes, pause/PFC bits, private flags, and cached flow rules. Hardware-persistent or firmware-owned state is modified through mlx4 commands and registers: WoL config, PTYS advertised link modes, port pause/PFC policy, CQ moderation, flow steering entries, PHV bit, module EEPROM reads, and port beacon duration. The file does not store durable configuration outside driver and firmware state.

## Dependencies and Integration Points
Depends on Linux ethtool, bitmap, netdevice, MII/link mode, IPv4 helpers, and mlx4 core command/register APIs. It integrates with `en_port.c` for port query and port configuration, `en_netdev.c` for resource reset/restart paths, `en_selftest.c` for test execution, the flow steering API for ntuple rules, and timestamp/PHC support exposed by the broader mlx4_en driver.

## Risks
Many ethtool setters restart live ports, so lock ordering around RTNL and `mdev->state_lock` is critical. Flow rule conversion accepts only restricted masks; loosening validation can create firmware rules that do not match Linux semantics. RSS indirection validation assumes evenly repeated ring ids and power-of-two sizes. RX timestamping conflicts with RX VLAN stripping, so reset paths must keep feature state coherent. Stats string count and stats value order must remain exactly aligned with `stats_bitmap` and per-ring counters.

## Test Signals
Useful tests include `ethtool -i`, `-S`, `--show-priv-flags`, `--set-priv-flags`, `-c/-C`, `-g/-G`, `-l/-L`, `-x/-X`, `-k/-K`, `--show-pause/--pause`, `--test online/offline`, WoL read/write, link speed/autoneg setting with PTYS-capable firmware, ntuple rule add/delete/list, timestamp info with and without PHC, module EEPROM reads for SFP/QSFP variants, beacon identify, and port restart coverage while traffic is running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_main.c

## Purpose
Provides module entry/exit and auxiliary-driver lifecycle for mlx4 Ethernet support. It validates module parameters, builds the per-device Ethernet profile, allocates mlx4 core resources shared by all Ethernet ports, registers event and netdev notifiers, creates one netdev per Ethernet port, and tears the device down on auxiliary remove.

## Important APIs, Types, and Functions
Module-level state includes parameters `udp_rss`, `pfctx`, `pfcrx`, and `inline_thold`, plus the `mlx4_en_adrv` auxiliary driver. Public helpers include `en_print` for per-port logging and `mlx4_en_update_loopback_state` for loopback feature propagation. Lifecycle functions are `mlx4_en_probe`, `mlx4_en_remove`, `mlx4_en_event`, `mlx4_en_get_profile`, `mlx4_en_verify_params`, `mlx4_en_init`, and `mlx4_en_cleanup`.

## Control Flow
Initialization verifies module parameters, initializes the mlx4-to-ethtool link-mode map, and registers an auxiliary driver named `mlx4_core.eth`. Probe allocates `mlx4_en_dev`, a protection domain, UAR, UAR mapping, and memory region, then derives the driver profile from module parameters and device capabilities. It counts Ethernet ports, sets default RX ring counts, creates a single-thread workqueue, marks the device up, registers the mlx4 event notifier, initializes netdevs for each Ethernet port, and registers a netdev notifier for bonding updates. Remove unregisters the event notifier, marks `device_up` false under `state_lock`, destroys every port netdev, destroys the workqueue, frees MR/UAR/PD resources, unregisters the netdev notifier, and frees `mdev`.

## State and Persistence Behavior
`struct mlx4_en_dev` is the main in-memory device container: core `mlx4_dev`, PCI device, DMA device, profile, UAR/PD/MR, workqueue, per-port netdev pointers, notifier blocks, and device-up state. Module parameters persist for the module lifetime and are copied into `mdev->profile`. Hardware resources such as PD, UAR, and MR persist until auxiliary remove. Loopback state updates per-port flags and, when supported, updates RX QPs through firmware source-check loopback controls.

## Dependencies and Integration Points
Depends on Linux module, auxiliary bus, netdevice, workqueue, memory mapping, and mlx4 core driver APIs. It integrates with `en_netdev.c` for per-port netdev creation/destruction and netdev notifier handling, `en_rx.c` for RX ring count selection, `en_resources.c` for loopback QP updates, and `en_ethtool.c` for PTYS map initialization.

## Risks
Probe has a staged resource allocation sequence; unwind labels must match the allocation order. Event handling queues link work rather than directly changing carrier, so queued work must be flushed before netdev memory is freed. Loopback update walks RSS QPs under `state_lock` and depends on valid `rss_map` state. Parameter validation mutates module parameter globals, so validation must run before profile creation.

## Test Signals
Module load/unload, auxiliary probe/remove, low-memory profile selection, invalid module parameter correction, UDP RSS disabled when unsupported, PFC parameter propagation, per-port netdev creation failure unwind, mlx4 event notifier link-up/link-down queuing, catastrophic event logging, and teardown with pending workqueue items are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_netdev.c

## Purpose
Implements the mlx4 Ethernet `net_device` lifecycle and most runtime control-plane behavior. It creates and destroys netdev instances, allocates and swaps RX/TX resources, opens and closes ports, configures QPs/CQs/steering, manages MAC/VLAN/multicast/promiscuous filters, handles feature changes, XDP, traffic classes, VF controls, VXLAN tunnel offload, bonding notifications, statistics collection, and restart recovery.

## Important APIs, Types, and Functions
Primary entry points are `mlx4_en_init_netdev`, `mlx4_en_destroy_netdev`, `mlx4_en_start_port`, `mlx4_en_stop_port`, `mlx4_en_reset_config`, `mlx4_en_try_alloc_resources`, `mlx4_en_safe_replace_resources`, `mlx4_en_setup_tc`, `mlx4_en_alloc_tx_queue_per_tc`, and `mlx4_en_netdev_event`. Netdev ops are collected in `mlx4_netdev_ops` and `mlx4_netdev_ops_master`. Important workers include `mlx4_en_do_set_rx_mode`, `mlx4_en_restart`, `mlx4_en_linkstate_work`, `mlx4_en_do_get_stats`, and `mlx4_en_service_task`. Optional RFS support uses `struct mlx4_en_filter` and asynchronous flow attach work.

## Control Flow
Netdev initialization allocates an Ethernet device with maximum queue counts, initializes private locks/work items/lists, reads MAC and MTU capabilities, allocates inactive CQs/rings, assigns netdev ops/features/ethtool ops/XDP metadata ops, programs initial port settings, starts periodic stats/service tasks, and registers the netdev. Open clears stats, starts the port, and refreshes link state. Port start activates RX rings/CQs, reserves the base QP, configures RSS and drop QPs, activates TX CQs/rings, programs port MTU/pause/VXLAN/default QPN, initializes the port, attaches steering and broadcast rules, schedules RX mode work, schedules NAPI for any pending completions, starts queues, and attaches the device. Stop reverses the sequence: close port, stop queues, mark port down, remove promiscuous/multicast/flow rules, destroy drop QP, deactivate/free TX buffers, release RSS steering and MAC QP, and deactivate RX rings/CQs.

## State and Persistence Behavior
Most runtime state lives in `struct mlx4_en_priv`: port status, `state` flags, current MAC, active VLAN bitmap, multicast and ethtool flow lists, RSS map, ring arrays, CQs, profile pointer, stats, PFC bitmap, XDP programs, timestamp config, private flags, and delayed work. Hardware state is programmed through mlx4 commands for port init/close, QP allocation and state, multicast/unicast steering, VLAN filters, VXLAN steering, CQ moderation, VF attributes, PHV, and QP rate limits. Reconfiguration uses temporary `mlx4_en_priv`/profile copies so resource allocation can fail without immediately destroying the active configuration.

## Dependencies and Integration Points
Depends on Linux netdevice, rtnetlink, NAPI, BPF/XDP, VLAN, VXLAN UDP tunnel, devlink port, RFS, bonding notifier, DCB, and mlx4 core command/CQ/QP/flow APIs. It integrates with `en_rx.c` for RX ring allocation, activation, RSS, drop QP, and buffer sizing; TX helpers in other mlx4_en files; `en_port.c` for VLAN and stats commands; `en_resources.c` for QP context and multicast loopback; `en_ethtool.c` for reset and moderation; and timestamp helpers.

## Risks
This file is lifecycle-sensitive: start and stop ordering must prevent packets, NAPI, interrupts, work items, and TX completions from touching freed rings or QPs. Resource replacement must preserve XDP program references and queue counts while avoiding leaks on partial allocation. RX mode work races with port teardown unless `state_lock` and workqueue flushing are respected. Flow steering behavior differs across A0, B0, and device-managed steering modes. XDP changes can reduce normal TX rings to fit `MAX_TX_RINGS`, and MTU is constrained by page-sized XDP buffers. Bonding notifier logic assumes two Ethernet ports and init-net devices.

## Test Signals
Cover netdev register/unregister, ifup/ifdown, repeated MTU changes, feature toggles for RXFCS/RXALL/VLAN/loopback, XDP attach/swap/detach and oversized MTU rejection, mqprio setup, channel and ring count changes under load, TX timeout restart, RFS flow steering, unicast/multicast/promiscuous/allmulti transitions, VLAN add/delete, VXLAN port sync, VF mac/vlan/rate/spoof/link/stat ops on master, bonding mode transitions, PTP timestamp reset interactions, and leak/race checks during failed port start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_port.c

## Purpose
Wraps mlx4 firmware commands for Ethernet port filtering, link query, and statistics extraction. It updates active VLAN filters, decodes port link state/speed/autoneg/transceiver data, folds software ring counters into netdev stats, and translates firmware Ethernet/PFC/PF/PHY counters into Linux-visible stats structures.

## Important APIs, Types, and Functions
The file exports `mlx4_SET_VLAN_FLTR`, `mlx4_en_QUERY_PORT`, `mlx4_en_fold_software_stats`, and `mlx4_en_DUMP_ETH_STATS`. The helper `en_stats_adder` sums priority-specific big-endian counters in `struct mlx4_en_stat_out_mbox`. Firmware mailbox structures come from `en_port.h`; software destination structs are `net_device_stats`, `mlx4_en_port_stats`, `mlx4_en_packet_stats`, `mlx4_en_phy_stats`, `mlx4_en_flow_stats`, and `mlx4_counter`.

## Control Flow
`mlx4_SET_VLAN_FLTR` allocates a command mailbox, packs `priv->active_vlans` into 128 big-endian 32-bit entries in reverse hardware order, sends `MLX4_CMD_SET_VLAN_FLTR`, and frees the mailbox. `mlx4_en_QUERY_PORT` sends `MLX4_CMD_QUERY_PORT`, then decodes link-up, speed, autoneg, ANC/ANE flags, and transceiver into `priv->port_state`. `mlx4_en_DUMP_ETH_STATS` allocates normal and flow-control mailboxes, dumps Ethernet stats, optionally reads default counter stats and flow-control stats, locks `stats_lock`, folds software counters, resets aggregate software fields, sums per-ring stats, updates Linux netdev stats, packet stats, PF stats, per-priority flow stats, non-PFC flow stats, and PHY stats, then frees mailboxes.

## State and Persistence Behavior
The file updates in-memory netdev and private stats snapshots. `reset` in `mlx4_en_DUMP_ETH_STATS` asks firmware to clear hardware counters after dumping. VLAN filters and port query state are firmware-backed; active VLAN membership itself is kept in `priv->active_vlans` by netdev VLAN callbacks. Stats are guarded by `priv->stats_lock`, while comments note that port query is called from already synchronized ethtool context.

## Dependencies and Integration Points
Depends on Linux VLAN helpers, netdevice stats, mlx4 command mailbox APIs, default counter APIs, and capability flags such as `FLOWSTATS_EN`. It integrates with `en_netdev.c` for VLAN add/remove, stats work, open stat clearing, and link updates, and with `en_ethtool.c` for statistics display and link settings.

## Risks
The stats mailbox layout is ABI-sensitive and uses many big-endian fields. Stats string order in ethtool must match the exact struct write order here. Flow-control mailbox memory is initialized to all `0xff` when unsupported, so consumers must tolerate invalid values. Software stats are skipped for master mode and inactive ports; changing that policy can double count PF/port counters. VLAN bit packing order is hardware-specific.

## Test Signals
Validate VLAN filter programming with sparse and dense VLAN sets, link query for all supported speed encodings and link-down state, stats dump/reset, slave/master/non-master stat differences, flow-control counters with and without `FLOWSTATS_EN`, software RX/TX counter folding under traffic, dropped/error counter mapping, and ethtool stats count/order consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_port.h

## Purpose
Defines Ethernet-port firmware ABI structures and constants used by mlx4_en port commands. It describes VLAN filter mailboxes, multicast command modes, hardware link-mode ids, speed encodings, query-port response layout, and the large Ethernet statistics mailbox returned by firmware.

## Important APIs, Types, and Functions
Important constants include promiscuous command shifts, `MLX4_EN_NUM_TC`, `VLAN_FLTR_SIZE`, multicast modes, `MLX4_PROT_MASK`, `MLX4_EN_*_SPEED` encodings, query masks such as `MLX4_EN_LINK_UP_MASK`, and link mode enum values like `MLX4_10GBASE_KR`, `MLX4_40GBASE_CR4`, and `MLX4_56GBASE_SR4`. Main types are `struct mlx4_set_vlan_fltr_mbox`, `enum mlx4_link_mode`, `struct mlx4_en_query_port_context`, and `struct mlx4_en_stat_out_mbox`.

## Control Flow
The header has no executable control flow. Its field layout directly controls how `en_port.c` packs command mailboxes and decodes firmware responses, while `en_ethtool.c` maps `enum mlx4_link_mode` values into ethtool link-mode masks and speeds.

## State and Persistence Behavior
All structures are transient host representations of firmware command mailboxes, but their layout is persistent ABI for driver/firmware communication. The statistics mailbox contains hundreds of big-endian counters grouped by receive/transmit frame size, priority, VLAN/non-VLAN, bytes, totals, drops, FCS/length errors, broadcast/multicast/unicast, and loopback categories.

## Dependencies and Integration Points
Depends on kernel fixed-width and big-endian types provided by including files. It is included by `en_port.c`, `en_netdev.c`, and `en_ethtool.c`. Its link-mode ids must match mlx4 firmware PTYS/query-port definitions, and its stats fields must match the conversion logic in `mlx4_en_DUMP_ETH_STATS` and string definitions in ethtool.

## Risks
This header is ABI-sensitive: changing field order, width, endian type, or enum values can silently corrupt command interpretation. The statistics struct is large and sparsely consumed; adding or reordering fields requires coordinated updates to stats extraction and ethtool string counts. Speed encodings differ from ethtool speed constants, so translation must remain centralized in users.

## Test Signals
Compile coverage for all include users, firmware query-port decoding, PTYS link-mode mapping, VLAN filter mailbox size checks, stats dump parsing, big-endian conversion checks, and static/layout validation against firmware documentation or known hardware counter output are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_resources.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_resources.c

## Purpose
Contains small shared resource helpers for mlx4_en queue-pair context setup and multicast loopback source-check updates. It centralizes how Ethernet TX/RX/RSS QPs are initialized before mlx4 core transitions them to ready state.

## Important APIs, Types, and Functions
Exports `mlx4_en_fill_qp_context`, `mlx4_en_change_mcast_lb`, and the no-op event callback `mlx4_en_sqp_event`. The central data type is `struct mlx4_qp_context`, filled from `struct mlx4_en_priv`, queue sizes, strides, QP/CQ numbers, RSS flags, port, protection domain, UAR, counter index, DB record, VLAN feature state, VXLAN tunnel mode, and user priority.

## Control Flow
`mlx4_en_fill_qp_context` zeroes the context, sets flags, PD, MTU/message max, SQ/RQ sizes, UAR index, local QPN, scheduler queue, optional forced Ethernet user priority, counter index, send/receive CQN, multicast loopback source-check controls, doorbell record address, VLAN stripping disable bit, and VXLAN receive tunnel mode. `mlx4_en_change_mcast_lb` builds `mlx4_update_qp_params` and calls `mlx4_update_qp` to enable or disable Ethernet source-check multicast loopback behavior. `mlx4_en_sqp_event` intentionally ignores async QP events.

## State and Persistence Behavior
The helper does not own long-lived state but writes hardware context consumed by mlx4 QP creation and modification. The generated QP context persists in firmware for the QP lifetime. The multicast loopback update changes live QP behavior through firmware. It reads `dev->features`, `priv->flags`, `priv->counter_index`, profile priority count, and device capability flags.

## Dependencies and Integration Points
Depends on Linux allocation headers, mlx4 QP definitions, and mlx4 core update APIs. It is used by `en_rx.c` for RSS receive QPs and the indirection QP, by TX setup code outside this subset for send QPs, and by `en_main.c` loopback feature updates.

## Risks
QP context bitfields are hardware-specific; incorrect size/stride logarithms, doorbell address scaling, scheduler queue bits, counter index, VLAN bit, or tunnel mode can break data path setup while compiling cleanly. Loopback source-check configuration interacts with SR-IOV, self-test loopback, and `NETIF_F_LOOPBACK`; regressions can cause duplicate looped packets or missed multicast.

## Test Signals
Validate RX and TX QP creation, RSS indirection QP creation, forced user-priority traffic classes, VLAN stripping enabled/disabled, VXLAN tunnel offload receive, SR-IOV multicast loopback behavior, self-test loopback, and `NETIF_F_LOOPBACK` toggles that call `mlx4_en_change_mcast_lb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_resources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_rx.c

## Purpose
Implements the mlx4_en receive data path and RX-side resource management. It creates page-pool backed RX rings, fills hardware descriptors, processes CQEs under NAPI, handles XDP pass/drop/redirect/TX, builds SKBs from page fragments, applies checksum/VLAN/RSS/timestamp metadata, recovers from RX allocation failures, and configures/release RSS and drop QPs.

## Important APIs, Types, and Functions
Resource APIs include `mlx4_en_set_num_rx_rings`, `mlx4_en_create_rx_ring`, `mlx4_en_activate_rx_rings`, `mlx4_en_deactivate_rx_ring`, `mlx4_en_destroy_rx_ring`, `mlx4_en_calc_rx_buf`, `mlx4_en_recover_from_oom`, `mlx4_en_config_rss_steer`, `mlx4_en_release_rss_steer`, `mlx4_en_create_drop_qp`, and `mlx4_en_destroy_drop_qp`. Packet path APIs are `mlx4_en_rx_irq`, `mlx4_en_poll_rx_cq`, `mlx4_en_process_rx_cq`, `mlx4_en_xdp_rx_timestamp`, and `mlx4_en_xdp_rx_hash`. Internal helpers allocate/free fragments, initialize descriptors, complete SKBs, validate loopback packets, refill buffers, and correct checksum-complete values.

## Control Flow
Ring creation allocates `struct mlx4_en_rx_ring`, creates a DMA-mapped page pool, registers XDP RX queue metadata, allocates RX bookkeeping, and allocates hardware queue memory. Activation calculates descriptor stride for the current MTU/XDP mode, stamps small-stride rings, initializes descriptors, allocates buffers across all rings, and posts producer doorbells. NAPI polling reads CQ ownership, drops error/FCS/self-loopback/self-test packets, runs XDP before SKB allocation, handles redirect/TX/drop/pass, creates an SKB fragment container, records timestamp/RX queue/checksum/hash/VLAN metadata, attaches page fragments, submits GRO frags, advances CQ consumer, flushes XDP redirects/doorbells, updates the CQ consumer index, and refills missing RX buffers.

## State and Persistence Behavior
Per-ring state includes producer/consumer indexes, descriptor memory, page-pool pages, RX allocation records, stride/size masks, CQN, FCS removal length, XDP program pointer, XDP metadata registration, counters, and NAPI association. `priv->frag_info`, `num_frags`, `rx_skb_size`, `rx_headroom`, `dma_dir`, and `log_rx_info` are recalculated from MTU and XDP state. Firmware state includes receive QPs, RSS QP range, RSS indirection QP, drop QP, CQ ownership, doorbell records, and QP ready/reset transitions.

## Dependencies and Integration Points
Depends on Linux page_pool, XDP/BPF, NAPI, SKB fragments, GRO, DMA sync, VLAN, IPv4/IPv6 checksum helpers, IRQ affinity, and mlx4 CQ/QP APIs. It integrates with `en_netdev.c` for port start/stop, resource allocation, XDP setup, service-task OOM recovery, and ring count decisions; `en_resources.c` for QP context filling; TX XDP helpers for `XDP_TX`; timestamp helpers; and ethtool/netdev stats via per-ring counters.

## Risks
The RX fast path is memory-ordering and ownership sensitive: CQE reads require DMA barriers, consumer updates must precede buffer reposting, and page-pool references must be exact. XDP changes DMA direction, headroom, and page reuse rules. Checksum-complete correction has protocol-specific exceptions for VLAN, IPv4, IPv6, short frames, SCTP, fragments, and extension headers. Error paths that leave `frags->page` inconsistent can cause page leaks, double recycling, or DMA reuse bugs. RSS setup has several partial-failure unwind paths.

## Test Signals
Exercise RX traffic at multiple MTUs, jumbo frames, low-memory allocation failure and recovery, ring shrink on buffer allocation pressure, checksum offload for TCP/UDP/non-TCP-UDP IPv4/IPv6, VLAN strip on/off, RXFCS on/off, RX hash metadata, hardware timestamping, XDP PASS/DROP/ABORTED/REDIRECT/TX and metadata kfuncs, GRO delivery, loopback self-test validation, CQ affinity changes, RSS with one and many rings, VXLAN inner-header RSS, and teardown under active NAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_selftest.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_selftest.c

## Purpose
Implements mlx4_en ethtool self-tests. It checks hardware health/register command execution, interrupt delivery, link state, link speed decoding, and optional offline unicast loopback packet delivery.

## Important APIs, Types, and Functions
The exported function is `mlx4_en_ex_selftest`, called by the ethtool wrapper. Internal tests are `mlx4_en_test_registers`, `mlx4_en_test_interrupts`, `mlx4_en_test_link`, `mlx4_en_test_speed`, `mlx4_en_test_loopback`, and `mlx4_en_test_loopback_xmit`. Constants such as `MLX4_EN_NUM_SELF_TEST`, `MLX4_LOOPBACK_TEST_PAYLOAD`, `MLX4_EN_LOOPBACK_RETRIES`, `MLX4_EN_LOOPBACK_TIMEOUT`, and `MLX4_SELFTEST_LB_MIN_MTU` define result layout and loopback timing.

## Control Flow
`mlx4_en_ex_selftest` clears the result buffer. For offline tests it records carrier state, turns carrier off, waits for TX queues to drain, and if unicast loopback is supported runs register and loopback tests, then restores carrier if it was previously up. Online portions always test async/MSI-X interrupts, query link state, and validate decoded speed. Loopback transmit builds an ARP-like Ethernet frame addressed to the device MAC with deterministic payload bytes and sends it through `mlx4_en_xmit`; the RX path validates payload bytes when `priv->validate_loopback` is set and flips `priv->loopback_ok`.

## State and Persistence Behavior
Self-test temporarily mutates carrier state, `priv->validate_loopback`, `priv->loopback_ok`, loopback-related feature/QP flags through `mlx4_en_update_loopback_state`, and the ethtool failure flag. It does not persist results outside the caller-provided `buf`. Hardware commands used for health, interrupt, link, speed, and loopback depend on current device state.

## Dependencies and Integration Points
Depends on Linux ethtool, netdevice SKB allocation, sleeps, mlx4 command and interrupt test APIs, `mlx4_en_QUERY_PORT` from `en_port.c`, `mlx4_en_xmit` from the TX path, `mlx4_en_update_loopback_state` from `en_main.c`, and RX loopback validation in `en_rx.c`.

## Risks
Offline testing deliberately manipulates carrier and injects a loopback packet, so it must not run unnoticed on latency-sensitive traffic. Loopback success depends on RX path scheduling, MTU minimum, device loopback capability, and feature state restoration. `mlx4_en_test_link` and speed return `-ENOMEM` for any query failure, which hides the real command error. Interrupt testing changes behavior depending on MSI-X and slave mode.

## Test Signals
Run `ethtool --test` online and offline with link up/down, MSI-X enabled/disabled, PF and VF/slave modes, devices with and without unicast loopback capability, MTU below and above loopback minimum, induced health command failure, interrupted link query, and RX-path validation that receives the deterministic payload and restores loopback flags afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_selftest.c -->
