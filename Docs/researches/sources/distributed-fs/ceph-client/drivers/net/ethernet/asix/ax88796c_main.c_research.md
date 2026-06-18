# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_main.c

## Purpose
Implements the AX88796C SPI Ethernet netdev driver: SPI device probe/remove, PHY attachment, netdev open/close, transmit and receive paths, interrupt deferral, MAC configuration, checksum offload, multicast filtering, statistics, and module registration.

## Important APIs, Types, and Functions
Core entry points are `ax88796c_probe()`, `ax88796c_remove()`, `ax88796c_open()`, `ax88796c_close()`, `ax88796c_start_xmit()`, and `ax88796c_work()`. It uses `struct ax88796c_device` from the header, `axspi_data` helpers for register access, a `mii_bus` for embedded PHY access, and `ax88796c_netdev_ops`. Helper paths include `ax88796c_soft_reset()`, `ax88796c_reload_eeprom()`, `ax88796c_load_mac_addr()`, `ax88796c_set_hw_multicast()`, `ax88796c_set_csums()`, `ax88796c_handle_link_change()`, `ax88796c_tx_fixup()`, `ax88796c_hard_xmit()`, `ax88796c_receive()`, and `ax88796c_rx_fixup()`.

## Control Flow and State
Probe allocates a devres-managed netdev, initializes per-CPU stats, mutex, MDIO bus, ethtool/netdev ops, hard-resets via GPIO, soft-resets the chip, validates revision, reloads EEPROM, loads a DT/chip/random MAC, disables power saving, connects the internal PHY, and registers the netdev. Open requests the IRQ, resets and configures MAC/SPI compression/checksum/LED/PHY polling registers, starts PHY and TX queue, and initializes the RX SPI message. IRQs are top-half minimized: the interrupt disables the IRQ, sets `EVENT_INTR`, and schedules `ax_work`. The workqueue serializes all SPI register access under `spi_lock`, handles multicast updates, drains RX interrupts, transmits queued SKBs, and re-enables IRQs. Close stops PHY/queue, clears event bits, masks interrupts, purges TX queue, resets the chip, cancels work, and frees IRQ.

## Dependencies and Integration Points
Depends on SPI core, GPIO descriptors, PHYLIB, netdev, per-CPU u64 stats, ethtool ops, and the AX88796C register/SPI helpers. Device tree supplies optional MAC address, reset GPIO, SPI IRQ, and compatible string.

## Risks and Test Signals
High-risk areas are serialized SPI access, IRQ/work race handling, TX buffer expansion, RX header validation, and reset/unwind paths. A likely logic issue exists in `ax88796c_set_mac()`: the full-duplex case sets `MACCR_SPEED_100` instead of `MACCR_DUPLEX_FULL`, which can misprogram duplex. Probe calls `ax88796c_hard_reset()` but ignores its return. Tests should cover sustained TX/RX, close while work is pending, SPI compression on/off, checksum feature toggles, PHY link changes, reset GPIO absence/failure, and ethtool register dumps.
