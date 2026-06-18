# Research Group: subset-b-004568

This grouped report covers Micrel KS8842 and KS8851 Ethernet driver sources under `sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/`. Each section is bounded for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8842.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8842.c

## Purpose

`ks8842.c` is a standalone Linux network driver for the Micrel KS8841/KS8842 Ethernet switch/MAC, including the Timberdale FPGA-attached variant. It registers a platform driver named `ks8842`, maps the device register window, creates a `net_device`, and implements transmit, receive, interrupt, DMA, link, MAC-address, timeout, and teardown paths.

## Important APIs, Types, and Functions

Key private state is `struct ks8842_adapter`, which holds the MMIO base, IRQ, configuration flags from the memory resource, tasklets, timeout work, `net_device`, device pointer, and TX/RX DMA control blocks. `struct ks8842_tx_dma_ctl` tracks a DMA channel, descriptor, coherent-ish staging buffer, scatterlist, and configured channel id. `struct ks8842_rx_dma_ctl` tracks the RX DMA channel, descriptor, current skb, scatterlist, tasklet, and channel id.

Register helpers such as `ks8842_select_bank()`, `ks8842_read16()`, `ks8842_write16()`, `ks8842_enable_bits()`, and `ks8842_clear_bits()` encapsulate banked register access. Lifecycle and configuration functions include `ks8842_probe()`, `ks8842_remove()`, `ks8842_open()`, `ks8842_close()`, `ks8842_reset_hw()`, `ks8842_init_mac_addr()`, and `ks8842_write_mac_addr()`. Packet paths are split across PIO and DMA: `ks8842_xmit_frame()`, `ks8842_tx_frame()`, `ks8842_tx_frame_dma()`, `ks8842_rx_frame()`, `ks8842_handle_rx()`, `__ks8842_start_new_rx_dma()`, and `ks8842_rx_frame_dma_tasklet()`. Interrupt and recovery paths are `ks8842_irq()`, `ks8842_tasklet()`, `ks8842_dma_rx_cb()`, `ks8842_dma_tx_cb()`, `ks8842_tx_timeout()`, and `ks8842_tx_timeout_work()`.

## Control Flow

Probe claims an MMIO resource, allocates an Ethernet device, maps registers, reads the IRQ, decides whether Timberdale DMA is usable from platform data and flags, initializes tasklets and locks, chooses a MAC address from platform data, hardware registers, or a random fallback, reads the switch ID, and registers the netdev. Opening the interface optionally allocates DMA channels/buffers and starts an RX DMA transfer, falls back to PIO on DMA setup failure, resets and configures the chip, writes the active MAC address, updates carrier state, and requests the IRQ.

TX enters through `ndo_start_xmit`. In DMA mode, the driver stages one skb at a time into a DMA buffer with a four-byte control header, submits a slave SG transfer, stops the netdev queue while the descriptor is live, and completes in `ks8842_dma_tx_cb()`. In PIO mode, the driver checks `REG_TXMIR`, writes a command/length header and packet data through 16-bit or 32-bit QMU data registers, enqueues the frame with `REG_TXQCR`, frees the skb, and stops the queue when remaining FIFO space is below MTU plus overhead.

RX in PIO mode is driven by IRQ tasklet processing: `ks8842_irq()` masks device interrupts and schedules `ks8842_tasklet()`, which acknowledges status, restores Timberdale interrupt state, handles link changes, drains RX frames while `REG_RXMIR` reports data, updates counters, releases frames through `REG_RXQCR`, and recovers stopped TX/RX engines. In DMA mode, Timberdale owns RX movement; DMA completion schedules `ks8842_rx_frame_dma_tasklet()`, which immediately arms the next RX DMA before validating and delivering the completed skb.

## State and Persistence Behavior

Persistent runtime state lives in `struct ks8842_adapter` and its DMA substructures. The hardware bank select register is mutable global device state, so tasklet paths save and restore it around interrupt processing. `conf_flags` determine Micrel-native versus Timberdale operation and 16-bit versus 32-bit PIO transfer layout. TX/RX statistics are accumulated through `netdev->stats`. MAC address state is mirrored between netdev state and KS8842 QMU/switch registers, with different switch MAC register ordering for genuine Micrel versus Timberdale wiring.

DMA state is transient but delicate: `adesc` indicates a live transfer, RX `skb` and scatterlist DMA address represent the currently mapped receive buffer, and `ks8842_stop_dma()` must terminate channels, unmap RX buffers, and free the skb. Open/close, timeout recovery, and remove paths do not persist configuration to nonvolatile storage.

## Dependencies and Integration Points

The driver integrates with the platform bus, the Linux netdev API, ethtool link reporting, interrupt handling, tasklets, DMAengine slave SG APIs, DMA mapping APIs, and platform data from `linux/ks8842.h`. It uses MMIO accessors and banked KS8842 register definitions directly. Timberdale-specific registers are accessed in the same MMIO range for reset, interrupt acknowledgement/enabling, FIFO, and DMA resume behavior.

## Risks

The code relies on manual bank selection and shared MMIO state; any missing restore or unsynchronized register access can corrupt subsequent operations. PIO TX/RX loops decrement by four bytes and assume hardware/data alignment sufficient for 16-bit or 32-bit transfers, which is a risk for odd frame tail handling if hardware expectations change. DMA mode allows one TX transfer at a time and uses `adesc` as the busy flag without a broad lock in all readers, so callback/order bugs could stall the queue. RX DMA arms the next receive before fully processing the previous skb, which is good for throughput but makes cleanup and timeout races important. Timberdale interrupt masking differs from native Micrel masking, and the driver must preserve RX interrupt semantics for the FPGA DMA engine.

## Test Signals

Useful test signals include probe success with expected chip family/id/revision logging, successful open/close in both PIO and Timberdale DMA modes, carrier transitions from port 1 link status, TX queue stop/wake behavior under FIFO pressure, RX delivery with multicast and error counters, timeout recovery reinitializing DMA and hardware, and remove/close paths without DMA mapping leaks or tasklet-after-free. Hardware or emulation tests should exercise 16-bit and 32-bit buses, Micrel-native and Timberdale flags, DMA fallback, IRQ storm handling, RX overrun, and invalid MAC fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8842.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851.h

## Purpose

`ks8851.h` is the shared register, bit definition, private-state, and callback contract header for the KS8851 Ethernet driver family. It supports both the SPI KSZ8851SNL path and the parallel KSZ8851-16MLL path by defining the common register map and a transport-neutral `struct ks8851_net` whose bus operations are supplied by the frontend driver.

## Important APIs, Types, and Functions

The file defines nearly all KS8851 register offsets and masks, including global control (`KS_CCR`, `KS_GRR`, `KS_PMECR`), MAC address registers, TX/RX control (`KS_TXCR`, `KS_RXCR1`, `KS_RXCR2`), FIFO pointers and queue commands, interrupt bits (`IRQ_LCI`, `IRQ_TXI`, `IRQ_RXI`, `IRQ_RXPSI`, `IRQ_SPIBEI`, and others), multicast hash registers, chip ID/revision fields, EEPROM control bits, and PHY/MII registers.

`struct ks8851_rxctrl` stores computed receive-filter programming: four multicast hash words and the target RXCR1/RXCR2 values. `union ks8851_tx_hdr` provides byte and little-endian word views over the transmit FIFO header. `struct ks8851_net` is the central private state shared by the common code and bus frontends. It contains netdev linkage, state lock, DMA-safe small buffers, message flags, cached TX space, frame id, cached interrupt/RX queue/chip capability registers, MII and EEPROM helpers, regulators, optional reset GPIO, optional MDIO bus, callback hooks for locking/register/FIFO/TX work, RX control work, skb TX queue, and queued length accounting.

Exported declarations are `ks8851_probe_common()`, `ks8851_remove_common()`, `ks8851_suspend()`, and `ks8851_resume()`. `ks8851_pm_ops` wires those suspend/resume callbacks into both bus drivers. The inline helper `ks8851_done_tx()` updates TX stats and frees a transmitted skb.

## Control Flow

The header itself has no runtime control flow beyond `ks8851_done_tx()`, but it defines the dispatch shape used by the implementation. Frontend drivers allocate a netdev with a bus-specific structure embedding `struct ks8851_net`, fill `lock`, `unlock`, `rdreg16`, `wrreg16`, `rdfifo`, `wrfifo`, `start_xmit`, and optionally `flush_tx_work`, set `rc_ier`, then call `ks8851_probe_common()`. The common layer invokes those callbacks for all register/FIFO operations and routes netdev TX through `ks->start_xmit`.

## State and Persistence Behavior

`struct ks8851_net` caches selected hardware state to avoid rereading critical registers and to coordinate asynchronous code. `rc_ier` stores the interrupt mask chosen by the bus frontend. `rc_ccr` stores chip capability bits such as EEPROM presence and bus type after probe. `rc_rxqcr` stores the base RX queue command value used when starting DMA/FIFO accesses or releasing RX frames. `tx_space` and `queued_len` coordinate software TX throttling, especially for SPI. `rxctrl` persists the desired receive filter until the RX process-stop interrupt allows safe hardware programming.

## Dependencies and Integration Points

The header depends on kernel networking, MII, regulator, GPIO, workqueue, EEPROM 93cx6, and MDIO types through including C files. It exposes a small internal ABI between `ks8851_common.c` and the bus frontends. Register definitions are also the integration point with the KS8851 datasheet and with device-tree matched SPI/parallel variants.

## Risks

The callback contract assumes frontends correctly serialize register and FIFO transactions. Misconfigured `rc_ier`, missing `flush_tx_work`, or incorrect FIFO alignment semantics can break common code despite type compatibility. Several register masks are variant-specific, so using SPI-only bits on the parallel device, or vice versa, is a compatibility risk. Cached state such as `rc_rxqcr` and `tx_space` must remain coherent with hardware changes made in interrupts, open/stop, and TX work.

## Test Signals

Header-level validation is mostly compile-time: both `ks8851_spi.c` and `ks8851_par.c` should build against the same `struct ks8851_net` layout and callback signatures. Runtime test signals include successful common probe through both frontends, correct interrupt masks per variant, valid MAC/EEPROM/MDIO operations using the shared register definitions, and stable TX/RX behavior after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_common.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_par.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_par.c

## Purpose

`ks8851_par.c` is the platform/parallel-bus frontend for the KSZ8851-16MLL variant. It maps the data and command register windows, validates the hardware endian strap, provides parallel MMIO implementations of the shared KS8851 callbacks, implements a synchronous transmit path, and registers an OF-matched platform driver for `micrel,ks8851-mll`.

## Important APIs, Types, and Functions

`struct ks8851_net_par` embeds `struct ks8851_net` and adds a spinlock, data-window MMIO pointer, command-window MMIO pointer, and command-register cache. The BE0-BE3 constants encode the parallel bus byte-enable bits. `ks8851_lock_par()` and `ks8851_unlock_par()` serialize register/FIFO access with `spin_lock_bh()`. `ks_check_endian()` detects an incorrect EESK endian strap by intentionally reading `KS_CIDER` with the byte-enable pattern that reveals swapped BE semantics.

Register access is provided by `ks8851_wrreg16_par()` and `ks8851_rdreg16_par()`, which write the command window with register offset plus computed byte enables and then access the data window. FIFO operations are `ks8851_rdfifo_par()` and `ks8851_wrfifo_par()`. TX is handled by `ks8851_start_xmit_par()`. Probe/remove are `ks8851_probe_par()` and `ks8851_remove_par()`.

## Control Flow

Probe allocates a managed Ethernet device with `struct ks8851_net_par` private data, fills the common KS8851 callback table, sets the interrupt mask to link-change, RX, and RX-process-stop events, initializes the parallel spinlock, maps two platform resources for data and command windows, checks endian strap correctness, obtains the platform IRQ, and calls `ks8851_probe_common()`.

Parallel TX is synchronous in `ndo_start_xmit`. It locks the bus, reads free TX memory from `KS_TXMIR`, and if enough space exists writes RXQCR with `RXQCR_SDA`, writes the FIFO header and aligned skb data, restores RXQCR, triggers enqueue with `TXQCR_METFE`, and polls `TXQCR_METFE` clear with `readx_poll_timeout_atomic()`. On success or timeout it currently calls `ks8851_done_tx()` in the enough-space branch, then unlocks. If space is insufficient, it returns `NETDEV_TX_BUSY`.

RX FIFO reads are invoked by common IRQ processing. The parallel callback uses `ioread16_rep()` from the data window into the caller buffer offset by one 16-bit word, matching the common layer's expectation that status/garbage bytes precede the Ethernet header in the destination.

## State and Persistence Behavior

Parallel-specific state is limited to MMIO mappings, the command cache, and the access lock. There is no deferred TX work and no bus-specific persistent configuration beyond the callback table and interrupt mask. The common layer owns power, MAC, RX filter, MDIO, and EEPROM state. `cmd_reg_cache` records the most recent computed command word but is not used as a coherency guard.

## Dependencies and Integration Points

The file integrates with the platform bus, OF matching, managed resource allocation, MMIO accessors, `readx_poll_timeout_atomic()`, and `ks8851_common.c`. It relies on two memory resources: one for the data register and one for the command register. It shares PM callbacks through `ks8851_pm_ops` and exposes a `message` module parameter for netif debug verbosity.

## Risks

Because TX is done inline while holding a bottom-half-disabled spinlock, long polling or slow MMIO can increase latency. `ks8851_start_xmit_par()` frees the skb even when the TXQCR poll times out after FIFO write, while returning `NETDEV_TX_BUSY`; that return convention can be risky because the networking stack may interpret BUSY as not consumed. FIFO writes use `ALIGN(txp->len, 4)` and 16-bit repeated writes from skb data, so unaligned or short-tail handling depends on skb data layout and hardware tolerance. The endian strap check is critical; without it, all register access can silently address wrong byte lanes.

## Test Signals

Test with device-tree compatible `micrel,ks8851-mll`, two valid MMIO resources, correct and intentionally incorrect endian strap configurations, open/close through common code, TX under full and low FIFO space, TXQCR poll timeout behavior, RX FIFO delivery, interrupt handling without TX interrupt support, suspend/resume, and platform remove. Build coverage should ensure the shared callbacks match `ks8851.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_par.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_spi.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/ks8851_spi.c -->
