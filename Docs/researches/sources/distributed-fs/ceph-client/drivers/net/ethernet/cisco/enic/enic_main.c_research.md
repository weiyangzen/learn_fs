<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_main.c

## Purpose

`enic_main.c` is the main Cisco VIC Ethernet PCI/netdev driver. It handles PCI probe/remove, vNIC registration/open/init, resource sizing, interrupt mode selection, NAPI, TX/RX completion polling, page-pool-backed RX setup, TX offloads, RSS, VXLAN offloads, address filtering, VLAN callbacks, SR-IOV/port-profile hooks, reset/hang recovery, MTU/link notification, and netdev operation registration.

## Important APIs, Types, and Functions

The file registers `enic_driver` with PCI IDs for VIC ENET PF, dynamic vNIC, and VF devices. Interrupt handlers are `enic_isr_legacy`, `enic_isr_msi`, `enic_isr_msix`, `enic_isr_msix_err`, and `enic_isr_msix_notify`; NAPI pollers are `enic_poll`, `enic_poll_msix_rq`, and `enic_poll_msix_wq`.

TX helpers include `enic_hard_start_xmit`, `enic_queue_wq_skb`, VLAN/checksum/TSO/encap queueing variants, and checksum preload helpers. Runtime lifecycle functions include `enic_open`, `enic_stop`, `_enic_change_mtu`, `enic_change_mtu_work`, `enic_reset`, `enic_tx_hang_reset`, `enic_dev_init`, `enic_dev_deinit`, `enic_probe`, and `enic_remove`. Feature/control helpers cover VXLAN UDP tunnel configuration, features check, link/MTU/message notification, adaptive interrupt moderation, RSS key/CPU/NIC config, interrupt request/free/synchronize, resource adjustment, address filters, SR-IOV VF MAC/port operations, and queue stats.

## Control Flow

PCI probe allocates a multiqueue netdev, enables PCI memory, requests regions, sets DMA mask to 47-bit or 32-bit, maps BARs, registers the vNIC, initializes devcmd, optionally enables SR-IOV and allocates port profiles, opens the vNIC, initializes locks, configures ingress VLAN rewrite, optionally initializes firmware for non-dynamic vNICs, allocates ENIC/vNIC resources, configures RSS/NIC settings, attaches NAPI, initializes timers/work, sets MAC/coalescing/features/MTU, and registers the netdev.

Open requests interrupts and affinity hints, sets notification delivery, creates one page pool per RQ, enables and fills RQs, enables WQs, adds station address for non-dynamic PFs, programs RX mode, wakes TX queues, enables NAPI, enables the device, unmasks interrupts, and starts notification/RFS timers. Stop masks and synchronizes interrupts, deletes timers and RFS filters, disables the vNIC, disables NAPI and queues, removes station address, disables/cleans WQ/RQ/CQ/intr resources, destroys page pools, unsets notification, and frees IRQs.

TX selects WQ by skb queue mapping, linearizes overly fragmented non-TSO SKBs, checks descriptor availability, maps SKB head/frags, writes descriptors for TSO, checksum, VLAN, VXLAN encapsulation, or plain VLAN mode, timestamps, doorbells unless batching, and stops the netdev queue near low descriptor thresholds. Completion polling reclaims WQ descriptors through helper code and returns interrupt credits.

RX NAPI services CQ entries through `enic_rq_cq_service`, returns credits, refills RQs via page-pool allocation, optionally recalculates adaptive coalescing, and unmasks interrupts on completion. Error interrupts log queue errors and schedule reset work; TX timeout schedules hang reset.

## State and Persistence Behavior

Device state lives in `struct enic` for the PCI device lifetime. Queue resources, NAPI, interrupt arrays, RSS key, port-profile records, coalescing settings, VXLAN port, address counts, and work/timer state are in memory. Firmware/vNIC state is reinitialized by probe, open, reset, and hang-reset flows. Dynamic vNICs can be provisioned later through port-profile operations. There is no disk persistence.

## Dependencies and Integration Points

The driver depends on PCI, DMA mapping, vNIC firmware command/resource helpers, NAPI, page pool, ethtool, netdev queues/stat ops, VXLAN UDP tunnel APIs, RFS acceleration when enabled, SR-IOV when enabled, rtnetlink, and helper modules from the ENIC object. It integrates with firmware for device open/init/enable/reset, RSS, filters, VLAN rewrite, overlay offload, and notifications.

## Risks and Edge Cases

The highest-risk areas are reset/open/stop ordering, devcmd locking around external API users, TX DMA mapping rollback, page-pool allocation failure during open/refill, interrupt-mode resource arithmetic, and SR-IOV/port-profile state transitions. `enic_probe` enables SR-IOV before several later init steps, so later failures must disable it correctly. `enic_remove` cancels reset and MTU work but not `tx_hang_reset` explicitly, which is worth checking against unregister/stop serialization. Dynamic and VF MAC validation permits zero addresses, so address-list behavior differs by device type. VXLAN offload supports only one UDP port and feature checks must disable offloads for unsupported inner/outer protocol combinations.

## Test Signals

Validate PCI probe/remove, DMA mask fallback, BAR mapping failures, MSI-X/MSI/INTx modes, queue count/resource constraints, open/stop cycles, RX page-pool refill failures, TX SG/checksum/TSO/TSO6/VLAN/VXLAN traffic, TX timeout and queue-error reset, link/MTU notification, SR-IOV enable/disable and VF MAC/port-profile ops, RFS steering, ethtool ring/coalescing/RSS changes, kdump minimal-resource mode, and module unload with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_main.c -->
