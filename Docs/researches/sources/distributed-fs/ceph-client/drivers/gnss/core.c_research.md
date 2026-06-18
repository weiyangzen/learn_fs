# sources/distributed-fs/ceph-client/drivers/gnss/core.c

## Purpose
`core.c` implements the GNSS character-device subsystem. It allocates `/dev/gnssN` devices, buffers incoming raw receiver data in a FIFO, provides blocking read and synchronous write operations, exposes receiver type through sysfs and uevents, and manages disconnect/open lifetimes for transport drivers.

## Important APIs, Types, and Functions
Public exported APIs are `gnss_allocate_device()`, `gnss_put_device()`, `gnss_register_device()`, `gnss_deregister_device()`, and `gnss_insert_raw()`. File operations are `gnss_open()`, `gnss_release()`, `gnss_read()`, `gnss_write()`, and `gnss_poll()`. Internal constants are `GNSS_MINORS`, `GNSS_READ_FIFO_SIZE`, and `GNSS_WRITE_BUF_SIZE`.

## Control Flow
Module init allocates 16 char minors and creates class `gnss`. Transport drivers allocate a `struct gnss_device`, set type and operations, then register it. Open takes a device reference, checks `disconnected` under `rwsem`, increments the open count, and calls transport `open()` on the first opener. Release decrements count and calls transport `close()` on the last close, resetting the read FIFO.

Reads block until data is available, the device disconnects, or a signal arrives. Incoming bytes are inserted by transport callbacks through `gnss_insert_raw()`, which wakes the read queue. Writes require a transport `write_raw` operation, copy userspace data in 1024-byte chunks under `write_mutex`, and call the transport while holding the read side of `rwsem`. Deregistration marks the device disconnected, wakes readers, closes active hardware once, and deletes the cdev.

## State and Persistence
State is volatile: IDA minor allocation, open count, disconnected flag, kfifo contents, write staging buffer, mutexes, rwsem, and wait queue. No GNSS data or configuration is persisted.

## Dependencies and Integration Points
The core depends on cdev, class, kfifo, IDA, wait queues, poll, and `linux/gnss.h`. Serial and USB drivers use the exported APIs.

## Risks and Test Signals
`gnss_insert_raw()` assumes caller serialization and must not be called for a closed device; transport drivers must honor that contract. FIFO overflow silently drops data by returning fewer bytes inserted. Writes ignore `O_NONBLOCK` by design and assume transport write can accept 1024-byte chunks. Tests should cover open count transitions, blocking read wakeup, disconnect read returning EOF, poll `EPOLLHUP`, write chunking, FIFO overflow accounting, and transport open failure rollback.
