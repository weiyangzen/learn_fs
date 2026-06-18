# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_async_fd.c

## Purpose

`uverbs_std_types_async_fd.c` implements the ioctl object for allocating async event file descriptors. These FDs receive device and object async events, including fatal-device events during provider disassociation.

## Important APIs, Types, and Functions

- `UVERBS_METHOD_ASYNC_EVENT_ALLOC` initializes a newly allocated `ib_uverbs_async_event_file`.
- `uverbs_async_event_destroy_uobj()` unregisters the IB event handler and injects `IB_EVENT_DEVICE_FATAL` during driver removal.
- `uverbs_async_event_release()` releases the fd-backed uobject and then frees the event queue after preserving the fatal-event delivery contract.
- `uverbs_async_event_fops` is supplied by `uverbs_main.c`; this file references it in the object declaration.
- `uverbs_def_obj_async_fd[]` exposes `UVERBS_OBJECT_ASYNC_EVENT` to the UAPI.

## Control Flow

The ioctl framework allocates an FD uobject, the method handler initializes the queue and registers the event handler through `ib_uverbs_init_async_event_file()`, and the file descriptor is returned to userspace. On object destruction, the event handler is unregistered. On release, the code temporarily holds the uobject while closing the fd-backed object and then drains/closes the event queue.

## State and Persistence Behavior

State is per-FD: an event queue, event handler registration, the uobject, and an optional role as the default async event file for the uverbs file. Queued events live until read, release, or queue cleanup. During driver removal, a fatal event may be queued so userspace can detect end of stream.

## Dependencies and Integration Points

The file depends on `rdma_core.h`, `uverbs.h`, `uverbs_std_types.h`, and event queue helpers in `uverbs_main.c` / `uverbs_std_types.c`. CQ, QP, SRQ, and WQ create paths can reference this object as an optional event FD.

## Risks and Edge Cases

The key edge case is preserving `IB_EVENT_DEVICE_FATAL` after disassociation. Cleaning the queue too early would hide fatal notification from userspace; releasing too late could leak events or references. The code handles this by delaying `ib_uverbs_free_event_queue()` until fd release and holding a temporary uobject reference.

## Test Signals

Test allocation, event read/poll/fasync, close with pending events, device removal with fatal-event delivery, default async file assignment, and release when `filp->private_data` is already NULL.
