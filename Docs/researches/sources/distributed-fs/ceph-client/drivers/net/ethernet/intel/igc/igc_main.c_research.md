# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_main.c

## Purpose

`igc_main.c` is the main Linux PCI Ethernet driver body for Intel I225/I226-class 2.5G controllers. It binds PCI IDs to the `igc` driver, allocates and registers the `net_device`, owns the `net_device_ops`, and coordinates the controller lifecycle from probe through open, traffic, reset, power management, PCI error recovery, and remove. It is also the central integration point for queue resources, DMA descriptor rings, NAPI, MSI/MSI-X/legacy interrupts, XDP and AF_XDP zero-copy, PTP timestamp delivery, traffic-control/TSN offloads, wake-on-LAN, filtering, statistics, and hardware register access.

## Important APIs, Types, and Functions

The exported or externally used driver entry points include `igc_open`, `igc_close`, `igc_reset`, `igc_up`, `igc_down`, `igc_reinit_locked`, `igc_update_stats`, `igc_has_link`, `igc_reinit_queues`, `igc_get_hw_dev`, `igc_rd32`, `igc_setup_tx_resources`, `igc_setup_rx_resources`, `igc_free_tx_resources`, `igc_free_rx_resources`, `igc_flush_tx_descriptors`, `igc_get_tx_ring`, `igc_add_nfc_rule`, `igc_del_nfc_rule`, `igc_enable_empty_addr_recv`, `igc_disable_empty_addr_recv`, and the ring enable/disable helpers. The file registers `igc_netdev_ops`, `igc_driver`, `igc_err_handler`, and PM ops, then wires them into `module_init`/`module_exit`.

Core state is carried by `struct igc_adapter`, `struct igc_hw`, `struct igc_ring`, `struct igc_q_vector`, `struct igc_tx_buffer`, `struct igc_rx_buffer`, `struct igc_nfc_rule`, `struct igc_flex_filter`, `struct igc_metadata_request`, and timestamp/TSN state embedded in the adapter and rings. The file relies heavily on descriptor unions such as `union igc_adv_tx_desc` and `union igc_adv_rx_desc`, hardware register macros from the igc headers, and state bits such as `__IGC_DOWN`, `__IGC_RESETTING`, and `__IGC_TESTING`.

Major functional groups are probe/lifetime, netdev lifecycle, queue resources, Tx/Rx hot paths, interrupt/NAPI handling, filtering, TSN traffic-control offloads, XDP/AF_XDP, PM, and PCI error recovery.

## Control Flow

Module load calls `pci_register_driver`, allowing PCI probe to match one of the IGC/I225/I226 IDs. `igc_probe` enables PCI memory access, configures DMA, requests BARs, optionally enables PTM, allocates a multiqueue Ethernet device, maps MMIO, copies MAC/PHY ops from board info, obtains hardware invariants, assigns netdev features, initializes software queues and interrupts, resets hardware, validates NVM if flash is present, reads or accepts the MAC address, initializes timers/work items/PTP/TSN/FPE, resets again, claims hardware control from firmware, and registers the netdev.

Interface open flows through `igc_open` into `__igc_open`: set real queue counts, runtime-PM resume, allocate Tx and Rx descriptor resources, power up and set up the copper link, configure hardware registers and rings, request interrupts, enable NAPI, enable interrupts, start Tx queues, and schedule the watchdog. Close and down paths stop traffic, disable hardware and interrupts, synchronize NAPI, snapshot stats, reset hardware when possible, clean rings, free IRQs, release firmware control, and free descriptor resources.

The Tx path selects a ring, reserves descriptors, handles TSN launch-time context, hardware timestamp requests, VLAN flags, preemption padding, TSO/checksum context descriptors, DMA mapping, descriptor tail writes, and queue stop/wake logic. Completion walks `next_to_watch` descriptors, frees SKBs/XDP/XSK resources, accounts stats, detects hangs, and wakes queues. The Rx path is NAPI-driven, reads completed descriptors, syncs DMA pages, handles inline timestamps and FPE mPackets, runs XDP, builds SKBs, applies checksum/hash/VLAN metadata, sends to GRO, recycles pages, replenishes descriptors, and finalizes XDP TX/redirect. AF_XDP zero-copy uses parallel Rx/Tx paths around `xsk_buff` pools.

The watchdog handles link transitions, stats, Tx hang detection, Rx allocation failure wakeups, and PTP Tx hang checks. Traffic-control setup routes taprio/ETF/CBS/MQPRIO into TSN state and applies offloads. Suspend/resume and PCI recovery close, reset, wake-configure, restore, and reopen the device as needed.

## State and Persistence Behavior

Persistent hardware state includes PCI config, MMIO registers, descriptor base/tail/head registers, receive address registers, multicast table, wake filters, PTP/TSN registers, NVM-derived MAC address, and PHY state. Runtime state lives in the adapter and rings: descriptor memory, DMA addresses, `next_to_use/clean/alloc`, NAPI vectors, interrupt masks, per-ring flags, XDP program pointer, AF_XDP pools, timestamp request slots, NFC rule list, stats counters, TSN schedule fields, timers, and work items.

The driver uses `wmb`, `dma_rmb`, and `smp_rmb` around descriptor ownership; `u64_stats_sync` for per-ring stats; spinlocks for PTP timestamp and Qbv transition state; a mutex for NFC rules; RCU for q_vector freeing and XDP program reads; RTNL around reset/recovery; and adapter state bits for down/reset/test coordination. The file does not persist configuration to disk. Runtime configuration is replayed into hardware after reset from adapter state.

## Dependencies and Integration Points

This file depends on Linux PCI, DMA mapping, netdevice, NAPI, GRO, skb, XDP, AF_XDP, BPF, PTP, ethtool, traffic-control, runtime PM, hrtimer, timers/workqueues, and MDIO infrastructure. Internal dependencies include `igc.h`, `igc_hw.h`, `igc_tsn.h`, `igc_xdp.h`, MAC/base/PHY/NVM/PTP/TSN/FPE/LED/ethtool modules, and `hw->mac.ops`/`hw->phy.ops`.

External integration surfaces include PCI driver callbacks, `net_device_ops`, ethtool ops, XDP metadata callbacks, AF_XDP metadata callbacks, TC offload callbacks, PM callbacks, PCI error handlers, wake-on-LAN, kernel stats, and MMIO/coherent DMA hardware interfaces.

## Risks and Edge Cases

Descriptor ownership is the highest-risk area: barriers, DMA unmapping, `next_to_*` accounting, XDP frame lifetime, and AF_XDP completion/timestamp timing can cause corruption, leaks, stalls, or hangs. Reset/open/close paths are concurrency-sensitive because watchdog work, interrupts, runtime PM, PCI recovery, TC changes, XDP setup, MTU changes, and feature changes can overlap. Filter programming can partially modify hardware before later rule setup fails. TSN/Qbv behavior depends on PTP time, per-ring gate state, hardware generation differences, and lock-protected transitions. Power management and wake paths can regress WoL, runtime suspend, wake packet delivery, or firmware ownership.

## Test Signals

Useful validation includes kernel build, modprobe/probe on I225/I226 hardware, link up/down, MTU changes, throughput and checksum/TSO/GSO tests, VLAN/RSS/multicast/promiscuous tests, ethtool stats, PTP timestamp tests, suspend/resume/runtime PM, wake-on-LAN, PCI error injection, and hot-unplug/MMIO-failure tests. XDP tests should cover program attach/detach, PASS/DROP/TX/REDIRECT, `ndo_xdp_xmit`, AF_XDP zero-copy, need-wakeup, XDP metadata hash/timestamp, and XSK Tx metadata timestamp/launch-time. TSN tests should cover taprio/ETF/CBS/MQPRIO setup, invalid schedule rejection, closed-gate/max-SDU drops, launch-time cycle boundaries, FPE, and queue reinit.
