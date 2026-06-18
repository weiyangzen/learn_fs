<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.c

## Purpose
This file implements the main Cadence USBHS gadget controller logic for non-control endpoints, transfer rings, DMA interrupts, gadget operations, endpoint matching/configuration, suspend/resume, and gadget initialization/removal.

## Important APIs, Types, And Functions
Core helpers include register bit setters, `cdns2_select_ep()`, `cdns2_trb_virt_to_dma()`, `cdns2_next_preq()`, TR segment allocation/free, and ring index advancement. Transfer preparation is handled by `cdns2_prepare_ring()`, `cdns2_count_trbs()`, `cdns2_count_sg_trbs()`, `cdsn2_isoc_burst_opt()`, `cdns2_ep_tx_isoc()`, `cdns2_ep_tx_bulk()`, `cdns2_ep_run_transfer()`, and `cdns2_start_all_request()`. Completion uses `cdns2_trb_handled()`, `cdns2_transfer_completed()`, `cdns2_gadget_giveback()`, and isochronous skip handling. Endpoint ops are enable/disable/queue/dequeue/set_halt/set_wedge and request alloc/free. Gadget ops include get_frame, wakeup, set_selfpowered, pullup, UDC start/stop, and match_ep. Public lifecycle functions are `cdns2_gadget_init()`, `cdns2_gadget_remove()`, `cdns2_gadget_suspend()`, and `cdns2_gadget_resume()`.

## Control Flow
`cdns2_gadget_init()` sets a 32-bit DMA mask, resumes the device, precomputes isochronous burst optimization, initializes the gadget, allocates endpoint DMA pools and EP0 setup/ZLP buffers, registers the gadget, and requests a shared threaded IRQ. Queueing maps a request, places it on the deferred list, starts all possible requests if the endpoint is not stalled, writes TRBs, uses a memory barrier before toggling the first TRB cycle bit, and rings the DMA doorbell. Interrupt handling has a hard IRQ that masks sources and wakes a thread, then the thread handles USB reset/suspend/LPM/setup and DMA endpoint bits. Completion advances ring dequeue state, updates request actual bytes, gives back completed requests, and starts deferred work.

## State And Persistence
Persistent state lives in `struct cdns2_device` and per-endpoint objects: transfer rings, pending/deferred request lists, endpoint state bits, buffering allocation, isochronous skip flag, and WA1 stale-address workaround state. The driver also stores on-chip TX/RX buffer sizes, available endpoint bitmap, selected endpoint, speed, wake/self-powered flags, DMA pool, ZLP buffer, and EP0 setup buffer.

## Dependencies And Integration Points
The file depends on CDNS2 register definitions and structs from `cdns2-gadget.h`, EP0 helpers from `cdns2-ep0.c`, tracepoints, Linux DMA pools/mapping, runtime PM, device properties, IRQ threading, and the USB gadget core.

## Risks
The documented WA1 stale-TRB-address workaround is central; incorrect cycle-bit restoration or doorbell timing can DMA from stale buffers. Ring wrap and link TRB handling are complex, especially for small rings, IN bulk extra link TRBs, and isochronous reserved TRBs. Isochronous transfer code has several hardware-specific workarounds for 4 KiB boundaries, packet loss, and first-packet corruption. `cdns2_gadget_set_selfpowered()` writes `pdev->is_selfpowered`, while EP0 GET_STATUS reads `pdev->gadget.is_selfpowered`; that mismatch should be reviewed. Interrupt masking/unmasking is shared-IRQ sensitive and intentionally avoids `IRQF_ONESHOT`.

## Test Signals
Validate full/high-speed enumeration, bulk/interrupt IN and OUT, scatter-gather, request ZLP insertion, dequeue of pending/deferred requests, halt/clear-halt/wedge, ring wrap, TRBERR/DESCMIS recovery, isochronous IN/OUT including missed packets, suspend/resume/LPM/wakeup, runtime PM remove paths, and tracing of DMA endpoint status and TRB completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.c -->
