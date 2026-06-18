<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/cassini.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/cassini.c

## Purpose

`cassini.c` is the Linux PCI Ethernet driver for Sun Cassini, Cassini+, and National Semiconductor Saturn gigabit adapters. It binds PCI devices, maps the MMIO register file, initializes the MAC, MII/GMII/PCS link layer, DMA descriptor rings, interrupt handling, NAPI receive polling, ethtool/MII control surfaces, suspend/resume, and teardown. The driver is centered on page-based RX buffers with separate completion rings and four TX rings used as round-robin load-balancing queues.

## Important APIs, Types, And Functions

The exported integration surfaces are `cas_driver` (`struct pci_driver`), `cas_netdev_ops`, `cas_ethtool_ops`, and module parameters `cassini_debug`, `link_mode`, and `linkdown_timeout`. Probe/remove enter through `cas_init_one()` and `cas_remove_one()`, while module init/exit register and unregister the PCI driver.

The main runtime state is `struct cas` from `cassini.h`: it stores the PCI/net devices, MMIO base, coherent init block DMA address, TX/RX descriptor pointers, page pools, ring cursors, stats, link state, firmware bytes, timers, work item, locks, and PM mutex. Descriptor-facing types include `struct cas_init_block`, `struct cas_tx_desc`, `struct cas_rx_desc`, `struct cas_rx_comp`, `cas_page_t`, and `struct cas_tiny_count`. Link state is tracked with `enum link_state` plus `link_transition` fields.

Core hardware setup functions are `cas_check_pci_invariants()`, `cas_check_invariants()`, `cas_reset()`, `cas_global_reset()`, `cas_init_hw()`, `cas_init_mac()`, `cas_init_dma()`, `cas_init_tx_dma()`, `cas_init_rx_dma()`, `cas_phy_init()`, and `cas_begin_auto_negotiation()`. Data path functions are `cas_start_xmit()`, `cas_xmit_tx_ringN()`, `cas_tx()`, `cas_tx_ringN()`, `cas_rx_ringN()`, `cas_rx_process_pkt()`, `cas_post_page()`, `cas_post_rxds_ringN()`, and `cas_post_rxcs_ringN()`. Fault and recovery paths are driven by `cas_interrupt()`, optional alternate interrupt handlers, `cas_poll()`, `cas_abnormal_irq()`, `cas_tx_timeout()`, `cas_reset_task()`, and `cas_link_timer()`.

## Control Flow

Probe enables the PCI device, claims memory BARs, configures PCI command bits and DMA mask, allocates the netdev, maps registers, saves PCI state, hard-resets the chip, derives chip flags, reads VPD/OF/random MAC address and PHY information, optionally loads Saturn firmware from `sun/cassini.bin`, allocates the coherent init block, wires descriptor pointers, initializes queues and NAPI, sets features and MTU bounds, registers the netdev, then starts PHY autonegotiation.

Opening the interface ensures hardware is running, allocates per-ring tiny TX DMA buffers, allocates all RX pages, initializes spare/in-use RX page lists, requests the shared IRQ, enables NAPI, cleans rings, initializes MAC/DMA/link state, marks the device opened, and starts the netdev queue. Closing disables NAPI, stops the queue, resets hardware, restarts PHY autonegotiation while closed, cleans rings, frees IRQs, RX pages, spare pages, and tiny buffers.

TX flow pads short frames, chooses one of four rings with a static round-robin hint, checks descriptor availability, maps the skb head and fragments, programs checksum offload fields for `CHECKSUM_PARTIAL`, applies the old-Cassini target-abort workaround by copying trailing bytes into coherent tiny buffers when needed, writes descriptors, updates the producer index, possibly stops the queue, and kicks the hardware. TX interrupts or NAPI poll read completion writeback state and call `cas_tx_ringN()` to unmap DMA segments, clear tiny-buffer bookkeeping, update per-ring stats, free skbs, and wake the queue when enough descriptors are available.

RX flow consumes completion descriptors until hardware ownership or budget stops it. `cas_rx_process_pkt()` decodes header/data/next page indices, allocates an skb, copies at least the required header bytes, attaches page fragments for larger payloads, handles split packets, strips FCS from checksum accounting when the MAC leaves it in place, sets protocol and checksum metadata, and returns the packet length. `cas_rx_ringN()` releases or batches packets by hardware flow id, updates stats, reposts descriptor pages indicated by completion release bits, and advances the completion cursor. Completion-ring space is returned by zeroing consumed descriptors and writing the hardware tail.

Interrupts first handle TX and RX-done fast paths, then housekeeping. Abnormal interrupts cover RX tag/length errors, PCS/MIF link events, TX/RX MAC counter rollover or errors, MAC pause state, and PCI errors. Serious conditions schedule `reset_task`; NAPI masks interrupts, polls RX across completion rings, then completes and unmasks when budget permits.

## State And Persistence Behavior

Persistent driver state lives in `struct cas` for the lifetime of the netdev. `pm_mutex` serializes open, close, ioctl, suspend, and resume. `cp->lock` protects most hardware and link state, individual `tx_lock[]` locks protect TX rings, `stat_lock[]` protects stats, and spare/in-use RX page lists have dedicated locks. Reset requests are accumulated in atomics for all-reset, MTU-reset, and spare-page recovery, with `reset_task_pending` used to gate shutdown.

RX buffers are page allocations mapped for DMA and tracked as `cas_page_t`. The driver keeps one ring of active pages and another used as a spare source, using page reference counts to decide whether an skb fragment still owns a page. Pages still referenced by the network stack move to `rx_inuse_list`; spare recovery later recycles pages whose refcount returns to one or allocates replacements. This state is transient and rebuilt on open, MTU reset, full reset, or close.

Hardware-visible descriptor state is persistent while the device is open in the coherent `cas_init_block`. Ring cursors such as `tx_old`, `tx_new`, `rx_old`, `rx_new`, and `rx_cur` are software mirrors and are reset by `cas_clean_rings()`. Link state persists across many resets; full resets restart PHY autonegotiation, while block-preserving resets can keep PCS/SERDES state. Saturn firmware bytes persist in `cp->fw_data` from probe until remove.

Statistics are accumulated per TX/RX ring and periodically collapsed into `net_stats[N_TX_RINGS]` by `cas_get_stats()`, which also harvests and clears MAC hardware counters. No user configuration is persisted outside kernel memory; module parameters affect defaults only when the module/device is initialized.

## Dependencies And Integration Points

The driver depends on the Linux PCI, DMA mapping, netdevice, NAPI, skb fragment, ethtool, MII, firmware loader, timer, workqueue, PM, and optional Open Firmware APIs. Hardware register definitions, descriptor layouts, firmware-program tables, PHY IDs, and bitfield helpers come from `cassini.h`.

It integrates with the networking stack through `register_netdev()`, `ndo_open`, `ndo_stop`, `ndo_start_xmit`, `ndo_get_stats`, `ndo_set_rx_mode`, `ndo_eth_ioctl`, `ndo_tx_timeout`, `ndo_change_mtu`, address validation, optional netpoll, hardware checksum and scatter-gather feature flags, and carrier state updates. Ettool exposes driver info, link settings, nway reset, message level, selected registers, and private stats. MII ioctls expose PHY register reads/writes under the PM mutex.

Hardware integration includes PCI bridge tuning for Intel 31154 bridges, 64-bit coherent DMA, expansion ROM VPD parsing for MAC/PHY data, MIF MDIO PHY access, PCS/SERDES management, MAC address filters and multicast hash programming, RX pause thresholds, MAC counter clearing, PCI error interrogation, and a `sun/cassini.bin` firmware payload for NS DP83065/Saturn PHY workarounds.

## Risks

The RX page reuse model is sensitive to page reference counts, DMA sync ranges, and completion release bits; mistakes can produce data corruption, leaks, or page reuse while skb fragments are live. Spare recovery is asynchronous and can defer descriptor reposting through the link timer, so low-memory paths need careful validation.

Reset coordination is complex: interrupts, TX timeout, link timer, MTU changes, spare recovery, suspend/resume, and close all interact through atomics, workqueue state, timers, `hw_running`, and `opened`. Races here could leave interrupts unmasked, queues detached, reset work pending during shutdown, or DMA running against cleaned rings.

The TX target-abort workaround splits buffers near page boundaries and tracks tiny coherent buffers separately from normal DMA mappings. Off-by-one descriptor accounting or partial skb release handling can stall rings or unmap the wrong DMA segment. The driver also uses one netdev queue for four hardware TX rings, so queue stop/wake decisions are approximate.

Link handling has several hardware-specific paths: MII fallback from autonegotiation to forced modes, PCS state-machine checks, link-down reset throttling, Saturn firmware loading, Broadcom/Lucent PHY workarounds, half-duplex FCS retention for checksum correction, and gigabit half-duplex carrier extension. Regressions may only appear on particular PHY, chip revision, or forced-speed combinations.

Probe/error-unwind paths touch many resources: PCI cacheline changes, MWI, MMIO mappings, coherent init block, firmware buffer, registered netdev, timers, reset work, RX pages, tiny buffers, and IRQs. Failures after partial initialization must not leak resources or leave modified PCI bridge/cacheline state behind.

## Test Signals

Build with the target kernel configuration covering `CONFIG_NET_POLL_CONTROLLER`, `USE_NAPI`, SPARC OF MAC-address discovery, and firmware loading. Exercise probe/remove and all probe failure points with fault injection for PCI enable, BAR request, DMA mask, MMIO map, invariant check, coherent allocation, and `register_netdev()`.

For data path validation, run small packets, jumbo MTU, fragmented/skb SG TX, hardware checksum offload, non-IP RX checksum behavior, multicast/promiscuous/allmulti changes, descriptor-ring pressure, RX buffer exhaustion, and low-memory RX page allocation failures. Confirm TX descriptors are reclaimed, queue stop/wake recovers, RX pages are not leaked, and `ethtool -S` counters match traffic and error injection.

For recovery validation, trigger TX timeout, PCI error status, RX tag/length errors, MAC RX/TX errors, link flaps, forced-speed changes, MTU changes while running, suspend/resume while open and closed, netpoll polling, and close/remove while reset work or timers are pending. Confirm carrier state, IRQ masking, NAPI completion, DMA disable, work cancellation, and resource cleanup.

For link/PHY coverage, test MII copper and PCS/fiber paths, autonegotiation and forced 10/100/1000 modes, half-duplex FCS/checksum handling, Saturn DP83065 firmware present/missing/bogus-length cases, VPD MAC/PHY parsing, OF fallback, and random MAC fallback warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/cassini.c -->
