# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ksz884x.c

## Purpose

`ksz884x.c` is the PCI network driver for Micrel KSZ8841 and KSZ8842 Ethernet devices. KSZ8841 behaves as a single-port PCI Ethernet controller; KSZ8842 adds a two-port switch fabric and can expose either one Linux netdev spanning both physical ports or two separate netdevs in `multi_dev` mode. The file owns the full hardware lifecycle: PCI probe/remove, MMIO register programming, DMA descriptor rings, TX/RX data paths, switch tables, PHY/link management, MIB statistics, ethtool operations, EEPROM access, Wake-on-LAN, suspend/resume, and module parameters.

## Important APIs, Types, And Functions

The main state containers are `struct ksz_hw`, `struct dev_info`, and `struct dev_priv`. `struct ksz_hw` caches MMIO base, switch pointer, per-port link/MIB state, DMA descriptor rings, interrupt masks, MAC/multicast lists, feature flags, and hardware overrides. `struct dev_info` is the shared adapter state behind one PCI function: PCI device, descriptor memory, locks, tasklets, timers, WOL settings, and the active RX routine. `struct dev_priv` is per-netdev state: `struct ksz_port`, MII shim, media state, message level, and multicast/promiscuous reference state.

Hardware setup functions include `hw_init`, `hw_reset`, `hw_setup`, `hw_setup_intr`, `hw_set_desc_base`, `hw_enable`, and `hw_disable`. Switch-specific routines include `sw_setup`, `sw_enable`, table access helpers, STP/VLAN/priority setup, and per-port link control. Netdev operations include open/close, TX, timeout, MTU, RX mode, MAC address, ioctl, stats, and feature changes. PCI lifecycle is handled by `pcidev_init`, `pcidev_exit`, `pcidev_suspend`, and `pcidev_resume`.

## Control Flow

Probe enables the PCI device, validates DMA, maps BAR0, checks chip ID, allocates descriptor memory, initializes locks/timers/wait queues, reads or overrides MAC addresses, configures hardware/switch defaults, and registers one or two netdevs. Open prepares shared hardware on the first open, requests IRQ, installs tasklets, resets hardware, programs descriptors and filters, initializes RX buffers and MIB counters, enables DMA/interrupts, powers up ports, configures link, starts timers, and starts the queue.

TX starts in `netdev_tx`, which reserves descriptors under `hwlock`, handles small-packet and checksum-copy workarounds, maps skb data/fragments, releases descriptors to hardware, and starts DMA. Completion is interrupt-driven through `tx_proc_task`, `tx_done`, and `transmit_cleanup`. RX is tasklet-driven: `rx_proc_task` calls `dev_rcv_packets`, `port_rcv_packets`, or `dev_rcv_special`; `rx_proc` copies DMA data into a fresh skb, sets protocol/checksum state, updates stats, and passes the packet to `netif_rx`.

Close stops queue/timers, updates switch/STP state, decrements filter references, and on final close disables interrupts/DMA, kills tasklets, frees IRQ, cleans descriptors, and clears static switch entries. Suspend closes running devices and optionally arms WOL/PME; resume disables PME and reopens running devices.

## State And Persistence

Runtime state lives in `struct ksz_hw`, `struct dev_info`, descriptor rings, timers, tasklets, and per-netdev `struct dev_priv`. Hardware-persistent state includes MMIO registers, switch tables, PHY registers, WOL pattern registers, and EEPROM contents. Ettool EEPROM writes permanently modify AT93C46 data. WOL enable state is stored in memory and programmed during ethtool set and suspend.

## Dependencies And Integration Points

The driver integrates with Linux PCI, netdevice, DMA mapping, ethtool, MII, timers, tasklets, interrupts, and PM APIs. It exposes PCI IDs for KSZ8841/8842, standard netdev and ethtool interfaces, MII ioctls, module parameters (`message`, `macaddr`, `mac1addr`, `fast_aging`, `multi_dev`, `stp`), and optional switch multi-netdev behavior.

## Risks And Test Signals

Key risks are DMA ring ownership, missing DMA mapping error checks, TX timeout reset ordering, old-style tasklet/timer synchronization, multi-netdev constraints, permanent EEPROM writes, and WOL ARP using a hard-coded IP address. Test with hardware-in-loop: probe, open/close, TX/RX with SG/checksum offloads, forced TX timeout, multicast/promiscuous changes, MTU boundary changes, ethtool register/EEPROM/WOL/stats operations, suspend/resume, link changes, and multi-dev/STP bridge behavior.
