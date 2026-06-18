# sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/sun4i-emac.c

## Purpose
`sun4i-emac.c` implements the Allwinner A10 Fast Ethernet MAC platform driver. It maps EMAC registers, claims clock/SRAM resources, attaches to a devicetree PHY, performs FIFO-based TX, RX through programmed I/O or optional DMAengine, handles interrupts, and exposes standard netdev/ethtool operations.

## Important APIs and functions
- Probe/remove/PM: `emac_probe()`, `emac_remove()`, `emac_suspend()`, and `emac_resume()`.
- Netdev lifecycle: `emac_open()`, `emac_stop()`, `emac_shutdown()`, `emac_init_device()`, and `emac_timeout()`.
- PHY integration: `emac_mdio_probe()`, `emac_mdio_remove()`, and `emac_handle_link_change()` use phylib and update MAC speed/duplex registers.
- Datapath: `emac_start_xmit()` writes packets into TX FIFO channel 0/1; `emac_tx_done()` clears FIFO state and wakes the queue; `emac_rx()` validates RX FIFO headers/status and passes SKBs to the stack.
- DMA helpers: `emac_configure_dma()`, `emac_dma_inblk_32bit()`, and `emac_dma_done_callback()` optionally use a DMAengine `rx` channel for large RX copies.
- Filtering/setup: `emac_setup()`, `emac_powerup()`, `emac_set_rx_mode()`, and `emac_set_mac_address()` configure MAC registers, frame length, flow control, RX acceptance, and MAC address.
- IRQ/netpoll: `emac_interrupt()` masks/clears/re-enables interrupts and dispatches RX/TX/abort handling; `emac_poll_controller()` supports netpoll when configured.

## Control flow
Probe allocates a netdev, maps MMIO from OF, maps the IRQ, optionally configures RX DMA, enables the clock, claims SUNXI SRAM, resolves a PHY phandle, reads or randomizes the MAC address, powers/resets hardware, installs netdev ops, and registers the device. Open requests the IRQ, resets/init hardware, connects/starts the PHY, and starts the TX queue. TX selects one of two hardware FIFO channels and stops the queue when both are occupied. RX loops while FIFO byte count is nonzero, checks an undocumented magic header, validates packet status/length, allocates SKBs, optionally starts DMA for large frames, otherwise reads through `readsl()`, and calls `netif_rx()`. Stop tears down PHY, shuts down MAC/interrupts, and frees IRQ.

## State and persistence behavior
Runtime state lives in `struct emac_board_info`: clock, MMIO, lock, netdev, TX FIFO bitmap, RX DMA channel, PHY node/interface, link/speed/duplex, and RX completion flag. The driver does not persist host data; MAC address comes from devicetree or is randomized. Hardware register state is reinitialized across probe/open/resume.

## Dependencies and integration points
The driver depends on OF platform resources, phylib, SUNXI SRAM claiming, clocks, DMAengine, IRQ/netpoll, and the register definitions in `sun4i-emac.h`. Kconfig selects `MDIO_SUN4I`, but this file attaches to an existing PHY node with `of_phy_connect()`.

## Risks and edge cases
The RX path uses a legacy `emacrx_completed_flag` to avoid overlapping RX/DMA processing. DMA RX falls back to programmed I/O if setup or transfer fails. RX length/status handling subtracts CRC (`rxlen - 4`) for SKB payload but stats add full RX length. The interrupt handler masks all interrupts under a spinlock and directly calls RX, so long RX bursts can increase IRQ latency. Suspend/resume reinitializes hardware without explicitly reattaching PHY state. Probe error paths must release SRAM, clock, IRQ mapping, DMA channel, and MMIO in correct order.

## Test signals
Test OF probe with valid/missing PHY and MAC address, clock/SRAM failures, optional DMA channel present/absent, link speed/duplex changes, TX FIFO saturation and wakeup, RX good/error frames, invalid magic FIFO flush path, netpoll, suspend/resume, and DMAengine fallback/error handling.
