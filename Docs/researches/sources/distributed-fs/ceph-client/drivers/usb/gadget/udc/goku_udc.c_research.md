# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/goku_udc.c

## Purpose

`goku_udc.c` implements the Toshiba TC86C001 "Goku-S" PCI USB full-speed device-controller driver. It exposes a small fixed-endpoint UDC to the USB gadget framework: ep0 plus three semi-configurable bulk/interrupt endpoints, with optional DMA for ep2 IN and cautious optional DMA for ep1 OUT. The driver manages PCI probing, MMIO register programming, control-request dispatch, PIO/DMA transfer progression, interrupt handling, and gadget bind/unbind.

## Important APIs, Types, and Functions

Endpoint operations are collected in `goku_ep_ops`: `goku_ep_enable()`, `goku_ep_disable()`, `goku_alloc_request()`, `goku_free_request()`, `goku_queue()`, `goku_dequeue()`, `goku_set_halt()`, `goku_fifo_status()`, and `goku_fifo_flush()`. Gadget operations are `goku_get_frame()`, `goku_udc_start()`, `goku_udc_stop()`, and `goku_match_ep()`. PCI integration is through `goku_probe()`, `goku_remove()`, `gadget_release()`, `pci_ids`, and `goku_pci_driver`.

Important internal helpers include `command()`, `ep_reset()`, `write_fifo()`, `read_fifo()`, `pio_advance()`, `start_dma()`, `dma_advance()`, `abort_dma()`, `done()`, `nuke()`, `goku_clear_halt()`, `udc_reinit()`, `udc_reset()`, `ep0_start()`, `udc_enable()`, `stop_activity()`, `ep0_setup()`, and `goku_irq()`. Optional proc debug output is produced by `udc_proc_read()`.

## Control Flow

PCI probe allocates `struct goku_udc`, enables the PCI device, reserves and maps BAR0, resets and reinitializes the controller, requests the shared IRQ, optionally enables bus mastering for DMA, creates debug proc output, and registers the gadget with `usb_add_gadget_udc_release()`. `udc_reinit()` creates four endpoint objects, sets FIFO/mode/status register pointers, initializes request queues, exposes ep1-ep3 for autoconfiguration, and leaves ep0 out of the normal endpoint list. A bound gadget driver calls `goku_udc_start()`, which stores the driver and starts power detection or ep0 enumeration.

Endpoint enable validates fixed endpoint number, transfer type, max packet size, direction, and endpoint invalid state. It chooses PIO or DMA based on endpoint number, direction, and `use_dma`, configures double buffering for ep1/ep2 where useful, writes endpoint mode, resets the endpoint, and marks it active. Queueing validates the request, maps it for DMA when needed, initializes status and actual length, forces ep0 IN ZLP policy, then either starts DMA or advances PIO immediately. If the request cannot complete synchronously, it is appended to the software queue and PIO dataset interrupts are enabled for non-DMA endpoints.

PIO IN writes bytes into the endpoint FIFO until maxpacket or request end and uses EOP to mark short/ZLP completion. PIO OUT reads active packet buffers, handles overflow by discarding excess bytes, completes on short packet or full request, and drains a second double buffer when possible. DMA setup writes start/end registers and `dma_master` bits; completion interrupts compute `actual` from the DMA current register, complete the request, and start the next queued request. Abort paths attempt FIFO disable plus DMA reset, but comments note weak hardware documentation and inconsistent OUT behavior.

The IRQ handler scans enabled interrupt bits under the spinlock, handles system error, power-detect connect/disconnect, suspend/resume callbacks, reset-done logging, ep0 setup/status/data events, DMA completion, and PIO dataset events, then rescans a bounded number of times to catch posted/new events. `ep0_setup()` reads the setup packet from split byte registers, handles selected `CLEAR_FEATURE` cases locally, tracks SET_CONFIGURATION for hardware state updates, delegates most requests to `driver->setup()`, and stalls ep0 on failure.

## State and Persistence Behavior

Driver state is volatile and anchored in `struct goku_udc`: gadget, lock, four endpoints, bound gadget driver, ep0 state, flags for PCI resources and configuration state, MMIO register pointer, interrupt-enable shadow, and IRQ counters. Each `struct goku_ep` tracks endpoint number, DMA flag, direction, stopped state, request queue, register pointers, and IRQ count. Each `struct goku_request` wraps a gadget request and queue node. Hardware-visible state lives in BAR0 registers for power detect, interrupt enable/status, endpoint mode/status/FIFO, dataset bits, EOP, command, and DMA registers. No disk persistence exists.

## Dependencies and Integration Points

The driver integrates with the PCI subsystem, Linux USB gadget framework, USB Chapter 9 descriptors, IRQ handling, optional procfs debug files, DMA mapping via `usb_gadget_map_request()`, and low-level MMIO accessors. It uses `usb_add_gadget_udc_release()` for UDC registration and callback release, and endpoint matching guides gadget autoconfiguration toward ep3 interrupt and ep2 bulk-IN when appropriate.

## Risks and Test Signals

Major risks are hardware quirks around DMA abort, OUT DMA hiding short packets, FIFO clear also clearing halt, ep0 status-stage timing, posted PCI/MMIO writes, and IRQ rescan ordering under concurrent events. The driver intentionally leaves OUT DMA disabled by default because short packets are protocol-significant. Test signals include PCI probe/remove resource cleanup, gadget bind/unbind, full-speed enumeration, ep0 setup requests with delegated and locally handled clear-feature cases, SET_CONFIGURATION state updates, PIO IN/OUT transfers for all endpoints, DMA IN transfers on ep2, optional OUT DMA stress if enabled, dequeue/disable while DMA is active, suspend/resume callbacks, disconnect/reconnect via power-detect IRQ, system-error recovery, endpoint halt/clear halt, fifo flush/status behavior, and proc debug visibility.
