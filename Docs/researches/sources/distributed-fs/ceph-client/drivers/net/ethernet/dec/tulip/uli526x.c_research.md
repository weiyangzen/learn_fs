<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/uli526x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/uli526x.c

Purpose: Standalone PCI Fast Ethernet driver for ULi M5261/M5263 Tulip-like controllers. It does not use `struct tulip_private`; it implements its own descriptor rings, PHY access, media timer, interrupt handler, and PM callbacks.

Important APIs and functions: `uli526x_init_one()` enables PCI, allocates coherent descriptor and TX buffer pools, maps I/O, reads SROM or ID-table MAC address, selects CR9 or CR10 PHY operations, and registers the netdev. `uli526x_open()` initializes hardware, requests IRQ, starts queue, and arms a one-second timer. `uli526x_init()` resets MAC, discovers PHY, resets PHY, programs media, initializes descriptors, sends a setup frame, and enables interrupts/RX/TX. `uli526x_start_xmit()` copies skb data into preallocated TX buffers. `uli526x_interrupt()` handles RX, TX completion, and bus errors. Timer logic handles dynamic reset, TX kick/timeout, link state, and speed/duplex sensing.

Control flow: Probe sets static device resources. Open resets and starts hardware. TX packets are copied into descriptor-owned buffers, then DCR1 is kicked. Interrupts drain RX and TX descriptors while holding `db->lock`. The periodic timer may reset and reinitialize the NIC on CR8 anomalies or TX timeout, and updates carrier state based on PHY registers.

State and persistence: `struct uli526x_board_info` stores I/O base, PCI device, CR register shadows, descriptor pool pointers and DMA addresses, ring cursors, TX/RX counters, media state, PHY ops/address, reset counters, SROM cache, and timer. Module parameters `debug`, `mode`, and `cr6set` set globals used at open/init. No persistent writes.

Dependencies and integration: Uses Linux PCI, netdevice, ethtool, DMA, timers, spinlocks, SROM bit-banging, and MII-like PHY access. PCI IDs bind vendor 0x10B9 devices 0x5261 and 0x5263.

Risks: TX copies into fixed `TX_BUF_ALLOC` buffers and rejects frames over 1514 bytes, so VLAN/jumbo handling is limited. RX DMA unmap/free paths use hand-managed descriptor state. `phy_readby_cr10()` busy-waits without an explicit timeout. Dynamic reset runs from timer under lock and reinitializes rings.

Test signals: Probe both 5261 and 5263 PHY-access paths, absent SROM fallback, forced and auto media modes, link up/down timer messages, TX timeout reset, RX allocation failures, multicast setup frame generation, suspend/resume, and netpoll builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/uli526x.c -->
