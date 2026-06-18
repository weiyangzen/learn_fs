# sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd_core.c

## Purpose
`kvaser_pciefd_core.c` is the main PCI driver for Kvaser PCIe CAN FD adapters. It binds supported Kvaser PCI device IDs, maps the board register BAR, discovers firmware/channel properties, allocates DMA receive buffers, creates one SocketCAN netdev per CAN channel, handles transmit/receive/error/status packets, and tears everything down at remove time.

## Important APIs, Types, And Functions
- Registers and packet fields are described with `KVASER_PCIEFD_*` macros for the system ID block, shared receive buffer, KCAN channel blocks, DMA mapping registers, interrupt masks, and packet encodings.
- Board-family data is modeled by static `kvaser_pciefd_address_offset`, `kvaser_pciefd_irq_mask`, `kvaser_pciefd_dev_ops`, and `kvaser_pciefd_driver_data` instances for Altera, SmartFusion2, and Xilinx variants.
- `kvaser_pciefd_rx_packet` and `kvaser_pciefd_tx_packet` are the wire-format packet helpers used for DMA receive parsing and TX FIFO writes.
- `kvaser_pciefd_id_table` maps many Kvaser vendor/device IDs to the correct address, IRQ, and DMA-map operations.
- Netdev entry points are `kvaser_pciefd_open()`, `kvaser_pciefd_stop()`, and `kvaser_pciefd_start_xmit()`.
- CAN core hooks include `kvaser_pciefd_set_nominal_bittiming()`, `kvaser_pciefd_set_data_bittiming()`, `kvaser_pciefd_set_mode()`, and `kvaser_pciefd_get_berr_counter()`.
- PCI lifecycle is handled by `kvaser_pciefd_probe()` and `kvaser_pciefd_remove()`, registered through `module_pci_driver()`.

## Control Flow
Probe allocates a devlink instance, enables PCI, requests regions, maps BAR0, reads system ID information, verifies DMA capability, configures DMA buffers, creates CAN controllers, allocates an IRQ vector, requests the shared IRQ, enables SRB and PCI-level interrupts, rearms both DMA buffers, registers all candevs, and finally registers devlink.

Each CAN netdev open resets TX/ACK indices, calls `open_candev()`, and performs `kvaser_pciefd_bus_on()`. Bus-on waits for flush completion, clears/arms KCAN interrupts, exits reset mode, waits for start completion, configures mode bits, sets state to `CAN_STATE_ERROR_ACTIVE`, wakes the queue, and clears cached error counters. Stop performs a flush, disables channel interrupts, deletes the BEC poll timer, sets the state to stopped, resets queue accounting, and calls `close_candev()`.

TX builds a KCAN packet from a CAN or CAN FD skb, assigns a sequence slot from `tx_idx`, saves an echo skb, updates BQL, writes the packet header/data to the channel FIFO, and uses the `FIFO_LAST` register to complete the hardware packet. ACK packets later validate the echo sequence, timestamp the skb, call `can_get_echo_skb()`, advance `ack_idx` with release semantics, update counters, and wake BQL in bulk after the receive DMA buffer is processed.

Receive interrupts come through the shared PCI interrupt. The handler masks the board interrupt source, dispatches SRB packet-done interrupts to `kvaser_pciefd_receive_irq()`, processes TX-side channel IRQs, then reenables the board mask. `kvaser_pciefd_receive_irq()` reads either DMA buffer, parses a packet list until the zero-size terminator, dispatches by KCAN packet type, reports DMA overflow/underflow errors, and rearms the consumed DMA buffer.

Status/error control flow is tied to completions. Status packets complete `flush_comp` or `start_comp` when reset/flush/bus-on state transitions are observed. Error packets and status responses update CAN state, deliver CAN error skbs when requested, track bus-off, and use a timer to limit high-rate error generation after `KVASER_PCIEFD_MAX_ERR_REP` reports.

## State And Persistence
Runtime state is in `struct kvaser_pciefd` and one `struct kvaser_pciefd_can` per channel. Persistent hardware state includes mapped register values, DMA buffer addresses programmed into variant-specific SerDes registers, KCAN mode/bittiming registers, and devlink firmware version information. Driver-owned volatile state includes `tx_idx`, `ack_idx`, `cmd_seq`, `ioc`, `bec`, completions, BEC poll timer, and per-buffer DMA memory. No on-disk state is stored.

## Dependencies And Integration Points
The file depends on the Linux PCI, DMA, netdevice, SocketCAN, ethtool, timer, completion, and devlink facilities. It integrates with `kvaser_pciefd.h` for private structures and with `kvaser_pciefd_devlink.c` through `kvaser_pciefd_devlink_ops`, `kvaser_pciefd_devlink_port_register()`, and `kvaser_pciefd_devlink_port_unregister()`. It exports no symbols; the PCI module is the integration boundary.

## Risks And Edge Cases
- Several probe error paths call `kvaser_pciefd_teardown_can_ctrls()` after partial setup; correctness depends on `pcie->can[i]` being NULL for uncreated channels and on devlink port registration being paired only for initialized channels.
- `dma_set_mask_and_coherent()` return value is ignored in `kvaser_pciefd_setup_dma()`, so systems unable to satisfy a 64-bit mask may proceed unexpectedly.
- RX packet parsing trusts packet sizes enough to index the 4 KiB DMA buffer; the final size check catches mismatch but happens after field reads.
- TX queue accounting relies on correct ACK sequencing; out-of-order or missing ACKs can leave echo slots occupied and queue progress dependent on later hardware behavior.
- Error-rate throttling disables EPEN after too many error reports and relies on the timer/status request path to reenable it.
- Hardware timestamp conversion multiplies `timestamp * 1000` before division; very large timestamp counters should be reviewed for overflow expectations.

## Test Signals
Useful signals include PCI probe/remove on each supported board family, one channel and multi-channel registration, CAN 2.0 and CAN FD TX/RX, loopback/self reception where available, bus-off and restart behavior, BERR reporting on/off, one-shot NACK handling, DMA overflow/underflow fault logging, IRQ sharing/MSI behavior, ethtool physical ID LED toggling, hardware timestamp reporting, and devlink firmware version visibility.
