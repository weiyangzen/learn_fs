# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-velocity.c

## Purpose
This is the VIA Velocity Gigabit Ethernet driver for VT6110/Velocity-family adapters on PCI and OF/platform buses. It implements option parsing, PCI/platform probe, MAC/PHY setup, CAM and VLAN filters, DMA ring allocation, NAPI RX/TX service, checksum/VLAN offloads, interrupt coalescing, WOL, suspend/resume, and ethtool operations.

## Important APIs, types, and functions
The driver depends heavily on `via-velocity.h` for descriptors, registers, options, and `struct velocity_info`. Main lifecycle functions are `velocity_init_module`, `velocity_cleanup_module`, `velocity_pci_probe`, `velocity_platform_probe`, shared `velocity_probe`, `velocity_open`, `velocity_close`, `velocity_remove`, `velocity_suspend`, and `velocity_resume`.

Traffic functions include `velocity_xmit`, `velocity_intr`, `velocity_poll`, `velocity_rx_srv`, `velocity_receive_frame`, `velocity_tx_srv`, `velocity_error`, and ring helpers such as `velocity_init_rings`, `velocity_init_dma_rings`, `velocity_init_rd_ring`, `velocity_init_td_ring`, `velocity_rx_refill`, `velocity_give_many_rx_descs`, and `velocity_free_rings`. MAC/PHY helpers include CAM accessors, `velocity_init_registers`, `velocity_soft_reset`, `velocity_set_media_mode`, `mii_init`, `velocity_mii_read`, `velocity_mii_write`, `enable_mii_autopoll`, and flow-control setup.

Netdev ops expose open/stop/start_xmit/stats/set_rx_mode/change_mtu/ioctl/VLAN add-kill and optional netpoll. Ettool ops expose link settings, WOL, stats, coalescing, link state, driver info, and begin/complete hooks that power the device up for register access while closed.

## Control flow
Module init registers an IPv4 address notifier for ARP WOL support, then registers PCI and platform drivers. PCI probe enables the device, requests regions, and calls shared probe. Platform probe resolves OF match data and IRQ, then calls shared probe. Shared probe allocates netdev/private state, initializes chip metadata, validates bus resources, maps the MAC register window, resets WOL state, reads the hardware MAC address, parses per-adapter module options, captures PHY ID, installs netdev/ethtool/NAPI hooks, enables checksum/scatter-gather/VLAN features, registers the netdev, sets carrier state, stores drvdata, and powers the chip down to D3hot until opened.

Open allocates coherent RX/TX descriptor pools and skb metadata, powers the chip to D0, performs cold register initialization, requests IRQ, gives prepared RX descriptors to the NIC in multiples of four, enables interrupts, starts queueing, enables NAPI, and marks the interface opened. Cold register initialization resets the chip, optionally reloads EEPROM, restores the MAC address, configures DMA and RX thresholds, initializes CAM/VCAM filters, sets multicast mode, enables MII autopolling, programs interrupt suppression, writes RX/TX ring bases and sizes, starts queues, configures flow control, initializes PHY media, writes the interrupt mask, and clears ISR.

TX maps the skb linear data and up to six fragments, linearizing if the hardware segment limit would be exceeded. It programs one TX descriptor, sets VLAN and checksum request bits when applicable, marks ownership, advances ring indexes, stops the queue if no descriptors remain, sets `TD_QUEUE` on the previous descriptor, and wakes the TX queue. TX service runs from NAPI, scans completed descriptors, updates stats or error counters, unmaps DMA, frees skbs, advances tail pointers, and wakes the netdev queue when descriptors are available.

RX service scans descriptors until budget, ownership, or missing skb stops it. For valid frames it synchronizes DMA, validates error bits, applies RX checksum status, copies small packets below `rx_copybreak` or consumes the DMA skb directly, optionally realigns the IP header, removes CRC length, restores hardware VLAN tags, passes the skb to the stack, updates stats, refills buffers, and returns descriptors to the NIC in hardware-required groups of four.

Interrupt handling locks, reads and acknowledges ISR, disables interrupts and schedules NAPI for packet events, and processes non-packet error/link/MIB events through `velocity_error`. MTU changes allocate a temporary complete ring set before swapping under lock, minimizing downtime and preserving old rings until the new setup succeeds.

## State and persistence behavior
Per-device state lives in `struct velocity_info`. RX/TX rings and buffers are allocated on open and freed on close. Module options are copied into `vptr->options` during probe and then used for register programming. Hardware MIB counters are read-and-accumulated into `mib_counter`. WOL settings, password, and cached IPv4 address are retained in memory and programmed during suspend. Suspend saves selected MAC register context, shuts the device down, optionally programs WOL, and enters D3hot; resume restores context and reinitializes the MAC in WOL-resume mode.

## Dependencies and integration points
The driver integrates with PCI, platform/OF address and IRQ parsing, DMA mapping, netdev/NAPI, ethtool, MII, VLAN acceleration, CRC32 and CRC-CCITT, IPv4 address notifications, PM sleep, and optional netpoll. It uses the header's register structure and macros for all hardware access. Platform devices can set `no-eeprom` to skip EEPROM reload.

## Risks and edge cases
The code is register- and revision-sensitive. RX descriptors must be returned in multiples of four, RX buffers require 64-byte alignment, and TX supports at most seven segments. There are limited DMA mapping error checks in the TX fragment path compared with modern patterns. WOL ARP setup uses a static local buffer and single cached IPv4 address, so multi-IP and concurrency scenarios deserve care. Ettool begin/complete use a nesting counter to power-manage closed devices; imbalance would leave the device in the wrong power state. Suspend only acts when netdev is running, while probe powers the chip down when closed. Register context save/restore is partial by design.

## Test signals
Build both PCI and platform variants. Runtime tests should cover open/close, high-throughput RX/TX, scatter-gather with more than six frags, checksum offload, VLAN TX/RX/filtering, jumbo MTU up to 9000, MTU changes while up, multicast/promiscuous modes, link setting changes, interrupt coalescing get/set, MIB overflow/stat reporting, WOL magic/unicast/ARP suspend-resume, ethtool access while down, and platform `no-eeprom` probing.
