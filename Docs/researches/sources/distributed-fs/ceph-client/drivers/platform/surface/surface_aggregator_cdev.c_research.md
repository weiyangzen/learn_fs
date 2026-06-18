# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_cdev.c

## Purpose
Provides a misc character device `/dev/surface/aggregator` for debugging and development access to the SSAM EC. Userspace can issue synchronous SSAM requests, enable/disable events, register observer notifiers, and read event records from per-client FIFOs.

## Important APIs, Types, And Functions
`struct ssam_cdev` tracks controller binding, miscdevice, shutdown flag, and open clients. `struct ssam_cdev_client` tracks notifier registrations, read/write locks, a 4 KiB FIFO, wait queue, and fasync state. Notifier functions translate `struct ssam_event` to `struct ssam_cdev_event`. IOCTL handlers are `ssam_cdev_request()`, notifier register/unregister, event enable/disable. File ops implement open, release, ioctl, read, poll, and fasync. Platform probe/remove create and destroy the misc device.

## Control Flow
Module init creates a platform device and registers a platform driver. Probe binds to the SSAM controller and registers the misc device. Open allocates a client and attaches it to the client list unless shutdown is set. IOCTLs take the cdev rwsem, reject shutdown, then issue controller operations or notifier changes. Incoming SSAM events are copied into the client's FIFO and wake blocking, polling, and async readers. Release unregisters all client notifiers, detaches the client, and frees it. Remove marks shutdown, unregisters all notifiers for live clients, signals readers, nulls controller pointers under lock, deregisters the misc device, and drops the cdev kref.

## State And Persistence Behavior
Each open file has independent in-memory notifier state and event FIFO. Events are dropped when the FIFO lacks room. No data persists across close or module unload. The cdev object is kref-managed so lingering file descriptors can release safely after device removal, but controller access is blocked once shutdown is set and `ctrl` is nulled.

## Dependencies And Integration Points
Depends on miscdevice, uaccess, kfifo, fasync, poll, Surface Aggregator cdev UAPI, controller APIs, SSAM notifier APIs, and protocol event target-category helpers. It is intentionally an observer and does not consume events from functional drivers.

## Risks
The debug interface can send arbitrary EC requests and enable/disable events, so it should remain appropriately permissioned by device node policy. Large user-provided payload/response lengths are bounded by UAPI field widths but can still allocate sizable buffers. `ssam_cdev_notifier_unregister_all()` loops all `SSH_NUM_EVENTS` and ignores unregister errors, which is reasonable for cleanup but may hide inconsistencies. Event FIFO overflow drops events without backpressure.

## Test Signals
Test open/read/poll/fasync, blocking read wake on event and on removal, IOCTL request with and without response, invalid user pointers, notifier duplicate/unregister-missing cases, event FIFO overflow, concurrent clients, remove with open descriptors, and event enable/disable calls.
