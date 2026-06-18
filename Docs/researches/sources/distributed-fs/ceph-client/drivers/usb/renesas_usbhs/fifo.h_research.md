<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.h

## Purpose
Defines FIFO and packet abstractions shared by the Renesas USBHS FIFO engine and frontends.

## Important APIs, Types, And Functions
`struct usbhs_fifo` stores FIFO register offsets, selected pipe, DMA channels, and SH-DMA slave metadata. `struct usbhs_fifo_info` contains CFIFO and four DFIFOs. `struct usbhs_pkt` is the queued transfer unit with list node, pipe, handler, callback, work/DMA fields, buffer, lengths, zero flag, and DATA sequence. `struct usbhs_pkt_handle` supplies `prepare`, `try_run`, and `dma_done`.

## Control Flow
Frontends set `pipe->handler`, push packets, and call `usbhs_pkt_start()`. FIFO code drives handler transitions.

## State And Persistence
FIFO selection is mirrored in software and hardware. Packets persist until completion/dequeue.

## Dependencies And Integration Points
Includes interrupt, DMA, workqueue, `asm/dma.h`, and `pipe.h`; host/gadget request wrappers embed `usbhs_pkt`.

## Risks
`dma_result` is only valid in DMA completion context. Requests must not be freed while `pkt.node` is linked. Direction semantics depend on pipe mode.

## Test Signals
Packet lifetime, handler switching, DMA result accounting, FIFO backpointer cleanup, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.h -->
