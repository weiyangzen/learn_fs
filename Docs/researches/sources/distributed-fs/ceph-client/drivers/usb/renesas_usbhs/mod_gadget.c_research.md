<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_gadget.c

## Purpose
USB gadget/UDC frontend for Renesas USBHS. It exposes endpoints to the gadget framework, translates `usb_request` into `usbhs_pkt`, handles selected standard control requests, manages pullup/VBUS, and registers gadget mode.

## Important APIs, Types, And Functions
`struct usbhsg_gpriv` embeds `usb_gadget`, `usbhs_mod`, gadget driver, optional transceiver, status flags, and endpoints. `struct usbhsg_uep` wraps `usb_ep` and pipe. `struct usbhsg_request` wraps request and packet. Endpoint ops cover enable/disable, alloc/free, queue/dequeue, halt, and wedge. Gadget ops cover frame, self-powered, UDC start/stop, pullup, and VBUS session. Mode hooks are `usbhsg_start()` and `usbhsg_stop()`.

## Control Flow
Probe allocates endpoint state, optionally gets a legacy PHY, registers gadget mode, initializes endpoint capabilities, and calls `usb_add_gadget_udc()`. Start waits until both cable/module and gadget-driver status are ready, then initializes FIFO/pipe, allocates DCP, enables function mode and pullup, and installs IRQ callbacks. Endpoint queues become packets with DMA-capable handlers. Control-stage IRQs select DCP handlers, read setup packets, handle clear/set feature and get status locally, or call driver `setup()`.

## State And Persistence
State includes status flags, endpoint-pipe mappings, queued packet nodes, `gadget.speed`, `vbus_active`, optional PHY binding, function-mode/pullup/test-mode registers, and pipe/FIFO state.

## Dependencies And Integration Points
Depends on USB gadget APIs, optional legacy USB PHY/OTG, and internal common/mod/pipe/FIFO layers.

## Risks
Giveback drops the shared lock before calling gadget completion. Endpoint disable must drain packets before freeing pipes. Direction helpers are easy to misread in gadget mode. Halt on IN endpoints can return `-EAGAIN` when queued/transmittable data exists. Atomic control-status allocations can fail.

## Test Signals
Enumeration, standard control requests, set/clear halt and wedge, zero packets, disconnect with queued I/O, pullup toggling, VBUS-session PHY mode, DMA/PIO fallback, and suspend notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_gadget.c -->
