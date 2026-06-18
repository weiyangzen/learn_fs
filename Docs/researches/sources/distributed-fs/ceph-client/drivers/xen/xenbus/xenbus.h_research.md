# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus.h

## Purpose
`xenbus.h` is the private header for Xenbus internals. It defines the bus-type abstraction for frontend/backend enumeration, Xenstore initialization modes, watch event containers, low-level request state, and declarations shared by Xenbus communications, probe, client, and user-device files.

## Important APIs, Types, And Functions
`struct xen_bus_type` wraps a Linux `bus_type` with Xenstore root, path depth, bus-id generation, probing, and otherend watch handlers. `enum xenstore_init` distinguishes unknown, PV, HVM, and local Xenstore modes. `struct xs_watch_event` carries Xenstore watch callbacks. `enum xb_req_state` and `struct xb_req_data` model queued, wait-reply, got-reply, and aborted Xenstore requests. The header declares shared lists/locks (`xs_reply_list`, `xb_write_list`, `xb_waitq`, `xb_write_mutex`, `xs_response_mutex`) and cross-file functions for communication, probing, suspend/resume, and user replies.

## Control Flow
The header ties the message pump to higher layers: `xenbus_dev_request_and_reply()` queues requests, `xenbus_comms.c` consumes `xb_write_list` and fills replies, `xenbus_dev_queue_reply()` returns replies to `/dev/xen/xenbus`, and probe files call common helpers like `xenbus_probe_devices()` and `xenbus_dev_changed()`.

## State And Persistence
All state declared here is runtime kernel state. `xb_dev_generation_id` invalidates user-space transaction handles across Xenstore reconnect/resume. Shared request and watch structures persist only while open files, watches, or queued Xenstore messages exist.

## Dependencies And Integration Points
The header depends on Linux mutex/uio and public `<xen/xenbus.h>`. It is included by the common communications, client, probe, frontend/backend probe, and misc-device implementations.

## Risks
Because this header exposes shared internal lists and locks, call ordering and lock nesting must remain consistent. Request-state transitions need barriers in implementation files so callbacks do not see partial replies. Path depth in `xen_bus_type.levels` must match frontend/backend Xenstore layouts.

## Test Signals
Build coverage, clean sparse/lockdep behavior, working frontend/backend enumeration, successful user-space Xenstore reads/writes, and stable resume transaction invalidation indicate this contract is sound.
