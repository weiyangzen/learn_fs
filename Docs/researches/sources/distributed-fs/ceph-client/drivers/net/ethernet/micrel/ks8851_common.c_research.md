# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_common.c

## Purpose

`ks8851_common.c` implements transport-independent KS8851 network-device behavior. It handles chip reset, regulators and optional reset GPIO, MAC address selection, RX/TX control setup, threaded interrupt processing, receive filtering, ethtool operations, EEPROM access, MII/MDIO support, suspend/resume, and shared probe/remove logic. SPI and parallel drivers provide the low-level register/FIFO callbacks.

## Important APIs, Types, and Functions

Callback wrappers `ks8851_lock()`, `ks8851_unlock()`, `ks8851_rdreg16()`, and `ks8851_wrreg16()` centralize access through `struct ks8851_net`. Hardware setup helpers include `ks8851_soft_reset()`, `ks8851_set_powermode()`, `ks8851_write_mac_addr()`, `ks8851_read_mac_addr()`, `ks8851_init_mac()`, and `ks8851_read_selftest()`. Network operations are implemented by `ks8851_net_open()`, `ks8851_net_stop()`, `ks8851_start_xmit()`, `ks8851_set_rx_mode()`, `ks8851_set_mac_address()`, and `ks8851_net_ioctl()`.

The RX/interrupt path is centered on `ks8851_irq()` and `ks8851_rx_pkts()`. Ethtool support includes driver info, message level, link settings, link state, nway reset, and EEPROM get/set/length operations. EEPROM bit-banging is provided by `ks8851_eeprom_regread()`, `ks8851_eeprom_regwrite()`, `ks8851_eeprom_claim()`, and `ks8851_eeprom_release()`. PHY integration includes MII mapping via `ks8851_phy_reg()`, `ks8851_phy_read_common()`, `ks8851_phy_read()`, `ks8851_phy_write()`, `ks8851_mdio_read()`, `ks8851_mdio_write()`, and MDIO bus registration helpers.

## Control Flow

`ks8851_probe_common()` initializes shared state after a frontend has filled callbacks. It obtains optional reset GPIO and required `vdd-io`/`vdd` regulators, releases reset, initializes locks/work/eeprom/MII state, registers an MDIO bus, initializes message flags and skb queue, assigns netdev operations, performs a global soft reset, validates `KS_CIDER`, caches `KS_CCR`, reads memory self-test results, initializes the MAC address from device tree, EEPROM, or random fallback, and registers the netdev.

Open requests a threaded IRQ, powers the chip to normal mode, resets the queue management unit, programs TXCR/RXCR/RXQ timing and count thresholds, clears/enables interrupts, initializes `queued_len` and `tx_space`, starts the netdev queue, and checks link. Stop disables interrupts, flushes bus-specific TX work and RX control work, disables RX/TX, enters soft power-down, frees queued TX skbs, and releases the IRQ.

The threaded IRQ reads and acknowledges `KS_ISR`. Link-detect events update PME wake bits and later call `mii_check_link()`. TX interrupts refresh cached TX space and wake the queue. RX interrupts drain packet count from `KS_RXFCTR`; each packet reads frame status and byte count, sets the RX FIFO pointer, starts FIFO access through `RXQCR_SDA`, reads aligned data through the frontend `rdfifo`, queues valid skbs locally, and releases the frame with `RXQCR_RRXEF`. RX process-stop interrupts apply the pending multicast hash and RXCR settings prepared by `ks8851_set_rx_mode()`.

## State and Persistence Behavior

The common state is mostly in `struct ks8851_net`. `rc_ier`, `rc_ccr`, and `rc_rxqcr` are cached hardware-derived or programmed values. `rxctrl` stores pending receive filter state across the asynchronous RXQ shutdown/programming sequence. `txq`, `queued_len`, and `tx_space` coordinate TX availability with bus frontend behavior. EEPROM access is transient and protected by the bus lock; the driver can modify 93C46 EEPROM bytes through ethtool only when the chip advertises EEPROM presence. Suspend and resume preserve netdev intent by stopping/opening only when the interface is running.

## Dependencies and Integration Points

The file integrates with the Linux netdev core, threaded IRQs, workqueues, ethtool, MII helper API, MDIO bus registration, device tree MAC address lookup, regulators, GPIO descriptors, CRC32 multicast hashing, and `eeprom_93cx6`. It is not independently probeable; bus-specific modules call `ks8851_probe_common()` and `ks8851_remove_common()` and export device IDs.

## Risks

Receive filtering depends on the RX process-stop interrupt occurring after `ks8851_rxctrl_work()` disables RXCR1. If that interrupt is lost, pending multicast/promiscuous changes may not program. RX packet handling does not explicitly drop bad `RXFSHR` status frames before delivery; it primarily validates length greater than CRC and relies on hardware filtering/status behavior. EEPROM set supports only single-byte writes and performs read-modify-write on 16-bit EEPROM words, so offset handling must remain correct. Probe error unwinding assumes regulator pointers are valid along each goto path and that frontend locks/register callbacks are usable before common probe begins. MDIO read intentionally returns zero for unsupported MII registers through the legacy MII path, which can hide capability mismatches.

## Test Signals

Test signals include successful probe with correct chip ID/revision and EEPROM presence logging, regulator and reset GPIO sequencing, netdev open/stop without leaked IRQs or queued skbs, RX packet delivery and stats, TX interrupt queue wakeups, multicast/promiscuous mode changes, ethtool EEPROM read/write error cases, MDIO reads through both legacy MII ioctl and registered mdiobus, suspend/resume while running and stopped, and removal after failed partial probe.
