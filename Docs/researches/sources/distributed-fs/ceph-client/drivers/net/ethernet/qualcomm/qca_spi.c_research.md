<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.c

## Purpose
`qca_spi.c` implements a QCA7000 Ethernet-over-SPI netdev driver. It manages SPI synchronization/reset, interrupt-driven RX, queued TX through a kernel thread, serial frame encoding/decoding, module parameters, netdev lifecycle, DT probing, and debug/ethtool integration.

## Important APIs, Types, and Functions
- Module parameters configure SPI clock, burst length, pluggable signature policy, and write verification retries.
- SPI transfer helpers move external FIFO data in burst or legacy mode.
- TX path: `qcaspi_netdev_xmit()` frames/pads/skb-queues packets; `qcaspi_transmit()` drains queued frames when device write-buffer space is available.
- RX path: `qcaspi_receive()` reads available bytes, runs `qcafrm_fsm_decode()`, and submits completed skbs through `netif_rx()`.
- Sync path: `qcaspi_qca7k_sync()` handles unknown/reset/ready states, signature checks, slave reset bit, CPU-on events, and reset timeouts.
- Thread/IRQ: `qcaspi_spi_thread()` is the serialized worker for sync, interrupt handling, RX, and TX; `qcaspi_intr_handler()` sets a flag and wakes it.
- Netdev/probe: open starts the thread and enables IRQ, close disables interrupts and stops the thread, probe validates DT/module params, configures SPI mode, allocates/registers netdev, requests IRQ, sets MAC address, optionally checks signature, and creates debugfs.

## Control Flow
Interrupts set `SPI_INTR` and wake the SPI thread. The thread synchronizes the device, disables carrier and flushes TX while not ready, handles interrupt causes by acknowledging CPU-on/read/write-buffer events, receives packets when ready, and transmits queued packets when write-buffer space allows. TX from the network stack only frames and enqueues skbs under netdev TX locking; actual SPI I/O is centralized in the thread.

## State and Persistence
`struct qcaspi` holds netdev/SPI pointers, thread, TX ring, stats, RX buffer/SKB, sync state, framing FSM, flags, reset counter, debugfs root, and user options. Hardware state includes QCA7K registers and FIFOs. Statistics persist until netdev teardown.

## Dependencies and Integration Points
Depends on Linux SPI, kthread, IRQ, netdev, OF MAC-address helpers, and the common QCA7K framing and register helpers. DT compatible is `"qca,qca7000"`. It integrates with `qca_debug.c` for ethtool/debugfs.

## Risks and Edge Cases
- Ring state uses fixed array storage but configurable active depth; invalid updates must remain clamped.
- `qcaspi_netdev_xmit()` updates `txr.size` before the thread drains; TX lock coverage is important for consistency.
- Sync recovery flushes queued TX and drops in-progress RX frames on CPU-on.
- Buffer-availability values larger than hardware max are treated as line interference and trigger retries/resets.
- Return paths sometimes use `NETDEV_TX_BUSY` after allocation failure, which can cause retry semantics rather than an immediate drop.
- Legacy mode changes transaction structure and has a TODO for GPIO reset.

## Test Signals
Probe with valid/invalid module params, signature failure for non-pluggable devices, open/close thread and IRQ lifecycle, RX frame decode under burst reads, TX ring full/wake behavior, SPI error reset recovery, ethtool stats/registers, and ringparam changes are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.c -->
