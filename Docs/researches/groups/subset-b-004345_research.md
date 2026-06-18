# subset-b-004345 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.c

Purpose: implements the common Atlantic NIC lifecycle and netdev-facing behavior above the chip-specific `aq_hw_ops` and firmware operations. It owns RSS defaults, vector sizing, netdev registration, link monitoring, TX mapping, ethtool link settings, filters, traffic-class setup, power, and shutdown sequencing.

Important APIs/functions: `aq_nic_cfg_start`, `aq_nic_ndev_register`, `aq_nic_init`, `aq_nic_start`, `aq_nic_xmit`, `aq_nic_xmit_xdpf`, `aq_nic_stop`, `aq_nic_deinit`, `aq_nic_get_stats`, `aq_nic_set_link_ksettings`, `aq_nic_setup_tc_mqprio`, and filter reservation/release helpers. Static service functions drive link/status refresh and polling mode.

Control flow: PCI probe allocates the netdev and calls config, netdev init, and registration. Open paths call `aq_nic_init` to reset hardware, initialize firmware/PHY/PTP/rings, then `aq_nic_start` to program filters, start vectors/PTP rings, enable interrupts, and start queues. TX maps skb or XDP fragments into ring buffers before calling `hw_ring_tx_xmit`. Stop disables queues, timers, IRQs, vectors, PTP rings, and hardware.

State and persistence: state is in `aq_nic_s`, including atomic readiness flags, `aq_nic_cfg`, rings/vectors, timers, link status, multicast/VLAN/filter state, PTP pointer, PCI state, and firmware mutex. Persistent device state is programmed into firmware/hardware, but no filesystem persistence exists.

Dependencies and integration: depends on Linux netdev, ethtool, timers, NAPI vectors, PCI IRQ allocation, firmware ops, `aq_ring`, `aq_vec`, PHY, PTP, filters, and optional MACsec. It is the central integration point between netdev operations and chip-specific A0/B0/ATL2 hardware methods.

Risks: vector count rounding and TC remapping can change queue topology; QoS can auto-disable PTP; TX mapping must unwind DMA mappings exactly on errors; link changes reprogram interrupt moderation and flow control; firmware calls require `fwreq_mutex`; hot-unplug paths rely on presence checks. Test signals include netdev probe/open/close, link up/down, ethtool speed changes, XDP TX, TC mqprio/rate-limit, PTP enablement, suspend/resume, and DMA mapping failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.h

Purpose: declares the shared NIC object model and public NIC control API used by PCI, netdev, vector, ring, PTP, filter, ethtool, and hardware layers.

Important APIs/types: defines `enum aq_fc_mode`, `struct aq_fc_info`, `struct aq_nic_cfg_s`, filter bookkeeping structs, and `struct aq_nic_s`. It declares lifecycle functions (`aq_nic_init`, `aq_nic_start`, `aq_nic_stop`, `aq_nic_deinit`, `aq_nic_shutdown`), TX functions, stats/register accessors, link settings, filter reservation, and TC configuration helpers. Macros map traffic class/vector IDs to hardware ring indices.

Control flow: consumers fill `aq_nic_cfg_s` from hardware capabilities, then drive the declared lifecycle in probe/open/close/remove/PM paths. Rings and vectors call back into `aq_nic_get_ndev`, `aq_nic_get_cfg`, and ring mapping macros to coordinate queue numbering.

State and persistence: `aq_nic_s` centralizes atomic flags, `aq_hw_s`, ops tables, netdev, PCI device, vector/ring arrays, timers, link state, multicast/VLAN state, firmware request mutex, optional MACsec, optional PTP, and RX filter reservations. This is runtime kernel state only.

Dependencies and integration: includes ethtool, XDP/BPF, `aq_common`, `aq_rss`, and `aq_hw`. It is included broadly by the Atlantic driver and forms the common ABI between generic and hardware-specific files.

Risks: macro ring mapping must stay synchronized with TC mode and vector count; flags are bit constants shared across asynchronous paths; optional fields under Kconfig require callers to tolerate absent MACsec/PTP support. Test signals are compile coverage for all include users, queue mapping tests through multiqueue TX/RX, and runtime transitions that mutate `aq_nic_cfg_s`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.c

Purpose: implements PCI driver registration, device ID to hardware-ops selection, PCI resource setup, IRQ allocation/freeing, probe/remove, shutdown, and power-management glue for Atlantic adapters.

Important APIs/functions: exports `aq_pci_func_alloc_irq`, `aq_pci_func_free_irqs`, `aq_pci_func_get_irq_type`, `aq_pci_func_register_driver`, and `aq_pci_func_unregister_driver`. Static probe helpers include `aq_pci_probe_get_hw_by_id`, `aq_pci_func_init`, `aq_pci_probe`, `aq_pci_remove`, `aq_pci_shutdown`, and PM suspend/resume wrappers.

Control flow: `aq_pci_probe` enables the device, requests regions, allocates the netdev, chooses A0/B0/ATL2 ops/caps from tables, allocates `aq_hw_s`, maps MMIO BARs, allocates IRQ vectors including PTP/service slots, starts NIC config, initializes and registers the netdev, then initializes driver info. Error labels unwind in reverse order. Remove unregisters netdev and frees filters, MACsec, vectors, IRQs, MMIO, hardware memory, PCI regions, and netdev.

State and persistence: stores `aq_nic_s` in PCI drvdata, tracks `irqvecs` and `msix_entry_mask`, maps MMIO into `aq_hw->mmio`, and controls PCI D0/D3/WOL state during shutdown and suspend. No disk persistence.

Dependencies and integration: binds Linux PCI core to `aq_nic`, hardware caps in `hw_atl_a0`, `hw_atl_b0`, `hw_atl2`, filters, MACsec, and driver metadata.

Risks: board table mismatches can select wrong ops/caps; IRQ mask bookkeeping must match vector ownership, especially link/PTP vectors; probe error unwinds must not leak BARs/MMIO/IRQ vectors; PM resume must deinit partially initialized hardware on errors. Test signals include PCI modalias binding, probe failure injection, MSI-X/MSI/INTx modes, suspend/resume, shutdown with WOL, and hot remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.h

Purpose: declares the PCI-facing interface used by NIC lifecycle code and module init/exit code.

Important APIs/types: `struct aq_board_revision_s` maps a PCI device/revision to `aq_hw_ops` and `aq_hw_caps_s`. Public functions allocate/free per-vector IRQs, query IRQ type, and register/unregister the PCI driver.

Control flow: `aq_nic_cfg_start` queries `aq_pci_func_get_irq_type`; `aq_nic_start` uses `aq_pci_func_alloc_irq`; `aq_nic_stop` uses `aq_pci_func_free_irqs`; module setup uses register/unregister. The board-revision structure is consumed internally by probe.

State and persistence: no storage beyond declarations. Runtime state is passed through `struct aq_nic_s` and maintained in the implementation.

Dependencies and integration: includes `aq_common` and `aq_nic`, tying PCI setup to the generic NIC object and hardware capability abstraction.

Risks: any change to IRQ helper signatures affects NIC start/stop paths; board table declarations must remain aligned with hardware ops/caps definitions. Test signals are compile coverage and successful probe/open/close across MSI-X, MSI, and legacy INTx variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.c

Purpose: provides low-level MDIO/PHY helper operations for Atlantic copper PHY discovery and PTP-disable workarounds.

Important APIs/functions: `aq_mdio_busy_wait`, `aq_mdio_read_word`, `aq_mdio_write_word`, `aq_phy_read_reg`, `aq_phy_write_reg`, `aq_phy_init_phy_id`, `aq_phy_init`, and `aq_phy_disable_ptp`.

Control flow: raw MDIO read/write first programs address registers, issues address/read/write commands, and waits for the MDIO busy bit. Higher-level PHY accesses acquire the firmware MDIO semaphore with polling, perform the MDIO transaction, then release the semaphore. PHY init scans possible PHY IDs until identifier registers respond, then reads the full PMA/PMD ID. PTP disable loops over vendor registers and clears the PTP enable bit.

State and persistence: mutates `aq_hw->phy_id` and writes PHY registers. Register changes persist in device hardware/PHY state until reset or firmware reprovisioning, but no host filesystem persistence exists.

Dependencies and integration: uses Linux MDIO constants, `hw_atl_llh` register accessors, `aq_hw_utils`, and `aq_hw`. Called from `aq_nic_init` for Atlantic TP devices and from B0 PTP external timestamp GPIO support.

Risks: timeout returns are coarse (`0xffff` for failed reads), semaphore misuse can race firmware, and the PTP-disable workaround only runs when quirks and detected PHY ID allow it. Test signals include PHY ID detection, MDIO timeout injection, bad-PTP quirk devices, and external timestamp GPIO register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.h

Purpose: declares MDIO and PHY helper APIs for Atlantic hardware code.

Important APIs/types: defines `HW_ATL_PHY_ID_MAX` and declares raw MDIO busy/read/write helpers, semaphore-protected PHY register read/write helpers, PHY ID initialization, PHY init, and PTP-disable workaround.

Control flow: callers use `aq_phy_init` to ensure `aq_hw->phy_id` is valid, use `aq_phy_read_reg`/`aq_phy_write_reg` for MMD register access, and call `aq_phy_disable_ptp` when hardware capability quirks require disabling PHY PTP blocks.

State and persistence: the header itself has no state. Implementations mutate `aq_hw_s` PHY ID and device registers.

Dependencies and integration: includes Linux MDIO definitions, low-level Atlantic register headers, hardware utilities, and `aq_hw`. It is consumed by `aq_nic.c` and B0 hardware PTP/GPIO support.

Risks: the header exposes low-level operations that assume the caller has a live `aq_hw_s` and valid MMIO mapping; misuse during remove/suspend can touch absent hardware. Test signals are build coverage plus PHY init and PTP GPIO paths on TP adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.c

Purpose: implements Linux PTP hardware clock support for capable Atlantic A1/B0-era devices, including clock adjustment, hardware timestamp TX/RX rings, timestamp filters, GPIO periodic output/external timestamp support, and timeout cleanup.

Important APIs/functions: exported functions include `aq_ptp_init`, `aq_ptp_ring_alloc/init/start/stop/deinit/free`, `aq_ptp_irq_alloc/free`, `aq_ptp_xmit`, `aq_ptp_tx_hwtstamp`, `aq_ptp_hwtstamp_config_set/get`, `aq_ptp_extract_ts`, `aq_ptp_link_change`, and stats helpers. Internal types include `struct aq_ptp_s`, `ptp_skb_ring`, and `ptp_tx_timeout`.

Control flow: init checks chip feature, hardware timestamp ops, firmware `enable_ptp`, and firmware-reported PHY PTP capability; it loads per-speed offsets, registers a PTP clock, creates NAPI, enables firmware PTP, and reserves filters. Ring allocation creates PTP TX/RX plus hardware timestamp RX rings and an skb queue. PTP NAPI cleans TX completions, timestamp completions, and RX traffic. HWTSTAMP configuration programs UDP/L2 filters into the dedicated PTP RX queue.

State and persistence: `aq_ptp_s` stores hwtstamp config, spinlocks, PTP clock info, offset atomics, rings, pending skb timestamp queue, reserved filters, delayed GPIO polling work, and last sync timestamp. Hardware/firmware PTP state is enabled/disabled through ops.

Dependencies and integration: depends on Linux `ptp_clock_kernel`, packet timestamping, NAPI, IRQ, `aq_ring`, `aq_phy`, and `aq_filters`. B0 hardware provides most PTP ops.

Risks: pending TX timestamp SKBs can overflow or timeout; filter programming failures return remote I/O errors; GPIO external timestamp polling samples multiple times to avoid unstable reads; PTP is disabled when TC count exceeds hardware PTP TC limits. Test signals include `ptp4l`/`phc2sys`, `SIOCSHWTSTAMP`, TX timeout logs, PTP RX filter routing, GPIO perout/extts, link changes, and disabled Kconfig stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.h

Purpose: declares the PTP interface used by the NIC, ring, ethtool/timestamp, and hardware paths, with no-op stubs when PTP clock support is unavailable.

Important APIs/types: defines dedicated ring indices (`PTP_8TC_RING_IDX`, `PTP_4TC_RING_IDX`, `PTP_HWST_RING_IDX`) and `aq_ptp_ring_idx`. Declares init/free, IRQ, ring lifecycle, service, clock init, TX/RX timestamp, hwtstamp config, ring identification, link-change, and PTP stats helpers.

Control flow: generic NIC code calls these hooks unconditionally, relying on inline stubs under `!CONFIG_PTP_1588_CLOCK`. Runtime-capable builds allocate and start PTP resources alongside normal rings, and ring RX code calls `aq_ptp_ring`/`aq_ptp_extract_ts` for timestamp-aware packets.

State and persistence: no header state; implementation state is opaque `struct aq_ptp_s` referenced from `aq_nic_s`.

Dependencies and integration: includes Linux timestamp config and `aq_ring`; bridges netdev timestamping, ring receive, and hardware timestamp extraction.

Risks: callers must check availability when dereferencing `aq_ptp_s`; ring index constants must remain compatible with TC mode and hardware ring count; stubs must preserve behavior for non-PTP builds. Test signals include compile tests with PTP enabled/disabled and runtime hwtstamp ioctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.c

Purpose: implements shared TX/RX ring memory allocation, DMA buffer lifecycle, TX cleanup, RX refill/clean, XDP receive/transmit handling, hardware timestamp RX cleanup, and per-ring software stats.

Important APIs/functions: `aq_ring_tx_alloc`, `aq_ring_rx_alloc`, `aq_ring_init`, `aq_ring_update_queue_state`, `aq_ring_tx_clean`, `aq_xdp_xmit`, `aq_ring_rx_clean`, `aq_ring_rx_fill`, `aq_ring_rx_deinit`, `aq_ring_free`, `aq_ring_hwts_rx_alloc/free/clean`, and `aq_ring_fill_stats_data`.

Control flow: allocation creates software buffer rings and coherent descriptor rings. RX fill allocates or reuses pages, DMA maps them, and advances software tail. Hardware receive ops populate buffer metadata; `aq_ring_rx_clean` selects skb or XDP path, validates descriptor chains, handles errors, syncs DMA for CPU, extracts PTP timestamps, builds skb/XDP buffers, applies VLAN/checksum/RSS metadata, and submits GRO or XDP actions. TX clean walks completed descriptors, unmaps DMA, frees SKBs or returns XDP frames, and wakes queues when space returns.

State and persistence: `aq_ring_s` owns descriptor memory, DMA addresses, head/tail pointers, page reuse parameters, XDP RX queue metadata, and u64 stats. State is volatile and freed on ring deinit.

Dependencies and integration: used by `aq_vec`, `aq_nic`, `aq_ptp`, and hardware ops. Integrates Linux DMA API, page allocator, NAPI, GRO, XDP/BPF, VLAN, checksum, and PTP timestamp extraction.

Risks: descriptor-chain validation is critical for jumbo/LRO/multibuffer XDP; page reuse relies on reference counts and correct DMA sync; TX cleanup must avoid freeing incomplete packets; XDP redirects must flush; hardware timestamp ring uses a special allocation size. Test signals include jumbo/LRO RX, XDP PASS/TX/DROP/REDIRECT with fragments, DMA mapping failures, small-packet checksum workaround, queue stop/wake, and PTP timestamped RX/TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.h

Purpose: defines the common ring data structures and function prototypes for TX, RX, XDP, and PTP hardware timestamp rings.

Important APIs/types: `struct aq_rxpage` stores page/DMA/page-offset information. Packed `struct aq_ring_buff_s` stores per-descriptor metadata for RX, TX, EOP, and TX context descriptors. Stats structs track RX/TX counters. `enum atl_ring_type`, `struct aq_ring_s`, and `struct aq_ring_param_s` define ring identity, DMA descriptor state, queue pointers, XDP RXQ metadata, and IRQ affinity inputs.

Control flow: hardware and generic code share `aq_ring_next_dx` and `aq_ring_avail_dx` for circular descriptor management. Public functions allocate/init/fill/clean/deinit/free rings and expose stats.

State and persistence: ring state is runtime memory plus coherent DMA descriptor memory visible to hardware. The header declares no global persistent state.

Dependencies and integration: includes common definitions and vector declarations; used by NIC, vector, PTP, and A0/B0 hardware files. It also includes Linux XDP-facing layout constants for headroom/tailroom.

Risks: `aq_ring_buff_s` is packed for cache layout and shared assumptions; bitfields and unions must stay consistent with generic mapping and hardware descriptor programming; circular queue arithmetic reserves one descriptor for empty/full distinction. Test signals include descriptor wraparound, fragment limits, XDP multi-buffer use, stats reads on 32-bit, and queue availability thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_rss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_rss.h

Purpose: defines Receive Side Scaling parameter storage shared by NIC configuration and hardware RSS programming.

Important APIs/types: `struct aq_rss_parameters` stores base CPU number, indirection table size, hash secret key size, the 40-byte hash key as `u32` words, and the maximum 64-entry indirection table.

Control flow: `aq_nic_rss_init` fills this structure with the default Toeplitz-style key and queue indirection based on vector count. A0/B0 hardware ops consume it in `hw_rss_set` and `hw_rss_hash_set` to program RSS redirection and hash-key registers.

State and persistence: stored inside `aq_nic_cfg_s`; it persists only for the lifetime of the NIC instance and is reprogrammed during init/reconfiguration.

Dependencies and integration: includes `aq_common` and `aq_cfg` for sizes and common hardware constants. It is a small contract between generic queue sizing and chip register programming.

Risks: indirection values assume power-of-two RSS queue counts; size constants must match hardware register packing; changes affect packet distribution and CPU affinity. Test signals include multiqueue RX distribution, RSS disabled fallback, ethtool RSS inspection if wired elsewhere, and vector-count changes from IRQ/CPU constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_rss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_utils.h

Purpose: provides tiny atomic flag helpers used throughout the Atlantic driver to set, clear, and test object state bits.

Important APIs/functions: `aq_utils_obj_set`, `aq_utils_obj_clear`, and `aq_utils_obj_test` operate on `atomic_t` flag words and 32-bit masks.

Control flow: set/clear use compare-exchange loops to avoid losing concurrent flag updates. Test returns the current masked bits. NIC and hardware code use these helpers for readiness, link-down, PTP datapath, unplug, and hardware-error flags.

State and persistence: no independent state. The helpers mutate caller-provided atomic flag fields.

Dependencies and integration: includes `aq_common`; used in NIC lifecycle, PTP filter state, hardware error/unplug handling, and other driver modules.

Risks: masks must fit the atomic flag layout; callers still need higher-level synchronization for compound state transitions; test returns a boolean interpretation of any matching bit, not an exact equality. Test signals include concurrent link/service/IRQ paths and fault paths that set or clear readiness/error bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.c

Purpose: implements per-interrupt-vector/NAPI aggregation for one TX/RX ring pair per active traffic class.

Important APIs/functions: `aq_vec_alloc`, `aq_vec_ring_alloc`, `aq_vec_init`, `aq_vec_start`, `aq_vec_stop`, `aq_vec_deinit`, `aq_vec_free`, `aq_vec_ring_free`, `aq_vec_isr`, `aq_vec_isr_legacy`, `aq_vec_get_affinity_mask`, `aq_vec_is_valid_tc`, and `aq_vec_get_sw_stats`. Internal `aq_vec_poll` is the NAPI poll routine.

Control flow: allocation creates the vector object and registers NAPI. Ring allocation creates TX/RX rings for each TC and registers RX XDP queue metadata. Init calls generic ring init, hardware ring init, RX fill, and hardware RX tail programming. Start enables hardware rings then NAPI. ISR schedules NAPI; legacy ISR reads/disables IRQ status before scheduling. Poll updates TX heads, cleans TX, receives RX heads, cleans RX, refills RX, updates hardware tails, and reenables the vector interrupt after NAPI completion.

State and persistence: `struct aq_vec_s` stores ops, hardware pointer, NIC pointer, ring counts, ring param/affinity, NAPI object, and a fixed `[AQ_CFG_TCS_MAX][2]` ring array. Runtime only.

Dependencies and integration: bridges `aq_nic`, `aq_ring`, hardware ops, Linux NAPI, IRQ affinity, and XDP RXQ registration.

Risks: TX and RX ring counts must remain aligned per TC; NAPI completion must only reenable IRQs when below budget; legacy INTx masking differs from MSI-X; XDP RXQ unregister must match allocation failures. Test signals include MSI-X and INTx interrupt modes, multitraffic-class polling, NAPI budget exhaustion, queue stats, and XDP-enabled ring allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.h

Purpose: declares the vector/NAPI API that connects NIC lifecycle code with ring allocation, interrupt handlers, and per-ring stats.

Important APIs/types: forward declares key driver structs and exposes ISR entry points, vector allocation/init/start/stop/deinit/free, ring allocation/free, IRQ affinity retrieval, TC validity, and software stat collection.

Control flow: NIC registration allocates vectors; NIC init allocates and initializes vector rings; NIC start starts vectors and requests IRQs using `aq_vec_isr`; NIC stop/deinit/free calls stop/deinit/ring_free/free; ethtool stats paths use `aq_vec_get_sw_stats`.

State and persistence: the vector structure is opaque to users of the header; state is owned by `aq_vec.c`.

Dependencies and integration: includes common, NIC, ring, hardware, IRQ, BPF filter, and netdevice headers. This header is part of the common driver contract between high-level NIC code and data-path implementation.

Risks: include coupling is high because `aq_vec.h`, `aq_ring.h`, and `aq_nic.h` reference one another; changing prototypes affects probe/open/close and IRQ handling. Test signals are compile coverage and runtime open/close under different TC/vector counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.c

Purpose: implements the Atlantic A0 chip-specific hardware operation table and capability records for early AQC100/AQC107/AQC108/AQC109 devices.

Important APIs/functions: exports A0 capability constants and `hw_atl_ops_a0`. Static functions handle reset, QoS, RSS key/table programming, offloads, TX/RX path initialization, MAC address programming, hardware init/start/stop, descriptor programming, IRQ masking/readback, packet/multicast filters, interrupt moderation, and L3/L4 filters.

Control flow: generic NIC init calls `hw_reset`/`hw_init`; A0 init programs TX/RX paths, MAC, link speed, firmware MPI state, QoS, RSS, initial stats, interrupt mapping, and offloads. Ring init writes descriptor base/length/interrupt/CPU registers. TX xmit converts generic buffer metadata into A0 TX/context descriptors and advances hardware tail. RX receive parses writeback descriptors into generic buffer flags, checksum/RSS metadata, packet length, EOP, and jumbo chains.

State and persistence: programs MMIO registers, firmware state, descriptor rings, multicast filter slots, interrupt moderation registers, and hardware stats. Runtime state remains in `aq_hw_s`, `aq_nic_cfg_s`, and rings.

Dependencies and integration: depends on `aq_hw`, `aq_hw_utils`, `aq_ring`, `aq_nic`, low-level `hw_atl_llh`, and A0 constants. It supplies ops selected by PCI board revision matching.

Risks: A0 has limited TC/offload capability; RX receive contains hardware workarounds for descriptor status anomalies and small checksum packets; descriptor bit packing must match hardware; interrupt moderation table depends on link speed index. Test signals include A0 probe, link speed programming, checksum/TSO, RSS distribution, jumbo RX, multicast/promisc modes, L3/L4 filters, and interrupt moderation modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.h

Purpose: declares the public A0 hardware capability records and operation table for PCI board matching.

Important APIs/types: extern declarations for `hw_atl_a0_caps_aqc100`, `hw_atl_a0_caps_aqc107`, `hw_atl_a0_caps_aqc108`, `hw_atl_a0_caps_aqc109`, and `hw_atl_ops_a0`.

Control flow: `aq_pci_func.c` references these symbols when a supported early Aquantia PCI ID/revision maps to A0 hardware. The selected caps feed `aq_nic_cfg_start`; the ops table drives reset/init/ring/filter/IRQ functions.

State and persistence: no direct state. The referenced constants describe hardware capability and ops linkage.

Dependencies and integration: includes `aq_common` for `aq_hw_caps_s` and `aq_hw_ops` declarations. It is the boundary between PCI enumeration and A0 implementation.

Risks: missing or mismatched declarations would break board selection; adding new A0 variants requires matching caps and PCI table entries. Test signals are compile/link coverage and successful probe of A0 revision devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0_internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0_internal.h

Purpose: defines A0-specific constants for MTU, ring counts, descriptor sizes, descriptor bit masks, MPI registers, buffer sizes, RSS packing, TC limits, firmware semaphore IDs, RX writeback bits, and descriptor count bounds.

Important APIs/types: constants include `HW_ATL_A0_MTU_JUMBO`, ring and descriptor sizing, MAC filter slot range, interrupt mask/error vector, TX descriptor control masks, MPI address/speed masks, TX/RX buffer sizes, RSS table properties, TC/RSS max, firmware expected version, and min/max RXD/TXD macros.

Control flow: `hw_atl_a0.c` uses these constants to build capability records, pack TX descriptors, parse RX writebacks, program RSS, map filters, size buffers, and validate descriptor limits.

State and persistence: no runtime state; it is compile-time hardware contract data.

Dependencies and integration: includes `aq_common` for common constants and alignment macros. It is private to A0 hardware code.

Risks: incorrect masks or sizes directly corrupt MMIO/descriptor programming; min/max descriptor macros must stay compatible with generic ring allocation and hardware multiples. Test signals include descriptor programming, RSS table packing, MTU boundary tests, ring size validation, and A0 hardware smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.c

Purpose: implements the B0/B1 Atlantic hardware operation table and capability records, adding richer offloads, TC/QoS, PTP, VLAN filters, temperature, and module EEPROM access beyond A0.

Important APIs/functions: exports B0 capability constants and `hw_atl_ops_b0`; selected helper functions are also declared in the header for reuse. Major functions cover reset, flow control, QoS/PTP TC reservation, RSS, offload setup, TC rate limiting, TX/RX path init, MAC, hardware init/start/stop, descriptor TX/RX, hardware timestamp RX, IRQ moderation, filters, VLAN control, loopback, PTP clock/frequency/GPIO/timestamp conversion, MAC temperature, SMBus module EEPROM reads, and stats/regs/fw version via utils.

Control flow: init programs TX/RX paths, MAC, firmware link/MPI state, QoS, RSS, PCI/MRRS workarounds, interrupt maps including optional link IRQ, and offloads. TX xmit emits context descriptors for GSO and VLAN before data descriptors. RX receive parses checksum, VLAN, RSS, LRO/jumbo chains, errors, and lengths. PTP ops expose PHC read/adjust, firmware frequency requests, GPIO pulse control, external timestamp PHY registers, RX timestamp trailers, and HWTS writebacks.

State and persistence: programs MMIO, firmware requests, PHY registers, `ptp_clk_offset`, descriptor rings, VLAN/L2/L3/L4 filters, IRQ moderation, and SMBus controller state. Runtime state is in `aq_hw_s`, configs, and rings.

Dependencies and integration: used by PCI board table for B0/B1 devices; depends on generic NIC/ring/PHY, low-level LLH registers, firmware request structures, and PTP/filter contracts.

Risks: rate-limit math depends on link speed and TC masks; PTP frequency adjustment uses fixed MAC/PHY counter constants; VLAN promisc behavior is deliberately forced in some modes; SMBus operations must always stop transfers on error; RX head validation protects against bogus hardware values. Test signals include B0 probe, TSO/TSO6/GSO UDP, VLAN strip/insert/filter, LRO, mqprio min/max rates, PTP PHC/GPIO/timestamps, loopback, module EEPROM reads, thermal reads, and interrupt moderation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.h

Purpose: declares B0/B1 hardware capability records, aliases for S-device variants, operation-table symbols, and selected B0 hardware helper APIs.

Important APIs/types: extern caps for AQC100/107/108/109/111/112, aliases for AQC100S through AQC112S, `hw_atl_ops_b0`, `hw_atl_ops_b1` alias, and declarations for RSS/offload/ring/mac/flow-control/loopback/IRQ/filter/start helpers.

Control flow: PCI board matching selects these caps and ops for B0/B1 device IDs. Other hardware modules can call declared B0 helper functions when sharing behavior with later Atlantic variants.

State and persistence: no direct state; referenced caps and ops drive runtime hardware programming elsewhere.

Dependencies and integration: includes `aq_common`, and its prototypes reference `aq_hw_s`, `aq_ring_s`, `aq_ring_param_s`, `aq_rss_parameters`, and `aq_nic_cfg_s`.

Risks: aliases assume S variants share the same capabilities; exported helper prototypes must stay synchronized with implementation and any ATL2 reuse; ops aliasing means B1 behavior changes with B0 implementation. Test signals include link/load coverage for all B0/B1 IDs and compile coverage for helper users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0_internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0_internal.h

Purpose: defines B0-specific hardware constants for descriptors, filters, IRQs, buffers, RSS/TC, LRO/LSO, firmware semaphore, interrupt moderation, VLAN/L2 actions, and descriptor count limits.

Important APIs/types: constants include jumbo/default MTU, ring/descriptor sizes, unicast/multicast filter counts, interrupt masks, TX data/context descriptor masks, MPI registers, PTP buffer reservations, RSS hash/redirection sizes, TC/RSS maxima, LRO limits, LSO max segment sizes, chip revision IDs, RX writeback status bits, filter actions, moderation min/max, descriptor bounds, and RSS mode encodings.

Control flow: `hw_atl_b0.c` uses these constants to build caps, program QoS and PTP TC buffers, pack GSO/VLAN TX descriptors, parse RX checksum/VLAN/LRO status, configure filters, choose RSS mode, and program interrupt moderation.

State and persistence: no runtime state; constants encode the B0 register/descriptor ABI.

Dependencies and integration: includes `aq_common`; private to B0 hardware implementation and any closely related helper reuse.

Risks: descriptor masks are tightly coupled to hardware layout; PTP buffer sizes reduce regular TC buffer budget; LSO/LRO limits must match netdev feature exposure; RSS mode constants must match TC mode decisions in `aq_nic_cfg_update_num_vecs`. Test signals include maximum MTU/descriptor tests, LSO boundary tests, LRO chains, PTP ring operation, RSS distribution for 4TC/8TC modes, and filter-slot exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0_internal.h -->
