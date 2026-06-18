# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/ag71xx.c

## Purpose
Implements the Atheros/QCA AR71xx-family built-in Ethernet MAC platform driver, including OF probe, MDIO bus, phylink integration, descriptor rings, DMA, NAPI RX/TX processing, ethtool stats/selftests, interrupt handling, MTU changes, and SoC-specific configuration.

## Important APIs, Types, and Functions
Central state is `struct ag71xx`, with RX/TX `struct ag71xx_ring`, OF `struct ag71xx_dcfg`, phylink config, reset/clock resources, NAPI, restart work, and OOM timer. Probe path is `ag71xx_probe()`. Lifecycle paths are `ag71xx_open()`, `ag71xx_stop()`, `ag71xx_hw_init()`, `ag71xx_hw_enable()`, and `ag71xx_hw_disable()`. Data path functions include `ag71xx_hard_start_xmit()`, `ag71xx_tx_packets()`, `ag71xx_rx_packets()`, and `ag71xx_poll()`. MDIO is handled by `ag71xx_mdio_probe()`, `ag71xx_mdio_mii_read()`, and `ag71xx_mdio_mii_write()`. Phylink callbacks are `ag71xx_mac_config()`, `ag71xx_mac_link_down()`, and `ag71xx_mac_link_up()`.

## Control Flow and State
Probe maps MMIO, enables clocks, requests reset and IRQ resources, initializes NAPI/work/timer/ring sizes, reads MAC address and PHY mode from DT, initializes hardware, registers an MDIO bus, creates phylink, and registers the netdev. Open connects phylink, calculates RX buffer size, writes max frame length/MAC address, allocates coherent descriptor memory, enables NAPI, starts queues, and starts phylink. IRQs mask poll interrupts and schedule NAPI. NAPI cleans completed TX, consumes RX descriptors into an skb list, refills RX buffers, handles overflow, and re-enables interrupts when work is complete. Stop tears down phylink, DMA, NAPI, timer, and rings.

## Dependencies and Integration Points
Depends on platform device/OF resources, syscon/regmap indirectly through platform data patterns, reset controls, clocks, OF MDIO, PHYLINK, DMA mapping, NAPI, and net selftests. OF compatible strings select FIFO data, max frame size, descriptor length mask, and TX hang workaround behavior for AR7100/AR7240/AR9130/AR9330/AR9340/QCA9530/QCA9550/QCA9560 variants.

## Risks and Test Signals
Risk areas include DMA descriptor ownership, RX refill under memory pressure, reset timing to avoid memory corruption, AR7100 descriptor splitting, and TX hang workaround scheduling. `ag71xx_mdio_probe()` uses a `static struct mii_bus *mii_bus`, which is unusual for per-device probe and merits scrutiny for multi-instance behavior. Tests should include link mode changes through phylink, MTU updates, RX OOM recovery timer, TX timeout restart, bus-error interrupts, ethtool stats/selftest output, and probe across supported compatible strings.
