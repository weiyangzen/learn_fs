# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunhme.c

## Purpose
`sunhme.c` implements the Sun Happy Meal Ethernet 10/100 driver for SBUS and PCI variants, including single-port HME and four-port Quattro/QFE cards. It owns device probing, MAC address discovery, register mapping, reset and initialization, PHY/MII access, autonegotiation and forced-link fallback, interrupt-driven RX/TX, multicast filters, ethtool operations, and module registration.

## Important APIs, Types, And Functions
- Module interface: `module_param_array(macaddr, ...)`, `happy_meal_probe()`, `happy_meal_exit()`, conditional SBUS and PCI driver registration, and PCI/OF match tables.
- Bus abstraction helpers: `sbus_hme_*`, `pci_hme_*`, `hme_write32`, `hme_read32`, `hme_write_rxd`, `hme_write_txd`, and `hme_read_desc32` handle endian and bus differences.
- PHY/MIF access: `happy_meal_bb_read()`, `happy_meal_bb_write()`, `happy_meal_tcvr_read()`, and `happy_meal_tcvr_write()` support bit-bang and frame-mode MII access.
- Link management: `happy_meal_begin_auto_negotiation()`, `happy_meal_timer()`, `try_next_permutation()`, `set_happy_link_modes()`, `display_link_mode()`, and `display_forced_link_mode()` implement autonegotiation, forced fallback, and BigMAC duplex updates.
- Hardware lifecycle: `happy_meal_stop()`, `happy_meal_tx_reset()`, `happy_meal_rx_reset()`, `happy_meal_tcvr_reset()`, `happy_meal_transceiver_check()`, `happy_meal_init_rings()`, `happy_meal_clean_rings()`, and `happy_meal_init()`.
- Data path: `happy_meal_interrupt()`, `happy_meal_tx()`, `happy_meal_rx()`, `happy_meal_start_xmit()`, `unmap_partial_tx_skb()`, `happy_meal_tx_timeout()`, `happy_meal_open()`, and `happy_meal_close()`.
- Netdev and ethtool integration: `hme_netdev_ops`, `hme_ethtool_ops`, `happy_meal_get_stats()`, `happy_meal_set_multicast()`, `hme_get_link_ksettings()`, `hme_set_link_ksettings()`, `hme_get_drvinfo()`, and `hme_get_link()`.
- Probe support: `happy_meal_addr_init()`, `happy_meal_common_probe()`, `happy_meal_sbus_probe_one()`, `happy_meal_pci_probe()`, `quattro_sbus_find()`, `quattro_pci_find()`, `is_quattro_p()`, and `find_eth_addr_in_vpd()`.

## Control Flow
Probe allocates an Ethernet netdev, resolves SBUS or PCI resources, maps global/TX/RX/BigMAC/MIF register windows, assigns MAC address, initializes locks and Quattro parent membership, allocates one coherent descriptor page, sets netdev operations/features, primes PHY advertisement, and registers the netdev. `ndo_open` requests the shared IRQ and calls `happy_meal_init()` under `happy_lock`. Initialization stops hardware, clears and refills rings, configures MIF access mode, detects internal/external transceiver, resets PHY and BigMAC, writes MAC and hash filters, programs DMA ring pointers and burst size, enables TX/RX DMA and BigMAC, and starts the link timer.

Interrupt handling reads `GREG_STAT` once, handles fatal errors through `happy_meal_is_not_so_happy()` and reset, reclaims TX on `TXALL`, and drains RX on `RXTOHOST`. TX maps the linear area and fragments into descriptors; fragment descriptors are written before the first descriptor to avoid hardware racing a partially populated packet. RX either passes the DMA SKB upward for large packets after replacing the ring buffer, or copies small packets into a fresh SKB and reuses the DMA buffer. Close stops hardware, frees RX/TX SKBs and DMA mappings, deletes the autoneg timer, and releases the IRQ.

## State And Persistence
All persistent runtime state lives in `struct happy_meal`: register bases, DMA coherent descriptor block, SKB rings, ring indexes, PHY software shadow registers, link timer state, flags, bus identity, and Quattro membership. There is no disk persistence. Module parameter `macaddr` is process-global module state and increments the last byte after assignment. Quattro parent lists are global in-memory lists and are freed at module exit. Device-managed allocations are used for many probe resources, while the Quattro membership array is manually cleared on probe failure.

## Dependencies And Integration Points
The driver depends on Linux netdev, ethtool, DMA mapping, SKB, CRC multicast hashing, timers, PCI, platform/OF, and SPARC SBUS support. It consumes definitions from `sunhme.h`. It integrates with Open Firmware names `SUNW,hme`, `SUNW,qfe`, and `qfe`, PCI ID `PCI_DEVICE_ID_SUN_HAPPYMEAL`, idprom MAC fallback on SPARC, PCI ROM VPD MAC lookup off-SPARC, and netdev features `NETIF_F_SG`, `NETIF_F_HW_CSUM`, and `NETIF_F_RXCSUM`.

## Risks And Edge Cases
- The hardware has documented write, parity, and reset quirks. The driver contains retries, rereads, and low-bit ring-pointer workarounds that must not be simplified without hardware validation.
- `unmap_partial_tx_skb()` advances neither `first_entry` inside its loop in the visible source, which is a high-risk area for DMA mapping failure handling if exercised.
- The driver is interrupt-driven, not NAPI, so high RX rates can spend a long time in IRQ context.
- Autonegotiation and forced fallback are timer-driven under `happy_lock`; reset paths must delete or restart the timer carefully.
- Descriptor ordering is critical: address writes must precede ownership flags and use `dma_wmb()`.
- Global `macaddr` assignment can generate sequential addresses and is not per-device isolated.
- Quattro parent tracking must stay synchronized with failed probes and module exit to avoid stale pointers.

## Test Signals
Important signals include SBUS and PCI probe/remove, QFE four-port detection, open/close cycles, IRQ sharing, TX with and without fragments, DMA mapping failure injection, RX small-copy and large-buffer replacement paths, multicast/promiscuous/allmulti changes, ethtool autoneg and forced speed/duplex settings, TX timeout reset, link-down forced-mode fallback, and module unload with Quattro lists populated.
