# sources/distributed-fs/ceph-client/drivers/net/ethernet/vertexcom/mse102x.c

## Purpose
This is the Linux netdev driver for Vertexcom MSE1021/MSE1022 Ethernet chips attached over SPI. It wraps Ethernet frames in the chip's SPI framing protocol, services an interrupt-per-received-packet model, queues TX work through a workqueue, exposes ethtool/debugfs diagnostics, and registers as a `spi_driver`.

## Important APIs, types, and functions
The main private state is split between `struct mse102x_net`, embedded in netdev private storage, and `struct mse102x_net_spi`, which adds SPI-specific synchronization and transfer state. `mse102x_net` tracks `ndev`, small fixed command RX/TX buffers, `msg_enable`, `txq`, and counters in `struct mse102x_stats`. `mse102x_net_spi` owns the SPI device, a mutex protecting frame transfer, one `spi_message`/`spi_transfer`, TX work, a `valid_cmd_received` diagnostic bit, and optional debugfs dentry.

The SPI protocol helpers are `mse102x_tx_cmd_spi`, `mse102x_rx_cmd_spi`, `mse102x_tx_frame_spi`, and `mse102x_rx_frame_spi`. They use `DET_CMD`, `DET_SOF`, `DET_DFT`, `CMD_RTS`, and `CMD_CTR` to negotiate receive/transmit readiness and frame boundaries. Netdev operations are `mse102x_net_open`, `mse102x_net_stop`, `mse102x_start_xmit_spi`, `eth_mac_addr`, and `eth_validate_addr`. Ettool hooks provide driver info, link reporting, message level control, and private statistics strings. PM hooks call stop/open around suspend and resume. Probe/remove are `mse102x_probe_spi` and `mse102x_remove_spi`.

## Control flow
Probe configures SPI mode 3, 8 bits per word, and a strict 6.0 MHz to 7.142857 MHz max-speed range. It allocates an Ethernet netdev, reserves headroom/tailroom for the SPI SOF/DFT markers, disables TX skb sharing, initializes the mutex, work item, SPI message, TX queue, netdev/ethtool ops, MAC address, and registers the netdev.

Open requests a threaded IRQ with `IRQF_ONESHOT`, starts the queue, forces carrier on, then polls one or two receive attempts to clear a potentially stuck pending SPI interrupt. IRQ handling locks the SPI mutex and calls `mse102x_rx_pkt_spi`. RX sends `CMD_CTR`, expects `CMD_RTS | len`, validates frame length, allocates an aligned skb, consumes invalid frames with maximum length when needed, verifies SOF/DFT unless dropping, then passes valid frames to `netif_rx`.

TX starts in `ndo_start_xmit`: the skb is appended to `txq`, the netdev queue is stopped if `TX_QUEUE_MAX` is reached, and `tx_work` is scheduled. The worker dequeues skbs, locks the SPI mutex, calls `mse102x_tx_pkt_spi`, updates stats, frees skbs, records timeout counters, and wakes the queue. `mse102x_tx_pkt_spi` repeatedly sends `CMD_RTS | len` until the device replies `CMD_CTR`, with a one-second work timeout and staged sleep/backoff, then sends the SOF + padded Ethernet frame + DFT.

Stop turns carrier off, flushes outstanding TX work, stops the queue, purges queued skbs, and frees the IRQ. Remove unregisters the netdev and removes debugfs.

## State and persistence behavior
Runtime state is in the netdev private struct and is not persistent across probe/remove. The driver does not program permanent device configuration other than using the configured SPI mode/speed and runtime MAC address. Statistics persist while the netdev instance lives. `valid_cmd_received` and debugfs `info` expose transient SPI protocol health. Suspend tears down the open netdev path; resume reopens it when it was running.

## Dependencies and integration points
The driver depends on the SPI core, netdev core, ethtool, optional debugfs, Device Tree MAC address helpers, IRQ infrastructure, workqueues, and skb queues. Device matching supports OF compatibles `vertexcom,mse1021` and `vertexcom,mse1022`, plus SPI IDs `mse1021` and `mse1022`. The Kconfig dependency on SPI is essential.

## Risks and edge cases
The SPI transfer object is reused, so the mutex is critical; any future path touching SPI must hold it. RX invalid command handling deliberately consumes a maximum-size frame, which avoids protocol desynchronization but can cost latency. TX timeout is internal to the work item rather than netdev watchdog, so external timeout observability is limited to private ethtool stats and an error-once log. The driver forces carrier on during open and does not manage PHY link state. Probe mutates `spi->controller->min_speed_hz`, which can affect controller-level behavior beyond this device. `velocity`-style DMA risks do not apply, but skb headroom/tailroom and padding are correctness-sensitive for the framing protocol.

## Test signals
Compile with `CONFIG_MSE102X=m/y`, bind via OF and SPI ID, verify SPI setup rejects speeds outside range, exercise ping/iperf traffic in both directions, test short-frame padding, unplug or stall device to trigger `xfer_err`, `invalid_*`, and `tx_timeout`, inspect `ethtool -S`, and verify debugfs `info` reports IRQ, effective SPI speed, mode, queue length, and valid command state. Suspend/resume should preserve functionality when the netdev is up.
