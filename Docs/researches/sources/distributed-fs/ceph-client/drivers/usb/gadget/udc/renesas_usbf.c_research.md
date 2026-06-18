# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/renesas_usbf.c

## Purpose

This file implements the Renesas USBF USB Function gadget UDC driver, targeting the `renesas,rzn1-usbf` compatible. It exposes up to 16 function endpoints, handles EP0 chapter-9 control transfers with a software state machine, supports PIO and endpoint DMA transfers, processes separate EPC and AHB/EPC bridge interrupts, and registers with the Linux USB gadget core as `usbf_renesas`.

## Important APIs, Types, and Functions

- `struct usbf_udc` is the controller object: gadget, driver pointer, device, MMIO base, spinlock, remote-wakeup/suspend flags, endpoint array, EP0 state, canned setup reply request, and EP0 buffer.
- `struct usbf_ep` wraps `usb_ep` with endpoint id, queue, direction, disabled/wedged/delayed-status flags, per-endpoint register bases, optional DMA register base, last status, processing guard, and bridge-DMA completion callback.
- `struct usbf_req` wraps `usb_request` with queue node, zero-packet state, DMA mapping state, transfer state (`xfer_step`), and DMA transfer size.
- `usbf_ep_info[]` encodes the fixed endpoint capabilities, internal RAM base addresses, buffer type, and maxpacket limits expected from the SoC datasheet.
- `usbf_ep_ops` implements endpoint methods; `usbf_gadget_ops` implements gadget methods including pullup and remote wakeup.
- EP0 flow is driven by `usbf_ep0_interrupt()`, `usbf_handle_ep0_setup()`, `usbf_handle_ep0_data_status()`, status-start helpers, local standard request handlers, and `usbf_ep0_pio_in()`/`usbf_ep0_pio_out()`.
- Endpoint-N data flow is driven by `usbf_epn_start_queue()`, `usbf_ep_process_queue()`, `usbf_epn_process_queue()`, PIO helpers, DMA helpers, and `usbf_epn_interrupt()`.
- Interrupt top halves are `usbf_epc_irq()` for USB/EPC events and `usbf_ahb_epc_irq()` for VBUS and bridge DMA completion.

## Control Flow

Probe maps registers, enables runtime PM, releases EPC reset, initializes gadget metadata, endpoint descriptors, endpoint register bases, optional DMA bases, and the setup reply request. It validates hardware endpoint type/buffer mode against `usbf_ep_info[]` via `usbf_epn_check()`, requests two IRQs, configures AHB burst and USB interrupt selection, and registers the gadget UDC.

`usbf_udc_start()` stores the gadget driver and enables VBUS bridge interrupts. Pullup is the actual attach/detach control: `usbf_attach()` enables D+ pullup and reset/speed/resume/suspend interrupts while leaving EP0 to be enabled by USB reset; `usbf_detach()` disables interrupts, resets active endpoints, and disconnects the function PHY. VBUS changes are reported from the AHB/EPC IRQ through `usb_udc_vbus_handler()` and gadget state changes.

On USB reset, `usbf_reset()` nukes active endpoints, updates full/high-speed state, clears remote wakeup, enables EP0, and calls `usb_gadget_udc_reset()`. EP0 interrupts run a state machine with states for idle, IN/OUT data phases, IN/OUT status start, status transfer, and status end. SETUP packets are read from two setup registers; standard GET_STATUS, CLEAR_FEATURE, SET_FEATURE, SET_ADDRESS, and SET_CONFIGURATION are handled locally when valid, while other requests delegate to the gadget driver. Delayed status is supported through `USB_GADGET_DELAYED_STATUS`.

Endpoint queueing is locked by `udc->lock`. EP0 queueing is constrained by the current control state and direction. Non-control endpoints reset request transfer state and, if the queue was empty, arm the hardware immediately. IN endpoints push PIO or DMA data right away; OUT endpoints clear NAK and enable OUT/OUT_NULL interrupts when a request is available.

PIO transfer functions process one maxpacket at a time and complete on requested length, short packet, zero packet, overflow, or explicit zero-length packet handling. DMA IN and DMA OUT are multi-step state machines in `req->xfer_step`. DMA IN maps aligned buffers, programs packet counts and last-packet size, waits for bridge-level completion before enabling USBF IN_END, then handles residues or optional ZLP. DMA OUT handles short packets separately, tracks bridge completion ordering, handles null packets, adjusts `actual` based on remaining DMA count, and may chain a final short DMA or residue read.

## State and Persistence Behavior

Software state is in memory only. Endpoint queue state is held in `usbf_ep.queue`, request transfer progress in `usb_request.actual`, and DMA substate in `usbf_req.xfer_step`, `dma_size`, and `is_mapped`. EP0 protocol state is explicit in `udc->ep0state`; remote wakeup and suspend state are tracked by booleans.

The hardware maintains FIFO contents, endpoint control/status, endpoint RAM mapping, DMA counters, USB address, and interrupt masks. The driver resets or flushes hardware state on detach, bus reset, endpoint disable, dequeue of active requests, stall clear, and transfer error. DMA mapping is carefully unwound in `usbf_ep_req_done()` through `usbf_epn_dma_abort()` if a request completes while still mapped.

## Dependencies and Integration Points

The driver depends on platform MMIO/IRQ resources, runtime PM, USB gadget/composite core, USB role header types, DMA mapping, atomic polling helpers, and Linux list/spinlock primitives. It uses `usb_add_gadget_udc()`, `usb_del_gadget_udc()`, `usb_udc_vbus_handler()`, `usb_gadget_udc_reset()`, `usb_gadget_set_state()`, request giveback, and gadget-driver callbacks for setup/suspend/resume. Its OF binding is `renesas,rzn1-usbf`.

## Risks and Edge Cases

- DMA requires 32-bit aligned request buffers; unaligned buffers intentionally fall back to PIO, but mixed aligned/residue paths need coverage.
- DMA OUT completion has subtle ordering between USBF endpoint interrupts and AHB bridge interrupts. The `bridge_on_dma_end` callback is central to avoiding premature completion.
- `usbf_ep_free_request()` unconditionally removes the request from its list under lock; callers must not free active requests outside normal gadget discipline.
- EP0 dequeue forces stall and nukes pending control requests because partial EP0 transactions cannot remain coherent.
- The driver intentionally avoids setting the USB suspend bit due to shared clock side effects; this is a hardware-integration tradeoff that may matter for power tests.
- Endpoint capabilities are fixed by `usbf_ep_info[]` and checked against hardware registers. Any new variant with different endpoint layout needs a new table or match data.

## Test Signals

Tests should include probe with endpoint availability/DMA availability variations, attach/detach through pullup, VBUS transitions, bus reset and speed changes, EP0 standard request matrix, delayed status from gadget functions, SET_CONFIGURATION state transitions, remote wakeup enable/disable and wakeup attempts, endpoint halt/wedge/clear behavior, EP0 and EPN dequeue paths, PIO transfer with short/ZLP/overflow cases, DMA IN/OUT aligned buffers, unaligned DMA fallback, bridge DMA interrupt ordering, suspend/resume callbacks, and remove/runtime-PM cleanup. Kernel logs should be checked for endpoint capability mismatches, bridge timeouts, flush timeouts, request queue while disabled, and "no request available" warnings.
