# subset-b-004415 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_main.c

## Purpose
Implements the main Engleder TSN endpoint Ethernet MAC platform driver. It owns probe/remove, MMIO resource setup, PHY/MDIO attachment, MAC address programming, queue discovery, IRQ/NAPI wiring, TX/RX descriptor rings, page-pool RX, XDP and AF_XDP zero-copy data paths, statistics, multicast filtering, hardware timestamp handoff, and netdev operations.

## Important APIs, Types, and Functions
Key entry points are `tsnep_probe`, `tsnep_remove`, `tsnep_netdev_open`, `tsnep_netdev_close`, `tsnep_netdev_xmit_frame`, `tsnep_netdev_bpf`, `tsnep_netdev_xdp_xmit`, `tsnep_netdev_xsk_wakeup`, `tsnep_enable_xsk`, `tsnep_disable_xsk`, `tsnep_set_irq_coalesce`, and `tsnep_get_irq_coalesce`. TX helpers include ring creation/cleanup, `tsnep_tx_map`, `tsnep_tx_activate`, `tsnep_tx_poll`, and XDP/XSK transmit helpers. RX helpers include page-pool and XSK allocation, `tsnep_rx_poll`, `tsnep_rx_poll_zc`, `tsnep_build_skb`, and XDP action handling. The file uses `struct tsnep_adapter`, `tsnep_queue`, `tsnep_tx`, `tsnep_rx`, and descriptor structs declared in `tsnep.h`/`tsnep_hw.h`.

## Control Flow and State
Probe allocates a multi-queue netdev, maps registers, reads hardware type/revision/queue count, initializes locks/lists, disables interrupts, configures queues, sets a 64-bit DMA mask, initializes MAC/MDIO/PHY/PTP/TC/RXNFC, sets features, and registers the device. Open allocates TX/RX rings per queue, registers NAPI and IRQs, sets real queue counts, enables link IRQ, starts PHY, then enables queues. Close disables link IRQ and PHY, disables queues, frees IRQ/NAPI, and releases rings. TX maps SKB heads/frags or inlines small segments, marks owner counters and last-fragment bits, rings hardware, and reclaims on NAPI. RX maintains page-pool or XSK buffers, checks owner counters, handles timestamp metadata, runs XDP when installed, builds SKBs for `XDP_PASS`, and refills before re-enabling hardware.

Persistent state is mostly in MMIO registers and descriptor rings. Software state includes queue read/write indices, owner counters, NAPI/IRQ names, per-queue packet/byte/drop counters, XSK pool pointers, page buffers used during XSK transitions, PHY state, MAC address cache, and the installed `xdp_prog`.

## Dependencies and Integration Points
Depends on platform devices, OF MAC/PHY/MDIO properties, PHYLIB, DMA mapping/coherent allocation, page_pool, NAPI, AF_XDP, XDP core helpers, BPF reference handling, netdev feature and queue APIs, ethtool hooks from `tsnep_ethtool.c`, PTP hooks from `tsnep_ptp.c`, taprio offload from `tsnep_tc.c`, and RX flow classification from `tsnep_rxnfc.c`.

## Risks and Test Signals
Risks center on descriptor ownership ordering, owner-counter/user-flag wrap, TX cleanup for mixed SKB/XDP/XSK entries, page-pool lifetime during XSK enable/disable, queue disable waiting for software TX drain, XDP frags handling, missing work between NAPI completion and IRQ re-enable, and ABI assumptions around inline timestamp metadata. Test signals include probe/remove, repeated up/down, multi-queue IRQ assignment, PHY link changes, TX/RX traffic with SG and small frames, `ethtool -S`, interrupt coalescing, XDP_PASS/DROP/TX/REDIRECT, `ndo_xdp_xmit`, AF_XDP zero-copy bind/unbind while running, hardware timestamp RX/TX, and fault injection for DMA/page allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_ptp.c

## Purpose
Provides PTP hardware clock registration and timestamp configuration for TSNEP. It exposes the MAC system time/counter to the kernel PTP layer and stores netdev hardware timestamp policy used by the main TX/RX paths.

## Important APIs, Types, and Functions
Exports `tsnep_get_system_time`, `tsnep_ptp_hwtstamp_get`, `tsnep_ptp_hwtstamp_set`, `tsnep_ptp_init`, and `tsnep_ptp_cleanup`. Internal PTP ops are `tsnep_ptp_adjfine`, `tsnep_ptp_adjtime`, `tsnep_ptp_gettimex64`, `tsnep_ptp_settime64`, and `tsnep_ptp_getcyclesx64`. State lives in `adapter->hwtstamp_config`, `ptp_clock_info`, `ptp_clock`, and `ptp_lock`.

## Control Flow and State
`tsnep_get_system_time` reads the high 32-bit register before and after the low register to avoid rollover tearing. HWTSTAMP set accepts TX off/on and normalizes every supported RX timestamping request to `HWTSTAMP_FILTER_ALL`, rejecting unsupported modes with `-ERANGE`. PTP init initializes default timestamping off, fills `ptp_clock_info`, initializes the spinlock, and registers the PHC. Time adjustment and setting write high then low so hardware commits synchronously when the low word is written.

## Dependencies and Integration Points
Depends on TSNEP MMIO time registers, kernel PTP clock APIs, net timestamp config APIs, and `tsnep_main.c` for TX/RX timestamp consumption. RX timestamps are passed through inline metadata in SKBs, and TX completion reads descriptor writeback timestamp/counter based on socket timestamp flags.

## Risks and Test Signals
Risks include assuming an 8 ns clock cycle in `adjfine`, lack of validation for hardware clock period, unsynchronized `hwtstamp_config` reads from data paths, and missed rollover if register semantics differ from the high-low-high pattern. Test with `ethtool -T`, `phc2sys`, `ptp4l`, `hwstamp_ctl`, TX timestamp sockets with and without bound PHC, RX timestamp filters, adjfine/adjtime stress, and remove/unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_rxnfc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_rxnfc.c

## Purpose
Implements TSNEP ethtool RX network flow classification for steering packets by EtherType to RX queues. It manages the in-memory ordered rule list and programs hardware RX assignment slots.

## Important APIs, Types, and Functions
Exports `tsnep_rxnfc_init`, `tsnep_rxnfc_cleanup`, `tsnep_rxnfc_get_rule`, `tsnep_rxnfc_get_all`, `tsnep_rxnfc_add_rule`, and `tsnep_rxnfc_del_rule`. Internal helpers enable/disable a hardware rule, find/add/delete list entries, choose a free location, initialize `struct tsnep_rxnfc_rule`, and reject duplicates. Rules use `struct tsnep_rxnfc_filter` with `TSNEP_RXNFC_ETHER_TYPE`.

## Control Flow and State
Initialization clears all hardware assignment slots. Add validates that the ethtool flow is `ETHER_FLOW` with only a full EtherType mask, validates queue cookie and location, allocates a rule, assigns an automatic location when requested, rejects duplicate filters at different locations, replaces any old rule at the same location, programs hardware, and inserts the rule in ascending location order. Delete disables hardware, removes from the list, decrements count, and frees memory. All list operations are protected by `adapter->rxnfc_lock`.

## Dependencies and Integration Points
Depends on ethtool RXNFC command structures, Linux list helpers, TSNEP RX assignment MMIO registers, queue count limits encoded by hardware masks, and ethtool glue in `tsnep_ethtool.c`.

## Risks and Test Signals
Risks include accepting a queue cookie that fits the hardware mask but exceeds the currently configured RX queues, duplicate filter replacement semantics surprising users, hardware/list divergence if MMIO writes fail silently, and no persistence across driver reload. Test with `ethtool -N/-n` for add/get/list/delete, automatic locations, duplicate EtherTypes, invalid masks, out-of-range queues and locations, full table behavior, and packet steering validation across multiple RX queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_rxnfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_selftests.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_selftests.c

## Purpose
Provides optional ethtool offline self-tests for TSNEP gate control and taprio offload behavior. The tests exercise gate-control enable timeout handling, static schedules, schedule changes, and cycle-time-extension edge cases.

## Important APIs, Types, and Functions
Exports `tsnep_ethtool_get_test_count`, `tsnep_ethtool_get_test_strings`, and `tsnep_ethtool_self_test` when `CONFIG_TSNEP_SELFTESTS` is enabled. Internal test helpers include `enable_gc_timeout`, `gc_delayed_enable`, `tsnep_test_gc_enable`, `delay_base_time`, `get_gate_state`, `get_operation`, `check_gate`, `enable_check_taprio`, `disable_taprio`, `run_taprio`, `tsnep_test_taprio`, `tsnep_test_taprio_change`, and `tsnep_test_taprio_extension`.

## Control Flow and State
Online tests are reported as skipped/successful without touching hardware. Offline tests directly program gate-control registers or call `tsnep_tc_setup` with synthetic `tc_taprio_qopt_offload` schedules, then repeatedly compare hardware gate state, next gate state, and change time against the driver's `adapter->gcl` software model. Failures set `ETH_TEST_FL_FAILED` and a per-test nonzero result. Each taprio test destroys the qdisc on failure paths to reset hardware state.

## Dependencies and Integration Points
Depends on `tsnep_tc.c` taprio programming, `tsnep_get_system_time`, `net/pkt_sched.h`, TSNEP gate-control MMIO registers, and ethtool self-test integration through `tsnep_ethtool.c`/`tsnep.h`.

## Risks and Test Signals
Risks include destructive offline behavior while traffic is active, timing sensitivity from `ndelay`, long runtime due to many schedule checks, and false failures if system time or gate-control hardware is paused or virtualized. These tests themselves are the main signal for taprio regressions; run `ethtool -t <dev> offline` on hardware with `gate_control` detected, including repeated runs after link up/down and after taprio qdisc changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_selftests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_tc.c

## Purpose
Implements TSNEP traffic-control offload for `taprio`, translating gate-control schedules into the hardware's two gate-control lists and handling live schedule changes with cut/extend/insert operations.

## Important APIs, Types, and Functions
Exports `tsnep_tc_init`, `tsnep_tc_cleanup`, and `tsnep_tc_setup`. Internal helpers validate schedules, write GCL operations, compute change limits, choose start times, insert transition operations, extend/cut current cycles, enable a new GCL, handle `TAPRIO_CMD_REPLACE`/`DESTROY`, and answer `TC_QUERY_CAPS`. State is held in `adapter->gate_control_active`, `adapter->gcl[2]`, `adapter->next_gcl`, and `gate_control_lock`.

## Control Flow and State
Validation requires nonzero cycle time, command `TC_TAPRIO_CMD_SET_GATES`, masks within `TSNEP_GCL_MASK`, intervals above hardware minimum, exact sum equal to cycle time, and extension shorter than cycle time. Replace writes the next inactive GCL, selects the current active GCL if any, enables the hardware timeout guard, calculates a safe future start/change time, writes either `TSNEP_GC_TIME` or `TSNEP_GC_CHANGE`, enables list A/B, retries on timeout, marks gate control active, and toggles the next list. Destroy disables gate control. Cleanup disables active gate control.

## Dependencies and Integration Points
Depends on kernel TC taprio offload structures, TSNEP gate-control registers and constants, `tsnep_get_system_time`, netdev `ndo_setup_tc`, and self-test coverage in `tsnep_selftests.c`.

## Risks and Test Signals
Risks are mostly timing and arithmetic: selecting start times beyond 32-bit hardware time reach, incorrect cut/extend choices near phase boundaries, stale inserted-operation bits after timeout or cleanup, off-by-one GCL count handling due to the reserved insertion slot, and lock contention with ethtool self-tests. Test using `tc qdisc replace ... taprio` with valid/invalid schedules, live schedule changes with shorter/longer/different-phase cycle times, destroy/recreate loops, `TC_QUERY_CAPS`, and the optional TSNEP offline self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_xdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_xdp.c

## Purpose
Provides the TSNEP netdev BPF/XDP setup helpers for installing an XDP program and binding/unbinding AF_XDP zero-copy pools to queue pairs.

## Important APIs, Types, and Functions
Exports `tsnep_xdp_setup_prog` and `tsnep_xdp_setup_pool`. Internal helpers `tsnep_xdp_enable_pool` and `tsnep_xdp_disable_pool` validate queue IDs, require paired TX/RX queues, map/unmap XSK pools for DMA, and delegate runtime queue conversion to `tsnep_enable_xsk`/`tsnep_disable_xsk` in `tsnep_main.c`.

## Control Flow and State
Program setup atomically swaps `adapter->xdp_prog` with `xchg` and drops the old BPF reference. Pool setup enables when a pool pointer is present and disables otherwise. Enable validates that the RX and TX queue indices match the requested queue, DMA maps the pool with `DMA_ATTR_SKIP_CPU_SYNC`, sets RX queue info through `tsnep_enable_xsk`, and unwinds DMA mapping on failure. Disable looks up the pool by queue id, disables XSK mode in the main driver, and DMA unmaps the pool.

## Dependencies and Integration Points
Depends on BPF program lifetime rules, AF_XDP pool APIs, DMA mapping, queue topology from `tsnep_main.c`, and netdev `ndo_bpf` dispatch. Actual XDP action execution and XSK RX/TX are implemented in `tsnep_main.c`.

## Risks and Test Signals
Risks include no explicit feature rejection for programs needing unsupported metadata, races around program replacement while RX is polling, queue-pair assumptions for future asymmetric queue layouts, and ensuring pool DMA unmap always follows successful map. Test with XDP attach/detach loops, replacing programs under traffic, invalid queue ids, AF_XDP zero-copy bind/unbind, queue-pair mismatch simulation, and packet paths for XDP_PASS/DROP/TX/REDIRECT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ethoc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ethoc.c

## Purpose
Implements the OpenCores Ethernet MAC platform driver. It handles register and optional buffer-memory mapping, descriptor ring setup in MAC-accessible memory, MDIO/PHY integration, NAPI RX/TX completion, multicast filtering, ethtool register/ring controls, MAC address setup, and platform/OF probing.

## Important APIs, Types, and Functions
Key private types are `struct ethoc` and `struct ethoc_bd`. Important functions include `ethoc_probe`, `ethoc_remove`, `ethoc_open`, `ethoc_stop`, `ethoc_interrupt`, `ethoc_poll`, `ethoc_rx`, `ethoc_tx`, `ethoc_start_xmit`, `ethoc_init_ring`, `ethoc_reset`, `ethoc_mdio_read`, `ethoc_mdio_write`, `ethoc_mdio_probe`, `ethoc_set_multicast_list`, `ethoc_set_ringparam`, and ethtool/netdev ops tables.

## Control Flow and State
Probe allocates the netdev, maps MMIO and either platform-provided or coherent buffer memory, derives TX/RX descriptor counts, gets MAC address from platform/DT/register/random fallback, sets MDIO clocking, registers an MDIO bus, connects a PHY, adds NAPI, and registers the netdev. Open requests the shared IRQ, enables NAPI, initializes descriptors, resets/enables hardware, starts the queue, and starts PHY. Interrupt handling masks TX/RX events and schedules NAPI. RX copies frames from IO buffer memory into SKBs, strips CRC, updates stats, and returns descriptors to hardware. TX copies SKBs into the current TX buffer, marks descriptors ready, stops the queue when the software ring fills, and completion stats/wakeups happen in NAPI.

Persistent state includes buffer descriptor rings in device memory, software TX/RX cursors (`cur_tx`, `dty_tx`, `cur_rx`), MDIO/PHY state, endian mode, multicast hash registers, and netdev stats.

## Dependencies and Integration Points
Depends on platform resources, optional `ethoc_platform_data`, OF MAC/endian discovery, DMA coherent allocation fallback, MII/PHYLIB, NAPI, CRC32 multicast hashing, ethtool ring/register operations, and the OpenCores register/descriptor ABI.

## Risks and Test Signals
Risks include CPU-copy data path performance, fixed 1536-byte buffers with no MTU support, descriptor count assumptions requiring power-of-two TX entries, races while changing ring parameters on a running device, endian mismatches, legacy stats fields, and suspend/resume stubs returning `-ENOSYS`. Test with platform buffer and coherent-buffer modes, big- and little-endian DT, up/down, PHY link/duplex changes, ping/iperf, multicast/promisc/allmulti toggles, `ethtool -d/-g/-G`, TX timeout recovery, low-memory RX allocation failure, and MDIO timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ethoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/Kconfig

## Purpose
Defines Kconfig options for EZchip Ethernet drivers, including the vendor menu gate and the NPS management Ethernet driver option.

## Important APIs, Types, and Functions
The declarative symbols are `NET_VENDOR_EZCHIP` and `EZCHIP_NPS_MANAGEMENT_ENET`. The vendor symbol is a boolean default-y menu selector. The NPS driver is a tristate depending on `OF_IRQ` and `HAS_IOMEM`.

## Control Flow and State
There is no runtime control flow. Build-time state controls whether EZchip-specific prompts are visible and whether `nps_enet.o` can be built in or as a module.

## Dependencies and Integration Points
Integrates with the kernel networking vendor-driver Kconfig hierarchy and the local Makefile's `obj-$(CONFIG_EZCHIP_NPS_MANAGEMENT_ENET)` rule. The help text documents the device as a simple interrupt-driven debug/management LAN device without DMA.

## Risks and Test Signals
Risks are missing dependencies rather than runtime bugs: the driver also needs OF platform and MMIO APIs, so Kconfig coverage should be checked under `allmodconfig`, `allyesconfig`, and `COMPILE_TEST`-like builds. Menu visibility and module/built-in selection should produce exactly `nps_enet.o` when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/Makefile

## Purpose
Builds the EZchip NPS management Ethernet driver object when its Kconfig symbol is enabled.

## Important APIs, Types, and Functions
Contains the single build rule `obj-$(CONFIG_EZCHIP_NPS_MANAGEMENT_ENET) += nps_enet.o`.

## Control Flow and State
No runtime control flow. Kbuild expands this line into built-in or module output depending on the tristate value of `CONFIG_EZCHIP_NPS_MANAGEMENT_ENET`.

## Dependencies and Integration Points
Depends on `drivers/net/ethernet/ezchip/Kconfig` defining the symbol and on `nps_enet.c`/`nps_enet.h` providing the implementation.

## Risks and Test Signals
Risks are limited to symbol drift or missing object additions if the driver is split. Test by building with the config disabled, built-in, and module-enabled and checking that only `nps_enet.o` is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/nps_enet.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/nps_enet.c

## Purpose
Implements the EZchip NPS management Ethernet platform driver. The hardware has no DMA and uses MMIO FIFOs plus RX-ready/TX-done interrupts, so the driver copies packet words directly between SKBs and device buffers.

## Important APIs, Types, and Functions
Important functions include `nps_enet_probe`, `nps_enet_remove`, `nps_enet_open`, `nps_enet_stop`, `nps_enet_start_xmit`, `nps_enet_irq_handler`, `nps_enet_poll`, `nps_enet_rx_handler`, `nps_enet_tx_handler`, `nps_enet_send_frame`, `nps_enet_hw_reset`, `nps_enet_hw_enable_control`, `nps_enet_hw_disable_control`, `nps_enet_set_hw_mac_address`, and `nps_enet_set_rx_mode`.

## Control Flow and State
Probe requires an OF node, allocates the netdev, maps registers, reads or randomizes the MAC address, obtains one IRQ, adds weighted NAPI, and registers the netdev. Open clears private TX/config state, disables hardware, requests the IRQ, enables NAPI, resets PCS/TX FIFO, configures MAC filtering/IFG/preamble/flow-control/max length, enables interrupts and RX/TX, and starts the queue. TX stops the queue, stores one outstanding SKB in `priv->tx_skb`, uses a write memory barrier, writes data words to the TX FIFO, then sets the TX control register. NAPI handles TX completion and at most one RX frame per poll, re-enables interrupts, and reschedules itself if a TX completion was missed while interrupts were masked.

Persistent state is small: `tx_skb`, cached MAC config registers 2/3, NAPI object, IRQ number, and MMIO base. The hardware holds FIFO contents and control bits.

## Dependencies and Integration Points
Depends on OF platform probing, big-endian MMIO access helpers from `nps_enet.h`, NAPI, netdev stats, `of_get_ethdev_address`, and netpoll when configured. It deliberately disables multicast support in `ndev->flags`.

## Risks and Test Signals
Risks include single-outstanding-TX behavior, watchdog behavior if TX-done interrupt is lost, alignment/endian handling for partial FIFO words, RX frame length limits, no DMA/checksum/multicast support, and config cache drift because `nps_enet_set_rx_mode` writes a local copy without updating `priv->ge_mac_cfg_2_value`. Test with management traffic, unaligned SKB data, minimum/maximum frames, CRC/error frames, promisc toggles, TX interrupt loss scenario, netpoll, up/down loops, and watchdog timeout injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/nps_enet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/nps_enet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/nps_enet.h

## Purpose
Defines the register map, bit masks, default values, private state, and endian-aware MMIO accessors for the EZchip NPS management Ethernet driver.

## Important APIs, Types, and Functions
Declares constants for TX/RX control and buffer registers, interrupt enable bits, GE MAC configuration registers, reset and phase FIFO control, field masks/shifts, defaults such as `NPS_ENET_NAPI_POLL_WEIGHT`, `NPS_ENET_MAX_FRAME_LENGTH`, and `NPS_ENET_GE_MAC_CFG_*`, plus `struct nps_enet_priv`. Inline helpers `nps_enet_reg_set` and `nps_enet_reg_get` perform big-endian 32-bit MMIO.

## Control Flow and State
There is no standalone runtime control flow beyond the two inline accessors. State modeled here includes the MMIO base, IRQ, one outstanding TX SKB, NAPI object, and cached GE MAC config values used by `nps_enet.c`.

## Dependencies and Integration Points
Consumed directly by `nps_enet.c`. The register definitions are the hardware ABI for FIFO access, MAC address programming, filtering, flow control, reset sequencing, and interrupt enablement.

## Risks and Test Signals
Risks are register ABI errors: wrong masks/shifts or endian access would break all runtime behavior. Test signals are compile coverage, register write/read validation on hardware or emulator, RX/TX FIFO operation, MAC address programming, reset sequencing, and promisc/filter bit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/nps_enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/Kconfig

## Purpose
Defines Kconfig menu and driver symbols for Faraday Ethernet controllers, including 10/100 FTMAC100 and gigabit FTGMAC100.

## Important APIs, Types, and Functions
Symbols are `NET_VENDOR_FARADAY`, `FTMAC100`, and `FTGMAC100`. The vendor menu defaults to yes but depends on `ARM || COMPILE_TEST`. `FTMAC100` selects `MII` and is blocked on `64BIT` unless `BROKEN`; `FTGMAC100` selects `PHYLIB`, `FIXED_PHY`, `CRC32`, and `MDIO_ASPEED` on `MACH_ASPEED_G6`, with the same ARM/64-bit constraints.

## Control Flow and State
No runtime control flow. Build-time state controls menu visibility, module/built-in selection, and dependency closure for the Faraday drivers.

## Dependencies and Integration Points
Integrates with the local Makefile entries for `ftmac100.o` and `ftgmac100.o`, and with PHY/fixed-link/Aspeed MDIO support required by the implementation.

## Risks and Test Signals
Risks include overrestrictive `!64BIT || BROKEN` hiding valid compile coverage, missing `NET_NCSI` selection despite optional NCSI runtime support, and dependency drift when driver code adds APIs. Test with disabled/vendor-only/module/built-in configs, ARM and COMPILE_TEST builds, Aspeed G6 builds, and configs with/without NCSI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/Makefile

## Purpose
Builds Faraday Ethernet driver objects according to Kconfig selections.

## Important APIs, Types, and Functions
Contains `obj-$(CONFIG_FTGMAC100) += ftgmac100.o` and `obj-$(CONFIG_FTMAC100) += ftmac100.o`.

## Control Flow and State
No runtime logic. Kbuild maps each tristate symbol to built-in or module objects.

## Dependencies and Integration Points
Depends on `faraday/Kconfig` for symbol definitions and on source files `ftgmac100.c` and `ftmac100.c`.

## Risks and Test Signals
Risks are build-only: stale object names if files are renamed or split. Test by building each symbol disabled, built-in, and module-enabled and checking expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftgmac100.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftgmac100.c

## Purpose
Implements the Faraday FTGMAC100 gigabit Ethernet platform driver, including Aspeed AST2400/AST2500/AST2600 variants. It manages DMA descriptor rings, RX/TX packet processing, PHY or NCSI link management, reset/recovery, checksum/VLAN offloads, multicast filtering, pause control, ring sizing, clocks/resets, and OF probing.

## Important APIs, Types, and Functions
The main private type is `struct ftgmac100`. Key functions include `ftgmac100_probe`, `ftgmac100_remove`, `ftgmac100_open`, `ftgmac100_stop`, `ftgmac100_hard_start_xmit`, `ftgmac100_interrupt`, `ftgmac100_poll`, `ftgmac100_rx_packet`, `ftgmac100_tx_complete`, `ftgmac100_reset`, `ftgmac100_reset_task`, `ftgmac100_adjust_link`, `ftgmac100_setup_mdio`, `ftgmac100_probe_dt`, `ftgmac100_probe_ncsi`, `ftgmac100_init_all`, `ftgmac100_alloc_rings`, `ftgmac100_alloc_rx_buffers`, `ftgmac100_set_ringparam`, and pause/multicast/MAC address helpers.

## Control Flow and State
Probe identifies the MAC variant, maps registers, initializes pause defaults, obtains MAC address, selects descriptor end-of-ring bit layout, sets up embedded MDIO where applicable, connects PHY/fixed PHY/NCSI, obtains resets/clocks for Aspeed, applies AST2600 test-mode workaround, initializes default ring sizes and feature flags, and registers the netdev. Open allocates descriptor rings and scratch RX buffer, sets initial link speed for NCSI or no-link for PHY, resets hardware, adds NAPI, requests IRQ, initializes rings/RX buffers/MAC registers, enables interrupts, and starts PHY or NCSI. TX maps the SKB head and frags to descriptors, sets checksum/VLAN control bits, publishes OWN on the first descriptor last, advances the ring pointer, stops the queue below threshold, and pokes TX polling. NAPI reclaims TX descriptors, receives RX descriptors, restarts MAC after overflow-class errors, and carefully clears/rechecks latched interrupts before completing.

Persistent state includes descriptor memory and SKB arrays, ring pointers, requested new ring sizes, scratch RX DMA buffer for allocation failures, multicast hash caches, pause settings, current speed/duplex, NCSI device pointer, reset work, clocks/resets, and variant flags.

## Dependencies and Integration Points
Depends on platform/OF APIs, DMA coherent and streaming mapping, PHYLIB, fixed PHY, optional NCSI, Aspeed clocks/reset/MDIO, NAPI, ethtool, VLAN helpers, checksum helpers, CRC32 multicast hashing, and register/descriptor definitions from `ftgmac100.h`.

## Risks and Test Signals
Risks include descriptor ownership/barrier mistakes, freeing the same SKB across multi-fragment TX descriptors, RX scratch-buffer behavior under allocation pressure, ring resize reset races, lock ordering among RTNL/PHY/MDIO during reset, NCSI fixed-PHY lifecycle, variant-specific end-of-ring bit differences, AST2400/AST2600 checksum errata, and restart behavior after RX overflow/AHB errors. Test with RGMII PHY and NCSI modes, AST2400/2500/2600 compatibles, up/down and remove during reset work, iperf with SG/checksum/VLAN on/off, multicast/promisc/allmulti, RX allocation failure, `ethtool -G/-a/-A`, link speed/duplex changes, TX timeout, AHB/error interrupt injection, and NCSI VLAN filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftgmac100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftgmac100.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftgmac100.h

## Purpose
Defines the FTGMAC100 register offsets, interrupt masks, MAC/PHY/flow-control fields, descriptor formats, checksum/VLAN bits, and error masks used by `ftgmac100.c`.

## Important APIs, Types, and Functions
Important declarations include MMIO offsets for interrupt, MAC address, hash, descriptor base, DMA arbitration, MAC control, PHY MDIO, flow control, statistics, and test-mode registers. It defines interrupt groups `FTGMAC100_INT_BAD`, `FTGMAC100_INT_RXTX`, and `FTGMAC100_INT_ALL`, MAC control flags, MDIO command/data fields, flow-control fields, aligned `struct ftgmac100_txdes` and `struct ftgmac100_rxdes`, TX descriptor size/first/last/own/checksum/VLAN bits, RX ready/first/last/error/checksum/VLAN bits, and `RXDES0_ANY_ERROR`.

## Control Flow and State
No runtime control flow exists in this header. It describes persistent hardware state in registers and DMA descriptors, including descriptor ownership, end-of-ring markers, packet size, checksum results, VLAN tag availability, multicast/broadcast status, and MAC enable/filter modes.

## Dependencies and Integration Points
Consumed by `ftgmac100.c` and tied to the FTGMAC100/Aspeed hardware ABI. The descriptor structs are shared with DMA hardware and therefore require the declared 16-byte alignment and little-endian fields.

## Risks and Test Signals
Risks are ABI-level: wrong bit positions can corrupt DMA ownership, interrupt masking, checksum offload, VLAN handling, or PHY MDIO transactions. Test signals include compile coverage, register dumps against datasheets, RX/TX descriptor traces, checksum/VLAN offload validation, interrupt error-path tests, and variant tests for Faraday versus Aspeed end-of-ring masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftgmac100.h -->
