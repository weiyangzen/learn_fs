# subset-b-004634 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol_mae.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol_mae.h

Purpose: this small protocol-extension header supplies one MCDI Match-Action Engine constant that is missing from the main generated `mcdi_pcol.h`. It exists so MAE action-set allocation code can pass a guaranteed-null counter-list identifier even before the corresponding firmware API is released in the shared protocol header.

Important API: `MC_CMD_MAE_COUNTER_LIST_ALLOC_OUT_COUNTER_LIST_ID_NULL` is defined as `0xffffffff`. There are no functions or persistent state; the header only exposes the sentinel value under an include guard.

Control flow and integration: consumers include this header alongside `mcdi_pcol.h` when building MAE commands, especially commands that need to express "no counter list" for action-set allocation. The dependency is intentionally one-way from driver MAE code to this compatibility definition.

Risks: the value must remain aligned with firmware semantics. If a later official `mcdi_pcol.h` defines the same name differently or starts providing a duplicate definition, build or behavior conflicts are possible. Test signals are compile coverage of MAE users and runtime TC/MAE offload tests that allocate action sets with and without counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_pcol_mae.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port.c

Purpose: this file is the thin MCDI-backed port facade for SFC NICs. It connects the generic NIC type `probe_port`, `remove_port`, PHY capability, and MAC fault hooks to the common MCDI PHY/MAC implementation in `mcdi_port_common.c`.

Important APIs: `efx_mcdi_phy_get_caps()` returns `efx->phy_data->supported_cap`; `efx_mcdi_mac_check_fault()` issues `MC_CMD_GET_LINK` and reports any RPC failure as a MAC fault; `efx_mcdi_port_probe()` calls `efx_mcdi_phy_probe()` then `efx_mcdi_mac_init_stats()`; `efx_mcdi_port_remove()` tears down PHY data and MAC stats.

Control flow: probe first populates PHY data, loopback modes, link state, FEC, and flow-control defaults through the common helper. Only after that does it allocate the DMA statistics buffer. Remove performs the inverse, clearing `efx->phy_data` and freeing the stats buffer. MAC fault checking is synchronous and intentionally conservative: failed firmware communication returns `true`.

State and dependencies: all state lives on `struct efx_nic`, especially `phy_data`, `link_state`, `loopback_modes`, and `stats_buffer`. The file depends on `mcdi.h`, `mcdi_pcol.h`, `mcdi_port_common.h`, `nic.h`, and `selftest.h`.

Risks and tests: initialization ordering matters because other ethtool and link paths assume `phy_data` is valid after port probe. Test signals include probe/remove smoke tests, simulated `GET_LINK` failures, ethtool link capability reads, and MAC stats allocation/free leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port.h

Purpose: this header declares the port-level MCDI entry points used by NIC type tables and driver core code. It intentionally hides the larger PHY/MAC helper surface in `mcdi_port_common.h` behind a compact port interface.

Important API: it declares `efx_mcdi_phy_get_caps()`, `efx_mcdi_mac_check_fault()`, `efx_mcdi_port_probe()`, and `efx_mcdi_port_remove()`. These functions operate on `struct efx_nic` and are backed by the MCDI management-controller protocol.

Control flow and integration: controller-specific NIC type instances can wire these functions into `struct efx_nic_type` callbacks. Probe and remove become lifecycle hooks; capability and fault methods become ethtool/link-monitor support. The only dependency is `net_driver.h` for the core NIC type.

State and risks: the header owns no state, but callers must obey lifecycle assumptions: `efx_mcdi_phy_get_caps()` requires `efx->phy_data` to have been populated by probe, and `remove` should only run after probe or a partial-probe cleanup path that is prepared for common helper teardown. Test signals are compile coverage of NIC type tables and probe/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port_common.c

Purpose: this is the shared MCDI implementation for PHY discovery, link configuration, FEC conversion, module EEPROM access, cable/BIST tests, MAC configuration, MAC stats DMA control, physical port lookup, and link-change event handling.

Important APIs and data: `efx_mcdi_get_phy_cfg()` fills `struct efx_mcdi_phy_data`; `mcdi_to_ethtool_linkset()` and `ethtool_linkset_to_mcdi_cap()` convert firmware capability bits to Linux link-mode bitmaps; `efx_mcdi_phy_probe()` allocates and initializes `efx->phy_data`, `efx->link_state`, `efx->loopback_modes`, `efx->fec_config`, and flow-control defaults. Link setters include `efx_mcdi_phy_set_link_ksettings()`, `efx_mcdi_phy_set_fecparam()`, and `efx_mcdi_port_reconfigure()`. Diagnostics include `efx_mcdi_phy_run_tests()` and module EEPROM/info helpers. MAC helpers include `efx_mcdi_set_mac()`, `efx_mcdi_set_mtu()`, stats start/stop/pull/init/fini, and `efx_mcdi_process_link_change()`.

Control flow: PHY probe sends `GET_PHY_CFG`, then `GET_LINK`, installs `phy_data`, derives advertised or forced capabilities, verifies loopback enum compatibility with firmware, fetches loopback modes, decodes initial link, records FEC, and sets default wanted flow control. Link setters recompute MCDI capability words from ethtool state plus saved FEC before issuing `SET_LINK`. MAC stats use `MC_CMD_MAC_STATS` with a coherent DMA buffer and a generation sentinel; pull waits briefly for firmware to update the last generation word. Module EEPROM reads page-sized media data through `GET_PHY_MEDIA_INFO`, handling SFP, QSFP, missing QSFP pages, and SFF-8472 diagnostics rules.

State and persistence: persistent runtime state is all in `struct efx_nic`: `phy_data`, `phy_type`, `link_advertising`, `wanted_fc`, `fec_config`, `link_state`, `loopback_modes`, `stats_buffer`, `num_mac_stats`, and `vport_id`. No on-disk persistence exists; firmware and module EEPROM are external state.

Dependencies and integration: this file is tightly coupled to MCDI protocol macros, ethtool link/FEC APIs, the SFC core link helpers, NIC revision checks, DMA allocation helpers from `nic.c`, and netdev feature state. It is the main implementation behind ethtool link settings, FEC settings, self-tests, module EEPROM reads, MAC reconfiguration, and link events.

Risks and tests: risk concentrates in bit translations, firmware output length validation, FEC semantics, race assumptions around link-change events outside `mac_lock`, and DMA stat generation handling. Test signals include ethtool link mode round-trips, forced/autoneg link changes, FEC get/set on 25G/50G/100G, loopback selftests, SFP/QSFP EEPROM reads, link-change event injection, stats pull under traffic, and firmware RPC error/short-response tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port_common.h

Purpose: this header defines the shared MCDI PHY data model and declares the common MCDI port/PHY/MAC helper surface used by SFC controller implementations.

Important types and APIs: `struct efx_mcdi_phy_data` stores firmware PHY flags, type, supported capabilities, channel, port, stats mask, media, MMD mask, name/revision strings, and saved forced capabilities. Declared functions cover PHY config fetch, link advertising and `SET_LINK`, loopback modes, link-mode conversion, PHY flags/media/link decode, FEC conversion, flow-control partner checks, PHY poll/probe/remove, ethtool link and FEC get/set, PHY tests and names, module EEPROM/info, MAC setup/MTU/stats lifecycle, port number lookup, and link-change event processing.

Control flow and integration: the header is consumed by `mcdi_port.c`, `mcdi_port_common.c`, and NIC type code that needs fine-grained helpers rather than only the port-level facade. It depends on `net_driver.h`, `mcdi.h`, and `mcdi_pcol.h`.

State and risks: the declared helpers expect `struct efx_nic` lifecycle invariants, especially valid `phy_data` after PHY probe and valid `stats_buffer` after MAC stats init. Adding fields to `struct efx_mcdi_phy_data` requires auditing MCDI response parsing and teardown. Test signals are compile coverage plus port probe, ethtool link/FEC operations, diagnostics, and link events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_port_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mtd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mtd.c

Purpose: this file adapts NIC-specific flash/NVRAM operations to the Linux MTD subsystem. It registers SFC firmware partitions as `struct mtd_info` devices and delegates erase/read/write/sync/rename behavior to the active `efx_nic_type`.

Important APIs: `efx_mtd_add()` initializes and registers an array of `struct efx_mtd_partition`; `efx_mtd_remove()` unregisters every partition and frees the partition allocation; `efx_mtd_rename()` refreshes partition names under RTNL. Internal wrappers are `efx_mtd_erase()`, `efx_mtd_sync()`, and `efx_mtd_remove_partition()`.

Control flow: add iterates partition records using the supplied stride, fills MTD callbacks, sets `MTD_WRITEABLE` unless `MTD_NO_ERASE` is present, asks the NIC type to rename the partition, registers it, and appends it to `efx->mtd_list`. On partial failure it unregisters already-created partitions in reverse and returns `-ENOMEM`. Remove waits out `-EBUSY` unregister results by sleeping and retrying, then unlinks list nodes and finally frees the first allocation block.

State and dependencies: persistent state is the in-memory `efx->mtd_list`; actual flash state lives on the device. Dependencies include `linux/mtd/mtd.h`, RTNL assertions for rename, and NIC type MTD callbacks.

Risks and tests: registration failure cleanup relies on list ordering and a single allocation block. `efx_mtd_remove()` warns if called while the netdev is registered. Test signals include MTD partition registration, read/write/erase/sync through firmware, rename after netdev rename, busy unregister handling, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/net_driver.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/net_driver.h

Purpose: this is the central shared type and helper header for the SFC network driver. It defines queue, channel, NIC, filter, RSS, XDP, link, MTD, and NIC-type operation structures used across the driver.

Important types: `struct efx_buffer` wraps coherent DMA buffers; `struct efx_tx_buffer` and `struct efx_tx_queue` model TX descriptor/software rings and counters; `struct efx_rx_buffer`, `struct efx_rx_page_state`, and `struct efx_rx_queue` model page-backed RX descriptors, recycling, refill, XDP, and stats; `struct efx_channel` combines event queue, NAPI, IRQ, RX/TX queues, RFS counters, and PTP sync-event state. `struct efx_nic` is the top-level device state, including PCI resources, interrupt mode, channels, queues, RSS, port/MAC/PHY state, filters, queue flush state, SR-IOV/representor state, PTP, devlink, locks, work items, and stats. `struct efx_nic_type` is the controller-specific operation table.

Control flow and integration: most source files call inline dispatchers that route TX, RX, event, interrupt, filter, MTD, PTP, stats, and port operations through `efx->type`. Helper macros iterate channels and queues, compute queue indices, manage NIC state flags, map timestamp flags, and compute max frame length.

State and persistence: all runtime device state is anchored here. No disk persistence exists, but the structures mirror durable hardware/firmware state: VIs, RSS contexts, MTD partitions, link settings, filters, timestamp configuration, and firmware capabilities.

Dependencies: the header depends on Linux netdev, ethtool, PCI, MTD, XDP, busy-poll, notifier, list, locking, and SFC local `enum.h`, `bitfield.h`, and `filter.h` definitions.

Risks and tests: this header is high blast radius. Layout, concurrency, cache-line annotations, and lifecycle invariants affect the whole driver. Test signals include full driver build coverage, probe/open/stop/remove, RX/TX stress, XDP, RSS/RFS, PTP, MTD, SR-IOV, reset/recovery, ethtool stats/register dumps, and lockdep/KASAN/KCSAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/net_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic.c

Purpose: this file provides generic NIC helpers for coherent DMA buffers, interrupt hookup/teardown, register dumping, and hardware statistics conversion.

Important APIs: `efx_nic_alloc_buffer()` and `efx_nic_free_buffer()` allocate/free coherent DMA; `efx_nic_event_present()`, `efx_nic_event_test_start()`, and `efx_nic_irq_test_start()` support self-tests; `efx_nic_init_interrupt()` requests MSI-X/MSI or legacy IRQs and optionally builds an RFS CPU rmap; `efx_nic_fini_interrupt()` frees them. `efx_nic_get_regs_len()` and `efx_nic_get_regs()` implement ethtool register dumps. `efx_nic_describe_stats()`, `efx_nic_copy_stats()`, `efx_nic_update_stats()`, and `efx_nic_fix_nodesc_drop_stat()` support ethtool statistics.

Control flow: interrupt setup branches on interrupt mode. MSI paths request an IRQ per channel and unwind partial success on failure; legacy requests a shared IRQ once. Stats copying uses firmware generation words around a memcpy to avoid torn DMA reads, retrying briefly then zeroing on failure. Register dumping walks revision-filtered register and table descriptors.

State and dependencies: state affected includes `efx->irqs_hooked`, `net_dev->rx_cpu_rmap`, channel IRQ registrations, `last_irq_cpu`, `event_test_cpu`, `stats_buffer`, and RX no-descriptor drop accumulators. Dependencies include PCI DMA APIs, Linux IRQ APIs, CPU rmap, SFC register access helpers, firmware stats layouts, and `struct efx_nic_type` interrupt callbacks.

Risks and tests: risks include IRQ unwind correctness, stale CPU rmap state, DMA generation races, register-table size mismatches, and stats leaking uninitialized data. Test signals include interrupt selftests, open/close under MSI-X/MSI/legacy modes, ethtool register dumps, stats under concurrent DMA updates, and error-injection for IRQ request and DMA allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic.h

Purpose: this EF10-family NIC header defines PHY type constants, EF10 statistic indexes, EF10 private NIC state, and exported NIC type instances.

Important types and APIs: the first enum lists legacy PHY type IDs used by diagnostics and MCDI PHY code. The large EF10 stats enum extends generic stats with port, RX/TX, FEC, CTPIO, and datapath counters. `struct efx_ef10_nic_data` stores EF10-specific runtime state: MCDI DMA buffer, warm boot count, VI and PIO allocation, write-combining mappings, MC stats buffers, firmware workaround flags, datapath capabilities, firmware IDs, PF/VF/vswitch state, vport MAC/VLANs, UDP tunnel ports, and licensed features. It declares `efx_ef10_tx_tso_desc()` and NIC type externs for Huntington and X4.

Control flow and integration: controller implementations allocate this private structure as `efx->nic_data` and use it during probe, reset recovery, datapath capability checks, stats, SR-IOV, UDP tunnel restore, and licensed feature checks such as PTP TX timestamps.

State and risks: many fields are recovery flags after MC reboot (`must_restore_piobufs`, `must_check_datapath_caps`, `must_probe_vswitching`, `udp_tunnels_dirty`). Incorrect handling can leave firmware resources stale after reset. Test signals include EF10 probe/reset, MC reboot recovery, stats, TSOv2, PIO/CTPIO, SR-IOV, UDP tunnel offload, and licensed timestamp feature behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic_common.h

Purpose: this header supplies architecture-neutral NIC helpers layered over `struct efx_nic_type`. It centralizes event, TX, RX, interrupt, DMA buffer, register, and stats dispatch for controller implementations.

Important APIs: inline helpers expose `efx_nic_rev()`, event access/presence checks, TX/RX descriptor address calculation, TX empty/push decisions, NIC-specific TX/RX/event queue probe/init/remove/write calls, sensor events, recycle-ring sizing, monotonically safe diff stats, interrupt self-test accessors, and atomic stats update dispatch. It declares generic buffer, register, stats, interrupt, and TSO helpers implemented elsewhere.

Control flow and integration: callers in datapath and lifecycle code use these wrappers so common code stays independent of EF10/EF100-specific register programming. Event presence intentionally checks both dwords for all-ones to tolerate DMA write ordering. TX push logic clears `empty_read_count` and pushes only a single descriptor to a queue the completion path saw empty.

State and dependencies: it reads and mutates queue counters such as `empty_read_count`, uses channel eventq buffers, and dispatches through `efx->type`. Dependencies include `net_driver.h`, `efx_common.h`, `mcdi.h`, and `ptp.h`.

Risks and tests: risks are mostly subtle fast-path assumptions around DMA ordering, queue counter wrap, and false negatives in emptiness checks. Test signals include RX/TX datapath stress, event queue processing, TX push latency tests, stats monotonicity, interrupt selftests, and compile coverage for each NIC type operation table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ptp.c

Purpose: this file implements SFC Precision Time Protocol and hardware timestamping support. Firmware assists timestamp capture through MCDI; the driver defers long operations to workqueues, manages PTP RX/TX filtering, synchronizes host and NIC time, registers a PHC clock for the primary function, and attaches timestamps to SKBs.

Important types and APIs: `struct efx_ptp_data` owns PTP queues, workqueues, filters, timestamp config, conversion functions, time-sync bounds, corrections, event fragments, DMA synchronization flag buffer, PHC/PPS state, statistics, and TX method selection. Public entry points include `efx_ptp_probe()`, `efx_ptp_remove()`, `efx_ptp_defer_probe_with_channel()`, `efx_ptp_start_datapath()`, `efx_ptp_stop_datapath()`, `efx_ptp_tx()`, `efx_ptp_is_ptp_tx()`, timestamp config get/set/info, event handlers, stats, and RX timestamp attach. PHC methods implement adjfine, adjtime, gettime, settime, and PPS enable.

Control flow: probe allocates `efx_ptp_data`, a coherent `start` flag buffer, RX/TX queues, workqueues, conversion/correction data from firmware, and possibly a PHC clock. PTP enable installs multicast filters, enables firmware PTP mode, clears event assembly, and synchronizes baseline time. TX packets are queued and transmitted either through a timestamped TX queue or via MCDI; RX packets are queued until a matching event or timeout. Work processing handles reset-required restarts, expired/unwanted RX packets, queued TX, and packet delivery. Datapath start/stop toggles sync events and PTP firmware state.

State and persistence: in-memory state includes queued SKBs, multicast/unicast filters with jiffies expiry, timestamp configuration, current frequency adjustment, sync-event state on the PTP channel, PHC registration, PPS enable, and counters. Firmware state includes enabled PTP mode, clock adjustment, filters, timestamp corrections, and sync-event subscription.

Dependencies and integration: the file depends on MCDI PTP commands, Linux PTP clock/PPS APIs, net timestamping APIs, SFC filter insertion/removal, TX enqueue, channel allocation through `efx_channel_type`, and NIC type hooks for host-time writes and timestamp config.

Risks and tests: risks include RX event/packet matching timeouts, filter leaks, workqueue lifetime races, incorrect timestamp conversion near wrap boundaries, sync-event loss, missing PHC cleanup, and firmware error recovery. Test signals include `ptp4l`/`phc2sys`, hardware TX/RX timestamp sockets, PPS enable events, PTP over IPv4/IPv6/Ethernet where supported, unicast filter expiry, MC timestamp-correction variants, reset/restart during PTP traffic, and event-fragment error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ptp.h

Purpose: this header declares the PTP and hardware timestamping interface used by the SFC core, datapath, ethtool timestamp reporting, and channel management code.

Important APIs: lifecycle functions are `efx_ptp_probe()`, `efx_ptp_defer_probe_with_channel()`, `efx_ptp_update_channel()`, `efx_ptp_channel()`, and `efx_ptp_remove()`. Configuration and reporting functions are `efx_ptp_set_ts_config()`, `efx_ptp_get_ts_config()`, and `efx_ptp_get_ts_info()`. Datapath hooks include `efx_ptp_is_ptp_tx()`, `efx_ptp_tx()`, `efx_ptp_event()`, `efx_time_sync_event()`, RX timestamp attach helpers, datapath start/stop, MAC TX timestamp capability, and `efx_ptp_nic_to_kernel_time()`.

Control flow and integration: normal RX delivery calls `efx_rx_skb_attach_timestamp()`, which only invokes the full attach path when channel sync events are valid. TX code can detect PTP packets and queue them for PTP handling. Event code routes PTP and time-sync events back to this module.

State and risks: the header exposes functions that assume `efx->ptp_data` may be absent, so callers must handle `-EOPNOTSUPP` or no-op behavior. The inline attach check depends on `channel->sync_events_state`. Test signals include compile coverage, timestamp config via `SIOCSHWTSTAMP`, TX/RX timestamping, and datapath restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx.c

Purpose: this file implements the second half of the RX datapath: interpreting completion metadata, validating lengths/fragments, syncing DMA buffers, pipelining packet delivery, running XDP, building SKBs, attaching checksums/timestamps, and passing packets to GRO, channel handlers, or the stack.

Important APIs: `efx_rx_packet()` is called by NIC-specific event/RX code when a packet completion is seen. `__efx_rx_packet()` consumes the pending packet recorded on the channel and delivers it. Internal helpers validate length, build SKBs from page fragments, deliver SKBs, and run XDP.

Control flow: `efx_rx_packet()` marks flags on the first RX buffer, validates fragment count/length/scatter assumptions, discards explicit or invalid packets, syncs DMA for all fragments, advances past the RX prefix, recycles pages, flushes any previously prefetched packet, then stores the new packet in `channel->rx_pkt_*`. `__efx_rx_packet()` reads prefix length if needed, handles loopback selftest, updates RX stats, runs XDP for single-fragment packets, clears checksum flags if netdev RX checksum is disabled, and chooses GRO for TCP packets without a special channel handler or normal SKB delivery otherwise.

State and dependencies: state spans `rx_buf->flags/len/page_offset`, queue packet/byte counters, channel pending packet fields, XDP stats, loopback state, and `efx->xdp_prog`. Dependencies include RX common buffer/free/GRO helpers, XDP APIs, checksum/GRO APIs, PTP timestamp attach, and channel `receive_skb` hooks.

Risks and tests: risks include overlength handling, prefix length zero packets, fragmented packets with XDP, page ownership transfer to SKB/XDP TX/redirect, checksum metadata correctness, and pending-packet flush ordering. Test signals include RX traffic with and without RX prefixes, jumbo/scattered frames, XDP PASS/DROP/TX/REDIRECT/error cases, loopback selftests, GRO throughput, RX checksum toggles, PTP RX timestamps, and low-memory SKB allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx_common.c

Purpose: this file provides common RX queue lifecycle, page allocation/recycling, descriptor refill, GRO fragment delivery, RSS defaults, filter specification utilities, filter table lifecycle, and optional accelerated RFS support.

Important APIs: queue lifecycle is `efx_probe_rx_queue()`, `efx_init_rx_queue()`, `efx_fini_rx_queue()`, `efx_remove_rx_queue()`, and `efx_destroy_rx_queue()` when used by other code. Buffer helpers include `efx_recycle_rx_pages()`, `efx_discard_rx_packet()`, `efx_unmap_rx_buffer()`, `efx_free_rx_buffers()`, slow-fill scheduling, page split configuration, and `efx_fast_push_rx_descriptors()`. Packet delivery helper `efx_rx_packet_gro()` builds GRO fragments. RSS/filter helpers include `efx_find_rss_context_entry()`, `efx_set_default_rx_indir_table()`, multicast-recipient tests, filter equality/hash, `efx_probe_filters()`, and `efx_remove_filters()`. Under `CONFIG_RFS_ACCEL`, it also owns ARFS hash operations, async filter insertion, `efx_filter_rfs()`, and expiry.

Control flow: RX queue init resets ring counters, initializes the recycle ring, computes max/trigger fill thresholds, registers XDP RXQ info, and calls NIC-specific RX init. Fast refill checks fill level, allocates or reuses pages in batches, maps pages for DMA, splits them into buffers with XDP headroom/tailroom, marks the last buffer in each page, and notifies the NIC. Finalization drains pending buffers, timer/work, recycle ring, and XDP RXQ registration. RFS flow inserts select a work slot, dissect packet flow keys, build an RX filter spec, update or create ARFS hash state, and schedule work to call the NIC filter insert operation.

State and dependencies: state includes RX ring counters, recycle page ring, min fill stats, XDP RXQ info, `efx->rss_context`, filter table state under `mac_lock`, per-channel RFS arrays, and global RPS hash/slot locks. Dependencies include DMA mapping, page refcounts, timers, workqueues, ethtool RSS contexts, filter APIs, RPS flow expiry, and NIC type RX/filter callbacks.

Risks and tests: risks include page refcount/DMA unmap mistakes, refill starvation, race assumptions around caller serialization, XDP RXQ registration failure, ARFS rule lifetime, and filter table teardown while async work exists. Test signals include RX queue probe/init/fini/remove cycles, memory pressure causing slow fill, page recycling counters, XDP attach/remove, RSS context lookup under lockdep, multicast filter tests, RFS acceleration under TCP/UDP IPv4/IPv6, and filter expiry under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx_common.h

Purpose: this header declares shared RX queue, buffer, GRO, RSS, filter, and RFS helpers used by NIC-specific receive code and the generic RX datapath.

Important APIs: constants define preferred refill batch size, maximum fragments per packet, and 10G recycle ring sizing. Inline helpers compute RX buffer virtual addresses, read packet hash values from RX prefixes with aligned or bytewise access, and sync DMA for CPU access. Declarations cover slow fill, page recycling/discard, RX queue lifecycle, buffer initialization/unmapping/freeing, page split config, fast descriptor push, GRO delivery, RSS context/default table helpers, filter spec helpers, optional RFS functions, and filter table probe/remove.

Control flow and integration: NIC-specific event/RX code calls these helpers when completions arrive or descriptors need refill. `rx.c` uses GRO and buffer helpers for delivery. Filter and RSS code use the common hash/equality/context functions.

State and risks: the header itself owns no state, but functions operate on `struct efx_rx_queue`, `struct efx_channel`, and `struct efx_nic` fields defined in `net_driver.h`. Risks include callers forgetting required serialization for refill, using hash offsets without a valid prefix, or calling RFS helpers without the feature enabled. Test signals include compile coverage with and without `CONFIG_RFS_ACCEL`, RX traffic, RSS hash reporting, descriptor refill, and XDP/GRO paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx_common.h -->
