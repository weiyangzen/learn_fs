<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.c

## Purpose
Packet transfer engine for CFIFO/DFIFO using PIO or DMA. It queues `usbhs_pkt` objects, selects FIFOs, moves data, controls BRDY/BEMP interrupts, maps DMA buffers, handles DMA completion, and initializes FIFO/DMA resources.

## Important APIs, Types, And Functions
Public functions include `usbhs_pkt_init()`, `usbhs_pkt_push()`, `usbhs_pkt_pop()`, `usbhs_pkt_start()`, `__usbhsf_pkt_get()`, `usbhs_fifo_probe/remove()`, `usbhs_fifo_init/quit()`, and `usbhs_fifo_clear_dcp()`. Exported handlers cover PIO push/pop, DMA push/pop, DCP data/status stages, and control-stage end. Core helpers include `usbhsf_pkt_handler()`, `usbhsf_fifo_select/unselect/clear/barrier()`, IRQ mask controls, PIO movers, DMA prep/done paths, and BRDY/BEMP IRQ callbacks.

## Control Flow
Packets are pushed onto a pipe with a handler and started. Prepare may complete immediately, arm IRQs, or start DMA. BRDY/BEMP IRQs call TRY_RUN for matching pipes. DMA completion calls DMA_DONE, which may finish or switch to PIO. Completed packets are removed under lock, callback is invoked outside the lock, and the next packet starts.

## State And Persistence
State lives in packet lists and packet fields, pipe running/FIFO pointers, FIFO backpointers, DMA channels, and mode IRQ masks. Hardware state is FIFO selector/control, DREQE, BVAL/BCLR/FRDY/DTLN, BRDY/BEMP status, and pipe PID/sequence.

## Dependencies And Integration Points
Depends on `pipe.c`, mode IRQ callback fields, DMAEngine, host/gadget DMA-map callbacks, and platform params such as `pio_dma_border`, `has_usb_dmac`, `cfifo_byte_addr`, and DFIFO IDs.

## Risks
FIFO ownership backpointers must stay synchronized. DMA/PIO fallback depends on alignment, length, endpoint type, and capability. Non-USB-DMAC prep uses workqueue because DMAEngine may not be atomic-safe. IRQ masks must match FIFO/pipe state.

## Test Signals
PIO/DMA IN and OUT, short and zero packets, DCP stages, cancellation, DMA alignment fallback, BRDY/BEMP progress, DMA residue handling, and repeated FIFO select/unselect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.c -->
