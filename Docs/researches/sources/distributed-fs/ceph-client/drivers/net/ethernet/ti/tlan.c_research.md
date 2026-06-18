# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/tlan.c

## Purpose
`tlan.c` is the Linux netdevice driver for legacy Texas Instruments ThunderLAN-based Ethernet adapters, including Compaq Netelligent/NetFlex PCI and EISA devices and selected Olicom boards. It discovers PCI and EISA devices, allocates descriptor rings, reads MAC addresses from serial EEPROM, drives the ThunderLAN host/DIO/MII/EEPROM register interfaces, manages PHY reset/autonegotiation/link monitoring, handles interrupts, transmits and receives frames, exposes MII ioctls and basic ethtool EEPROM access, and supports suspend/resume.

The file is a complete classic Ethernet driver with custom DMA descriptor rings rather than a phylib-driven modern design.

## Important APIs, Types, And Functions
Module parameters are `aui[]`, `duplex[]`, `speed[]`, and `debug`. These select per-board media behavior and debug masks. `board_info[]` describes supported board labels, adapter flags, and EEPROM MAC offsets. `tlan_pci_tbl[]` maps PCI IDs to `board_info` entries.

The main private state type is `struct tlan_priv` from `tlan.h`. It stores PCI/netdev pointers, coherent descriptor storage, RX/TX ring pointers and DMA addresses, ring indexes, PHY state, timers, adapter metadata, media settings, selected PHY addresses, spinlock, and timeout work item.

Driver lifecycle functions are `tlan_probe()`, `tlan_init_one()`, `tlan_probe1()`, `tlan_remove_one()`, `tlan_eisa_probe()`, `tlan_eisa_cleanup()`, and `tlan_exit()`. Netdevice operations are `tlan_open()`, `tlan_close()`, `tlan_start_tx()`, `tlan_tx_timeout()`, `tlan_get_stats()`, `tlan_set_multicast_list()`, and `tlan_ioctl()`. Optional netpoll uses `tlan_poll()`.

Interrupt handling uses `tlan_handle_interrupt()` plus the `tlan_int_vector[]` table, dispatching to `tlan_handle_tx_eof()`, `tlan_handle_stat_overflow()`, `tlan_handle_rx_eof()`, `tlan_handle_dummy()`, `tlan_handle_tx_eoc()`, `tlan_handle_status_check()`, and `tlan_handle_rx_eoc()`.

Hardware setup and ring helpers include `tlan_init()`, `tlan_start()`, `tlan_stop()`, `tlan_reset_lists()`, `tlan_free_lists()`, `tlan_read_and_clear_stats()`, `tlan_reset_adapter()`, `tlan_finish_reset()`, and `tlan_set_mac()`.

PHY, MII, and EEPROM routines include `tlan_phy_detect()`, `tlan_phy_power_down()`, `tlan_phy_power_up()`, `tlan_phy_reset()`, `tlan_phy_start_link()`, `tlan_phy_finish_auto_neg()`, `tlan_phy_monitor()`, `__tlan_mii_read_reg()`, `tlan_mii_read_reg()`, `__tlan_mii_write_reg()`, `tlan_mii_write_reg()`, `tlan_mii_send_data()`, `tlan_mii_sync()`, `tlan_ee_send_start()`, `tlan_ee_send_byte()`, `tlan_ee_receive_byte()`, and `tlan_ee_read_byte()`.

## Control Flow
Module initialization registers the PCI driver and then scans EISA slots. If no PCI or EISA devices were installed, it unregisters the PCI driver and returns `-ENODEV`. EISA probing checks slot IDs, enable state, IRQ encoding, reserves the I/O region, and calls the shared `tlan_probe1()` path.

`tlan_probe1()` enables PCI and reserves I/O resources when `pdev` is present, allocates an Ethernet netdev, selects board metadata from PCI driver data or EISA ID, sets DMA mask, finds an I/O BAR for PCI, records IRQ/base/revision, applies module or legacy `mem_start` media parameters, initializes timeout work and the spinlock, calls `tlan_init()`, and registers the netdev. EISA devices are linked onto `tlan_eisa_devices` for manual cleanup.

`tlan_init()` allocates one coherent DMA block for RX and TX `struct tlan_list` descriptors, aligns the RX list to 8 bytes, places TX descriptors immediately after RX descriptors, reads six MAC bytes from EEPROM at the board-specific offset, swaps bytes for Olicom boards using offset `0xf8`, assigns the hardware address, turns carrier off, installs netdev and ethtool ops, and sets the watchdog timeout.

Opening the device requests the shared IRQ, initializes the primary timer and media timer, reads the ThunderLAN revision, and calls `tlan_start()`. `tlan_start()` resets descriptor lists, clears stats, resets the adapter, and wakes the queue. Closing calls `tlan_stop()`, frees the IRQ, and frees all SKBs/DMA mappings in the rings.

Transmit starts in `tlan_start_tx()`. If the PHY is not online, the skb is dropped as successfully consumed. Otherwise the skb is padded to minimum Ethernet size, mapped for DMA, stored in the next TX descriptor, and the descriptor is marked ready under `priv->lock`. If TX is idle, the driver writes the descriptor DMA address to `TLAN_CH_PARM` and issues `TLAN_HC_GO`; otherwise it links the previous descriptor's `forward` pointer. The skb pointer is hidden in descriptor buffer slots 8 and 9 by `tlan_store_skb()`.

Interrupt handling reads `TLAN_HOST_INT`, extracts the interrupt type, acknowledges the host interrupt register, calls the vector handler, and writes an ACK command when the handler returns nonzero bits. TX EOF processing walks completed descriptors, unmaps and frees SKBs, updates byte stats, marks descriptors unused, restarts queued TX if an end-of-channel occurred, and pulses the activity LED. RX EOF processing walks completed RX descriptors, allocates replacement SKBs, unmaps and delivers received SKBs through `netif_rx()`, remaps replacements, appends descriptors back to the ring, restarts RX on EOC, and pulses the activity LED.

Status-check interrupts handle two different paths. Adapter-check interrupts stop the queue, log the adapter error from `TLAN_CH_PARM`, clear stats, issue adapter reset, schedule timeout work, and suppress normal ACK. Network status checks clear DIO status bits and, for internal PHY interrupts, adjust polarity swap in `TLAN_TLPHY_CTL` when needed.

Reset and link bring-up are timer-driven. `tlan_reset_adapter()` asserts adapter reset, disables interrupts, clears address/hash registers, configures NetConfig, loads timers/thresholds, unresets MII, disables TX/RX EOC interrupts on newer chips, detects PHYs, selects bit-rate/AUI/full-duplex behavior, powers down managed PHYs, or finishes reset immediately for unmanaged PHYs. Timers then sequence PHY power-up, PHY reset, link start, autonegotiation finish, and final reset completion.

`tlan_finish_reset()` enables NET_CMD/NET_MASK/MAX_RX, reads PHY IDs/status, reports link details for National Semiconductor PHYs, enables internal PHY interrupts, programs AREG0 with the netdev MAC, enables host interrupts, starts the RX channel with `TLAN_HC_GO | TLAN_HC_RT`, sets link LED/carrier, and applies multicast filters. If link is inactive it retries after ten seconds.

## State And Persistence Behavior
Persistent host-visible configuration is limited to module parameters and netdevice settings. Runtime state lives in `struct tlan_priv`: descriptor rings, ring heads/tails, DMA addresses, PHY selection, media choices, timers, carrier state, and stats. Hardware state is programmed into I/O port registers, DIO internal registers, MII PHY registers, EEPROM reads, descriptor lists, and adapter command registers.

Descriptor rings persist while the netdev exists. RX SKBs are allocated and DMA-mapped in `tlan_reset_lists()` and recycled by RX EOF; TX SKBs remain mapped until TX EOF or ring free. Hardware statistics registers clear as a side effect of reading; the driver accumulates them into `dev->stats` only when `record` is true.

The serial EEPROM is read for MAC and ethtool dump access; the driver does not write EEPROM. PHY link and media behavior are volatile and renegotiated after reset, link loss, timeout, suspend/resume, or internal/external PHY switching.

## Dependencies And Integration Points
The file depends on `tlan.h`, PCI, EISA, DMA mapping, netdevice, etherdevice, MII ioctl helpers, timers, workqueues, spinlocks, I/O port accessors, and module infrastructure. It integrates with the kernel through `struct pci_driver`, `struct net_device_ops`, `struct ethtool_ops`, `SIMPLE_DEV_PM_OPS`, shared IRQ handling, netpoll when enabled, and legacy MII ioctls (`SIOCGMIIPHY`, `SIOCGMIIREG`, `SIOCSMIIREG`).

Hardware integration is strongly tied to ThunderLAN DIO registers, host command/status registers, descriptor format, internal PHY registers, external MII devices, and Microchip-style serial EEPROM signaling over `TLAN_NET_SIO`.

## Risks And Edge Cases
This is legacy I/O-port hardware with hand-rolled MII, EEPROM, timers, and DMA rings. Concurrency relies on `priv->lock` across IRQ, ioctl, timer, and EEPROM/MII paths; lock ordering or missed locking can corrupt serial bus transactions or ring state.

Several paths assume PCI device context even for EISA. DMA allocation/free calls use `priv->pci_dev->dev`, so EISA cleanup and init paths are sensitive to how `pci_dev` is represented. Probe and cleanup error paths must avoid freeing coherent memory when allocation failed.

RX refill can run out of memory. If replacement SKB allocation fails, the code reuses the descriptor after `drop_and_reuse` without having unmapped/delivered the old SKB, which avoids immediate allocation failure but requires careful descriptor state preservation. TX ring full returns `NETDEV_TX_BUSY` after stopping the queue, and TX timeout resets rings and adapter.

`netcp`-style phylib abstractions are not used; this driver bit-bangs MII and manually interprets autonegotiation. PHY reset/autoneg timers can retry indefinitely on inactive link. Internal/external PHY switching for `TLAN_ADAPTER_USE_INTERN_10` is subtle, especially around AUI, forced speed/duplex, and link-loss recovery.

Descriptor SKB pointer storage splits an `unsigned long` into two 32-bit descriptor fields. It is intended to work on 64-bit kernels via `upper_32_bits()`, but any descriptor format changes or hardware use of those buffer slots would break pointer recovery.

## Test Signals
Build coverage should include PCI, EISA, suspend/resume, netpoll, and 32-bit/64-bit configurations. Runtime tests need real or emulated ThunderLAN hardware: PCI probe/remove, EISA scan/cleanup, EEPROM MAC read and ethtool EEPROM dump, open/close, TX/RX traffic, multicast/promiscuous/allmulti modes, MII ioctl reads/writes, link autonegotiation, forced speed/duplex/AUI, link loss/recovery, suspend/resume, and watchdog timeout recovery.

Useful logs and counters include the probe banner and installed-device counts, adapter error logs, "PHY reset timeout", "Starting autonegotiation", "Autonegotiation complete", "Link inactive, will retry", TX/RX EOC counts, TX busy counts, carrier transitions, and absence of DMA mapping leaks or stuck queues under stress.
