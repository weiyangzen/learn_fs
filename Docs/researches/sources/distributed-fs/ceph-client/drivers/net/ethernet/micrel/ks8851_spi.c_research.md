# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_spi.c

## Purpose

`ks8851_spi.c` is the SPI frontend for the KSZ8851SNL Ethernet controller. It translates the shared KS8851 register and FIFO callback interface into SPI messages, implements asynchronous TX batching through a workqueue and skb queue, supports half-duplex SPI controllers, and registers an OF/SPI driver for `micrel,ks8851` and alias `spi:ks8851`.

## Important APIs, Types, and Functions

`struct ks8851_net_spi` embeds `struct ks8851_net` and adds a mutex, TX work item, `spi_device`, and pre-initialized one-transfer and two-transfer SPI messages. SPI opcodes are `KS_SPIOP_RD`, `KS_SPIOP_WR`, `KS_SPIOP_RXFIFO`, and `KS_SPIOP_TXFIFO`; `MK_OP()` encodes register offset and byte enables into the command word.

Bus callbacks are `ks8851_lock_spi()`, `ks8851_unlock_spi()`, `ks8851_wrreg16_spi()`, `ks8851_rdreg16_spi()`, `ks8851_rdfifo_spi()`, and `ks8851_wrfifo_spi()`. `ks8851_rdreg()` is the low-level read helper that switches between half-duplex two-transfer messages and full-duplex single-transfer messages. TX helpers are `calc_txlen()`, `ks8851_tx_work()`, `ks8851_flush_tx_work_spi()`, and `ks8851_start_xmit_spi()`. Driver entry points are `ks8851_probe_spi()` and `ks8851_remove_spi()`.

## Control Flow

Probe allocates a managed Ethernet device, forces `spi->bits_per_word = 8`, fills the common callback table including `flush_tx_work`, sets a broader interrupt mask that includes TX done, SPI bus error, TX process stop, RX, RX process stop, and link change, initializes the mutex and TX work, prepares reusable SPI message objects, stores the SPI IRQ in the netdev, and enters `ks8851_probe_common()`.

Register writes use one four-byte SPI transfer containing command and 16-bit value. Register reads use either a two-message half-duplex sequence of command then data, or a full-duplex command+dummy receive where the first two returned bytes are skipped. RX FIFO reads issue a one-byte RXFIFO opcode followed by a receive transfer into the common buffer. TX FIFO writes build a five-byte command/header beginning at `txh.txb[1]` for alignment, then send the aligned skb payload as the second transfer.

TX from the netdev layer is queued. `ks8851_start_xmit_spi()` computes aligned FIFO requirement, takes `statelock`, compares `queued_len + needed` with cached `tx_space`, stops the queue and returns busy if insufficient, otherwise queues the skb and schedules `tx_work`. The worker serializes the SPI bus, drains queued skbs, wraps each FIFO write with RXQCR SDA enable/restore, triggers TXQCR enqueue, frees skbs via `ks8851_done_tx()`, then refreshes `KS_TXMIR` and adjusts `queued_len` and `tx_space`. The common IRQ handler refreshes `tx_space` again on TX interrupts and wakes the queue.

## State and Persistence Behavior

SPI-specific persistent state includes the mutex, reusable `spi_message` and `spi_transfer` objects, and deferred TX work. Shared state in `struct ks8851_net` tracks queued TX length, cached hardware TX space, frame IDs, small DMA-safe command/data buffers, and the skb queue. No nonvolatile state is written by this frontend; EEPROM operations are in common code and use SPI register callbacks.

## Dependencies and Integration Points

The file integrates with the SPI core, OF device matching, Linux workqueues, netdev queueing, and `ks8851_common.c`. It depends on the SPI controller's `SPI_CONTROLLER_HALF_DUPLEX` flag to choose transaction shape. PM is inherited through `ks8851_pm_ops`; removal delegates to `ks8851_remove_common()`. Module parameter `message` controls netif debug verbosity.

## Risks

Reusable SPI transfer structures are mutated for each operation, so all access must be protected by the mutex; any callback path bypassing the lock would corrupt concurrent transfers. TX queue accounting depends on `queued_len`, `tx_space`, TX interrupts, and worker refreshes staying coherent; missed TX interrupts or worker errors can leave the queue stopped. SPI sync failures are logged but most callbacks have no error propagation path to common code, so higher layers may continue after failed register/FIFO operations. The TX worker reads `last = skb_queue_empty()` before locking and uses it to decide loop entry; correctness depends on the scheduling pattern and queue state at worker start.

## Test Signals

Test signals include successful SPI probe with 8-bit words, both full-duplex and half-duplex register reads, RX FIFO reads with aligned packet delivery, TX queue stop/wake under constrained `KS_TXMIR`, TX batching with last-packet IRQ selection, SPI bus error interrupt logging, suspend/resume with flushed TX work, remove after queued traffic, and device-tree compatible `micrel,ks8851`. Fault injection around `spi_sync()` is valuable because errors are mostly observational.
