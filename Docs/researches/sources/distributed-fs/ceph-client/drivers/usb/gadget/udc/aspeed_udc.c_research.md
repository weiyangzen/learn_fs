# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed_udc.c

## Purpose
Implements the standalone Aspeed AST2600 USB device controller driver, separate from the multi-device vHub driver. It exposes one control endpoint plus four programmable endpoints to the Linux USB gadget framework, handles EP0 setup/status/data stages, programs endpoint DMA in single-stage or descriptor mode, dispatches controller interrupts, and binds the controller as an OF platform driver compatible with `aspeed,ast2600-udc`.

## Important APIs, Types, And Functions
Private state types are `struct ast_udc_request`, `struct ast_dma_desc`, `struct ast_udc_ep`, and `struct ast_udc_dev`. The gadget endpoint ops are implemented by `ast_udc_ep_enable`, `ast_udc_ep_disable`, request allocation/free, `ast_udc_ep_queue`, `ast_udc_ep_dequeue`, and `ast_udc_ep_set_halt`. Gadget ops are `ast_udc_gadget_getframe`, `ast_udc_wakeup`, `ast_udc_pullup`, `ast_udc_start`, and `ast_udc_stop`.

Transfer helpers include `ast_udc_done`, `ast_udc_nuke`, `ast_dma_descriptor_setup`, `ast_udc_epn_kick`, `ast_udc_epn_kick_desc`, `ast_udc_ep0_queue`, `ast_udc_ep0_in`, `ast_udc_ep0_out`, `ast_udc_epn_handle`, and `ast_udc_epn_handle_desc`. Setup handling is centralized in `ast_udc_ep0_handle_setup`, with `ast_udc_getstatus` and `ast_udc_ep0_data_tx` for simple standard replies. Platform lifecycle is handled by `ast_udc_probe`, `ast_udc_remove`, `ast_udc_init_ep`, `ast_udc_init_dev`, and `ast_udc_init_hw`.

## Control Flow
Probe allocates the device structure, maps registers, enables the clock, detects whether full-speed-only mode is requested from maximum speed, allocates one coherent DMA region for EP0 and all EPn buffers/descriptors, initializes endpoint objects, initializes hardware, requests the IRQ, and registers the gadget UDC. Hardware init enables PHY clock/reset, sets long descriptor mode for 256 descriptors, masks/acks interrupts, enables bus/EP0/EP-pool ACK interrupts, and clears EP0 control.

When a gadget driver starts, `ast_udc_start` records the driver and marks endpoints active. Pullup toggles `USB_UPSTREAM_EN`. Endpoint enable derives endpoint number, direction, type, maxpacket, descriptor-mode eligibility for IN endpoints, programs DMA mode and endpoint config, clears data toggle, and leaves the endpoint ready. Queueing maps the request for DMA, initializes progress, queues it, and kicks immediately if idle. EP0 queues write the EP0 data buffer address and set TX/RX ready bits; EPn queues either write a single DMA address/length or populate descriptors and update the hardware write pointer.

The ISR acknowledges `AST_UDC_ISR`, handles bus reset/suspend/resume by updating gadget state and invoking driver callbacks outside the lock, advances EP0 on IN/OUT ACKs, parses setup packets, and handles EP-pool ACKs by reading `AST_UDC_EP_ACK_ISR` and dispatching each active endpoint to single-stage or descriptor completion.

## State And Persistence Behavior
State is runtime-only: request queues, mapped DMA addresses, saved descriptor write pointer, endpoint stopped/dir/desc-mode flags, current gadget driver, `suspended_from`, `is_control_tx`, wakeup enable, and coherent descriptor memory. Hardware state lives in controller registers and is reset during probe/remove/stop. There is no persistent storage. Completion callbacks run with `udc->lock` dropped, so subsequent queue operations must tolerate callback-side mutation.

## Dependencies And Integration Points
Depends on Linux platform device, OF match, clock, DMA mapping, interrupt, and USB gadget APIs. It integrates with AST2600 UDC MMIO registers, coherent DMA memory, and gadget function drivers through `usb_add_gadget_udc`. Device tree supplies the compatible string and optional maximum-speed policy.

## Risks
The code has several fragile paths. `ast_udc_ep_dequeue` deletes the request from the queue before calling `ast_udc_done`, but `ast_udc_done` also deletes the request, which is a double-delete risk. If the request is not found, the post-loop check references the iterator variable after traversal in a way that is easy to get wrong. `ast_udc_ep_set_halt` uses `usb_endpoint_num(ep->desc)` and reads the root `AST_UDC_EP_CONFIG` for nonzero endpoints instead of the endpoint register helper, which looks suspicious and can misprogram stalls. `ast_udc_ep_queue` adds the request to the queue before DMA mapping and does not remove/unmap it on mapping or EP0 alignment failures. Descriptor-mode completion sums lengths into a `u16 total_len`, which can overflow if descriptor windows grow beyond 64 KiB. EP0 SET_ADDRESS writes address immediately rather than after status ACK, so host timing should be tested carefully.

## Test Signals
Primary signals are configfs gadget enumeration on AST2600, SET_ADDRESS/GET_STATUS handling, bulk/interrupt/iso transfers across all four programmable endpoints, descriptor-mode large IN transfers, single-stage fallback, active dequeue, halt/clear-halt, bus reset during traffic, suspend/resume callbacks, remote wake, and module remove while idle. KASAN/list-debug warnings around dequeue and queue error paths, incorrect endpoint halt behavior, DMA descriptor pointer warnings, or mismatched request actual lengths are high-value findings.
