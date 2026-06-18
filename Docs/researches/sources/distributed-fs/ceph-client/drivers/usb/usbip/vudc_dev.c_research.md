# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_dev.c

## Purpose

`vudc_dev.c` implements the virtual USB gadget device side of USB/IP VUDC. It allocates virtual endpoints, registers a gadget UDC, handles gadget endpoint operations, and implements common USB/IP shutdown/reset/unusable behavior.

## Important APIs, Types, and Functions

URB helpers are `alloc_urbp()`, `free_urbp_and_urb()`, and `free_urb()`. `nuke()` completes queued endpoint requests with `-ESHUTDOWN`; `stop_activity()` resets address, nukes all endpoints, and frees queued URBs. Gadget ops are `vgadget_get_frame()`, `vgadget_set_selfpowered()`, `vgadget_pullup()`, `vgadget_udc_start()`, and `vgadget_udc_stop()`. Endpoint ops implement enable/disable, request alloc/free, queue/dequeue, halt, and wedge. Event callbacks are `vudc_shutdown()`, `vudc_device_reset()`, and `vudc_device_unusable()`. `init_vudc_hw()` creates ep0 plus 15 IN and 15 OUT endpoints and initializes common USB/IP state.

## Control Flow

Probe allocates `struct vudc`, initializes the gadget and virtual endpoints, then registers it with `usb_add_gadget_udc()`. A gadget driver bind calls UDC start; pullup-on sets speed, ep0 maxpacket, fetches gadget descriptors, and starts USB/IP event handling. Pullup-off invalidates descriptors and queues removal. Endpoint operations maintain request queues under `udc->lock`. Shutdown stops socket threads, closes sockets, clears activity, and calls gadget disconnect if needed.

## State and Persistence Behavior

Runtime state includes endpoint descriptors, queued gadget requests, queued USB/IP URBs, pullup/connected/descriptor-cache flags, address, device status, socket/tasks, and transfer timer. No persistent state exists.

## Dependencies and Integration Points

It integrates with USB gadget core, platform devices, USB/IP common/event code, VUDC sysfs descriptor retrieval, VUDC RX/TX/transfer modules, kthreads, sockets, and timer initialization.

## Risks and Test Signals

Risks include request `udc` pointer assumptions in dequeue, races between pullup changes and event shutdown, freeing URBs while RX/TX references remain, endpoint halt semantics for queued IN requests, descriptor cache failure, and reset while a gadget driver is active. Test signals include gadget registration, pullup on/off, descriptor retrieval failure, endpoint queue/dequeue/halt/wedge, USB/IP shutdown/reset events, active request nuke, and remove after gadget unbind.
