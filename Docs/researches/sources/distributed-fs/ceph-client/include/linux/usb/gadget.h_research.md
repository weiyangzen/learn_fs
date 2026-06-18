# `sources/distributed-fs/ceph-client/include/linux/usb/gadget.h`

## Purpose

`gadget.h` is the core device-side USB controller and gadget-driver contract. It defines the portable abstractions that function drivers use to talk to USB device controller hardware: `usb_request`, `usb_ep`, `usb_gadget`, `usb_gadget_driver`, endpoint capability matching, descriptor/string helpers, DMA mapping helpers, and UDC registration APIs.

## Important APIs, Types, and Constants

- `struct usb_request` is the gadget-side analogue of a host URB, carrying buffer, DMA, scatter-gather, stream, completion, status, and byte-count fields.
- `struct usb_ep_ops` and `struct usb_ep` define endpoint operations, endpoint capabilities, descriptor binding, max packet limits, burst/stream metadata, and driver-private storage.
- Endpoint wrappers include `usb_ep_enable()`, `usb_ep_disable()`, request allocation/free, queue/dequeue, halt/clear/wedge, FIFO status, and FIFO flush; disabled `CONFIG_USB_GADGET` builds get inert inline stubs.
- `struct usb_gadget_ops` exposes controller-wide hooks for frame number, remote wakeup, VBUS, pullup, UDC start/stop, speed/SSP rate, async callbacks, endpoint matching, and configuration checks.
- `struct usb_gadget` is the persistent UDC object with ep0, endpoint list, speed/state, OTG flags, controller quirks, power/wakeup/connection state, IRQ, and driver-model state.
- `struct usb_gadget_driver` defines bind/unbind, ep0 `setup()`, disconnect, suspend/resume, reset, UDC name matching, and single-bind state.
- Utility APIs cover gadget registration, string descriptors, descriptor copying/assignment/freeing, OTG descriptor creation, request DMA map/unmap, state changes, reset notification, request giveback, endpoint lookup, descriptor matching, VBUS notification, and endpoint autoconfiguration.

## Control Flow and Lifetimes

A UDC driver initializes a `usb_gadget`, adds it to the UDC core, and exposes endpoints in `gadget->ep_list`. A gadget function driver registers a `usb_gadget_driver`; the UDC core binds it to a matching gadget, invokes `bind()`, then ep0 `setup()` callbacks drive enumeration and configuration. Non-control traffic flows by allocating `usb_request` objects from an endpoint, filling buffers and flags, queueing them with `usb_ep_queue()`, and receiving completion callbacks with interrupts disabled. Teardown reverses this: disconnect/deactivate, disable endpoints, dequeue or complete pending requests, unbind the gadget driver, remove the gadget, and release descriptors/requests.

## State and Persistence Behavior

State is in memory and hardware, not on disk. `usb_gadget` persists for the UDC lifetime; endpoint enabled/claimed/descriptor state persists while configurations are active; requests persist from allocation until explicit free. Completion callbacks are interrupt-context sensitive. `state_lock` protects `state` and `teardown`, while endpoint queues and hardware FIFOs are controlled by UDC implementations. DMA mapping flags in `usb_request` prevent double mapping/unmapping.

## Dependencies and Integration Points

The header depends on Linux device model, configfs, workqueue, list, scatterlist, and USB Chapter 9 definitions. It integrates with UDC drivers, composite gadget functions, configfs USB gadget configuration, OTG support, DMA APIs, and platform-specific UDC controller headers. `gadget_configfs.h` builds on its string/configfs helpers.

## Risks and Edge Cases

Ep0 `setup()` and request completion callbacks may run in interrupt context and must not sleep. Request ownership must be clear: queued requests cannot be freed until completion/dequeue. Controller quirks such as no ZLP, no stall, no altsettings, or OUT alignment affect function driver behavior. DMA mapping helpers must match direction and request lifetime. Misdescribed endpoint descriptors can overrun controller limits or produce invalid enumeration.

## Test Signals

Useful signals include `CONFIG_USB_GADGET` builds with several UDCs and composite functions, configfs gadget creation/removal, ep0 enumeration tests, endpoint autoconfig tests across FS/HS/SS/SSP, request queue/dequeue cancellation tests, DMA and scatter-gather transfers, suspend/resume/remote wakeup tests, disconnect during active I/O, and builds with gadget support disabled to verify stub users.
