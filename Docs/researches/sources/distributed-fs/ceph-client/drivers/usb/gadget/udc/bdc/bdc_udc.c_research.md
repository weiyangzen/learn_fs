<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_udc.c

## Purpose
This file provides the BDC USB gadget registration layer, status report ring interrupt handler, upstream port status handling, remote wake behavior, and gadget-level operations.

## Important APIs, Types, And Functions
Status ring flow uses `srr_dqp_index_advc()` and `bdc_udc_interrupt()`. Port events are handled by `bdc_sr_uspc()`, `bdc_uspc_connected()`, `bdc_uspc_disconnected()`, and `handle_link_state_change()`. Remote wake retry logic is in `bdc_func_wake_timer()`. Gadget ops are `bdc_udc_start()`, `bdc_udc_stop()`, `bdc_udc_pullup()`, `bdc_udc_set_selfpowered()`, and `bdc_udc_wakeup()`. UDC lifecycle is `bdc_udc_init()` and `bdc_udc_exit()`.

## Control Flow
`bdc_udc_init()` requests the shared IRQ, initializes endpoints, registers the gadget, preallocates/enables EP0 BD resources, initializes delayed work, and enables global interrupts. The IRQ handler verifies global and SRR pending bits, consumes status report entries until the software dequeue index reaches hardware enqueue, dispatches XSF or USPC reports, writes the updated SRR dequeue pointer, and runs reinit if requested by disconnect/reset handling. USPC reports detect connect, VBUS, reset/disconnect, and link-state changes. On connect, speed is decoded, EP0 maxpacket is set, EP0 is configured in hardware, and gadget state becomes default. On disconnect, EP0 is disabled, gadget driver disconnect is called, speed/state/status flags are reset, and optional reinit is requested.

## State And Persistence
This file maintains gadget speed/state, pullup state, device status bits for suspend/remote wake/function wake, EP0 descriptor state, delayed remote wake work, and SRR dequeue index. It also sets `bdc->gadget_driver` and `gadget.dev.driver` on UDC start/stop.

## Dependencies And Integration Points
It integrates BDC core operations, command functions, endpoint functions, Linux USB gadget registration, IRQ handling, delayed work, and USB device state management. It consumes status reports produced by the BDC hardware and endpoint handlers from `bdc_ep.c`.

## Risks
The interrupt handler holds `bdc->lock` while dispatching reports; handlers must carefully drop/reacquire around gadget callbacks. Remote wake for superspeed relies on repeated Function Wake notifications until a transfer clears `FUNC_WAKE_ISSUED`. `bdc_udc_set_selfpowered()` appears to set the self-powered status bit when `is_self` is false and clear it when true, which is counterintuitive and should be reviewed against hardware/gadget expectations. Disconnect-triggered reinit is deferred until after SRR processing, so failure leaves the controller logged but not recovered.

## Test Signals
Validate connect/disconnect at low/full/high/superspeed as supported, EP0 maxpacket changes, VBUS-only pullup behavior, bus reset, suspend/resume callbacks, remote wake from U3, delayed Function Wake retry cancellation after host traffic, SRR wraparound, and UDC bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_udc.c -->
