# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/core.c

## Purpose

`core.c` implements the Linux USB Device Controller core framework. It mediates between gadget function drivers and hardware-specific UDC drivers. It exports endpoint APIs, gadget APIs, DMA mapping helpers, request giveback, endpoint matching, UDC registration/removal, gadget-driver registration, driver binding/unbinding, sysfs attributes, uevents, and the `gadget` bus.

## Important APIs, Types, And Functions

The central private type is `struct usb_udc`, binding a `usb_gadget`, optional `usb_gadget_driver`, class device, list node, VBUS status, started state, connect permission, VBUS work item, and `connect_lock`. `udc_list` is protected by `udc_lock`, and `gadget_id_numbers` assigns gadget device IDs.

Endpoint exports validate and delegate to endpoint ops: enable/disable, request allocation/free, queue/dequeue, halt/clear halt, wedge, FIFO status, and FIFO flush. Gadget exports delegate to gadget ops for frame number, wakeup, remote wakeup, self-powered status, VBUS session/draw, connect/disconnect, deactivate/activate, and state changes.

DMA helpers map either SG lists or linear buffers and reject vmalloc/stack buffers for linear DMA. `usb_gadget_giveback_request()` calls the completion callback and emits USB LED activity on successful completions. `usb_gadget_ep_match_desc()` is the endpoint autoconfiguration predicate.

UDC lifecycle APIs include `usb_initialize_gadget()`, `usb_add_gadget()`, `usb_add_gadget_udc_release()`, `usb_add_gadget_udc()`, `usb_del_gadget()`, `usb_del_gadget_udc()`, and `usb_get_gadget_udc_name()`. Gadget driver APIs are `usb_gadget_register_driver_owner()` and `usb_gadget_unregister_driver()`.

## Control Flow

UDC hardware drivers initialize a `usb_gadget` and call `usb_add_gadget_udc*()`. The core allocates `struct usb_udc`, creates a UDC class device, links the gadget device, assigns a gadget ID, adds the gadget to the `gadget` bus, creates a sysfs link, and sets initial state to `USB_STATE_NOTATTACHED`.

Gadget drivers register as drivers on the `gadget` bus. Bind flow marks the driver bound, stores it in the UDC, sets maximum speed, calls gadget `bind()`, starts hardware through `udc_start`, enables async callbacks, allows connection, and applies VBUS-driven connect control. Unbind prevents new connects, cancels VBUS work, disconnects pullup, disables async callbacks, synchronizes IRQ, calls `unbind()`, stops the UDC, clears binding state, and emits a uevent.

## State And Persistence

State is in memory and sysfs only. `started`, `allow_connect`, `vbus`, `gadget->connected`, and `gadget->deactivated` determine whether pullup calls reach hardware or are just remembered. `connect_lock` serializes start/stop/pullup/deactivate transitions, while `udc_lock` serializes the global UDC list and binding pointers. Gadget state changes are reported asynchronously through sysfs `state` notification.

## Dependencies And Integration Points

This file depends on the Linux device model, IDA, DMA mapping, workqueues, USB gadget structures, and UDC tracepoints. UDC drivers integrate through `usb_ep_ops` and `usb_gadget_ops`, especially `udc_start`, `udc_stop`, optional `pullup`, speed-setting, async callback gating, wakeup, and VBUS operations. Gadget function drivers integrate through `struct usb_gadget_driver`.

## Risks

The main risks are concurrency and callback ordering. The code separates `udc_lock` and `connect_lock`; violating ordering in UDC or gadget drivers can deadlock. Request completion callbacks must not be called from `usb_ep_queue()`, and UDC drivers must honor async callback disablement during unbind. DMA mapping rejects non-DMA-capable buffers, so gadget drivers using stack or vmalloc buffers fail.

## Test Signals

Core tests should cover UDC registration/removal, binding by explicit `udc_name`, failed bind unwinding, VBUS connect/disconnect work, deactivate/activate preserving desired connection state, endpoint autoconfig matching, DMA mapping failure for invalid buffers, request giveback, sysfs `soft_connect`, and unbind with async callbacks disabled.
