# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget.c

## Purpose

`musb_gadget.c` implements the peripheral-side USB gadget controller support for the Mentor MUSB HDRC core. It exposes non-EP0 endpoint operations to Linux gadget drivers, manages endpoint enable/disable, request allocation and queueing, PIO/DMA transfer progression, gadget registration, pullup/wakeup/VBUS operations, and gadget-side bus lifecycle events. The source was read as a complete 2095-line file.

## Important APIs, Types, and Functions

The exported surface is `musb_g_giveback`, `musb_g_tx`, `musb_g_rx`, `musb_alloc_request`, `musb_free_request`, `musb_ep_restart`, `musb_gadget_setup`, `musb_gadget_cleanup`, `musb_g_resume`, `musb_g_suspend`, `musb_g_wakeup`, `musb_g_disconnect`, and `musb_g_reset`. The file defines the non-control `usb_ep_ops` table through `musb_gadget_enable`, `musb_gadget_disable`, `musb_gadget_queue`, `musb_gadget_dequeue`, `musb_gadget_set_halt`, `musb_gadget_set_wedge`, `musb_gadget_fifo_status`, and `musb_gadget_fifo_flush`, plus the `usb_gadget_ops` table through frame, wakeup, self-powered, VBUS draw, pullup, start, and stop callbacks. Transfer helpers include `map_dma_buffer`, `unmap_dma_buffer`, `nuke`, `txstate`, `rxstate`, and `init_peripheral_ep`.

## Control Flow

Gadget setup initializes `musb->g`, enters device mode, builds endpoint objects from `musb->endpoints`, and registers the UDC with `usb_add_gadget_udc`. A gadget function driver starts through `musb_gadget_start`, which binds the transceiver or generic PHY to device mode, marks the controller active, and starts the MUSB core. Endpoint enable validates descriptor direction, endpoint number, maxpacket and high-bandwidth support, programs TXMAXP/RXMAXP and CSR bits, enables endpoint interrupts, and optionally allocates a DMA channel. Queueing maps the buffer if the DMA engine accepts it, links the `musb_request`, and schedules resume work to call `musb_ep_restart`; TX requests call `txstate`, RX requests wait for RXPKTRDY and use `rxstate`. IRQ handlers from the core call `musb_g_tx` and `musb_g_rx`, which finish DMA or PIO segments, handle stalls/underruns/overruns, complete requests with `musb_g_giveback`, and start the next queued request.

## State and Persistence Behavior

State is runtime-only and protected mainly by `musb->lock`: endpoint descriptors, queue lists, DMA channel pointers, endpoint busy/wedged flags, softconnect, `is_active`, suspend state, negotiated speed, HNP flags, and endpoint CSR state. DMA mappings are tracked per `musb_request` with `UN_MAPPED`, `PRE_MAPPED`, or `MUSB_MAPPED` and are synchronized/unmapped before giveback. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on USB gadget core APIs, runtime PM, DMA mapping APIs, MUSB core state (`musb_core.h`), tracepoints (`musb_trace.h`), platform hooks for VBUS/idling, PHY/OTG helpers, and controller register definitions. It integrates with `musb_gadget_ep0.c` through EP0 ops and shared request helpers, with core interrupt dispatch through `musb_g_tx/rx/reset/suspend/resume/disconnect`, and with platform glue through mode, VBUS, and idle hooks.

## Risks and Edge Cases

Risk is concentrated around DMA fallback and CSR sequencing: several paths must clear DMAENAB before DMAMODE, handle double-buffered FIFOs, avoid stale INDEX selection after callbacks release the lock, and recover if DMA programming fails. Queueing maps DMA before taking the main lock, so failures after queue validation must unmap correctly. Endpoint stall clearing can restart queued requests, while wedged endpoints intentionally ignore clear-halt requests. Pullup work and runtime PM introduce asynchronous ordering with gadget driver bind/unbind.

## Test Signals

Useful signals are gadget enumeration with configfs or common gadget functions, bulk IN/OUT stress with and without DMA, short packet and zero-length packet tests, endpoint halt/wedge/clear-halt tests, disconnect during active DMA, runtime PM resume while requests are queued, high-bandwidth ISO descriptor rejection/acceptance, and tracepoint coverage for request enqueue, transfer, and giveback.
