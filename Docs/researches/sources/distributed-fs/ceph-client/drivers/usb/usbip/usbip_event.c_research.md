# sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_event.c

## Purpose

`usbip_event.c` provides the shared USB/IP event handler. It coalesces shutdown/reset/unusable events per `usbip_device`, serializes handling through a single workqueue, and lets connection threads and sysfs paths wait for teardown completion.

## Important APIs, Types, and Functions

`struct usbip_event` links devices into `event_list`. `set_event()` and `unset_event()` update `ud->event` under the device lock. `event_handler()` drains pending devices, locks `ud->sysfs_lock`, runs `eh_ops.shutdown`, `eh_ops.reset`, and `eh_ops.unusable` in order, clears bits, and wakes `eh_waitq`. Exported APIs are `usbip_start_eh()`, `usbip_stop_eh()`, `usbip_init_eh()`, `usbip_finish_eh()`, `usbip_event_add()`, `usbip_event_happened()`, and `usbip_in_eh()`.

## Control Flow

Core module init creates a singlethread workqueue. Device setup initializes waitqueue and event bits. Any side queues an event with `usbip_event_add()`, which sets bits, avoids duplicate queued nodes for the same device, and schedules work. Stop waits until all non-`BYE` bits are cleared.

## State and Persistence Behavior

Global state is the workqueue, event list, event lock, and `worker_context` pointer. Per-device event bits are runtime-only. No persistent state exists.

## Dependencies and Integration Points

It depends on workqueues, spinlocks, waitqueues, exported symbols, and `usbip_device.eh_ops` implementations from stub, VHCI, and VUDC.

## Risks and Test Signals

Risks include allocation failure dropping queued work after setting bits, waiting interruptibly in stop, `worker_context` assumptions, event coalescing obscuring repeated events, and lock ordering with sysfs paths. Test signals include concurrent event_add calls, duplicate-device coalescing, shutdown-before-reset ordering, wait completion in stop, and module unload with active events.
