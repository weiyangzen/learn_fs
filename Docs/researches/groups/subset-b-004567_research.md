# Research: subset-b-004567

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mac.c

## Purpose
`fbnic_mac.c` programs the Meta FBNIC ASIC MAC-side hardware and exposes the MAC operation table used by PCI, phylink, ethtool stats, pause storm protection, and sensor readers. It initializes AXI request sizing, queue manager defaults, RX/TX packet buffers, flow-control/drop/ECN thresholds, and MAC link-up/link-down behavior.

## Important APIs, Types, And Functions
The public entry points are `fbnic_mac_init()`, `fbnic_mac_get_fw_settings()`, `fbnic_mac_ps_protect_to_config()`, `fbnic_mac_ps_protect_handler()`, and `fbnic_mac_check_tx_pause()`. The file instantiates `static const struct fbnic_mac fbnic_mac_asic`, whose hooks include register init, link event/status, prepare, stats readers, link transitions, and sensor reads. Internal initializers include `fbnic_mac_init_axi()`, `fbnic_mac_init_qm()`, `fbnic_mac_init_rxb()`, and `fbnic_mac_init_txb()`.

## Control Flow
Probe calls `fbnic_mac_init()`, which assigns the ASIC vtable and runs register initialization. RXB setup either preserves already-enabled FIFO sizing, warning when smaller than expected, or programs cut-through, base/size, credits, pause, drop, ECN, calendar, DRR weights, and endian/FCS registers. TXB setup initializes internal queues, TSO/CSO behavior, packet size limits, calendars, weighted scheduling, and SOP protection before enabling TCAM load.

Link detection clears stale PCS status, clears link interrupts, reads lane-lock status according to AUI/FEC mode, then advances the PMD training state machine. Link-up programming enables pause generation and pause storm protection, releases MAC clock resets, and enables RX/TX. Link-down asserts MAC clock resets and disables pause. Firmware settings map firmware speed/FEC capability fields into driver AUI/FEC enums.

## State And Persistence
Persistent driver state includes `fbd->mac`, `fbd->pmd_state`, `fbd->end_of_pmd_training`, and `fbd->ps_timeout`. Statistics are kept as software deltas using old register snapshots in `struct fbnic_stat_counter`; RSFEC/PCS narrow counters are accumulated after clear-on-read accesses. Hardware state persists in FBNIC CSR registers for queue manager, packet buffers, MAC command config, PCS interrupt masks, pause storm timers, and TCAM enable state.

## Dependencies And Integration Points
This file depends on CSR definitions from `fbnic_csr.h` via `fbnic.h`, register access helpers, firmware mailbox helpers for TSENE sensor reads, `fbnic_net` state for FEC, and phylink callers in `fbnic_phylink.c`. PCI service work invokes pause storm handling, ethtool stats code reaches the stats hooks, and phylink calls prepare/get_link/link_up/link_down through the vtable.

## Risks
Many values are hardware-policy constants: FIFO partitioning, queue credits, calendar slots, and TX/RX thresholds. Wrong values can cause packet loss, BMC starvation, or flow-control deadlocks. PMD training relies on `jiffies` timing and barriers; races can report carrier before training is stable or leave it stuck initializing. Pause storm protection is only active when TX pause is enabled and a nonzero timeout exists, so config transitions must preserve the interrupt mask and timer reset behavior.

## Test Signals
Useful signals include successful probe register initialization, phylink carrier only after the four-second PMD training delay, correct FEC/AUI reporting from firmware modes, pause storm interrupt count increments and resets, ethtool MAC/RMON/FEC counter deltas, and sensor read success/failure paths including timeout and firmware error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mac.h

## Purpose
`fbnic_mac.h` defines the MAC-facing contract for the FBNIC driver: link/FEC/AUI enums, pause storm constants, sensor IDs, jumbo frame bounds, and the `struct fbnic_mac` operations table consumed by other driver modules.

## Important APIs, Types, And Functions
The key type is `struct fbnic_mac`, a vtable with hooks for register initialization, link events, link status, PHY/MAC preparation, statistics collection, link transitions, and sensor reads. Public prototypes are `fbnic_mac_init()`, `fbnic_mac_get_fw_settings()`, `fbnic_mac_ps_protect_to_config()`, `fbnic_mac_ps_protect_handler()`, and `fbnic_mac_check_tx_pause()`. Constants include pause storm unit conversion helpers, default/max pause storm timeouts, `FBNIC_MAX_JUMBO_FRAME_SIZE`, PMD states, link event enums, FEC mode bits, AUI modes, and sensor IDs.

## Control Flow
The header does not execute code, but it shapes the runtime flow. PCI probe initializes `fbd->mac`, phylink calls the prepare/link hooks, service work calls pause storm and link training helpers, and ethtool/hwmon paths call stats/sensor hooks through this table.

## State And Persistence
The header defines state values stored elsewhere: PMD state in `fbnic_dev`, FEC/AUI in `fbnic_net`, and pause storm timeout in `fbnic_dev`. `struct fbnic_mac` itself is normally static const implementation data, while hardware state lives in registers configured through the hooks.

## Dependencies And Integration Points
It forward declares `struct fbnic_dev` and references statistics structs declared in the broader driver headers. It is included by MAC implementation, phylink, PCI service logic, and netdev-facing code that needs jumbo MTU limits or link mode names.

## Risks
Enum bit meanings are consumed by register programming and phylink reporting. Changing AUI or FEC values breaks lane-mask logic, firmware setting translation, and ethtool FEC exposure. Pause storm constants depend on ASIC RXB clock granularity and register field width.

## Test Signals
Build coverage across `fbnic_mac.c`, `fbnic_phylink.c`, and netdev MTU paths is the primary signal. Runtime signals are correct MTU maximum, stable AUI/FEC translation, pause storm timeout bounds, and expected PMD state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mdio.c

## Purpose
`fbnic_mdio.c` creates a software Clause 45 MDIO bus that lets Linux phylink/XPCS code interact with FBNIC PMA/PMD and PCS state even though the underlying data comes from FBNIC CSRs and driver-maintained PMD training state.

## Important APIs, Types, And Functions
The public API is `fbnic_mdiobus_create()`. Bus callbacks are `fbnic_mdio_read_c45()` and `fbnic_mdio_write_c45()`, which dispatch to PMD helpers (`fbnic_mdio_read_pmd()`, `fbnic_mdio_write_pmd()`) or PCS helpers (`fbnic_mdio_read_pcs()`, `fbnic_mdio_write_pcs()`). Constants translate Synopsys XPCS vendor-page bit usage into FBNIC PCS page layout.

## Control Flow
Probe calls `fbnic_mdiobus_create()`, which allocates a devm-managed `mii_bus`, installs C45 callbacks, masks all PHY addresses to prevent autoprobing, registers it, and stores it in `fbd->mdio_bus`. PMD reads synthesize device IDs, device presence, reset-ready status, and lane detection, returning lane detect only when `fbd->pmd_state == FBNIC_PMD_SEND_DATA`. PCS reads either synthesize XPCS IDs/capability registers or read mapped FBNIC PCS CSRs. PCS writes are translated and forwarded to CSR space; PMD writes are logged only.

## State And Persistence
The created bus is devm-managed and stored on `fbnic_dev`. PCS writes persist in hardware registers. PMD results are mostly synthetic and depend on driver state (`netdev`, `fbn->aui`, `fbd->pmd_state`) rather than a real MDIO-attached PHY.

## Dependencies And Integration Points
This file depends on Linux MDIO, `pcs-xpcs`, `fbnic_mac.h` state values, and FBNIC CSR register access. `fbnic_phylink_create()` uses the bus with `xpcs_create_pcs_mdiodev()`, making this file a bridge between phylink/XPCS generic code and FBNIC-specific hardware.

## Risks
The synthetic MDIO layer must match what XPCS expects. Returning zero for unsupported registers is simple but can hide missing emulation if XPCS starts depending on more PMD/PCS registers. Vendor-page bit remapping and address bounds determine whether writes hit the intended PCS half, especially for 50G R2 mode. The PMD lane-detect read is gated by driver training state, so stale PMD state can alter phylink behavior.

## Test Signals
Probe should create the MDIO bus and XPCS PCS successfully. Phylink should read expected PMA/PCS device IDs, supported devices, and lane-detect bits after training. Register tracing or dynamic debug can confirm PCS vendor-page read/write translation and absence of PHY autoprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_netdev.c

## Purpose
`fbnic_netdev.c` binds FBNIC hardware to the Linux `net_device` model. It allocates/registers the netdev, handles open/stop, MAC address and RX filter programming, MTU/XDP/timestamp configuration, queue stats, and netdev feature advertisement.

## Important APIs, Types, And Functions
Important public functions are `__fbnic_open()`, `fbnic_netdev_alloc()`, `fbnic_netdev_free()`, `fbnic_netdev_register()`, `fbnic_netdev_unregister()`, `fbnic_reset_queues()`, `__fbnic_set_rx_mode()`, `fbnic_clear_rx_mode()`, and `fbnic_check_split_frames()`. Netdev ops include open, stop, transmit, features check, set MAC, change MTU, async RX mode, stats, BPF setup, and hwtstamp get/set. Queue stat ops expose per-RX/TX and base counters.

## Control Flow
Allocation creates an Ethernet netdev, initializes `struct fbnic_net`, default queue sizes/coalescing, HDS threshold, RSS tables/key/masks, feature flags, MTU limits, XDP capabilities, and phylink. Registration derives a permanent MAC from PCI DSN and refuses invalid DSN-derived addresses.

Open names IRQs, allocates NAPI vectors and ring resources, binds queues to netdev, tells firmware the host has ownership, starts PTP time refresh, initializes firmware heartbeat, requests MAC IRQs, initializes BMC RPC/RSS, and resumes phylink. On failure it unwinds in reverse. Stop frees MAC IRQs, suspends phylink while preserving BMC link when present, downs datapath, stops time, releases ownership, unbinds queues, and frees resources.

RX mode synchronization programs host unicast, multicast, broadcast, promiscuous/all-multicast, and BMC all-multicast filters through RPC shadow TCAM helpers, then writes MACDA/action/TCE TCAMs. Timestamp configuration normalizes Linux hwtstamp filters to supported broader filters and reinitializes RSS/action rules when RX timestamping changes.

## State And Persistence
`struct fbnic_net` stores queue arrays, NAPI vectors, phylink handles, AUI/FEC, RSS state, time offset/cache, queue counts, accumulated stats after ring destruction, timestamp config, XDP program, and pause state. Netdev feature flags persist while registered. Hardware filter state is mirrored in `fbnic_dev` TCAM arrays and flushed through RPC writers.

## Dependencies And Integration Points
This file integrates with firmware ownership/heartbeat, MAC IRQ handling, phylink, PTP time, RSS/RPC filtering, TX/RX rings, ethtool ops, XDP, netdev queue management, and hardware stats. It depends heavily on `fbnic_txrx.c`, `fbnic_rpc.c`, `fbnic_phylink.c`, and firmware helpers declared elsewhere.

## Risks
Open/stop unwind ordering is critical because firmware ownership, time workers, IRQs, NAPI, and ring memory have strict dependencies. RX filter space is limited; overflow promotes to promiscuous/all-multicast modes. XDP is constrained by HDS threshold unless programs support fragments. Timestamp filtering is intentionally broader than requested, reported as `HWTSTAMP_FILTER_SOME`, which can surprise tests expecting exact filtering.

## Test Signals
Signals include successful register/unregister, valid DSN-derived MAC, open/stop leak-free cycles, RX mode changes for unicast/multicast/promisc/allmulti, hwtstamp filter normalization and rule rewrite, XDP attach rejection when MTU exceeds HDS threshold for non-frag XDP, correct queue stats after ring teardown, and expected netdev feature masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_netdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_netdev.h

## Purpose
`fbnic_netdev.h` defines `struct fbnic_net`, the per-netdev private state shared across FBNIC netdev, phylink, time, RSS, and TX/RX modules, plus prototypes for lifecycle, queue, PTP, RX mode, and phylink helpers.

## Important APIs, Types, And Functions
The central type is `struct fbnic_net`. It stores XDP program, TX/RX ring arrays, NAPI vectors, netdev/device back-pointers, queue sizes, coalescing settings, HDS threshold, phylink objects, AUI/FEC, timestamp conversion state, queue counts, RSS tables/key/hash options, accumulated stats, hardware timestamp config, and pause state. Public declarations cover open/up/down, netdev allocation/register/free/unregister, queue reset, ethtool setup, PTP/time setup, RX mode sync/clear, phylink ethtool helpers, and split-frame validation.

## Control Flow
The header establishes cross-file call boundaries: PCI allocates/registers the netdev, netdev open drives TX/RX allocation and firmware ownership, phylink updates AUI/FEC/link state, time code updates `time_high`/`time_offset`, and RPC/TXRX code uses RSS and queue state.

## State And Persistence
Most runtime network state for an FBNIC interface is persisted in `struct fbnic_net` for the life of the registered netdev. The time fields use `u64_stats_sync` to make 64-bit offset reads safe on 32-bit machines. Ring statistics can be accumulated into base stats after rings are destroyed, keeping counters visible across queue lifecycle changes.

## Dependencies And Integration Points
It includes phylink, CSR, RPC, and TXRX headers, making it the common dependency surface for major driver modules. Constants such as `FBNIC_MAX_NAPI_VECTORS`, `FBNIC_MIN_RXD_PER_FRAME`, and tunnel GSO features are shared by netdev and queue code.

## Risks
Because this header joins many modules, layout or semantic changes have wide blast radius. Queue count limits must remain compatible with ring arrays and hardware queue limits. Time fields require correct synchronization discipline. RSS table dimensions must match hardware and RPC definitions.

## Test Signals
Build coverage across all fbnic modules is the main static signal. Runtime signals include stable open/close, queue resizing, RSS programming, PTP timestamp conversion, XDP attach, phylink creation/destruction, and stats continuity after resource destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_pci.c

## Purpose
`fbnic_pci.c` is the driver entry/lifecycle module. It registers the PCI driver, maps BARs, allocates device/devlink/netdev resources, initializes firmware and MAC hardware, owns service work, handles suspend/resume/shutdown, and participates in PCI error recovery.

## Important APIs, Types, And Functions
Externally used helpers include `fbnic_rd32()`, `fbnic_fw_present()`, `fbnic_fw_wr32()`, `fbnic_fw_rd32()`, `fbnic_up()`, `fbnic_down_noidle()`, and `fbnic_down()`. PCI callbacks are `fbnic_probe()`, `fbnic_remove()`, suspend/resume helpers, shutdown, and AER handlers. Service functions include `fbnic_service_task()`, `fbnic_health_check()`, and `fbnic_fw_config_after_crash()`.

## Control Flow
Module init initializes debug support and registers the PCI driver. Probe enables the device, configures DMA mask, maps BAR0/BAR4, allocates devlink state, creates health reporters, sets queue limits and pause storm default, saves PCI state, allocates IRQs, initializes MAC registers, initializes firmware logging/mailbox, registers devlink/debug/hwmon, snapshots stats, creates MDIO, allocates netdev, sets up PTP, and registers netdev. Some late failures enter init-failure mode but return success so devlink remains available for firmware remediation.

`fbnic_up()` enables rings, fills RX buffers, writes RSS/filter state, enables NAPI, wakes TX queues, starts service work, and initializes debug NAPI entries. Down paths stop service work, disable NAPI/TX, clear RX rules, disable RSS and rings, wait for idle when requested, and flush descriptors. The service task runs under RTNL after initial phylink training notification, updates stats, handles pause storm, checks firmware heartbeat/health, syncs BMC RPC requests, and triggers depletion checks when carrier is up.

Suspend stops netdev if running, disables firmware log/mailbox/IRQs, and nulls MMIO pointers. Resume restores BAR pointers, IRQs, MAC registers, mailbox/logging, OTP checks, reopens netdev if running, and attaches device/queues. PCI error recovery uses the same suspend/resume/attach pieces around slot reset.

## State And Persistence
Persistent module state includes `fbnic_driver_name`, PCI ID tables, board info, and the registered `pci_driver`. Per-device state includes MMIO pointers, devlink, firmware mailbox/log, IRQs, service delayed work, netdev/PTP/hwmon/debug objects, and hardware stats. All-ones MMIO reads invalidate `uc_addr0/uc_addr4` and detach the netdev to await reset.

## Dependencies And Integration Points
This file is the top-level integration point for devlink, PCI, netdev, phylink, PTP, firmware mailbox/logging, IRQ allocation, hardware stats, debugfs, hwmon, BMC RPC, MAC, and TX/RX modules.

## Risks
Init-failure mode intentionally returns success after late probe failures; callers must tolerate devices with devlink but no netdev. Defensive MMIO read invalidation can cascade into netif detach and later resume/reset recovery. Service work holds RTNL while doing several health/stat/filter actions, so long firmware paths can affect netdev control latency. Suspend/resume unwind ordering must keep mailbox/logging/devlink locks and netdev locks consistent.

## Test Signals
Test probe success and init-failure probe, BAR all-ones read detection, open/down cycles through `fbnic_up()`/`fbnic_down()`, firmware crash recovery after heartbeat loss, suspend/resume with netdev up and down, PCI AER slot reset, module load/unload, and devlink availability after late probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_phylink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_phylink.c

## Purpose
`fbnic_phylink.c` adapts FBNIC MAC/PCS state to Linux phylink and XPCS. It creates/destroys phylink objects, maps firmware AUI modes to PHY interfaces, reports ethtool link/FEC/pause data, and performs MAC prepare/finish/link-up/link-down callbacks.

## Important APIs, Types, And Functions
Public APIs are `fbnic_phylink_get_pauseparam()`, `fbnic_phylink_set_pauseparam()`, `fbnic_phylink_ethtool_ksettings_get()`, `fbnic_phylink_get_fecparam()`, `fbnic_phylink_create()`, `fbnic_phylink_destroy()`, and `fbnic_phylink_pmd_training_complete_notify()`. The callback table `fbnic_phylink_mac_ops` implements PCS selection, MAC prepare/config/finish, and link state transitions.

## Control Flow
Creation instantiates an XPCS PCS over the FBNIC synthetic MDIO bus, fills `phylink_config` capabilities and supported interfaces, obtains firmware AUI/FEC defaults, and creates phylink with the selected interface. MAC prepare masks/clears PCS interrupts and resets PMD state if link is absent. MAC finish rechecks link and reenables link-change interrupts. Link-down calls the MAC hook and increments `link_down_events`; link-up stores pause state, configures RX drop mode based on TX pause, and calls the MAC link-up hook.

PMD training notification runs from service work. If the state is training and the four-second timer has elapsed, it atomically advances through LINK_READY to SEND_DATA and calls `phylink_pcs_change()` so phylink can observe stable link.

## State And Persistence
Phylink and PCS pointers live in `fbnic_net`. AUI/FEC mode, `tx_pause`, and link-down counters are stored there too. PMD state and training deadline live in `fbnic_dev`. Hardware MAC state is changed through the `fbnic_mac` vtable.

## Dependencies And Integration Points
The file depends on Linux phylink, PHY interface enums, `pcs-xpcs`, the synthetic MDIO bus, MAC hooks, TX/RX drop-mode configuration, and netdev ethtool integration. `fbnic_netdev.c` creates/destroys phylink and forwards ethtool calls; PCI service work calls training notification.

## Risks
FEC support is inferred from supported link modes and firmware defaults; mismatches can expose unsupported ethtool modes. The training state machine uses atomic compare/exchange and barriers; skipped notifications can delay carrier, while premature transitions can log link flaps. Link-up drop mode depends on TX pause and RX queue count, so pause configuration affects data-path loss behavior.

## Test Signals
Signals include phylink create/destroy success, correct interface selection for 25G/50G/50G-R2/100G-R2, ethtool FEC and lanes reporting, pause get/set propagation, carrier changes after training completion, link-down event count increments, and RX drop-mode changes when pause changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_phylink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_rpc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_rpc.c

## Purpose
`fbnic_rpc.c` manages receive packet classification and action programming: RSS tables/keys/action masks, BMC routing rules, host MAC filters, promiscuous/all-multicast handling, IP TCAM entries, action TCAM entries, TCE TCAM entries, and firmware MACDA synchronization flags.

## Important APIs, Types, And Functions
Public APIs include RSS helpers (`fbnic_reset_indir_tbl()`, `fbnic_rss_key_fill()`, `fbnic_rss_init_en_mask()`, `fbnic_flow_hash_2_rss_en_mask()`, `fbnic_rss_reinit()`, `fbnic_rss_reinit_hw()`, `fbnic_rss_disable_hw()`), BMC helpers (`fbnic_bmc_rpc_init()`, `fbnic_bmc_rpc_all_multi_config()`, `fbnic_bmc_rpc_check()`), MAC/IP sync helpers (`__fbnic_uc_sync()`, `__fbnic_mc_sync()`, `__fbnic_xc_unsync()`, `fbnic_promisc_sync()`, `fbnic_sift_macda()`, `__fbnic_ip4_sync()`, `__fbnic_ip6_sync()`, `__fbnic_ip_unsync()`), and hardware writers (`fbnic_write_macda()`, `fbnic_write_tce_tcam()`, `fbnic_write_ip_addr()`, `fbnic_write_rules()`, `fbnic_clear_rules()`, `fbnic_rpc_reset_valid_entries()`).

## Control Flow
Netdev allocation initializes RSS indirection, key, and hash options. Open calls BMC RPC init and RSS rule init; `fbnic_up()` writes RSS hardware and RX filters. RX mode changes use sync helpers to populate software shadow MACDA entries and set action bits for host/BMC/broadcast/multicast/promisc owners, then write action and address TCAMs.

RSS rule initialization creates 14 action TCAM rules split between host-unicast and xcast flows when BMC is present. Timestamp RX filter state adds TS enable bits to selected flow actions. BMC init consumes firmware BMC MAC capabilities, reserves MACDA indices, and creates action TCAM rules routing BMC traffic. Writers only flush shadow entries whose state has the update bit set; delete states clear hardware and zero software entries, while add/update states write hardware and mark valid.

## State And Persistence
The file manages shadow arrays in `fbnic_dev`: `mac_addr`, `ip_src`, `ip_dst`, `ipo_src`, `ipo_dst`, and `act_tcam`, plus `mac_addr_boundary`, `tce_tcam_last`, and firmware capability flags such as `need_bmc_tcam_reinit` and `need_bmc_macda_sync`. Hardware persistence lives in RPC RSS tables/key registers, MACDA/IP/action TCAMs, and TCE TCAM entries.

## Dependencies And Integration Points
It depends on netdev RSS/hash flags, ethtool hash option semantics, firmware capabilities and MACDA sync mailbox, BMC presence checks, CSR access, hwtstamp configuration from `fbnic_netdev.c`, and RX/TX descriptor constants for DMA hint/timestamp action fields.

## Risks
TCAM state transitions are subtle and shared with BMC rules. MACDA space is partitioned between BMC, broadcast, multicast, host unicast, and promisc entries; overflow silently changes host behavior through promisc/allmulti decisions in netdev code. IP prefix insertion attempts to preserve ordering by mask specificity; mistakes can make later rules unreachable. BMC MACDA sync is deferred by flags, so firmware and hardware may be temporarily inconsistent until service work runs.

## Test Signals
Test RSS table/key writes, hash option to RSS mask conversion, BMC present/absent paths, BMC all-multicast toggles, unicast/multicast overflow into promisc/allmulti, deletion of last owner bit causing TCAM delete, firmware MACDA sync request flagging, IPv4/IPv6 prefix insertion order, timestamp filter rule bits, and crash recovery via `fbnic_rpc_reset_valid_entries()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_rpc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_rpc.h

## Purpose
`fbnic_rpc.h` defines the shadow TCAM model and public RPC/RSS/filtering interfaces used by FBNIC netdev, firmware recovery, and receive classification code.

## Important APIs, Types, And Functions
Key types are `struct fbnic_mac_addr`, `struct fbnic_ip_addr`, and `struct fbnic_act_tcam`, each carrying value/mask data, state, and action ownership or destination data. The header defines TCAM states (`DISABLED`, `VALID`, `ADD/UPDATE`, `DELETE`), table dimensions, MACDA index layout, action table offsets reserved for BMC/NFC/RSS, RSS enable indexes, hash option indexes, action TCAM field masks, and prototypes for all RSS, BMC, MAC, IP, and rule writer helpers.

## Control Flow
The header documents the intended state progression: disabled to add to valid, valid to update/add back to valid, and valid to delete to disabled. Inline wrappers `__fbnic_uc_unsync()` and `__fbnic_mc_unsync()` call the generic MAC owner-bit removal helper with host owner indexes.

## State And Persistence
Shadow state represented by these structs lives inside `struct fbnic_dev` and mirrors hardware TCAM entries. Bitmaps in MAC/IP entries link address entries to action TCAM owners. `rss_en_mask` and `dest` in action entries become hardware action-table words.

## Dependencies And Integration Points
It includes IPv6 UAPI and bitfield helpers, forward declares `fbnic_dev`/`fbnic_net`, and is included by netdev and RPC implementation. Netdev RX mode code depends on the MACDA index constants; RSS and timestamp code depends on hash option and action table constants.

## Risks
The numeric layout is part of the hardware/software contract. Changing offsets or reserved entries can break BMC traffic isolation, RSS rule allocation, and promisc/allmulti behavior. The state values intentionally use bit-compatible update/delete checks; arbitrary enum changes would break writer tests like `state & FBNIC_TCAM_S_UPDATE`.

## Test Signals
Build and sparse coverage should catch struct/prototype drift. Runtime signals include expected TCAM state transitions, correct reservation of BMC/broadcast/promisc entries, RSS action count matching table reservations, and no overflow of MACDA/action/IP TCAM dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_time.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_time.c

## Purpose
`fbnic_time.c` implements FBNIC PTP clock support and timestamp conversion support. The hardware clock free-runs, while the driver maintains software offset and cached high bits to turn 40-bit descriptor timestamps into full nanosecond PHC time.

## Important APIs, Types, And Functions
Public functions are `fbnic_time_init()`, `fbnic_time_start()`, `fbnic_time_stop()`, `fbnic_ptp_setup()`, and `fbnic_ptp_destroy()`. PTP callbacks include `fbnic_ptp_adjfine()`, `fbnic_ptp_adjtime()`, `fbnic_ptp_gettimex64()`, `fbnic_ptp_settime64()`, and `fbnic_ptp_do_aux_work()`. Internal helpers read stable 64-bit hardware time, program the addend, refresh cached high bits, and reset PTP hardware.

## Control Flow
PTP setup initializes `time_lock`, resets PTP registers, copies the static `ptp_clock_info`, and registers the PHC. Open calls `fbnic_time_start()`, which refreshes cached high bits and schedules periodic PTP auxiliary work. Aux work warns if refresh is stale, reads the hardware high register, intentionally caches a slightly older high value, and reschedules. Stop cancels the worker and checks for refresh stalls.

PTP adjfine computes a 600 MHz clock period in Q16.32 fixed-point ns, applies scaled ppm adjustment, writes addend registers, and triggers hardware addend set. Adjtime and settime update the software offset under lock and `u64_stats_sync`. Gettime reads high/low/high registers around system timestamp capture to produce a stable PHC reading plus offset.

## State And Persistence
Hardware state includes PTP control, addend, init, adjust, and counter registers. Driver state includes `fbd->ptp`, `fbd->ptp_info`, `fbd->time_lock`, `fbd->last_read`, and per-netdev `fbn->time_high`, `fbn->time_offset`, and `fbn->time_seq`. The free-running counter is not stepped for settime/adjtime; only addend and software offset change.

## Dependencies And Integration Points
This file depends on Linux PTP clock APIs, jiffies/timers, CSR helpers, and `fbnic_net` private state. `fbnic_txrx.c` uses the `time_high`/`time_offset` scheme to convert RX/TX descriptor timestamps. Netdev open/stop controls the aux worker lifecycle.

## Risks
The timestamp conversion design assumes periodic high-bit refresh with large margin before 40-bit wrap. If the worker stalls long enough, descriptor timestamp conversion can become ambiguous. Offset updates need `u64_stats_sync` on 32-bit systems. MMIO disappearance returns `-EIO` from hardware-touching PTP callbacks only after reads/writes notice `fbnic_present()` is false.

## Test Signals
Signals include successful PHC registration, stable gettimex reads, adjfine addend changes, settime/adjtime offset behavior, aux worker refresh warnings when delayed, correct conversion of RX/TX timestamps across 40-bit low wrap, and clean PTP unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_tlv.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_tlv.c

## Purpose
`fbnic_tlv.c` implements page-sized firmware TLV message construction, attribute extraction, validation, parsing, nested/array support, and a built-in randomized self-test message/parser used to verify TLV mechanics.

## Important APIs, Types, And Functions
Public builders include `fbnic_tlv_msg_alloc()`, flag/value/int/MAC/string put helpers, and nested start/stop helpers. Public readers/parsers include unsigned/signed/string getters, `fbnic_tlv_attr_addr_copy()`, `fbnic_tlv_attr_parse_array()`, `fbnic_tlv_attr_parse()`, `fbnic_tlv_msg_parse()`, and `fbnic_tlv_parser_error()`. Test support includes `fbnic_tlv_test_create()`, `fbnic_tlv_parser_test()`, and `fbnic_tlv_test_index`.

## Control Flow
Messages are allocated as one zeroed page with a message header length in dwords. Attribute put helpers check remaining page space, write an attribute header, copy and pad data, and increase message length by aligned dwords. Nested start creates an attribute whose temporary length is also in dwords; nested stop adds the nested length to the parent and converts the nested header length to bytes.

Parsing first validates that the top header is a message and within one page, selects a parser by message ID, parses attributes using an index, then calls the parser function with a results array. Attribute validation rejects message headers in attribute position, out-of-range IDs, required unknown cannot-ignore attributes, page overrun, bad string termination, bad flag length, oversized ints/binaries, and unaligned nested/array data. Duplicate known attributes are rejected.

## State And Persistence
TLV messages are transient page allocations owned by callers. Parser results point into the original message buffer. The test path keeps a static randomized `test_struct` initialized by `get_random_once()` and compares parsed output against it, including nested and array contents.

## Dependencies And Integration Points
The file depends on byteorder definitions from the header, Linux page allocation, random data, string helpers, Ethernet address sizes, and firmware message definitions elsewhere. Firmware mailbox modules use this TLV API to encode and decode host/firmware messages.

## Risks
Length units differ between message headers (dwords) and attribute headers (bytes), with nested attributes temporarily using dwords until closed. Misuse can corrupt later attributes or trigger parser rejection. Results arrays are indexed by TLV ID and capped at 32; adding attributes with larger IDs requires design changes. `cannot_ignore` unknown attributes fail parsing, so firmware/driver version skew must be handled intentionally.

## Test Signals
The built-in test message/parser exercises unsigned/signed integer sizing, MAC copying, flags, strings, arrays, nested attributes, and duplicate/invalid parsing behavior. Additional useful tests include page-full ENOSPC, unterminated string rejection, cannot-ignore unknown rejection, duplicate attribute rejection, and array overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_tlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_tlv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_tlv.h

## Purpose
`fbnic_tlv.h` defines the on-wire/on-page TLV layout for FBNIC firmware messages and the parser/builder API used by firmware mailbox code.

## Important APIs, Types, And Functions
Key types are `struct fbnic_tlv_hdr`, `struct fbnic_tlv_msg`, `enum fbnic_tlv_type`, `struct fbnic_tlv_index`, and `struct fbnic_tlv_parser`. Macros describe alignment/size, result array capacity, unknown IDs, typed attribute descriptors, parser table entries, value pointer access, boolean flag reads, getter shorthands, and the test message schema. Function declarations cover allocation, put helpers, nested helpers, getters, address copy, array parsing, attribute/message parsing, error parsing, and test creation/parser.

## Control Flow
The header establishes the parser contract: each message parser table maps a message ID to an attribute index and callback, while each attribute index maps IDs to expected type/length. Message length is in dwords including the header; attribute length is bytes including the header; all payloads are aligned to 32-bit boundaries.

## State And Persistence
TLV state lives in caller-owned page buffers. Header bitfields persist in little-endian firmware message format and vary by CPU bitfield ordering macros. Parser result arrays contain non-owning pointers into the parsed message.

## Dependencies And Integration Points
The header includes byteorder, bits, constants, and types. It forward declares `fbnic_dev` for test helpers. Firmware command/response modules include it to build messages and define parser tables.

## Risks
Bitfield layout depends on `__LITTLE_ENDIAN_BITFIELD`/`__BIG_ENDIAN_BITFIELD`; unsupported build environments fail intentionally. Attribute IDs must fit the results array if callers want direct indexed access. The alignment and maximum raw-data constants assume page-sized messages with space reserved for safety.

## Test Signals
Compile on supported endian configurations, TLV self-test success, parser tables ending with `FBNIC_TLV_ATTR_LAST`, parser arrays ending with `FBNIC_TLV_MSG_ERROR`, and correct little-endian integer round trips are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_tlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_txrx.c

## Purpose
`fbnic_txrx.c` implements the FBNIC packet data path and ring lifecycle: TX mapping/offloads/completion, RX buffer provisioning/completion, XDP pass/drop/TX, NAPI polling, MSI-X cleanup, ring resource allocation, hardware queue enable/disable/flush/fill, stats aggregation, idle waits, interrupt coalescing, drop-mode control, and dynamic queue memory operations.

## Important APIs, Types, And Functions
Public entry points include `fbnic_xmit_frame()`, `fbnic_features_check()`, counter aggregation helpers, NAPI/resource allocation/free, queue binding/reset, `fbnic_msix_clean_rings()`, NAPI enable/disable, `fbnic_enable()`, `fbnic_disable()`, `fbnic_flush()`, `fbnic_fill()`, `fbnic_config_drop_mode()`, `fbnic_napi_depletion_check()`, `fbnic_wait_all_queues_idle()`, `fbnic_ring_csr_base()`, and `fbnic_queue_mgmt_ops`. Major internal flows are TX offload metadata (`fbnic_tx_offloads()`/`fbnic_tx_lso()`), DMA mapping (`fbnic_tx_map()`), completion cleaning (`fbnic_clean_tcq()`/`fbnic_clean_twq*()`), RX packet assembly (`fbnic_pkt_prepare()`, `fbnic_add_rx_frag()`, `fbnic_clean_rcq()`), and XDP transmit (`fbnic_pkt_tx()`).

## Control Flow
Transmit pads short frames, checks descriptor availability, builds a metadata descriptor, requests TX timestamp/CSO/LSO as needed, DMA maps skb head/frags, marks the last descriptor, updates BQL, and rings the tail doorbell when needed. Completion polling reads TCQ descriptors, handles normal head updates and timestamp completions, unmaps descriptors, completes SKBs, updates stats, wakes stopped queues, and accounts lost timestamps during discard flush.

RX allocation creates page pools, descriptor rings, per-ring buffers, and XDP RXQ info. Fill paths allocate netmem pages, split them into BD fragments, and ring BDQ tails. RCQ polling reads header/data/optional metadata/final metadata descriptors, builds an XDP buffer from header and payload pages, converts optional timestamps, runs XDP, builds SKBs for pass, commits XDP_TX tails, returns pages on consume/drop, refills BDQs, writes RCQ heads, and updates stats.

Enable paths program descriptor DMA bases, sizes, queue controls, completion interrupt mapping, RDE layout/HDS/drop mode, page-pool direct recycling, and interrupt rearm values. Disable paths mask NAPI interrupts and clear queue enables. Flush drops outstanding TX/RX work and resets completions/BQL. Dynamic queue ops allocate replacement RX triads, stop a queue by disabling its NAPI vector and waiting idle, copy out old resources, and restart the vector with the replacement.

## State And Persistence
Rings track descriptor memory, DMA address, head/tail, doorbells, flags, queue indexes, buffers, page pools, deferred heads, and stats. NAPI vectors own flexible arrays of queue triads. Netdev-level stats aggregate destroyed ring counters. Hardware state persists in per-queue CSR registers for TWQ/TCQ/BDQ/RCQ, interrupt masks/rearms, idle status, and drop controls.

## Dependencies And Integration Points
This file depends on Linux netdev queues, BQL, DMA mapping, page_pool/netmem, XDP, NAPI, TCP/GSO helpers, PTP timestamp conversion state from `fbnic_time.c`, ring constants from `fbnic_txrx.h`, and CSR definitions. Netdev open/stop and PCI up/down call its lifecycle APIs; netdev TX and feature-check ops call its transmit paths; service work calls depletion checks.

## Risks
Descriptor accounting and wrap handling are correctness-critical. TX timestamp SKBs can block cleaning until timestamp completion unless flush discard handles them. XDP with fragments depends on HDS threshold and program capabilities enforced elsewhere. Page-pool bias/refcount handling must match BDQ cleanup or pages leak/recycle unsafely. Dynamic queue stop must wait for idle and synchronize IRQs before copying resources. Idle wait treats all-ones register values as idle masks and can trigger Tx flush, so MMIO failure semantics interact with shutdown.

## Test Signals
Exercise TX small-frame padding, CSO/LSO/GSO feature fallback, DMA map failure unwind, TX timestamp completion/loss, BQL stop/wake, RX single and fragmented packets, checksum/hash/timestamp population, XDP PASS/DROP/ABORTED/TX and invalid action paths, BDQ allocation failure, NAPI budget behavior, open/stop flush leak checks, interrupt coalescing settings, queue idle timeouts, and dynamic RX queue replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_txrx.h

## Purpose
`fbnic_txrx.h` defines queue/ring constants, descriptor capacity limits, RX buffer geometry, ring/stat structures, NAPI vector layout, and public TX/RX lifecycle APIs for the FBNIC data path.

## Important APIs, Types, And Functions
Key constants set maximum descriptors per SKB, TX/RX minimum ring sizes, maximum TX/RX/XDP queues, queue size bounds/defaults, coalescing defaults, RX headroom/tailroom/padding, ring flags, HDS threshold bounds, and page-count bias. Key structs are `fbnic_pkt_buff`, `fbnic_queue_stats`, `fbnic_rx_buf`, `fbnic_ring`, `fbnic_q_triad`, and `fbnic_napi_vector`. Prototypes expose transmit, feature checks, stat aggregation, resource/NAPI/queue lifecycle, interrupt handling, enable/disable/fill/flush, drop-mode and depletion checks, idle wait, ring CSR base, debug hooks, and queue management ops.

## Control Flow
The header models each queue triad as two sub-rings plus one completion ring. TX triads use TWQ0/TWQ1 and TCQ; RX triads use HPQ/PPQ and RCQ. NAPI vectors hold flexible arrays of these triads, allowing mixed TX/RX assignment.

## State And Persistence
Ring structs hold both fast-path state (`head`, `tail`, descriptors, buffers, doorbells, stats) and slow-path DMA allocation metadata. Queue stats use `u64_stats_sync` for concurrent readers. Accumulated stats are moved to `fbnic_net` before ring destruction.

## Dependencies And Integration Points
The header includes netdevice, skbuff, u64 stats, and XDP APIs. It is included by netdev, PCI lifecycle, and TX/RX implementation modules. `fbnic_queue_mgmt_ops` integrates with netdev queue memory management.

## Risks
Constants must remain consistent with hardware descriptor formats and netdev/XDP constraints. Increasing stats fields requires updating aggregation `BUILD_BUG_ON()` checks in implementation. Ring flag semantics determine whether a ring has context, stats, or is disabled; misuse can leak counters or allocate the wrong buffers.

## Test Signals
Compile-time signals include descriptor-limit and stats-size checks. Runtime signals include correct ring allocation for configured queue sizes, XDP fragment compatibility, queue stats consistency, and no descriptor starvation under worst-case SKB fragment counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/Kconfig

## Purpose
`drivers/net/ethernet/micrel/Kconfig` defines the Linux kernel configuration menu for Micrel Ethernet device drivers. It gates visibility of individual Micrel drivers and declares their bus, PHY, CRC, EEPROM, and optional PTP dependencies.

## Important APIs, Types, And Functions
This is Kconfig data, not C code. Symbols are `NET_VENDOR_MICREL`, `KS8842`, `KS8851`, `KS8851_MLL`, and `KSZ884X_PCI`. The vendor symbol is a boolean menu gate defaulting to `y`. Driver symbols are tristate module/built-in selections for platform bus, SPI, memory-mapped, and PCI variants.

## Control Flow
When `NET_VENDOR_MICREL` is enabled, Kconfig presents the device-specific options. `KS8842` depends on `HAS_IOMEM && DMA_ENGINE`. `KS8851` depends on `SPI` and optional PTP support, selecting MII, CRC32, EEPROM_93CX6, PHYLIB, and MICREL_PHY. `KS8851_MLL` depends on HAS_IOMEM and optional PTP support with similar selects. `KSZ884X_PCI` depends on PCI and selects MII and CRC32.

## State And Persistence
Selected symbols persist in the kernel `.config` and drive object inclusion through the adjacent Makefile. Tristate values determine built-in versus module output.

## Dependencies And Integration Points
The file integrates with the top-level Ethernet vendor menu and `drivers/net/ethernet/micrel/Makefile`. It also selects PHY and helper subsystems needed by the corresponding drivers.

## Risks
Incorrect dependencies can expose drivers on unsupported platforms or hide valid hardware. Missing `select` entries can cause link failures or runtime probe failures. The broad vendor dependency expression is permissive because child symbols do precise gating.

## Test Signals
Run Kconfig allmodconfig/allyesconfig/targeted configs, verify expected prompts appear only under `NET_VENDOR_MICREL`, and verify selected objects in the Makefile match the chosen symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/Makefile

## Purpose
`drivers/net/ethernet/micrel/Makefile` maps Micrel Kconfig symbols to the object files built by Kbuild for each supported Micrel Ethernet driver variant.

## Important APIs, Types, And Functions
This is Kbuild metadata. It declares `obj-$(CONFIG_KS8842) += ks8842.o`, `obj-$(CONFIG_KS8851) += ks8851_common.o ks8851_spi.o`, `obj-$(CONFIG_KS8851_MLL) += ks8851_common.o ks8851_par.o`, and `obj-$(CONFIG_KSZ884X_PCI) += ksz884x.o`.

## Control Flow
Kbuild evaluates each `obj-*` line from the kernel configuration. SPI and parallel KS8851 variants both include `ks8851_common.o` plus their bus-specific object. PCI and KS8842 variants build standalone driver objects.

## State And Persistence
The Makefile has no runtime state. Its persistent effect is build output: objects are linked built-in or as modules according to the tristate value of the corresponding Kconfig symbol.

## Dependencies And Integration Points
It integrates directly with `micrel/Kconfig` and the source files in the Micrel Ethernet driver directory. The shared common object for KS8851 variants must stay compatible with both SPI and parallel front ends.

## Risks
If Kconfig symbols change without updating this Makefile, selected drivers will not build. Shared object inclusion must avoid duplicate symbol problems when multiple variants are built in the same configuration.

## Test Signals
Build targeted configs for each Micrel symbol as built-in and module. Verify `ks8851_common.o` is included for both KS8851 variants and that resulting module names match Kconfig help expectations, especially `ksz884x` for `KSZ884X_PCI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/Makefile -->
