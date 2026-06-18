# sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/xgmac.c

## Purpose
This is a complete Linux platform `net_device` driver for the Calxeda Highbank 10G XGMAC block. It owns the MAC and DMA register programming, coherent descriptor rings, NAPI receive/transmit completion, multicast/unicast filtering, ethtool controls, hardware statistics, wake-on-LAN, suspend/resume, and OF platform binding for `calxeda,hb-xgmac`.

## Important APIs, Types, And Functions
Key local types are `struct xgmac_dma_desc`, `struct xgmac_extra_stats`, and `struct xgmac_priv`. The descriptor helpers initialize RX/TX rings, encode buffer lengths split across descriptor fields, manage ownership via `DESC_OWN`, and preserve end-of-ring flags. `xgmac_open()`, `xgmac_stop()`, `xgmac_xmit()`, `xgmac_poll()`, `xgmac_set_rx_mode()`, `xgmac_change_mtu()`, `xgmac_get_stats64()`, `xgmac_set_features()`, and `xgmac_set_mac_address()` form the `net_device_ops`. `xgmac_ethtool_ops` exposes link settings, pause parameters, stats strings, and wake-on-LAN configuration.

## Control Flow
`xgmac_probe()` claims the MMIO resource, allocates an Ethernet device, maps registers, detects the available perfect-address filters, requests the main and PMT IRQs, reads the initial MAC address, installs NAPI, and registers the netdev. `xgmac_open()` validates or randomizes the MAC address, resets and configures hardware, allocates DMA rings, fills RX descriptors with mapped SKBs, enables MAC/DMA, enables NAPI and queueing, and unmasks DMA interrupts. TX maps the skb head and fragments into consecutive descriptors, marks the first descriptor owned last to avoid DMA races, rings `XGMAC_DMA_TX_POLL`, and stops the queue when descriptor space is low. Interrupts acknowledge DMA status, collect abnormal-event counters, mask normal interrupts down to abnormal-only while NAPI runs, and schedule NAPI. NAPI reclaims completed TX descriptors, receives packets until budget, refills RX, completes NAPI, and restores the interrupt mask. TX timeout work disables NAPI and TX DMA, frees and reinitializes the TX ring, restarts DMA, and wakes the queue. Suspend disables interrupts and either arms PMT wake logic or fully disables MAC/DMA; resume clears PMT and re-enables DMA, interrupts, device attachment, and NAPI.

## State And Persistence
Runtime state is held in `xgmac_priv`: ring virtual/DMA addresses, SKB arrays, ring indices, flow-control flags, WOL options, IRQ numbers, NAPI, and software error counters. Hardware state is in XGMAC/DMA/MMC/PMT registers. No filesystem persistence is used. Statistics are partly hardware counters and partly in-memory software counters; `xgmac_get_stats64()` freezes MMC counters while reading. WOL choices persist only for the current driver lifetime and are applied to PMT registers during suspend.

## Dependencies And Integration Points
The driver integrates with the platform bus, OF match table, Linux netdev core, NAPI, ethtool, DMA mapping API, interrupt subsystem, PM sleep hooks, and netpoll when configured. It depends on MMIO accessors, coherent DMA, skbuff helpers, multicast/unicast address lists, and CRC32 hashing for hash filters.

## Risks
Risk centers on DMA ring correctness, ownership ordering, and descriptor-space accounting. RX assumes complete packets fit in one descriptor; fragmented RX descriptors are dropped. `xgmac_change_mtu()` stops and reopens the device in-place, so failures during reopen can leave the interface down. TX mapping failure cleanup must match exactly which fragments were mapped. Interrupt and NAPI ordering relies on barriers and mask writes. PMT wake enable toggles IRQ wake on `dev->irq` while the PMT interrupt is a separate IRQ, so platform wiring matters. The hardware init uses a fixed AXI bus magic value and no detailed feature negotiation beyond checksum support.

## Test Signals
Useful signals are successful platform probe and netdev registration; `ip link set up/down`; MTU changes up to 9000; TX/RX traffic with SG and checksum offload; multicast and unicast filter overflow into hash mode; NAPI interrupt rate under traffic; `ethtool -S`, pause parameter changes, RX checksum toggling, and WOL configuration; suspend/resume wake by magic or unicast; fault-injection for DMA mapping failure and TX timeout recovery.
