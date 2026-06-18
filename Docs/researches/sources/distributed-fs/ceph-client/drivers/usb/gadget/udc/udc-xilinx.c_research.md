<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/udc-xilinx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/udc-xilinx.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/udc-xilinx.c` implements the Xilinx USB2 device controller as a Linux USB gadget UDC. It registers a platform driver for `xlnx,usb2-device-4.00.a`, exposes `usb_gadget_ops` and `usb_ep_ops`, manages endpoint zero Chapter 9 traffic, queues gadget requests on up to eight endpoints, and drives the controller register block with little- or big-endian accessors detected at probe time. The source was read as a complete 2266-line file.

## Important APIs, Types, and Functions

Core types are `struct xusb_udc`, `struct xusb_ep`, and `struct xusb_req`. `xusb_udc` owns the `usb_gadget`, endpoint array, bound gadget driver, cached setup packet, dummy status request, MMIO base, spinlock, optional DMA flag, clock, and endian-specific read/write callbacks. `xusb_ep` wraps `struct usb_ep`, queue state, descriptor, endpoint DPRAM address, endpoint number, ping-pong buffer state, and direction/type flags.

Important entry points include endpoint ops `xudc_ep_enable()`, `xudc_ep_disable()`, `xudc_ep_queue()`, `xudc_ep_dequeue()`, `xudc_ep_set_halt()`, request allocation/free, and EP0-specific queue/enable stubs. Gadget ops are `xudc_get_frame()`, `xudc_wakeup()`, `xudc_pullup()`, `xudc_start()`, and `xudc_stop()`. Interrupt and protocol handling is split across `xudc_irq()`, `xudc_startup_handler()`, `xudc_ctrl_ep_handler()`, `xudc_nonctrl_ep_handler()`, `xudc_handle_setup()`, `xudc_ep0_in()`, and `xudc_ep0_out()`. Data movement uses `xudc_eptxrx()`, `xudc_read_fifo()`, `xudc_write_fifo()`, and optional DMA helpers `xudc_start_dma()`, `xudc_dma_send()`, and `xudc_dma_receive()`.

## Control Flow

Probe allocates the UDC and a reusable status request, maps MMIO, requests the IRQ, detects optional built-in DMA from `xlnx,has-builtin-dma`, enables `s_axi_aclk` if present, probes register endianness through the test-mode register, initializes endpoints, registers the gadget with `usb_add_gadget_udc()`, and enables global/event/buffer interrupts. Binding a gadget driver calls `xudc_start()`, which stores the driver, sets gadget speed to the driver's max, enables EP0 with a control descriptor, resets address, and clears remote wakeup.

For non-control endpoints, `queue()` maps DMA if needed, attempts immediate service if the endpoint queue is empty, and otherwise appends the request. IN transfers fill DPRAM or DMA into the next free ping-pong buffer, program count registers, and set `XUSB_BUFFREADY_OFFSET`. OUT transfers consume hardware buffer counts, copy or DMA into the request buffer, detect short packets or full request completion, and complete via `xudc_done()`. Interrupt completion clears per-buffer ready flags and re-enters the per-endpoint read/write path for the queue head.

EP0 receives setup packets through `xudc_ctrl_ep_handler()`. The UDC handles standard GET_STATUS, SET_ADDRESS, SET/CLEAR_FEATURE locally, including remote wakeup, test mode, endpoint halt, and deferred address/test-mode application after status stage. Other setup requests are passed to the gadget driver's `setup()` callback outside the spinlock. Reset, suspend, resume, and disconnect events are handled in `xudc_startup_handler()`, which updates speed/state, nukes queues on reset, clears stalls, re-enables selected event interrupts, and calls gadget suspend/resume/disconnect callbacks outside the lock.

## State and Persistence Behavior

The driver has no file-backed persistence. Runtime state is in MMIO registers, endpoint queue lists, per-endpoint ping-pong flags, request `actual/status`, `usb_state`, `remote_wkp`, and EP0 setup phase variables `setupseqtx/setupseqrx`. DMA mappings are per-request and unmapped on completion for nonzero endpoints. System sleep clears/sets the USB ready bit and gates the optional clock, while register contents are otherwise expected to be maintained or reset by the controller/hardware lifecycle.

## Dependencies and Integration Points

The file depends on Linux platform devices, OF matching, clocks, IRQs, DMA mapping, `linux/usb/gadget.h`, and USB Chapter 9 definitions. It integrates upward with composite or function gadget drivers through `usb_add_gadget_udc()` and gadget callbacks, and downward with the Xilinx controller register/DPRAM layout. Device tree integration is the compatible string plus optional `s_axi_aclk` and `xlnx,has-builtin-dma` properties.

## Risks and Edge Cases

The code relies on correct ping-pong buffer bookkeeping; mismatched `curbufnum`, `buffer0ready`, and `buffer1ready` can stall endpoints or overwrite data. DMA uses controller DPRAM addresses derived from MMIO pointers and `virt_to_phys()`, so platform DMA address assumptions are sensitive. Several callbacks deliberately drop and reacquire the spinlock around gadget driver calls; queue state must remain valid across re-entry. EP0 local handling must preserve Chapter 9 sequencing, especially SET_ADDRESS, test mode, zero-length status stages, and setup request cancellation. Endianness detection writes the test-mode register and assumes the attempted big-endian write/read is harmless. Suspend/resume is shallow and does not reconstruct all endpoint registers after full power loss.

## Test Signals

Useful signals include successful bind/unbind of standard gadget functions, enumeration at full and high speed, control request coverage for GET_STATUS/SET_ADDRESS/SET_FEATURE/CLEAR_FEATURE/test mode, remote wakeup behavior, halt/clear-halt with pending requests and busy buffers, IN/OUT bulk and interrupt transfers crossing max-packet boundaries, short packet and overflow handling, DMA and PIO transfer modes, reset/suspend/resume/disconnect interrupt paths, endian variants, and probe/remove with absent/present clock and DMA device-tree properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/udc-xilinx.c -->
