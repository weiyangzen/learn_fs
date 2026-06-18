# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-irq.h

## Purpose
This header defines ivtv interrupt bit values, standard interrupt masks, and the public IRQ/DMA helper entry points.

## Important APIs, Types, and Functions
It exports bit definitions for encoder capture/EOS/VBI/DMA/PIO events, decoder audio/data/DMA/VBI/vsync events, and DMA error/read/write status. It defines `IVTV_IRQ_MASK_INIT`, `IVTV_IRQ_MASK_CAPTURE`, and `IVTV_IRQ_MASK_DECODE`, and declares `ivtv_irq_handler`, `ivtv_irq_work_handler`, `ivtv_dma_stream_dec_prepare`, and `ivtv_unfinished_dma`.

## Control Flow
There is no executable flow. The masks are consumed by driver init, capture/decode start/stop paths, and the IRQ implementation to enable or disable groups of hardware events.

## State and Persistence Behavior
The header stores no state. Its constants control persistent hardware interrupt mask state in `itv->irqmask` and transient DMA scheduling state in the implementation.

## Dependencies and Integration Points
It integrates with stream lifecycle code, UDMA/YUV decode preparation, the kernel IRQ API, timer callbacks, and hardware register definitions from the core driver.

## Risks
Incorrect bit definitions or mask composition can lose DMA completions, flood IRQs, or leave capture/decode paths stalled. Callers must use the capture and decode masks in the right lifecycle phase.

## Test Signals
Build coverage catches signature drift. Runtime signals include clean IRQ enable/disable transitions during init, start/stop capture, start/stop decode, YUV playback, and DMA timeout paths.
