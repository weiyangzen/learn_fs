# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tehuti.c

## Purpose
This is the legacy Tehuti 10G PCI ethernet driver for devices `0x3009`, `0x3010`, and `0x3014`. It implements PCI probe/remove, netdev open/stop/transmit, NAPI interrupt handling, firmware loading through the TX descriptor FIFO, RX/TX FIFO allocation, VLAN/multicast/MAC programming, private register ioctl access, and ethtool support for link, coalescing, ring sizing, and hardware statistics.

## Important APIs, Types, and Functions
The driver registers `bdx_pci_driver` with `bdx_probe` and `bdx_remove`; module init calls `init_txd_sizes` before `pci_register_driver`. Netdev operations are `bdx_open`, `bdx_close`, `bdx_tx_transmit`, `bdx_setmulti`, `bdx_change_mtu`, `bdx_set_mac`, VLAN add/kill, and `bdx_siocdevprivate`. NAPI/IRQ flow is handled by `bdx_isr_napi`, `bdx_poll`, `bdx_rx_receive`, and `bdx_tx_cleanup`. Resource helpers include `bdx_fifo_init/free`, `bdx_tx_init/free`, `bdx_rx_init/free`, `bdx_fw_load`, reset helpers, and TX/RX database functions. Ettool is installed by `bdx_set_ethtool_ops`.

## Control Flow and State
Probe enables PCI, sets a 64-bit DMA mask, maps BAR0, detects one or two ports, allocates one netdev per port, initializes `struct bdx_priv`, reads the MAC address, registers netdev, and leaves carrier/queue stopped. Open resets hardware, creates TX/RX FIFOs and databases, loads firmware `tehuti/bdx.bin`, primes RX buffers, requests the IRQ, enables interrupts, then enables NAPI. Interrupts read `regISR`, schedule NAPI for RX descriptors/TX frees, and process link/error conditions immediately. Poll reclaims TX descriptors, receives packets up to budget, completes NAPI, and reenables interrupts. Close disables NAPI, resets/stops hardware, frees IRQ, and tears down RX/TX DMA resources.

## State and Persistence Behavior
Persistent runtime state is in `struct bdx_priv`: mapped registers, NAPI object, RXD/RXF and TXD/TXF FIFOs, RX skb database, TX DMA/skb circular database, cached FIFO sizes, coalescing register values, stats, port number, and NIC-wide pointer. TX ownership is tracked by `txdb` entries followed by a negative descriptor-size sentinel and skb pointer. RX ownership is tracked by `rxdb` stack entries holding skb DMA mappings. Hardware-visible state is in DMA-coherent FIFO memory and MMIO read/write pointers. Firmware initialization uses `regINIT_SEMAPHORE` so only one function loads firmware for multi-port hardware.

## Dependencies and Integration Points
The file depends on `tehuti.h` register definitions, Linux PCI, netdevice, NAPI, DMA mapping, firmware loader, ethtool, VLAN, and user-copy APIs. It integrates with the network stack through `net_device_ops`, ethtool, `netif_receive_skb`, checksum/VLAN offload flags, and carrier/queue APIs. It exposes a privileged private ioctl path for raw register reads/writes guarded by `CAP_SYS_RAWIO`.

## Risks and Test Signals
High-risk areas include DMA mapping error handling gaps in TX/RX, private register ioctl safety, FIFO wrap copying, descriptor length parsing, reset ordering, IRQ/NAPI races, firmware load timeouts, and multi-port cleanup on partial probe failures. `BDX_ASSERT` is `BUG_ON`, so invariant failures are fatal. Test signals include PCI probe/remove, ifup/ifdown loops, firmware missing/failing paths, high-rate RX/TX with VLAN/TSO/checksum offloads, multicast/promiscuous transitions, ethtool coalesce/ring updates while up, private ioctl permission checks, and two-port adapter cleanup.
