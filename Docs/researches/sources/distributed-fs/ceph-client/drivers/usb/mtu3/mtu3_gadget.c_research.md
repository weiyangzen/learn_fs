# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_gadget.c

## Purpose

`mtu3_gadget.c` implements the Linux USB gadget controller operations for non-EP0 endpoints and UDC registration behavior. It maps gadget requests to MTU3 QMU descriptors, manages endpoint enable/disable, halt/wedge, pullup, wakeup, driver bind/unbind, and gadget suspend/resume/disconnect callbacks.

## Important APIs, Types, and Functions

Core functions include `mtu3_req_complete()`, `nuke()`, `mtu3_ep_enable()`, `mtu3_ep_disable()`, `mtu3_gadget_queue()`, `mtu3_gadget_dequeue()`, `mtu3_gadget_ep_set_halt()`, `mtu3_gadget_pullup()`, `mtu3_gadget_start()`, `mtu3_gadget_stop()`, and `mtu3_gadget_setup()`. `mtu3_ep_ops` exposes endpoint operations, and `mtu3_gadget_ops` exposes UDC operations.

## Control Flow

UDC setup initializes endpoint objects and registers the gadget. When a function driver starts, the driver pointer is stored and peripheral-only mode starts hardware immediately. Endpoint enable validates descriptor number/direction, configures hardware FIFO/CSR, allocates a QMU ring, starts QMU, and marks the endpoint active. Queue maps the request for DMA, prepares the transfer, appends it to `req_list`, inserts a GPD, and resumes QMU. Completion unmaps non-EP0 requests and gives them back with the controller lock temporarily dropped. Stop and disconnect paths clear softconnect, nuke all endpoint queues, notify function drivers, and reset state.

## State and Persistence Behavior

State is in `struct mtu3`, `struct mtu3_ep`, and `struct mtu3_request`: endpoint descriptors, QMU rings, request lists, active endpoint count, softconnect, gadget driver pointer, speed, wake flags, and callback enablement. It is runtime-only and rebuilt after probe.

## Dependencies and Integration Points

The file depends on USB gadget core, QMU helper functions, endpoint hardware config from `mtu3_core.c`, tracepoints, runtime PM, and EP0 operations from `mtu3_gadget_ep0.c`. It is the bridge between composite/function drivers and MTU3 hardware queues.

## Risks and Test Signals

Risks include DMA mapping leaks on `mtu3_prepare_transfer()` failure, queueing while endpoints are disabled, request length limits differing for Gen2-compatible QMU, halting endpoints with active requests, and callbacks while holding or dropping `mtu->lock`. Test signals include gadget bind/unbind, endpoint enable for all transfer types and speeds, queue/dequeue/completion, halt and wedge semantics, pullup before and after `mtu3_start()`, remote wakeup at HS and SS, and disconnect while requests are pending.
