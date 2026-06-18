# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_host.c

## Purpose

`musb_host.c` implements MUSB host-controller support for Linux usbcore. It creates the HCD, maps URBs onto MUSB hardware endpoints, schedules control/bulk/interrupt/isochronous transfers, programs endpoint registers for PIO or DMA, handles host endpoint interrupts, cleans up/unlinks URBs, and bridges root hub operations into MUSB virtual hub helpers. The source was read as a complete 2765-line file.

## Important APIs, Types, and Functions

Externally visible functions include `hcd_to_musb`, `musb_h_ep0_irq`, `musb_host_tx`, `musb_host_rx`, `musb_host_alloc`, `musb_host_cleanup`, `musb_host_free`, `musb_host_setup`, `musb_host_resume_root_hub`, and `musb_host_poke_root_hub`. Key internal functions are `musb_start_urb`, `musb_ep_program`, `musb_advance_schedule`, `musb_schedule`, `musb_urb_enqueue`, `musb_urb_dequeue`, `musb_cleanup_urb`, `musb_h_disable`, `musb_host_packet_rx`, `musb_rx_reinit`, `musb_bulk_nak_timeout`, `musb_h_ep0_continue`, and DMA helpers for TX/RX mode selection.

## Control Flow

Host setup creates an HCD with `musb_hc_driver`, sets host PHY/OTG mode, adds the HCD, and enables wakeup. URB enqueue validates active host state, links the URB to usbcore's endpoint list, creates a `musb_qh` when needed, precomputes type/interval/address/hub fields, and schedules it. Control transfers always use EP0; bulk transfers prefer reserved bulk endpoint rings; periodic transfers claim the best-fitting free hardware endpoint. `musb_start_urb` initializes queue offsets and calls `musb_ep_program`, which selects endpoint registers, configures address/type/interval/maxpacket/toggles, programs DMA when possible, or loads/requests FIFO data for PIO. IRQ dispatch calls `musb_h_ep0_irq`, `musb_host_tx`, or `musb_host_rx`; they handle stalls, errors, NAK timeouts, DMA completion, PIO FIFO movement, short packets, iso frame status, and queue advancement. Completion calls `musb_advance_schedule`, which saves toggles, gives back the URB with the lock dropped, releases DMA channels when queues empty, and starts the next URB/QH.

## State and Persistence Behavior

Host state is in-memory: HCD private pointer, per-endpoint `in_qh/out_qh`, bulk/control rings, `musb_qh` offsets/segment sizes/iso index/toggle metadata, endpoint reinit flags, DMA channel pointers, root port status, and runtime MUSB OTG state. Temporary aligned buffers may replace URB transfer buffers for DMA on RTL 1.8+ and are copied/free on unmap. There is no persistent state outside usbcore's runtime device model.

## Dependencies and Integration Points

The file depends on Linux usbcore HCD APIs, DMA mapping APIs, scatterlist iterators, MUSB core/register/FIFO helpers, `musb_host.h`, tracepoints, and virtual hub functions from `musb_virthub.c`. Platform operations provide toggle access, endpoint/busctl offsets, VBUS, root reset quirks, DMA controller implementation, and endpoint interrupt clearing.

## Risks and Edge Cases

Risks include hardware CSR ordering constraints, endpoint toggle preservation, bulk fairness under NAK timeout, shared FIFO reconfiguration, double-buffered FIFO flushing, DMA mode 1 terminal packet behavior, CPPI/TUSB/Inventra differences, unaligned DMA buffers, URB unlink races while callbacks drop the lock, and iso error accounting. Several comments document known partial behavior and silicon quirks, so regressions often appear only under stress or specific controller variants.

## Test Signals

Signals include usbtest control/bulk/iso/interrupt cases, high-throughput bulk with multiple devices behind a hub, disconnect during active TX/RX DMA, URB unlink tests, short-packet and `URB_SHORT_NOT_OK` tests, unaligned buffer DMA tests on RTL 1.8+, periodic endpoint scheduling exhaustion, bulk NAK fairness with network/serial adapters, and root hub suspend/resume/reset sequencing.
