# Research: subset-b-004684

Grouped research for the requested networking/MDIO/netdevsim files. Each section preserves the original source path and is wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-thunder.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-thunder.c

## Purpose
This file implements the PCI wrapper for Cavium ThunderX MDIO controllers. It discovers up to four child MDIO bus nodes below the PCI device firmware node, maps each child resource into BAR0, enables the corresponding SMI block, and registers each bus with PHYLIB through `of_mdiobus_register()`. The driver is a hardware integration layer over the shared Cavium MDIO register-access helpers in `mdio-cavium.h`.

## Important APIs, Types, and Functions
`struct thunder_mdiobus_nexus` stores the BAR0 mapping and an array of `struct cavium_mdiobus *` entries so remove can unregister and disable each SMI bus. `thunder_mdiobus_pci_probe()` is the main setup path: it uses `pcim_enable_device()`, `pcim_request_all_regions()`, `pcim_iomap()`, `device_for_each_child_node_scoped()`, `of_address_to_resource()`, `devm_mdiobus_alloc_size()`, and `of_mdiobus_register()`. The registered `mii_bus` callbacks are `cavium_mdiobus_read_c22()`, `cavium_mdiobus_write_c22()`, `cavium_mdiobus_read_c45()`, and `cavium_mdiobus_write_c45()`. `thunder_mdiobus_pci_remove()` calls `mdiobus_unregister()` and writes zero to `SMI_EN`.

## Control Flow
Probe allocates nexus state, enables the PCI device, claims and maps BAR0, then iterates firmware children. Non-OF children stop discovery because this driver only handles OF-described child buses. For each OF child, it translates the child register address, allocates a managed `mii_bus` with private Cavium bus state, computes the SMI register base as `bar0 + child_resource_start - pci_bar_start`, enables SMI via `oct_mdio_writeq()`, initializes bus identity and MDIO operation callbacks, and asks OF MDIO helpers to register child PHYs/devices. Discovery stops after four buses or on translation/allocation failure. Remove walks the stored bus pointers and performs the inverse bus unregister and SMI disable steps.

## State and Persistence
Persistent runtime state is limited to managed allocations and PCI driver data. `bar0` is managed by PCIM, `mii_bus` objects are device-managed, and bus pointers are retained in `nexus->buses[]` for teardown. Hardware state changes are the SMI enable bit per child bus and the side effects of registering MDIO/PHY devices. There is no on-disk persistence or userspace configuration in this file.

## Dependencies and Integration Points
The file depends on PCI core, OF address translation, OF MDIO registration, PHYLIB/MDIO core, and the Cavium shared MDIO helpers. The PCI ID table matches Cavium vendor device `0xa02b`; module registration is through `module_pci_driver()`. Firmware must provide child OF nodes with address resources under the PCI device, and those child nodes become MDIO bus roots for PHY discovery.

## Risks and Edge Cases
Probe currently returns success even if a child registration fails after logging `of_mdiobus_register failed`; only early PCI/BAR failures unwind with an error. The bus array has a fixed size of four and discovery silently stops at that limit. A non-OF firmware child causes the loop to break rather than skip, so mixed firmware descriptions can prevent later OF children from being processed. Since a bus pointer is stored before registration, remove may call `mdiobus_unregister()` on buses whose registration failed, which relies on core tolerance for unregistering an unregistered or partially registered bus. Address arithmetic assumes child resources lie inside BAR0.

## Test Signals
Useful signals include successful probe logs `Added bus at ...`, visible MDIO buses under sysfs, PHY devices registered from child nodes, successful Clause 22 and Clause 45 transactions, and SMI enable bits being cleared on device removal. Negative tests should cover missing/invalid child resources, more than four children, `of_mdiobus_register()` failures, and PCI unbind/rebind cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-thunder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-xgene.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-xgene.c

## Purpose
This file implements the Applied Micro X-Gene SoC MDIO platform driver. It supports both RGMII and XFI MDIO register layouts, maps SoC CSR blocks, resets/initializes the Ethernet management block, and exposes an `mii_bus` to PHYLIB using either OF child enumeration or ACPI child PHY registration.

## Important APIs, Types, and Functions
The driver revolves around `struct xgene_mdio_pdata`, which is allocated in probe and carries mapped MAC, MDIO, and diagnostic CSR bases, a clock pointer, the MDIO variant id, a MAC spinlock, and the registered bus. Exported helpers include `xgene_mdio_rd_mac()`, `xgene_mdio_wr_mac()`, `xgene_mdio_rgmii_read()`, `xgene_mdio_rgmii_write()`, and `xgene_enet_phy_register()`. XFI accesses use `xgene_xfi_mdio_read()` and `xgene_xfi_mdio_write()`. Probe selects the variant from OF or ACPI match data, maps resource 0, initializes the hardware through `xgene_mdio_reset()`, allocates `struct mii_bus`, installs callbacks, and registers it with `of_mdiobus_register()` or `mdiobus_register()` plus ACPI namespace walking.

## Control Flow
RGMII reads and writes program MAC management registers through serialized MAC CSR read/write helpers, poll the MII management busy indicator, and return either PHY data or `-EBUSY`. XFI paths write MIIM field/command CSRs directly, poll `MIIM_INDICATOR_ADDR`, clear the command register, and return data or an error for read timeout. Hardware reset toggles the OF clock or invokes ACPI `_RST`, releases diagnostic RAM shutdown through `xgene_enet_ecc_init()`, and resets GMAC. Probe configures the appropriate callback set and bus id, registers the bus, then stores it in `pdata`. Remove unregisters/frees the bus and disables the clock for OF-backed devices.

## State and Persistence
Runtime state lives in `pdata`, the allocated `mii_bus`, and the hardware CSR state. The RGMII MAC lock serializes shared MAC command registers. ACPI child devices receive `adev->driver_data = phy_dev` during manual PHY registration. The driver has no persistent storage; all state is rebuilt on probe. Clock enable state is persistent while the OF device remains probed and is disabled on remove or reset failure.

## Dependencies and Integration Points
The file integrates with platform device matching, OF, ACPI, clock framework, PHYLIB, MDIO core, and the X-Gene register definitions in `<linux/mdio/mdio-xgene.h>`. It exports several functions for other X-Gene Ethernet code to reuse. OF compatibles are `apm,xgene-mdio-rgmii` and `apm,xgene-mdio-xfi`; ACPI IDs are `APMC0D65` and `APMC0D66`.

## Risks and Edge Cases
The XFI write path does not report timeout as an error, unlike the XFI read and RGMII paths. Several polling loops use small fixed retry counts, making timing-sensitive failures possible on slow hardware. ACPI registration masks all PHYs then manually registers children with a `phy-channel` property, so malformed ACPI properties silently skip PHYs. Error unwinding after `mhi`-style registration is not relevant here, but in this file `mdiobus_alloc()` is unmanaged and must be freed on every failure path, which the probe handles via `out_mdiobus`. Clock toggling assumes a valid OF clock and may leave hardware reset state platform-specific under ACPI.

## Test Signals
Validation should include OF and ACPI boot paths, both RGMII and XFI variants, successful PHY reads/writes, timeout/error handling for busy indicators, clock enable/disable balance, and removal after partially populated buses. Good test observations are registered MDIO bus ids `xgene-mii-rgmii` or `xgene-mii-xfi`, registered PHY devices under expected addresses, and successful link negotiation by consumers of the bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-xgene.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/of_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/of_mdio.c

## Purpose
This file provides OpenFirmware/device-tree helpers for MDIO and Ethernet PHY registration. It bridges OF nodes to the generic firmware-node MDIO helpers, populates `mii_bus` instances from child nodes, supports fixed-link PHY binding compatibility, and exposes convenience APIs for network drivers to find and connect PHY devices described in the device tree.

## Important APIs, Types, and Functions
Exported entry points include `of_mdiobus_phy_device_register()`, `of_mdiobus_child_is_phy()`, `__of_mdiobus_register()`, `of_mdio_find_device()`, `of_phy_find_device()`, `of_phy_connect()`, `of_phy_get_and_connect()`, `of_phy_is_fixed_link()`, `of_phy_register_fixed_link()`, and `of_phy_deregister_fixed_link()`. Internal helpers route through firmware-node APIs such as `fwnode_get_phy_id()`, `fwnode_mdiobus_register_phy()`, `fwnode_mdiobus_phy_device_register()`, `fwnode_mdio_find_device()`, and `fwnode_phy_find_device()`. The `whitelist_phys[]` table recognizes legacy PHY compatible strings that should not be used for real driver matching.

## Control Flow
`__of_mdiobus_register()` handles the main bus setup. If no OF node is supplied it delegates to `__mdiobus_register()`. For an OF node, it rejects disabled nodes, masks automatic PHY probing, attaches the OF fwnode to the bus device, reads optional reset delays, registers the bus, then parses child nodes. `__of_mdiobus_parse_phys()` recursively descends valid `ethernet-phy-package` nodes, parses each child address with `of_mdio_parse_addr()`, classifies children as PHYs or generic MDIO devices, and registers the appropriate device type. If a child lacks a valid `reg`, the caller can request a scan; the later scan attempts all PHY addresses for nodes without `reg`, skipping already registered devices and stopping when a PHY registers successfully. The PHY connect helpers find a PHY node or fixed-link node, connect through `phy_connect_direct()`, then drop the lookup reference.

## State and Persistence
The file stores no global mutable state beyond constant match tables. It mutates `mii_bus` fields such as `phy_mask`, bus fwnode, and reset delays during registration. Registered MDIO, PHY, and fixed PHY devices persist in kernel device state until bus unregister or explicit fixed-link deregistration. Reference handling is important: find helpers return devices with elevated refcounts, and connect helpers balance the temporary lookup reference after `phy_connect_direct()`.

## Dependencies and Integration Points
Dependencies include OF core, OF IRQ, OF net helpers, PHYLIB, fixed PHY support, netdevice APIs, module exports, and generic fwnode MDIO code. Hardware-specific MDIO bus drivers call `of_mdiobus_register()`, which maps to this implementation. Ethernet MAC drivers use `of_phy_get_and_connect()` or `of_phy_connect()` to bind a netdev to a PHY or fixed-link description.

## Risks and Edge Cases
The child classification rule treats nodes without a `compatible` property as PHYs, preserving old bindings but allowing ambiguous nodes to become PHY probes. Invalid `ethernet-phy-package` nodes without `reg` are ignored, while other invalid `reg` values can trigger a full bus scan. Deprecated array-style fixed links are accepted with a warning. Fixed links with `managed = "in-band-status"` register a zeroed status, so consumers must interpret the managed mode correctly. Errors during child registration unwind by unregistering the entire bus; errors during scan only continue for `-ENODEV`.

## Test Signals
Test coverage should include DT buses with explicit PHY `reg`, child MDIO devices with non-PHY compatibles, nested `ethernet-phy-package` nodes, children without `reg` requiring scan, disabled MDIO nodes, fixed-link new and deprecated bindings, and `managed` modes. Runtime signals are registered MDIO/PHY devices with OF fwnodes, expected link callbacks from `phy_connect_direct()`, warning logs for whitelisted/deprecated bindings, and clean unregister on parse failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/of_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mhi_net.c -->
# sources/distributed-fs/ceph-client/drivers/net/mhi_net.c

## Purpose
This file implements a raw-IP network driver over MHI channels. It creates a point-to-point `net_device` for modem data channels, queues SKBs to the MHI uplink and downlink rings, refills RX buffers asynchronously, classifies received packets as IPv4, IPv6, or MAP, and maintains per-device 64-bit network statistics.

## Important APIs, Types, and Functions
`struct mhi_net_dev` is the private netdev state: it stores the `mhi_device`, netdev, RX aggregation pointers, delayed refill work, stats, RX queue size, optional MRU, and message flag field. `struct mhi_net_stats` uses `u64_stats_t` and syncp fields for lockless stats reads. Netdev operations are `mhi_ndo_open()`, `mhi_ndo_stop()`, `mhi_ndo_xmit()`, and `mhi_ndo_get_stats64()`. MHI callbacks are `mhi_net_dl_callback()` and `mhi_net_ul_callback()`. Lifecycle functions are `mhi_net_probe()`, `mhi_net_newlink()`, `mhi_net_dellink()`, and `mhi_net_remove()`.

## Control Flow
Probe allocates a raw-IP netdev using the matched channel-specific name, attaches it to the MHI device, and calls `mhi_net_newlink()`. Newlink initializes private state, starts MHI transfer channels with `mhi_prepare_for_transfer()`, records RX queue depth, and registers the netdev. Opening the netdev schedules immediate RX refill, marks carrier on because link state is managed out of band, and starts TX queues. TX queues the skb to MHI with `mhi_queue_skb()` and stops the queue if the MHI TX ring becomes full. TX completion frees the skb, updates stats, and wakes the netdev queue if descriptors are available. RX completion handles MHI errors, aggregates `-EOVERFLOW` fragments through `frag_list`, classifies successful frames by first nibble, accounts bytes/packets, hands packets to `__netif_rx()`, and schedules refill when descriptors fall below half full.

## State and Persistence
The driver maintains only runtime state. Aggregated RX fragments are held in `skbagg_head` and `skbagg_tail` until the final successful transfer completes; stale aggregation is freed during dellink. RX refill work persists while the netdev is open and is canceled on stop. Stats are kept in private memory and exposed through `ndo_get_stats64()`. MHI transfer preparation persists between newlink and dellink.

## Dependencies and Integration Points
The file depends on MHI core APIs, Linux netdev core, SKB allocation/classification, raw-IP ARP type definitions, and u64 stats helpers. It binds to MHI channels `IP_HW0` and `IP_SW0`, using predictable names `mhi_hwip%d` and `mhi_swip%d`. Higher-level modem control such as QMI establishes carrier semantics outside this driver.

## Risks and Edge Cases
RX aggregation assumes `-EOVERFLOW` fragments will be followed by a successful final fragment; repeated errors can hold memory until teardown. RX classification reads `skb->data[0]` after `skb_put()` without an explicit zero-length guard, relying on MHI transfers to provide data. `mhi_net_newlink()` calls `mhi_prepare_for_transfer()` before `register_netdev()` but does not unprepare transfers if netdev registration fails. Refill work can reschedule itself when starved, so stop/remove correctness depends on `cancel_delayed_work_sync()` and transfer teardown ordering. MHI queue full handling relies on callbacks to wake queues.

## Test Signals
Useful tests include probe/remove for both channel names, open/stop cycles, TX ring full and wake behavior, RX refill starvation, normal IPv4/IPv6/MAP receive classification, fragmented receive aggregation, and MHI error statuses `-EOVERFLOW`, `-ENOTCONN`, and unknown errors. Stats should reflect packets, bytes, errors, and drops accurately under concurrent traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mhi_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mii.c -->
# sources/distributed-fs/ceph-client/drivers/net/mii.c

## Purpose
This file is the legacy MII helper library used by Ethernet drivers that manage PHYs through `struct mii_if_info`. It translates MII/GMII registers into ethtool settings, applies requested link advertisements or forced media settings, checks link and media state, restarts autonegotiation, and handles old MII ioctl commands.

## Important APIs, Types, and Functions
The key dependency type is `struct mii_if_info`, supplied by caller drivers with `mdio_read`, `mdio_write`, `dev`, `phy_id`, masks, and capability flags. Exported functions include `mii_ethtool_gset()`, `mii_ethtool_get_link_ksettings()`, `mii_ethtool_sset()`, `mii_ethtool_set_link_ksettings()`, `mii_check_gmii_support()`, `mii_link_ok()`, `mii_nway_restart()`, `mii_check_link()`, `mii_check_media()`, and `generic_mii_ioctl()`. Internal `mii_get_an()` reads advertised or partner abilities and converts them to ethtool legacy bitmaps.

## Control Flow
The get-settings paths read `MII_BMCR`, `MII_BMSR`, and, when GMII is supported, `MII_CTRL1000` and `MII_STAT1000`. They build supported/advertising/link-partner fields, determine negotiated or forced speed/duplex, update `mii->full_duplex`, and convert to either legacy `ethtool_cmd` or modern link-mode arrays. The set-settings paths validate speed, duplex, port, phy address, autoneg mode, and GMII capability. For autoneg, they rewrite advertisement registers, optionally `MII_CTRL1000`, then set `BMCR_ANENABLE | BMCR_ANRESTART`; for forced mode, they clear autoneg/speed/duplex bits and set the requested BMCR bits. Link check reads BMSR twice to handle latch behavior. Media check compares old/new carrier, updates netdev carrier, reads advertised/LPA registers, reports link messages, and returns whether duplex changed. The ioctl handler masks phy/reg ids, handles read commands, tracks duplex/advertising side effects for writes, and delegates MDIO writes.

## State and Persistence
The library does not allocate or own objects. It updates fields in the caller-owned `mii_if_info`: `full_duplex`, `force_media`, and `advertising`. It also changes persistent PHY register state through caller-provided MDIO operations and updates netdev carrier state. There is no internal locking; callers must serialize if their MDIO path or netdev state requires it.

## Dependencies and Integration Points
The file integrates with MDIO register definitions, ethtool legacy and link-ksettings APIs, netdevice carrier APIs, and ioctl commands `SIOCGMIIPHY`, `SIOCGMIIREG`, and `SIOCSMIIREG`. It is exported as GPL module symbols for older drivers rather than being a standalone device driver.

## Risks and Edge Cases
Autoneg result calculation can fall back to 10 Mbps when no common ability is available, which matches legacy behavior but can be misleading if reads failed. The code does not check negative MDIO read errors before interpreting register bits, so drivers must provide reliable callbacks or tolerate odd ethtool output. Forced 1000 Mbps is allowed only when `supports_gmii`; half/full setting is derived directly from BMCR. `generic_mii_ioctl()` allows writes to arbitrary masked PHY/register pairs and only updates cached state when the target PHY matches `mii_if->phy_id`.

## Test Signals
Tests should cover C22 register read/write callback interactions, ethtool get/set for legacy and link-ksettings APIs, autoneg restart, forced speed/duplex, GMII support detection through `BMSR_ESTATEN` and `MII_ESTATUS`, link latch double-read behavior, carrier transitions, and ioctl read/write state changes. Driver tests should verify caller locking and correct duplex-change notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/net_failover.c -->
# sources/distributed-fs/ceph-client/drivers/net/net_failover.c

## Purpose
This file implements the `net_failover` upper netdev used by paravirtualized drivers to present a stable interface backed by a standby paravirtual device and an optional primary direct-attached VF. It provides active-backup transmit behavior, lower device registration hooks for the generic failover core, statistics folding across lower devices, VLAN and multicast synchronization, and public create/destroy APIs.

## Important APIs, Types, and Functions
The central private state is `struct net_failover_info` from `<net/net_failover.h>`, containing RCU-protected `primary_dev` and `standby_dev` pointers, stats snapshots, and a stats lock. Exported APIs are `net_failover_create()` and `net_failover_destroy()`. Netdev operations include open/close, start xmit, select queue, get stats, change MTU, set RX mode, VLAN add/del, address validation, and feature checks. Failover integration uses `struct failover_ops net_failover_ops` with slave pre-register/register/unregister/link/name-change and RX handler callbacks.

## Control Flow
Create allocates an Ethernet upper with 16 queues, copies the standby MAC and MTU bounds, sets failover features/flags, registers the upper netdev, then registers with the generic failover core. Opening the upper opens primary then standby lowers and enables carrier/queues if either lower is ready. Transmit first tries the primary lower if running and carrier-up, falls back to standby, and drops if neither can transmit. Queue selection delegates to the primary when present, stores the original queue mapping for later restoration, and folds the selected queue into the upper queue range. Slave registration aligns MTU, holds the lower device, opens it if needed, syncs unicast/multicast lists and VLANs, assigns it to primary or standby based on parent device identity, snapshots stats, recomputes features, and emits `NETDEV_JOIN`. Unregistration reverses VLAN/address sync, closes and drops the lower, clears the RCU pointer, recomputes features, and preserves accumulated stats.

## State and Persistence
State is runtime-only: RCU pointers to lower devices, cached stats snapshots, accumulated failover stats, upper netdev flags/features, lower VLAN/address lists, and carrier/queue state. No data survives module unload or device destruction. RCU is used for fast transmit/RX paths, RTNL for structural changes, and `stats_lock` for stats folding.

## Dependencies and Integration Points
The file depends on netdevice core, etherdevice helpers, ethtool, VLAN helpers, PCI device checks, netpoll headers, RTNL, scheduler queue metadata, and the generic failover infrastructure. Paravirtual drivers call `net_failover_create()` with their standby device and later call `net_failover_destroy()`. The generic failover core discovers and binds compatible primary VF devices by MAC and invokes these operations.

## Risks and Edge Cases
Primary eligibility is approximated by requiring a PCI parent because there is no generic VF test. If standby VLAN synchronization fails after primary VLAN setup, the code rolls back the primary VLAN add. MTU changes roll back primary MTU if standby fails, but lower devices may have side effects. RX handler drops standby-origin frames with `RX_HANDLER_EXACT` while primary exists, enforcing primary preference but making standby receive inactive until failover. Stats folding filters negative deltas and handles apparent 32-bit counters, but lower driver stat resets can still make accounting approximate. Destroy assumes proper failover core serialization under RTNL.

## Test Signals
Tests should create/destroy failover devices, attach/detach standby and PCI primary lowers, verify transmit preference and fallback, check carrier transitions on lower link changes, exercise MTU and VLAN rollback paths, confirm multicast/unicast list propagation, validate RX handler behavior, and inspect folded stats across lower removal/re-add. Live migration scenarios should show traffic moving from VF to standby when the VF unregisters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/net_failover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netconsole.c -->
# sources/distributed-fs/ceph-client/drivers/net/netconsole.c

## Purpose
This file implements `netconsole`, a crash-oriented kernel console that sends printk output over UDP using netpoll. It supports boot/module parameter targets, optional dynamic configfs targets, basic and extended console formats, per-target userdata/sysdata, automatic deactivation and resume on network-device events, and transmit error counters.

## Important APIs, Types, and Functions
`struct netconsole_target` is the key object. It holds list/configfs nodes, cached userdata and sysdata fields, a message counter, per-target stats, state (`STATE_DISABLED`, `STATE_ENABLED`, `STATE_DEACTIVATED`), formatting flags, a `struct netpoll`, a fixed send buffer, and resume work. Global state includes `target_list`, `target_cleanup_list`, `target_list_lock`, `target_cleanup_list_lock`, `dynamic_netconsole_mutex`, the workqueue, and two `struct console` instances (`netconsole` and `netconsole_ext`). Important functions include `alloc_and_init()`, `enabled_store()`, `netconsole_netdev_event()`, `netconsole_write()`, `send_ext_msg_udp()`, `netconsole_parser_cmdline()`, `alloc_param_target()`, `init_netconsole()`, and `cleanup_netconsole()`.

## Control Flow
Initialization parses semicolon-separated `netconsole=` targets, creates netpoll targets, registers a workqueue, netdevice notifier, configfs subsystem, and the needed console types. Console writes run under `target_list_lock` via the console device lock. `netconsole_write()` filters by `oops_only`, target format, enabled state, and running netdev, enters nbcon unsafe context, then sends either basic chunks or extended messages. Extended messages may prepend kernel release, append userdata and runtime sysdata, and fragment over `MAX_PRINT_CHUNK` with an `ncfrag` header. Dynamic enable through configfs validates the extended/release combination, registers the relevant console if needed, calls `netpoll_setup()`, and marks the target enabled. Dynamic disable marks the target disabled, moves it to the cleanup list under the spinlock, unregisters unused console types, and performs deferred `netpoll` cleanup under RTNL. Netdevice events update names, deactivate targets on unregister, disable them on join/release, and schedule resume work for matching reappearing devices.

## State and Persistence
State is in memory only, but configfs exposes mutable target parameters: enable state, format flags, device name, local/remote ports and IPs, local/remote MACs, transmit errors, userdata entries, and sysdata feature toggles. Enabled targets own active netpoll state. Deactivated targets remember enough identity to resume by device name or MAC. Userdata is cached as a formatted string and swapped under the target list spinlock so the write path can append it safely. Sysdata is generated per message for enabled features such as CPU, task name, release, and message id.

## Dependencies and Integration Points
The driver integrates with console/nbcon, netpoll, configfs, netdevice notifier chain, RTNL, workqueues, IPv4/IPv6 parsers, ethernet helpers, UTS release data, and u64 stats. The boot option parser accepts `[src-port]@[src-ip]/[dev-or-mac],[tgt-port]@<tgt-ip>/[tgt-mac]`, with `+` for extended mode and `r` for release prepending.

## Risks and Edge Cases
The write path must be IRQ/crash safe, so sleeping cleanup is deferred through a cleanup list. Lock ordering between RTNL, cleanup mutex, dynamic mutex, and target spinlock is critical. Dynamic configfs removal must cancel pending resume work and avoid racing deactivated targets. Extended fragmentation assumes an extended console header containing `;`; missing headers trigger warnings and drop. Userdata length is bounded, but many entries can still enlarge output and force fragmentation. Netdevice unregister moves targets to deactivated state so messages stop until a matching device returns; join/release disable instead to avoid auto-resuming enslaved devices. `oops_only` suppresses normal messages.

## Test Signals
Tests should cover boot parameter parsing for IPv4/IPv6, device name and MAC binding, dynamic configfs create/enable/disable/remove, basic versus extended console registration, release flag validation, userdata and sysdata updates, message fragmentation, transmit error counters, netdevice rename/unregister/register/join/release events, and cleanup during module exit. Crash-path confidence comes from verifying netpoll sends while normal networking locks may be unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netconsole.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/Makefile

## Purpose
This Makefile builds the `netdevsim` kernel module and conditionally includes simulator feature objects based on kernel configuration. It defines the base object list for the network device simulator and adds optional capability files for BPF, XFRM, psample, PSP, and MACsec.

## Important APIs, Types, and Functions
The important build variables are `obj-$(CONFIG_NETDEVSIM) += netdevsim.o` and `netdevsim-objs := ...`. The base object list includes `netdev.o`, `dev.o`, `ethtool.o`, `fib.o`, `bus.o`, `health.o`, `hwstats.o`, `udp_tunnels.o`, and `tc.o`. Conditional blocks append `bpf.o` when `CONFIG_BPF_SYSCALL=y`, `ipsec.o` when `CONFIG_XFRM_OFFLOAD` is set, `psample.o` when `CONFIG_PSAMPLE` is set, `psp.o` when `CONFIG_INET_PSP` is set, and `macsec.o` when `CONFIG_MACSEC` is set.

## Control Flow
Kbuild evaluates the Makefile at build time. If `CONFIG_NETDEVSIM` is disabled, no module is built. If it is enabled as built-in or module, Kbuild links `netdevsim.o` from the base object list plus any optional feature objects whose configs are enabled.

## State and Persistence
There is no runtime state. The file persists only build composition, determining which C files contribute symbols to the final module.

## Dependencies and Integration Points
This file integrates with kernel Kbuild and the configuration system. Its conditional object inclusion must match preprocessor declarations and function calls in `netdevsim.h` and the base files. For example, BPF entry points in `bpf.c` are only linked when `CONFIG_BPF_SYSCALL=y`, and XFRM/psample/PSP/MACsec support is linked only when the relevant subsystems are configured.

## Risks and Edge Cases
Incorrect conditionals can produce unresolved symbols or silently omit test features. The `ifneq ($(CONFIG_*),)` form includes objects for both built-in and module-valued options, while the BPF block specifically requires `y`; that distinction matters when dependencies cannot be modular or when a feature is unavailable for module builds. The base object list must include files needed for module init/exit and common simulator lifecycle.

## Test Signals
Build tests should exercise `CONFIG_NETDEVSIM=y`, `CONFIG_NETDEVSIM=m`, and feature combinations with BPF, XFRM offload, psample, PSP, and MACsec enabled or disabled. The expected signal is a linked `netdevsim` module with no unresolved references and feature-specific debugfs/devlink behavior only when corresponding objects are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/bpf.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/bpf.c

## Purpose
This file implements netdevsim's BPF and XDP offload simulation. It provides fake verifier/offload callbacks, debugfs-controlled accept/reject knobs, TC classifier offload handling, XDP driver and hardware attach paths, and a tiny in-memory implementation of offloaded BPF array/hash maps for selftests.

## Important APIs, Types, and Functions
`struct nsim_bpf_bound_prog` tracks an offloaded program's owning simulated device, BPF program pointer, debugfs directory, verifier state string, loaded flag, and list membership. `struct nsim_bpf_bound_map` tracks an offloaded map, a mutex, and up to two key/value entries. Important entry points are `nsim_bpf_setup_tc_block_cb()`, `nsim_bpf_disable_tc()`, `nsim_bpf()`, `nsim_bpf_dev_init()`, `nsim_bpf_dev_exit()`, `nsim_bpf_init()`, and `nsim_bpf_uninit()`. Offload callbacks are exposed through `struct bpf_prog_offload_ops nsim_bpf_dev_ops` and `struct bpf_map_dev_ops nsim_bpf_map_ops`.

## Control Flow
When an offloaded program is prepared, `nsim_bpf_verifier_prep()` checks `bpf_bind_accept`, creates program state, debugfs files, and stores state in `prog->aux->offload->dev_priv`. The verifier instruction hook can delay on the first instruction, logs a message on the last instruction, and rejects if `bpf_bind_verifier_accept` is false. Translation marks state as `xlated`; destroy warns if still loaded, removes debugfs, unlinks, and frees state. TC offload validates type, chain, protocol, debugfs accept flags, and bound-program requirements, then swaps `ns->bpf_offloaded`. XDP driver attach validates non-offloaded programs and MTU constraints; XDP hardware attach requires a translated offloaded program and shares the same single hardware offload slot with TC. Map allocation accepts only array/hash maps with at most two entries and no map flags, installs map ops, and stores data in kernel memory.

## State and Persistence
All state is runtime and debugfs-visible. Per-device debugfs toggles control verifier acceptance, verifier delay, TC acceptance, unbound TC acceptance, XDP driver/hardware acceptance, and map acceptance. Program and map lists live under `nsim_dev`; netdev-specific state stores current XDP attachments and the currently offloaded BPF id. Offloaded maps persist until BPF frees them; their key/value entries are protected by a mutex.

## Dependencies and Integration Points
The file integrates with BPF verifier/offload infrastructure, TC classifier offload, XDP attachment helpers, rtnetlink locking, debugfs, netdevsim device lifecycle, and packet classifier extack reporting. It depends on `netdevsim.h` for simulator structures and debugfs directories.

## Risks and Edge Cases
Only one TC or hardware XDP program can occupy the simulated offload slot, so the code rejects conflicting loads. The TC path treats old-program mismatches carefully to avoid removing a program that no longer matches driver state. Offloaded array map allocation initializes all two possible slots, regardless of requested `max_entries` bounded to two; callers rely on BPF map metadata for valid indexes. Map list operations are not protected by an explicit list lock here, relying on offload lifecycle serialization. MTU checks reject XDP programs without frag support when MTU exceeds `NSIM_XDP_MAX_MTU`.

## Test Signals
Selftests can flip debugfs booleans to force verifier, TC, XDP, and map failures; observe bound program debugfs directories with `state`, `id`, and `loaded`; load and unload TC and XDP offloads; attempt conflicting TC/XDP hardware programs; exercise offloaded hash and array map lookup/update/delete/next-key operations; and verify cleanup warnings do not fire after normal unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/bus.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/bus.c

## Purpose
This file implements the synthetic bus used to create and manage `netdevsim` devices from sysfs. It provides bus attributes to add/delete simulated devices and link/unlink netdevsim peers, per-device attributes to configure SR-IOV-like VFs and ports, and module lifecycle for bus and driver registration.

## Important APIs, Types, and Functions
Global state includes an IDA for device ids, `nsim_bus_dev_list`, `nsim_bus_dev_list_lock`, `nsim_bus_enable`, a refcount of bus devices, and a completion for teardown. Per-device sysfs attributes are `sriov_numvfs`, `new_port`, and `del_port`. Bus attributes are `new_device`, `del_device`, `link_device`, and `unlink_device`. Probe/remove bridge to `nsim_drv_probe()` and `nsim_drv_remove()`. Public lifecycle functions are `nsim_bus_init()` and `nsim_bus_exit()`.

## Control Flow
Writing `new_device` parses `id [port_count [num_queues]]`, checks the bus enable flag under the list mutex, allocates/registers a `struct nsim_bus_dev`, increments the device refcount, marks the device initialized with release semantics, and adds it to the global list. Device registration triggers bus probe, which creates the devlink/netdevsim instance in `dev.c`. Writing `del_device` finds the id under the list lock, removes it from the list, and unregisters the device. Per-device `new_port` parses a PF port id plus optional MAC address, validates initialization and MAC format, and calls `nsim_drv_port_add()`. `del_port` removes a PF port. `sriov_numvfs` calls `nsim_drv_configure_vfs()` while the device lock is held. Link/unlink look up net namespaces by fd, find netdevs by ifindex under RTNL, validate both are netdevsim devices, then assign or clear reciprocal RCU peer pointers and carrier state.

## State and Persistence
State is in-memory synthetic device state plus sysfs-visible attributes. `init` and `nsim_bus_enable` use acquire/release ordering to prevent sysfs operations from racing uninitialized or exiting objects. Device ids are reserved in the IDA until device deletion. Peer links are RCU pointers and are cleared with `synchronize_net()` on unlink before waking queues.

## Dependencies and Integration Points
This file integrates with Linux driver core bus/device APIs, sysfs attributes, net namespace fd lookup, RTNL, netdevsim core creation/destruction in `dev.c`, and SR-IOV-style netdevsim configuration. It registers a `bus_type` named `DRV_NAME` and a matching `device_driver`.

## Risks and Edge Cases
Input parsing is strict and reports format errors. `unlink_device_store()` parses `netnsfd` as unsigned despite storing in an `int`, which can make negative fd inputs fail format expectations differently from `link_device_store()`. Link creation refuses already-linked devices and self-links. Bus exit disables new operations, unregisters all remaining devices, waits for release completion, then unregisters driver and bus; correctness depends on refcounting every created `nsim_bus_dev`. Device deletion while sysfs operations run is guarded by list/device locks and init flags but remains concurrency-sensitive.

## Test Signals
Tests should write sysfs `new_device`/`del_device`, create/delete PF ports with and without MAC addresses, change `sriov_numvfs`, link and unlink devices across namespaces, verify carrier behavior when linked devices are up, and unload the module with devices present. Expected signals include created bus devices, netdevsim netdevs and devlink instances, reciprocal peer pointers, and no leaks or use-after-free warnings on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/dev.c

## Purpose
This file implements most of the device-level netdevsim/devlink simulation: devlink allocation and registration, resources, parameters, regions, reload, flash update, traps, rate objects, ports, VF/switchdev behavior, debugfs controls, FIB/health/BPF/psample/hwstats integration, and driver probe/remove paths behind the synthetic bus.

## Important APIs, Types, and Functions
Major functions include `nsim_drv_probe()`, `nsim_drv_remove()`, `nsim_dev_reload_create()`, `nsim_dev_reload_destroy()`, `__nsim_dev_port_add()`, `__nsim_dev_port_del()`, `nsim_drv_port_add()`, `nsim_drv_port_del()`, `nsim_drv_configure_vfs()`, `nsim_dev_resources_register()`, `nsim_dev_traps_init()`, `nsim_dev_traps_exit()`, `nsim_dev_flash_update()`, and `nsim_dev_init()/nsim_dev_exit()`. `nsim_dev_devlink_ops` wires devlink callbacks for eswitch mode, reload, info, flash, traps, policers, rates, and drop counters. Debugfs file operations provide snapshot creation, trap flow action cookie injection, and `max_vfs` mutation.

## Control Flow
Probe allocates a devlink instance in the bus device's initial net namespace, initializes `struct nsim_dev`, stores bus drvdata, allocates VF configs, registers devlink, resources, params, dummy region, traps, debugfs, FIB, health, BPF offload device, psample, hwstats, and initial PF ports. Port add registers a devlink port with physical or PCI VF attributes, optional PF resource, debugfs directory, creates the netdevsim netdev via `nsim_create()`, optionally creates a devlink rate leaf, and links it into `port_list`. Switchdev mode creates VF ports for configured VFs; legacy mode destroys VF ports and rate nodes. Reload down destroys the reloadable parts unless debugfs forbids it; reload up recreates them unless debugfs forces failure. Trap work periodically reports generated UDP packets for running ports and enabled traps under the devlink lock. Remove reverses reloadable state, exits BPF/debugfs/params/resources, unregisters devlink, frees VF configs and flow action cookie, and releases the devlink object.

## State and Persistence
State is runtime-only but widely exposed through debugfs and devlink. Persistent-in-memory fields include port list, switch id, eswitch mode, VF configs, reload failure flags, firmware update controls, max MAC/test params, dummy region snapshots, trap action/counter state, flow action cookie, rate parent names and bandwidth values, FIB data, and feature subsystem state. Devlink driverinit parameters can be staged and loaded on reload. Delayed trap work persists while traps are initialized and must be canceled before unregistering trap structures.

## Dependencies and Integration Points
The file integrates with devlink, debugfs, rtnetlink/devlink locking, netdevsim netdev creation in `netdev.o`, FIB resource accounting, health reporters, BPF offload setup, psample, hardware stats, UDP tunnel simulation, flow action cookies, SKB construction, and bus device lifecycle from `bus.c`. It also creates the top-level debugfs directory used by other netdevsim files.

## Risks and Edge Cases
Error unwinding is long and must maintain exact reverse order for devlink, debugfs, delayed work, and subsystem registrations. Trap report work requeues itself and takes the devlink lock; teardown cancels it before unregistering traps. Reload destroy skips work if devlink is in reload-failed state, changing cleanup expectations. `max_vfs` can only change when no VFs are configured and is bounded by the VF port index range. Switching to switchdev with VF creation failures rolls back already-created VF ports. Rate values must be exact 1 Mbps units and under 5000 Mbps. Debugfs-controlled failure knobs intentionally create negative paths for tests.

## Test Signals
Validation should exercise bus probe/remove, devlink resource and parameter visibility, dummy region snapshots, reload success/failure/forbidden paths, flash update status notifications, trap action/group/policer operations and counters, switchdev/legacy mode transitions, VF configuration, PF/VF port add/delete, rate leaf/node operations, max_vfs changes, and subsystem cleanup under module unload. Selftests should check debugfs knobs cause expected extack errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/ethtool.c

## Purpose
This file provides ethtool operations for each netdevsim netdev. It simulates pause parameters and stats, coalescing, ring parameters, channels/queue counts, FEC settings and statistics, and timestamp PHC reporting, with debugfs knobs for selected failure and reporting behaviors.

## Important APIs, Types, and Functions
`nsim_ethtool_ops` installs handlers for pause stats/params, coalesce get/set, ring get/set, channels get/set, FEC get/set/stats, and timestamp info. Helper functions include `nsim_get_pause_stats()`, `nsim_get_pauseparam()`, `nsim_set_pauseparam()`, `nsim_get_coalesce()`, `nsim_set_coalesce()`, `nsim_get_ringparam()`, `nsim_set_ringparam()`, `nsim_get_channels()`, `nsim_set_channels()`, `nsim_get_fecparam()`, `nsim_set_fecparam()`, `nsim_get_fec_stats()`, `nsim_get_ts_info()`, and `nsim_ethtool_init()`.

## Control Flow
Initialization assigns the ethtool ops to the netdev, initializes default ring limits and pending sizes, enables pause stat reporting by default, sets FEC to none, sets channel count from the bus device queue count, and creates debugfs files under the port's `ethtool` directory. Getters mostly copy simulator state into ethtool structures. Setters copy user-requested state back into `ns->ethtool`, with validation for unsupported pause autoneg and injected FEC get/set errors. Channel setting calls `netif_set_real_num_queues()` for RX and TX and, when linked to a peer, synchronizes networking and wakes local and peer queues. FEC setting computes active FEC as the highest selected mode after normalizing AUTO/OFF/NONE semantics.

## State and Persistence
Per-netdevsim runtime state lives under `ns->ethtool`: pause reporting flags, pause rx/tx settings, coalesce structure, ring structure, channel count, FEC parameters, and injected `get_err`/`set_err` values. Debugfs files expose error injection and selected pause/ring maxima. There is no persistent storage beyond the lifetime of the simulated netdev.

## Dependencies and Integration Points
The file depends on ethtool core structures, `netdev_queues` queue count helpers, debugfs, RCU peer pointers from netdevsim linking, and mock PHC support through `mock_phc_index(ns->phc)`. It complements `bus.c` queue-count creation and `dev.c` port/debugfs lifecycle.

## Risks and Edge Cases
Pause autoneg is rejected because the simulator does not support link ksettings. Ring setters update pending values but not max values; max values can be adjusted through debugfs to exercise ethtool validation paths. Channel changes can fail if queue count changes are invalid, and linked peers require wakeups to avoid stuck queues. FEC error injection returns negative values of debugfs-controlled integers, so tests must set sensible errno values. Active FEC selection uses `fls()` on a normalized bitmask and assumes at least one bit is set.

## Test Signals
Tests should verify `ethtool -a/-A`, coalesce, ring, channels, FEC, FEC stats, and timestamp info on netdevsim devices. Debugfs `get_err` and `set_err` should force FEC failures. Channel tests should confirm real queue count changes and peer queue wakeups when devices are linked. Pause stat toggles should change reported RX/TX pause frame counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/ethtool.c -->
