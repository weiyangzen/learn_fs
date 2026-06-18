# subset-b-004571 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ptp.c

Purpose: implements IEEE 1588/PTP support for the LAN743x PCI Ethernet driver. It owns the PHC registration, clock read/set/step/frequency adjustment, GPIO and LED-pin muxing for periodic outputs, PCI11x1x PTP-IO external timestamp capture, TX hardware timestamp queue matching, interrupt/aux-worker handling, latency compensation, and the netdev hardware timestamping get/set hooks.

Important APIs and functions: exported entry points are `lan743x_gpio_init`, `lan743x_ptp_init`, `lan743x_ptp_open`, `lan743x_ptp_close`, `lan743x_ptp_isr`, `lan743x_ptp_request_tx_timestamp`, `lan743x_ptp_unrequest_tx_timestamp`, `lan743x_ptp_tx_timestamp_skb`, `lan743x_ptp_update_latency`, `lan743x_ptp_hwtstamp_get`, and `lan743x_ptp_hwtstamp_set`. The registered `ptp_clock_info` callbacks are `lan743x_ptpci_adjfine`, `lan743x_ptpci_adjtime`, `lan743x_ptpci_gettime64`, `lan743x_ptpci_settime64`, `lan743x_ptpci_enable`, `lan743x_ptpci_do_aux_work`, and `lan743x_ptpci_verify_pin_config`. Hardware command helpers include `lan743x_ptp_clock_get`, `lan743x_ptp_io_clock_get`, `lan743x_ptp_clock_set`, `lan743x_ptp_clock_step`, and `lan743x_ptp_wait_till_cmd_done`.

Control flow: initialization sets up the PTP command mutex, TX timestamp spinlock, event-channel bookkeeping, GPIO defaults, and LED mux snapshots. `lan743x_ptp_open` resets and enables the PTP block, syncs the device clock to TAI, enables TX timestamp/error interrupts, builds pin descriptors based on chip ID, and registers the PHC when `CONFIG_PTP_1588_CLOCK` is enabled. PTP requests are dispatched by `lan743x_ptpci_enable`: PEROUT programs either LAN743x GPIO-backed event channels or PCI11x1x PTP-IO output routing; EXTTS is only valid on PCI11x1x and configures edge-lock capture and PTP-IO interrupts. The ISR masks the 1588 interrupt and schedules the PHC worker for TX timestamps; the worker drains interrupt status, reads TX egress timestamps or PTP-IO capture registers, posts `PTP_CLOCK_EXTTS` events, completes queued SKBs, and reenables interrupts.

State and persistence: all state is kernel-resident in `adapter->ptp` and `adapter->gpio`. Persistent runtime state includes registered PHC pointer/flags, per-pin descriptors, reserved event channels, perout pin/channel assignments, PCI11x1x EXTTS edge flags and last timestamps, LED mux state, and paired TX timestamp queues for SKBs and hardware timestamp records. `command_lock` serializes CSR command sequences and PTP-IO selection; `tx_ts_lock` serializes pending timestamp counters and queues. Hardware-visible state is held in PTP command/control, clock, target/reload, PTP-IO, GPIO, latency, and TX modifier registers until close, reset, or a new timestamping configuration.

Dependencies and integration points: depends on `lan743x_main.h` CSR accessors and register definitions, TX/RX timestamping helpers (`lan743x_tx_set_timestamping_mode`, `lan743x_rx_set_tstamp_mode`), Linux PHC APIs, hwtstamp netdev APIs, SKB timestamp delivery, PCI device identity, and netdevice logging. Pin muxing integrates with LAN7430 LED pins, while PCI11x1x paths use PTP-IO capture/output registers and additional interrupt bits.

Risks: queue matching assumes TX timestamp SKBs and hardware captures arrive in order and within a fixed four-entry limit; missed calls to request/unrequest can exhaust or underflow the pending counter. PTP command polling timeouts leave hardware state uncertain. PEROUT programming has many validity constraints around pulse width, period, event-channel reuse, and GPIO mux state. EXTTS selection uses shared PTP-IO registers, so concurrent changes must stay under `command_lock`. Close must unregister the PHC, disable interrupts, free pending SKBs, restore LEDs, and disable PTP in the right order to avoid late worker or ISR use.

Test signals: build with and without `CONFIG_PTP_1588_CLOCK`; `phc2sys`/`testptp` get/set/adjfine/adjtime; hwtstamp TX off/on/one-step and RX filters; TX timestamp queue saturation and cancellation; PEROUT on each available pin with duty-cycle and small-period rejection; PCI11x1x rising/falling EXTTS events; link-speed latency updates for 10/100/1000; interface close/open while timestamps and perouts are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ptp.h

Purpose: declares the LAN743x PTP/GPIO interface shared with the rest of the LAN743x driver. It defines chip GPIO limits, event-channel/perout/extts counts, PTP flags, TX timestamp queue sizing, GPIO state, perout state, external timestamp state, and the main `struct lan743x_ptp` layout.

Important APIs and types: `struct lan743x_gpio` tracks GPIO register shadows plus used/output/PTP bitmaps behind `gpio_lock`. `struct lan743x_ptp_perout` records the event channel and GPIO pin allocated to a periodic output. `struct lan743x_extts` stores EXTTS flags and the last captured timestamp. `struct lan743x_ptp` owns `ptp_clock_info`, pin descriptors, PHC pointer, command lock, event-channel bitmap, perout/extts arrays, LED mux state, and the fixed TX timestamp SKB/timestamp queues. Public functions expose init/open/close, ISR, TX timestamp reservation and SKB enqueue, hwtstamp get/set, GPIO init, and latency update.

Control flow and integration: LAN743x main, TX, RX, and ethtool/netdev code include this header to coordinate timestamping. TX code calls request/unrequest and SKB timestamp functions; RX/netdev code calls hwtstamp get/set and latency update; interrupt code calls `lan743x_ptp_isr`; probe/open lifecycle calls init/open/close.

State and persistence: the header defines the in-memory ABI between `lan743x_ptp.c` and the rest of the LAN743x driver. The fixed queue length `LAN743X_PTP_NUMBER_OF_TX_TIMESTAMPS` limits outstanding hardware TX timestamp work. `PTP_FLAG_PTP_CLOCK_REGISTERED` and `PTP_FLAG_ISR_ENABLED` drive close-time cleanup. GPIO register shadows persist across pin reservations to prevent unrelated pins from being overwritten.

Dependencies and integration points: depends on Linux PTP clock and netdevice types plus `struct lan743x_adapter` from the main driver. Constants reflect LAN7430/LAN7431/PCI11x1x hardware limits, including LAN7430 LED-multiplexed GPIOs and eight PCI11x1x PTP-IO channels.

Risks and test signals: layout changes can break timestamp queue management, close-time cleanup, or users of the exported functions. Compile coverage should include LAN743x TX/RX/main users and both PTP-enabled and PTP-disabled builds. Runtime tests should validate the fixed queue limit, GPIO reservation/release, and PHC registration flags through repeated open/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/Kconfig

Purpose: adds the `CONFIG_LAN865X` tristate for Microchip LAN8650/1 10BASE-T1S MAC-PHY support under `NET_VENDOR_MICROCHIP`.

Important behavior: the symbol depends on `SPI` and selects `OA_TC6`, making the OPEN Alliance TC6 helper layer mandatory when the driver is enabled. The help text documents LAN8650/1 Rev.B0/B1 support and that the module name is `lan865x`.

Control flow and state: no runtime control flow or state. At build time it controls whether `lan865x.o` is built and whether the OA-TC6 support is pulled in.

Dependencies and integration points: integrates with the kernel networking vendor menu, SPI subsystem, and OA-TC6 MAC-PHY framework. The runtime driver depends on PHYLIB through source includes and netdev operations, but the Kconfig dependency expressed here is SPI plus selected OA_TC6.

Risks and test signals: missing dependencies show up as build failures in randconfig/allmodconfig. Test signals are `CONFIG_LAN865X=m/y/n` builds, SPI-disabled configurations, and verification that enabling this symbol selects OA_TC6 and produces a `lan865x` module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/Makefile

Purpose: Kbuild fragment for the LAN865x MAC-PHY driver.

Important behavior: `obj-$(CONFIG_LAN865X) += lan865x.o` compiles the single implementation file into the built-in image or module based on the Kconfig symbol.

Control flow and state: no runtime behavior. The only persistent effect is the build graph edge from `CONFIG_LAN865X` to `lan865x.o`.

Dependencies and integration points: depends on the surrounding Microchip Ethernet Makefile recursing into the `lan865x` directory and on the Kconfig symbol being visible.

Risks and test signals: the file is simple, but renaming the object or symbol breaks module generation. Test with `make M=drivers/net/ethernet/microchip/lan865x` or equivalent tree builds for modular and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/lan865x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/lan865x.c

Purpose: implements the Microchip LAN8650/1 10BASE-T1S SPI MAC-PHY netdevice driver on top of the OPEN Alliance TC6 framework. It handles probe/remove, MAC address programming, multicast/promiscuous filtering, TX/RX enablement, PHY-backed link operations, OA-TC6 packet transmit, and hardware-specific Rev.B0/B1 configuration/errata setup.

Important APIs and functions: `lan865x_probe` allocates the netdev, initializes `oa_tc6`, applies TSU timer and zero-align receive-frame settings, configures the MAC address, and registers the netdev. `lan865x_remove` cancels multicast work, unregisters the netdev, exits OA-TC6, and frees memory. Netdev ops include `lan865x_net_open`, `lan865x_net_close`, `lan865x_send_packet`, `lan865x_set_multicast_list`, `lan865x_set_mac_address`, `eth_validate_addr`, and `phy_do_ioctl_running`. Filtering helpers include `lan865x_hash`, `lan865x_set_specific_multicast_addr`, `lan865x_set_all_multicast_addr`, `lan865x_clear_all_multicast_addr`, and `lan865x_multicast_work_handler`.

Control flow: probe allocates private state, binds it to the SPI device, initializes a work item for filter changes, calls `oa_tc6_init`, writes the MAC TSU timer increment to 40 ns, enables zero-align receive frame mode for the documented erratum, obtains a device-tree MAC or random address, programs the two hardware address registers, sets netdev callbacks, and registers the interface. Open enables MAC RX/TX bits, starts the PHY, and starts the netdev queue. Stop stops the queue and PHY, then clears RX/TX enable bits. TX is delegated directly to `oa_tc6_start_xmit`. RX mode changes are deferred to workqueue context, where promiscuous, all-multicast, specific multicast hash, or local-unicast filtering is programmed.

State and persistence: `struct lan865x_priv` stores the work item, netdev, SPI device, and OA-TC6 context. Hardware state persists in MAC network control/configuration registers, multicast hash registers, specific-address registers, TSU increment register, and OA-TC6 errata configuration. Multicast state is not cached locally; the worker reads current netdev flags and multicast list each time.

Dependencies and integration points: depends on SPI driver registration, OA-TC6 register and transmit APIs, PHYLIB ethtool/ioctl helpers, netdev address validation/change helpers, device-tree Ethernet address lookup, and module SPI/of ID matching for `microchip,lan8650` and `microchip,lan8651`.

Risks: MAC address programming writes low bytes before high bytes and attempts rollback on high-register failure; rollback failure can leave hardware and netdev address out of sync. The multicast worker writes a full MAC config value built from mode bits and does not preserve unknown hardware bits. Remove cancels the worker before unregistering, which is important because RX-mode changes can be scheduled asynchronously. Open/close return `-ENODEV` on register access failures and must keep PHY/queue state consistent.

Test signals: SPI probe/remove; random and device-tree MAC address paths; `ip link set address`; multicast joins/leaves, allmulti, and promisc toggles; open/close under traffic; OA-TC6 TX path; PHY ethtool settings; failure injection for OA-TC6 register reads/writes; Rev.B0/B1 errata path verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/lan865x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/Kconfig

Purpose: defines build options for the Microchip LAN966x switch driver and optional DCB support.

Important behavior: `CONFIG_LAN966X_SWITCH` is a tristate depending on optional PTP clock support, MMIO, device tree, switchdev, and bridge availability; it selects `PHYLINK`, `PAGE_POOL`, `VCAP`, and `FDMA`. `CONFIG_LAN966X_DCB` is a bool depending on `LAN966X_SWITCH && DCB`, defaults to yes, and enables DCB apptrust/app/rewrite operations.

Control flow and state: no runtime control flow. Build-time state determines whether the main switch object is compiled and whether `lan966x_dcb.o` is included.

Dependencies and integration points: ties the driver into switchdev/bridge, phylink, PTP, page_pool, VCAP, and the shared Microchip FDMA helper. The DCB symbol controls whether `lan966x_dcb_init` is a real initializer or an inline no-op from the main header.

Risks and test signals: dependency mistakes can produce link or compile failures in bridge-disabled, PTP-disabled, DCB-disabled, or modular configurations. Test `LAN966X_SWITCH=m/y`, `BRIDGE=n`, `DCB=n`, and debugfs combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/Makefile

Purpose: Kbuild file for the LAN966x switch driver.

Important behavior: builds `lan966x-switch.o` when `CONFIG_LAN966X_SWITCH` is enabled. The composite object contains main switch lifecycle, phylink, port, MAC, ethtool/stats, switchdev, VLAN, FDB/MDB, PTP, FDMA, LAG, TC, MQPRIO, TAPRIO/TBF/CBS/ETS, matchall police/mirror, XDP, VCAP implementation/API, flower, and goto support. DCB and debugfs VCAP sources are conditionally appended. Include paths for shared Microchip `vcap` and `fdma` headers are added with `ccflags-y`.

Control flow and state: no runtime state. It defines object composition and include-path contracts for the driver.

Dependencies and integration points: integrates local files with shared `drivers/net/ethernet/microchip/vcap` and `fdma` directories. Conditional lines must match Kconfig symbols and the no-op stubs in `lan966x_main.h`.

Risks and test signals: missing objects cause unresolved symbols across the tightly coupled modules. Include path changes affect VCAP/FDMA users. Test with `CONFIG_LAN966X_DCB` and `CONFIG_DEBUG_FS` enabled/disabled, and confirm the composite object links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_cbs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_cbs.c

Purpose: translates Linux TC CBS queue offload requests into LAN966x queue scheduler element configuration.

Important APIs and functions: `lan966x_cbs_add` validates `tc_cbs_qopt_offload`, computes committed information rate and burst size, enables AVB/frame mode on the queue scheduler element, and writes `QSYS_CIR_CFG`. `lan966x_cbs_del` disables frame mode and clears CIR rate/burst.

Control flow: add rejects non-positive idleslope, non-negative sendslope, and invalid credit ranges. It computes the scheduler element index as `SE_IDX_QUEUE + chip_port * NUM_PRIO_QUEUES + queue`, converts rate to 100 kbps units and burst to 4 KB units, clamps zero to one, verifies field widths, then programs QSYS registers. Delete uses the same index and clears the rate/burst.

State and persistence: no local state is kept. Hardware CBS state persists in QSYS scheduler registers until deletion, port reset, or driver teardown.

Dependencies and integration points: called from the driver TC setup path declared in `lan966x_main.h`. Depends on Linux `tc_cbs_qopt_offload` semantics and LAN966x QSYS scheduler register macros.

Risks and test signals: arithmetic overflow or integer truncation can misprogram rates/bursts. Unsupported parameters are rejected with `-EINVAL`, so TC tests should cover bad slopes, credit boundaries, field-limit overflow, add/delete on all queues, and traffic shaping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_cbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_dcb.c

Purpose: implements optional DCBNL support for LAN966x QoS classification and rewrite mapping. It maps DCB APP entries, DSCP/PCP trust policy, default priority, and rewrite tables into the port QoS configuration consumed by lower-level port code.

Important APIs and functions: `lan966x_dcb_init` installs `dcbnl_ops` on each probed port, sets default apptrust to DSCP+PCP, and enables DSCP rewrite mode. DCB callbacks are `lan966x_dcb_ieee_setapp`, `lan966x_dcb_ieee_delapp`, `lan966x_dcb_setapptrust`, `lan966x_dcb_getapptrust`, `lan966x_dcb_setrewr`, and `lan966x_dcb_delrewr`. `lan966x_dcb_app_update` reads DCB app/rewrite maps and calls `lan966x_port_qos_set`.

Control flow: setapp validates selector/protocol/priority, removes an existing mapping for the same selector/protocol, replicates DSCP mappings to every LAN966x port because DSCP classification is global, stores the DCB entry, and refreshes hardware QoS. Rewrite callbacks follow the same validate/delete-existing/set/update pattern. Apptrust validation only accepts predefined ordered policies: empty, DSCP, PCP, or DSCP then PCP. `lan966x_dcb_app_update` builds a `struct lan966x_port_qos`, enabling PCP and/or DSCP ingress and rewrite maps only when the current trust policy contains that selector.

State and persistence: per-port apptrust pointers are held in the static `lan966x_port_apptrust[NUM_PHYS_PORTS]` array. DCB APP and rewrite mappings are stored in the kernel DCB app tables and re-read on every update. Hardware QoS state persists through `lan966x_port_qos_set` and DSCP rewrite mode programming.

Dependencies and integration points: depends on `CONFIG_LAN966X_DCB`, Linux DCBNL helpers (`dcb_getapp`, `dcb_ieee_setapp`, rewrite helpers), `struct lan966x_port_qos` from the main header, and port QoS programming functions from the port module.

Risks: static apptrust storage is indexed by chip port and assumes one active LAN966x instance or compatible lifetime behavior. DSCP replication means one port operation can fail midway and leave per-port DCB tables inconsistent. Rewrite maps use first-set-bit extraction and support only one rewrite target per priority/protocol. Hardware behavior depends on apptrust order, so accepting unsupported selector sequences would change classification semantics.

Test signals: `dcb app add/del` for DSCP, PCP, and default priority; invalid selector/protocol/priority rejection; apptrust policy changes; rewrite set/delete for PCP and DSCP; multiple ports sharing DSCP maps; DCB-disabled build; traffic priority classification and rewritten PCP/DSCP verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ethtool.c

Purpose: provides LAN966x ethtool operations and statistics aggregation. It exposes link settings, pause parameters, private hardware counters, standard MAC/RMON stats, timestamping capabilities, and the background counter polling worker.

Important APIs and functions: `lan966x_ethtool_ops` wires phylink-backed link/pause operations, string/set count/stat retrieval, MAC/RMON stats, link state, and `get_ts_info`. `lan966x_stats_init` allocates counter storage and starts the delayed workqueue. `lan966x_stats_update` snapshots per-port 32-bit hardware counters into 64-bit software counters with wrap handling. `lan966x_stats_get` fills `rtnl_link_stats64` for netdev users.

Control flow: stats update iterates every physical port, selects the port counter view in `SYS_STAT_CFG`, reads each offset from `lan966x_stats_layout`, and extends it into a 64-bit counter. EtHTool stat reads force an immediate update, then copy the relevant port slice. MAC and RMON standard stats are synthesized from named counter indexes, including PMAC counters. The delayed work refreshes counters every two seconds so wraparound is handled even without user polling. Timestamp info reports PHC capabilities only when PTP is present and the port PHC is registered; otherwise it falls back to generic software timestamp info.

State and persistence: `lan966x->stats_layout`, `num_stats`, `stats`, `stats_lock`, `stats_work`, and `stats_queue` are initialized once at probe. Hardware counters are 32-bit and persist until hardware reset; software counters preserve wrap-extended totals in memory. Netdev `dev->stats` is combined with hardware drop counters for some fields.

Dependencies and integration points: depends on phylink ethtool helpers, ethtool MAC/RMON structures, PTP clock index APIs, LAN966x SYS counter registers, and netdev stats consumers. TC police/mirror stats also call `lan966x_stats_get`.

Risks: counter index constants must match `lan966x_stats_layout`; a mismatch silently corrupts reported stats. `FrameCheckSequenceErrors` adds the same CRC counter twice rather than PMAC CRC, which is a likely accounting bug. RMON jumbo histogram currently reuses the 1024-1526 counters for the 1519-10239 bucket. Workqueue teardown must cancel delayed work before destroying the queue.

Test signals: `ethtool -S`, `ethtool --include-statistics`, standard `ip -s link`, MAC/RMON ethtool netlink stats, counter wrap simulation or long traffic runs, PTP present/absent `ethtool -T`, pause/link setting get/set, and probe/remove workqueue cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ets.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ets.c

Purpose: implements TC ETS offload for LAN966x port schedulers using hardware DWRR costs.

Important APIs and functions: `lan966x_ets_add` validates `tc_ets_qopt_offload`, converts Linux weights to hardware costs with `lan966x_ets_hw_cost`, writes per-priority DWRR configuration, and sets scheduler DWRR count. `lan966x_ets_del` clears all DWRR costs and disables DWRR count.

Control flow: add accepts only root qdisc offload with exactly `NUM_PRIO_QUEUES` bands. It requires the priority map to match the hardware model, where DWRR applies to the lowest consecutive priorities in reverse priority order. It rejects nonzero quanta with zero weight. After finding the minimum active weight, it writes cost values for active bands and updates `QSYS_SE_CFG` for the port scheduler element.

State and persistence: no local software state is stored. Scheduler state persists in QSYS `SE_DWRR_CFG` and `SE_CFG` registers until deleted or overwritten.

Dependencies and integration points: called from TC qdisc setup. Depends on Linux ETS offload structures, LAN966x scheduler element numbering, and QSYS register macros.

Risks and test signals: unsupported priority maps or band counts are rejected, but users may expect more general ETS behavior than hardware supports. Cost rounding affects bandwidth share accuracy. Test add/delete, invalid maps, zero weights, all queues active/inactive combinations, and traffic share measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_fdb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_fdb.c

Purpose: handles switchdev FDB notifications for LAN966x. It converts bridge/port/LAG FDB add/delete events into hardware MAC table operations and maintains a CPU-copy FDB list for bridge master entries that may need to be written when VLAN CPU membership changes.

Important APIs and functions: `lan966x_fdb_init` creates an ordered workqueue and initializes `fdb_entries`; `lan966x_fdb_deinit` destroys the queue and purges entries; `lan966x_handle_fdb` queues switchdev FDB work. `lan966x_fdb_write_entries` and `lan966x_fdb_erase_entries` replay or remove stored bridge FDB entries for a VLAN. Work handlers split events among physical LAN966x ports, bridge masters, and LAG masters.

Control flow: notifier context allocates `lan966x_fdb_event_work`, copies the FDB address, and queues ordered work. Port events only offload user-added entries, calling `lan966x_mac_add_entry` or `lan966x_mac_del_entry`. Bridge-master events maintain a reference-counted software FDB entry; hardware CPU MAC learn/forget is only done if the CPU is a member of the VLAN. LAG-master events only act on the first LAN966x member port to avoid duplicate offload.

State and persistence: `lan966x->fdb_entries` stores MAC/VID plus reference count for bridge-master CPU entries. The ordered workqueue serializes event handling outside atomic notifier context. Hardware state is persisted through `lan966x_mac_cpu_learn`, `lan966x_mac_cpu_forget`, and MAC entry add/delete calls.

Dependencies and integration points: depends on switchdev FDB notifier semantics, bridge and LAG netdevice type helpers, VLAN CPU membership helpers, MAC table helpers, and LAG first-port selection. VLAN code calls write/erase helpers when CPU membership changes.

Risks: allocation failures in notifier context drop FDB updates. Reference-counted bridge entries must match bridge notifications exactly or CPU-copy MAC entries leak/stale. Workqueue destruction must happen after notifier paths are quiesced. LAG first-port selection must stay consistent across membership changes.

Test signals: static FDB add/delete on a port, bridge master, and LAG master; FDB events before/after VLAN CPU membership; duplicate bridge FDB references; notifier flush on teardown; LAG first-port changes; user-added versus learned FDB filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_fdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_fdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_fdma.c

Purpose: implements LAN966x frame DMA RX/TX support, including descriptor allocation, page_pool-backed RX buffers, NAPI polling, XDP integration, TX completion cleanup, MTU-triggered RX ring reload, and FDMA interrupt handling.

Important APIs and functions: lifecycle APIs are `lan966x_fdma_init`, `lan966x_fdma_deinit`, `lan966x_fdma_netdev_init`, and `lan966x_fdma_netdev_deinit`. TX APIs are `lan966x_fdma_xmit` for SKBs and `lan966x_fdma_xmit_xdpf` for XDP frames/pages. RX/NAPI paths are `lan966x_fdma_irq_handler`, `lan966x_fdma_napi_poll`, `lan966x_fdma_rx_check_frame`, and `lan966x_fdma_rx_get_frame`. MTU and page-pool reload APIs are `lan966x_fdma_change_mtu` and `lan966x_fdma_reload_page_pool`.

Control flow: init configures RX channel 6 and TX channel 0 FDMA structures, allocates RX page_pool and coherent descriptors, allocates TX descriptors and per-DCB bookkeeping, then starts RX. IRQ disables FDMA DB interrupts, acknowledges DB status, and schedules NAPI. NAPI first clears completed TX buffers, then consumes RX DCBs up to budget: it syncs DMA, extracts source port from IFH, runs XDP when present, builds SKBs for pass frames, handles PTP RX timestamps, sets bridge offload marks, submits GRO, allocates replacement DCBs, reloads RX, flushes XDP redirects, and reenables interrupts on completion. SKB TX pads/expands headroom/tailroom, pushes IFH and dummy FCS, maps DMA, fills a DCB, marks PTP two-step SKBs for later release, and activates or reloads TX.

State and persistence: `lan966x->rx` stores FDMA descriptors, page pointers, page order, max frame size, and page_pool. `lan966x->tx` stores FDMA descriptors, per-DCB buffer metadata, and activation state. `lan966x->napi` is attached to the first FDMA netdev. Hardware state persists in FDMA channel LLP/config/interrupt/activation registers and QS CPU port mode. RX pages and TX DMA mappings persist until NAPI completion or deinit.

Dependencies and integration points: depends on shared Microchip `fdma_api`, page_pool, DMA mapping APIs, XDP helpers, LAN966x IFH parsing/building, PTP timestamp functions, netdev queue control, NAPI/GRO, and QSYS CPU-port flushing. Main TX serializes calls with `lan966x->tx_lock`; XDP TX also takes that lock internally.

Risks: deinit disables NAPI after channel disable and must not race with IRQ/NAPI or TX users. `lan966x_fdma_rx_alloc` returns `PTR_ERR(rx->page_pool)` even when the helper failed with a plain error, which depends on `rx->page_pool` being an error pointer. MTU reload temporarily disables NAPI and netdev queues; restore paths must preserve old descriptors/page_pool on allocation failure. TX completion deliberately does not consume PTP two-step SKBs, so timestamp release must happen elsewhere. XDP/page_pool DMA direction changes require page_pool reload when XDP is installed.

Test signals: FDMA probe/remove; RX/TX traffic with and without FDMA fallback; NAPI budget limits; XDP PASS/DROP/TX/REDIRECT/NDO_XMIT; MTU changes under traffic; PTP two-step TX and RX timestamps; descriptor exhaustion stopping/waking queues; FDMA error interrupt injection; page_pool reload when XDP programs attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_fdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_goto.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_goto.c

Purpose: offloads TC goto-chain actions by enabling or disabling VCAP lookups for a port.

Important APIs and functions: `lan966x_goto_port_add` calls `vcap_enable_lookups` with source/destination chain IDs and a goto cookie, translating common VCAP errors to extack messages and `-EOPNOTSUPP`. `lan966x_goto_port_del` disables the lookup for the goto ID.

Control flow: add validates indirectly through VCAP. `-EFAULT` becomes "Unsupported goto chain", `-EADDRINUSE` becomes "VCAP already enabled", and other errors are returned with a generic extack. Delete calls the same VCAP API with `enable=false`.

State and persistence: no local state is kept. VCAP lookup enablement persists in the shared `vcap_ctrl` and hardware VCAP/port state until disabled or VCAP teardown.

Dependencies and integration points: used by LAN966x TC flower/goto handling. Depends on `vcap_api_client.h`, `lan966x->vcap_ctrl`, port netdevice identity, chain ID conventions from `lan966x_main.h`, and netlink extack reporting.

Risks and test signals: correctness depends on VCAP chain IDs matching hardware lookup stages. Test valid and invalid goto chains, duplicate goto add, delete after add, delete missing goto, and flower rules that depend on enabled lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_goto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ifh.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ifh.h

Purpose: documents the LAN966x Injection/Extraction Frame Header bit layout and field widths used by CPU injection, extraction, FDMA, PTP, QoS, forwarding, and rewriter paths.

Important APIs and types: this header defines `IFH_LEN`, `IFH_LEN_BYTES`, every `IFH_POS_*` bit position, and every `IFH_WID_*` field width. Fields include timestamp, bypass, masquerade, length, rewriter command, PDU type, source port, TCI, QoS class, CPU queue mask, destination port mask, internal priority, and many hardware classification/status fields.

Control flow and integration: no executable control flow. `lan966x_main.c` uses these positions to set IFH fields for manual injection and parse source port/length/timestamp on extraction. FDMA and PTP paths rely on the same layout for RX/TX timestamp metadata.

State and persistence: no runtime state. The constants are an ABI between software and LAN966x hardware; changing them changes packet injection/extraction semantics.

Dependencies and integration points: included by `lan966x_main.h` and therefore visible to most LAN966x modules. It must match the hardware IFH transmitted most-significant byte first.

Risks and test signals: an incorrect bit position or width silently misroutes packets, breaks PTP timestamp IDs, corrupts VLAN/QoS metadata, or loses source-port extraction. Test CPU-injected packets to each port, extracted packets from each port, VLAN/QoS tagging, PTP one-step/two-step fields, and FDMA/manual extraction equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ifh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_lag.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_lag.c

Purpose: implements LAN966x hardware offload support for Linux bonding/LAG membership, hash configuration, active link state, bridge offload integration, and MAC entry migration as the representative first LAG port changes.

Important APIs and functions: exported entry points are `lan966x_lag_port_join`, `lan966x_lag_port_leave`, `lan966x_lag_port_prechangeupper`, `lan966x_lag_port_changelowerstate`, `lan966x_lag_netdev_prechangeupper`, `lan966x_lag_netdev_changeupper`, `lan966x_lag_first_port`, and `lan966x_lag_get_mask`. Internal helpers program port IDs and aggregation PGIDs via `lan966x_lag_update_ids`, `lan966x_lag_set_port_ids`, and `lan966x_lag_set_aggr_pgids`.

Control flow: pre-change validates that LAG TX type is hash-based, all LAN966x LAGs use the same hash type, and the hash type is one of L2, L23, or L34; it then programs `ANA_AGGR_CFG`. Join records `port->bond`, recalculates port IDs/forward masks/aggregation PGIDs, registers switchdev bridge-port offload for the lower port, sets STP state from the bridge port, and migrates stored MAC entries when this port becomes the first LAG representative. Leave migrates or removes LAG MAC entries if the first port leaves, clears bond state, recalculates IDs, and restores forwarding STP state. Lower-state changes update `lag_tx_active` and rebuild aggregation PGIDs.

State and persistence: per-port LAG state is `bond`, `lag_tx_active`, and `hash_type`. Hardware state persists in source/destination PGIDs, aggregation PGIDs, `ANA_PORT_CFG_PORTID_VAL`, and `ANA_AGGR_CFG`. Software MAC entries track whether they were learned for a LAG and may be reprogrammed to a new representative port.

Dependencies and integration points: depends on Linux netdev LAG notifier data, bridge STP helpers, switchdev bridge port offload, LAN966x switchdev notifier blocks, forwarding-mask update code, and MAC table LAG migration helpers.

Risks: only one hash type is allowed across all LAN966x LAGs because the hardware aggregation config is global. First-port selection changes can race logically with FDB/MAC notifier updates if ordering is wrong. Aggregation PGID programming must handle zero active members without division by zero. Bridge offload failure must roll back `port->bond` and hardware IDs.

Test signals: create/delete bonds with LAN966x ports; unsupported TX/hash type extack; L2/L23/L34 hash traffic distribution; link up/down active member changes; adding/removing the lowest-numbered LAG member; bridge+bond FDB offload; STP state transitions; multiple bonds with matching and mismatched hash types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_lag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mac.c

Purpose: manages the LAN966x hardware MAC table and synchronizes dynamically learned, static, CPU, multicast, and LAG-aware entries with switchdev bridge notifications.

Important APIs and functions: basic table operations are `lan966x_mac_learn`, `lan966x_mac_ip_learn`, `lan966x_mac_forget`, `lan966x_mac_cpu_learn`, and `lan966x_mac_cpu_forget`. Lifecycle and policy functions include `lan966x_mac_init`, `lan966x_mac_set_ageing`, and `lan966x_mac_purge_entries`. Static/software entry APIs are `lan966x_mac_add_entry`, `lan966x_mac_del_entry`, `lan966x_mac_lag_replace_port_entry`, and `lan966x_mac_lag_remove_port_entry`. `lan966x_mac_irq_handler` scans hardware changes and emits switchdev FDB add/delete notifications.

Control flow: learn/forget select a MAC/VID in `ANA_MACLDATA/MACHDATA`, write a MACACCESS command, and poll until idle under `mac_lock`. Driver-managed entries are stored in `lan966x->mac_entries`; adding a user/static entry checks hardware, avoids duplicate software entries, sends `SWITCHDEV_FDB_OFFLOADED`, and learns a locked hardware entry. The MAC IRQ uses `MACACCESS_CMD_SYNC_GET_NEXT` to scan changed rows, compares raw row columns with the software list, notifies bridge deletions for aged/missing entries, and adds/notifies new learned entries.

State and persistence: `lan966x->mac_entries` stores MAC, VID, port index, hardware row, and LAG flag. `mac_lock` protects both the list and serialized table commands. Hardware MAC entries persist in ANA MAC table until aged, forgotten, initialized, or reset. Switchdev notifications provide persistence to the Linux bridge FDB view.

Dependencies and integration points: depends on switchdev FDB notifiers, ANA MACACCESS/MACTINDX register protocol, LAG port migration, MDB/FDB helpers, CPU MAC learning from main and VLAN code, and bridge ageing configuration.

Risks: MACACCESS commands are serialized with a spinlock while polling hardware, so timeout behavior is critical. IRQ row scanning relies on hardware stop conditions and four-column row semantics. Software/hardware divergence can produce duplicate or missing FDB notifications. LAG migration must preserve locked entries when the representative port changes. Atomic allocations in MAC add paths can fail under pressure.

Test signals: hardware learning/ageing notifications to a bridge, static FDB add/delete, CPU MAC learn/forget, multicast MAC types from MDB code, LAG member migration, ageing time changes, MAC table init/purge on probe/remove, and stress with many learned addresses across rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_main.c

Purpose: main platform driver and netdevice data path for the LAN966x switch. It maps MMIO targets, resets/initializes the switch core, registers ports, handles manual CPU injection/extraction when FDMA is absent, builds/parses IFH headers, wires netdev ops, handles interrupts, and orchestrates subsystem probe/remove order.

Important APIs and functions: platform lifecycle is `lan966x_probe`, `lan966x_remove`, `lan966x_switch_driver_init`, and `lan966x_switch_driver_exit`. Port lifecycle/data path includes `lan966x_probe_port`, `lan966x_cleanup_ports`, `lan966x_port_open`, `lan966x_port_stop`, `lan966x_port_xmit`, `lan966x_port_change_mtu`, and RX extraction handler `lan966x_xtr_irq_handler`. Shared IFH helpers are `lan966x_ifh_set_bypass`, `lan966x_ifh_set_port`, `lan966x_ifh_get_src_port`, and `lan966x_ifh_get_timestamp`. `lan966x_hw_offload` decides whether bridge packets should retain offload forwarding marks.

Control flow: probe allocates `struct lan966x`, chooses a base MAC, maps two MMIO ranges into target pointers, resets the switch unless already initialized, requests XTR/ANA/PTP/FDMA/PTP-EXT interrupts when present, creates debugfs, initializes switch hardware, stats, each device-tree port, MDB/FDB/PTP/FDMA/VCAP/DCB subsystems, and returns registered netdevs. Port probe creates a multiqueue netdev, learns its CPU MAC, configures phylink/PCS capabilities, registers the netdev, initializes VLAN defaults, and later port hardware/XDP. TX builds an IFH with bypass, destination port, priority, VLAN, and optional PTP rewriter metadata, then sends via FDMA or manual QS injection under `tx_lock`. Manual RX drains QS extraction words, parses IFH, builds SKBs, applies PTP RX timestamps and bridge offload marks, and submits to the stack.

State and persistence: main state lives in `struct lan966x`: MMIO target bases, port array, base MAC, bridge masks, VLAN masks, stats, IRQ numbers, FDB/MDB/PTP/FDMA/VCAP/debugfs state, and TX lock. Hardware initialization persists in ANA/QSYS/QS/SYS/REW registers for flooding PGIDs, CPU port, queue modes, ageing, learning, BPDU copy, buffer reservations, and extraction/injection modes. Netdev state persists per port through phylink, VLAN defaults, MAC table entries, and TC/XDP features.

Dependencies and integration points: integrates platform device tree resources and child `ethernet-ports`, reset control, phylink/PHY/SerDes, switchdev notifier registration, bridge and LAG helpers, PTP/FDMA/VCAP/DCB/TAPRIO/MAC/VLAN/FDB/MDB modules, debugfs, netdev XDP and hwtstamp operations, and Microchip generated register macros.

Risks: probe/remove ordering is complex; partial failures must unwind ports, IRQs, workqueues, stats, FDB, PTP, FDMA, and debugfs without double-freeing devm-managed resources. Manual injection/extraction paths require correct IFH bit packing and FIFO polling. `lan966x_hw_offload` may call `skb_vlan_untag` on a local SKB pointer and must preserve bridge forwarding behavior for IGMP/MLD. FDMA changes MTU globally based on the maximum port frame size. PTP hwtstamp setup installs traps before netdev timestamp config and must undo traps on failure.

Test signals: platform probe/remove and module load/unload; all device-tree port modes; manual QS RX/TX and FDMA RX/TX; bridge forwarding with IGMP/MLD snooping; port MAC changes; MTU changes; hwtstamp get/set for netdev and PHYLIB sources; XDP attach and transmit; interrupt handling for XTR/ANA/PTP/FDMA; failure injection through each probe stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_main.h

Purpose: central LAN966x driver header. It defines hardware constants, shared enums, device/port/FDMA/PTP/TC/QoS state structures, cross-module prototypes, register access helpers, and configuration stubs.

Important APIs and types: `struct lan966x` is the device-wide state container for MMIO targets, ports, bridge/VLAN/FDB/MDB/MAC/PTP/FDMA/VCAP/stats/debugfs state. `struct lan966x_port` stores netdev, chip port, VLAN/learning/mcast state, phylink/PCS/SerDes, PTP TX state, LAG state, TC state, and XDP state. `struct lan966x_rx`, `struct lan966x_tx`, and `struct lan966x_tx_dcb_buf` define FDMA rings and buffer ownership. `struct lan966x_phc` defines per-PHC PTP registration state. `struct lan966x_port_qos` and substructures define DCB QoS maps. Inline helpers `lan_addr`, `lan_rd`, `lan_wr`, and `lan_rmw` abstract generated register addressing.

Control flow and integration: all LAN966x modules include this header to share prototypes. Main calls subsystem init/deinit in probe/remove; TC modules call shaping/police/mirror/VCAP functions; switchdev calls FDB/MDB/LAG/VLAN/MAC helpers; data paths call IFH, PTP, FDMA, XDP, and stats helpers. `CONFIG_LAN966X_DCB` controls whether `lan966x_dcb_init` is real or a no-op.

State and persistence: the header defines all long-lived software state and many hardware index constants: physical ports, CPU port, PGIDs, queue counts, PHC count, FDMA channels, scheduler element indices, VCAP chain IDs, and IFH rewrite op/PDU types. These constants must remain synchronized with hardware and generated register definitions.

Dependencies and integration points: includes Linux netdevice, switchdev, phylink, PTP, page_pool, packet classifier/scheduler, XDP, shared FDMA and VCAP APIs, LAN966x registers, and IFH layout. It is the module boundary for files in this subset and related VLAN/PTP/TC/XDP sources.

Risks and test signals: structure or prototype changes ripple through almost every LAN966x source. Register helpers use `WARN_ON` bounds checks but still calculate addresses, so invalid generated macro arguments can write wrong MMIO. Test signals are compile coverage across Kconfig combinations, sparse/lockdep for shared state, and runtime coverage of every subsystem that stores fields in `struct lan966x` or `struct lan966x_port`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mdb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mdb.c

Purpose: handles switchdev multicast database offload for LAN966x. It maintains multicast group membership, allocates shared PGIDs for L2 multicast destinations, encodes IPv4/IPv6 multicast entries for special MAC table entry types, and updates CPU-copy behavior as VLAN membership changes.

Important APIs and functions: lifecycle functions are `lan966x_mdb_init` and `lan966x_mdb_deinit`. Switchdev object handlers are `lan966x_handle_port_mdb_add` and `lan966x_handle_port_mdb_del`. VLAN interaction APIs are `lan966x_mdb_write_entries`, `lan966x_mdb_erase_entries`, `lan966x_mdb_clear_entries`, and `lan966x_mdb_restore_entries`.

Control flow: MDB add classifies the MAC as IPv4 multicast, IPv6 multicast, or generic L2. IPv4/IPv6 entries encode the destination port mask into bytes of the MAC value and use `lan966x_mac_ip_learn`, avoiding PGID allocation. L2 entries allocate or reuse a general PGID with the same port mask, program `ANA_PGID`, and learn a locked MAC entry pointing at that PGID. Delete paths remove CPU or front-port membership, forget the old MAC encoding, drop PGID references, delete empty entries, or re-learn updated entries. VLAN write/erase helpers add or remove CPU copy for entries whose bridge requested CPU membership.

State and persistence: `lan966x->mdb_entries` stores MAC, VID, front/CPU port mask, PGID pointer, and CPU-copy reference count. `lan966x->pgid_entries` stores PGID index, port mask, and refcount so L2 multicast groups sharing a port set reuse hardware PGIDs. Hardware state persists in ANA PGID entries and MAC table entries.

Dependencies and integration points: depends on switchdev MDB objects, bridge-master detection for CPU port membership, VLAN CPU membership helpers, MAC table learn/forget APIs, PGID constants from the main header, and multicast address classification conventions.

Risks: PGID resources are limited to `PGID_GP_START..PGID_GP_END`, so L2 multicast can fail with `-ENOSPC`. Error paths after PGID allocation or MAC forget/relearn can leave software and hardware out of sync. CPU-copy handling differs between IP multicast and L2 multicast and depends on VLAN membership callbacks. `lan966x_mdb_restore_entries` reuses a `cpu_copy` variable across loop iterations, which is risky if false is not reset for each IP entry.

Test signals: bridge MDB add/delete for IPv4, IPv6, and L2 multicast; multiple groups sharing a port mask; PGID exhaustion; bridge CPU port joins/leaves VLAN; VLAN clear/restore cycles; duplicate CPU-copy references; teardown purge; multicast traffic forwarding and CPU copy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mirror.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mirror.c

Purpose: implements TC matchall mirror offload for LAN966x ingress and egress port mirroring.

Important APIs and functions: `lan966x_mirror_port_add` validates the monitor device, updates mirror masks and monitor port, programs ANA mirror registers, and records per-port mirror IDs. `lan966x_mirror_port_del` removes a port from the relevant mirror mask, disables hardware mirroring, and clears global monitor state when no mirrors remain. `lan966x_mirror_port_stats` reports immediate action stats using deltas from `lan966x_stats_get`.

Control flow: add requires the destination to be another LAN966x port, rejects duplicate mirrors for the same ingress/egress direction, prevents changing monitor port while any mirror is active, and rejects mirroring the monitor port itself. Ingress mirroring sets `ANA_PORT_CFG_SRC_MIRROR_ENA`; egress mirroring writes the egress mirror port mask. Delete mirrors the add path and clears `ANA_MIRRORPORTS` when `mirror_count` reaches zero.

State and persistence: global state is `lan966x->mirror_monitor`, `mirror_mask[2]`, and `mirror_count`; per-port TC state stores ingress/egress mirror IDs and one `mirror_stat` baseline. Hardware mirror destination and source masks persist in ANA registers until deletion or reset.

Dependencies and integration points: called from TC matchall handling. Depends on LAN966x netdevice checking, netlink extack, ANA mirror registers, and ethtool stats aggregation for action stats.

Risks: ingress and egress share one `mirror_stat` baseline, so simultaneous stats queries for both directions can interfere. Egress delete writes `mirror_mask[0]` to `ANA_EMIRRORPORTS`, which appears to use the ingress mask rather than egress mask and is a likely bug. The hardware supports only one monitor port while any mirror is active.

Test signals: ingress mirror add/delete, egress mirror add/delete, duplicate add rejection, destination outside LAN966x rejection, monitor-port self-mirror rejection, changing monitor while active, simultaneous ingress+egress stats, and register verification for egress mask handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mirror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mqprio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mqprio.c

Purpose: implements the LAN966x mqprio TC offload shim by configuring Linux netdev traffic classes.

Important APIs and functions: `lan966x_mqprio_add` validates the requested traffic-class count and maps each class to one queue. `lan966x_mqprio_del` resets the netdev traffic-class configuration.

Control flow: add accepts only exactly `NUM_PRIO_QUEUES` classes, calls `netdev_set_num_tc`, and assigns each TC to queue offset `i` with count one. Delete calls `netdev_reset_tc`.

State and persistence: no driver-private state is kept. The netdev TC-to-queue mapping persists in core netdev state until reset.

Dependencies and integration points: called from LAN966x TC setup. Depends on the driver exposing eight TX queues and on `NUM_PRIO_QUEUES` matching hardware priority queues.

Risks and test signals: requests for fewer/more traffic classes are rejected even if Linux can express them. Test `tc qdisc mqprio` with exactly eight classes, invalid class counts, delete/reset, and interaction with ETS/CBS queue offloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mqprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_phylink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_phylink.c

Purpose: provides LAN966x phylink MAC and PCS operations. It connects Linux phylink state transitions to SerDes mode selection, port link configuration, PCS status/configuration, and link down reset handling.

Important APIs and functions: exported ops are `lan966x_phylink_mac_ops` and `lan966x_phylink_pcs_ops`. MAC callbacks include `lan966x_phylink_mac_select`, `lan966x_phylink_mac_prepare`, `lan966x_phylink_mac_link_up`, and `lan966x_phylink_mac_link_down`. PCS callbacks include `lan966x_pcs_get_state`, `lan966x_pcs_config`, and `lan966x_pcs_aneg_restart`.

Control flow: phylink selects the per-port PCS, optionally programs SerDes Ethernet mode in `mac_prepare`, records speed/duplex/pause in `port->config` on link up, updates RGMII SerDes speed when needed, and calls `lan966x_port_config_up`. Link down calls `lan966x_port_config_down` and releases PCS reset bits. PCS config copies current port config, updates interface/in-band/autoneg/advertising, and delegates to `lan966x_port_pcs_set`.

State and persistence: per-port `lan966x_port_config` persists the active interface, speed, duplex, pause, in-band, autoneg, and advertising data used by port configuration code. Hardware state is programmed by port/PCS helpers and SerDes PHY APIs.

Dependencies and integration points: depends on Linux phylink, PHY/SerDes APIs, LAN966x port config/status helpers, and generated DEV clock reset registers.

Risks and test signals: `mac_config` is empty, so all meaningful changes must be handled in prepare/link_up/PCS config. SerDes mode failures abort link setup. RGMII speed updates assume `port->serdes` is valid when required. Test every supported interface mode, in-band autoneg, pause negotiation, link flap, SerDes mode failures, and PCS state polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_phylink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_police.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_police.c

Purpose: implements ingress port policer offload for TC matchall/flower actions on LAN966x.

Important APIs and functions: `lan966x_police_port_add` validates a TC police action, converts rate/burst units, programs the port policer, enables it in `ANA_POL_CFG`, and initializes action stats. `lan966x_police_port_del` disables the configured policer and clears the stored police ID. `lan966x_police_port_stats` reports deltas using netdev RX stats. Internal helpers `lan966x_police_add`, `lan966x_police_del`, and `lan966x_police_validate` handle register programming and semantic checks.

Control flow: validation requires exceed action drop, conform action pipe or accept, accept only as the last action, no peakrate/avrate/overhead, byte-rate rather than packet-rate policing, ingress direction only, no shared ingress block, and at most one policer per port. Add converts bytes/sec to kbps and then to the hardware 33 1/3 kpps-like rate unit, converts burst to 4 KB units, checks field widths, programs ANA policer mode/state/PIR config, enables the port policer, and stores the ID. Delete verifies ID and restores default policer settings.

State and persistence: per-port state is `port->tc.police_id` and `police_stat` baseline. Hardware state persists in ANA policer registers and port policer enable/order bits.

Dependencies and integration points: called from LAN966x TC matchall/flower paths. Depends on Linux flow action structures, netlink extack, LAN966x stats aggregation, and ANA policer register macros.

Risks: rate conversion is coarse and field-limited; accepted software police configurations may not map exactly to hardware. Only one ingress policer per port is tracked. Stats are derived from whole-port RX counters/drops, not policer-specific hardware counters, so unrelated traffic can affect action stats.

Test signals: valid ingress police add/delete/stats; invalid exceed/conform actions; egress rejection; shared-block rejection; duplicate police ID behavior; rate/burst boundary values; traffic drop-rate measurement; action stats under mixed traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_police.c -->
