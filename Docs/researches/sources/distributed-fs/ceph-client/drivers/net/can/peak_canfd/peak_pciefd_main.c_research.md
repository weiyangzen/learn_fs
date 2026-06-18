# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_pciefd_main.c

## Purpose
`peak_pciefd_main.c` is the PCIe backend for PEAK PCAN-PCIe FD, cPCIe FD, PCIe-104 FD, mini-PCIe FD, OEM, and M.2 CAN FD cards. It discovers board/channel count, maps PCI registers, allocates per-channel DMA buffers, wires transport callbacks into the common uCAN layer, handles IRQs, and manages TX/RX DMA rings.

## Important APIs, Types, And Functions
- PCI IDs are listed in `peak_pciefd_tbl`.
- Board/system and per-channel register offsets/bits define clock, timestamp, command, DMA, and IRQ controls.
- `struct pciefd_rx_dma`, `struct pciefd_tx_link`, `struct pciefd_page`, `struct pciefd_can`, and `struct pciefd_board` model RX DMA records, TX page links, per-channel state, and board state.
- `pciefd_irq_handler()` processes one channel's DMA IRQ tag, RX message list, TX page-link completion, queue wake, and RX DMA rearm.
- Backend callbacks are `pciefd_pre_cmd()`, `pciefd_write_cmd()`, `pciefd_post_cmd()`, `pciefd_enable_tx_path()`, `pciefd_alloc_tx_msg()`, and `pciefd_write_tx_msg()`.
- `pciefd_can_probe()` allocates/registers one channel; `peak_pciefd_probe()` handles the whole PCI device.

## Control Flow
PCI probe enables the device, requests regions, reads subsystem ID to derive one to four CAN channels, allocates a flexible board structure, maps BAR0, reads FPGA firmware version, applies a 32-bit DMA mask workaround for old firmware on 64-bit DMA architectures, stops the system clock, sets bus master, probes each channel, resets the system timestamp counter, starts the system clock, and stores board drvdata.

Per-channel probe allocates a PEAK CAN FD netdev, fills common backend callbacks and command buffer, computes the channel register base, allocates coherent RX and TX DMA areas, resets channel timestamp/clock state, determines the CAN clock from the hardware clock selector, assigns the shared PCI IRQ, registers the candev, initializes `tx_lock`, and stores the channel in the board.

Entering normal/listen-only mode triggers `pciefd_pre_cmd()`: request the channel IRQ, program RX DMA address and IRQ coalescing limits, clear RX reset, reset channel timestamp, acknowledge the initial RX tag, and enable channel IRQ. The command is then written atomically as a 64-bit command through the board command lock. After reset-mode commands, `pciefd_post_cmd()` disables IRQs, clears TX/RX DMA, performs a read flush, frees the IRQ, and marks the channel stopped.

TX pages are 2 KiB regions inside the 4 KiB TX DMA area. `pciefd_alloc_tx_msg()` reserves space in the current page, emits a link record to a new page when the current page is full, tracks free pages, and returns available room to the common TX code. `pciefd_write_tx_msg()` advances the page offset and rings the TX request accumulator. IRQ link notifications free TX pages and wake the queue if echo space is available.

## State And Persistence
Per-board state includes BAR base, PCI device, channel count, and a command spinlock. Per-channel state includes register base, coherent RX/TX DMA virtual/logical addresses, TX page descriptors, free-page count, current page index, TX lock, last IRQ status, and expected IRQ tag. Hardware timestamp counter and DMA addresses are volatile hardware state.

## Dependencies And Integration Points
The backend depends on PCI, DMA coherent allocation, MMIO accessors, SocketCAN through `peak_canfd.c`, and PEAK uCAN protocol definitions. It shares the PCI IRQ across channels by requesting it per channel with `IRQF_SHARED`.

## Risks And Edge Cases
- `pciefd_can_probe()` returns `-ENOMEM` through the `failure` label even for `register_candev()` errors, losing the original error code.
- IRQs are requested during mode transition rather than PCI probe, so repeated open/close must balance request/free exactly.
- TX page allocation updates page offsets after the common code fills the returned message; concurrency relies on the netdev TX serialization plus `tx_lock` around page selection.
- Old firmware DMA mask workaround is conditional on decoded version; incorrect version decode could leave an incompatible 64-bit DMA mode.
- Shared IRQ tag matching assumes RX DMA status memory is coherent and updated before interrupt handling reads it.

## Test Signals
Test all supported PCI IDs/subsystem channel counts, firmware versions below and above 3.3.0 on 64-bit systems, shared IRQ handling across multiple channels, open/close request/free IRQ balancing, TX page rollover/link interrupts, RX DMA tag sequence, CAN FD TX/RX, bus-off/reset-mode cleanup, and remove after active channels.
