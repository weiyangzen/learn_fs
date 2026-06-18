# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eer.c

## Purpose
This file implements DASD extended error reporting for ECKD devices. It exposes a misc character device named `dasd_eer`, keeps one event ring buffer per open file, and exports hooks that DASD device code calls to record fatal errors, PPRC suspension, no-path/no-space/autoquiesce conditions, and state changes.

## Important APIs, Types, and Functions
`struct eerbuffer` owns one reader's ring buffer: page vector, buffer size, page count, head, tail, residual bytes for partial record delivery, and list linkage. `struct dasd_eer_header` prefixes every emitted record with total size, trigger id, wall-clock timestamp, and DASD bus id. Ring helpers are `dasd_eer_get_free_bytes()`, `dasd_eer_get_filled_bytes()`, `dasd_eer_write_buffer()`, `dasd_eer_read_buffer()`, and `dasd_eer_start_record()`.

Event producers use exported `dasd_eer_write()` and `dasd_eer_snss()`. Enabling/disabling per device uses `dasd_eer_enable()` and `dasd_eer_disable()`. Trigger encoders are `dasd_eer_write_standard_trigger()` and `dasd_eer_write_snss_trigger()`. The SNSS request callback is `dasd_eer_snss_cb()`. Userspace file operations are `dasd_eer_open()`, `dasd_eer_close()`, `dasd_eer_read()`, and `dasd_eer_poll()`, registered by `dasd_eer_init()` and removed by `dasd_eer_exit()`.

## Control Flow
Opening `/dev/dasd_eer` allocates an `eerbuffer`, validates the module parameter `eer_pages`, allocates page backing storage, attaches the buffer to `filp->private_data`, and links it into the global `bufferlist` under `bufferlock`. Closing removes it from the list and frees the pages.

When a DASD driver calls `dasd_eer_write()`, the function first checks whether EER is enabled for that device through `device->eer_cqr`. Standard triggers compute record size from the header plus any valid 32-byte sense buffers found along the CQR reference chain, then write the record to every open buffer and wake readers. Triggers without immediate sense data write only the header and `EOR` marker. State-change triggers are special: `dasd_eer_snss()` queues a preallocated SNSS request, and `dasd_eer_snss_cb()` writes the result or a header-only state-change record when the request completes.

Reads deliver complete records when possible but allow userspace to read a record in chunks. If a partial record is being delivered, `residual` tracks remaining bytes. If old records are discarded while a reader still has residual bytes, the residual is marked invalid and the next read fails with `-EIO`. Blocking reads wait on `dasd_eer_read_wait_queue`; nonblocking reads return `-EAGAIN`. `poll()` reports readable when head and tail differ.

## State and Persistence
All state is volatile. Global state consists of `eer_pages`, `bufferlist`, `bufferlock`, `dasd_eer_read_wait_queue`, a shared one-page `readbuffer`, and its mutex. Each open file has independent buffered history. Each EER-enabled DASD device owns one preallocated SNSS `dasd_ccw_req` in `device->eer_cqr`; the flags `DASD_FLAG_EER_IN_USE` and `DASD_FLAG_EER_SNSS` serialize and coalesce SNSS requests. No event data is persisted after readers close or the module exits.

## Dependencies and Integration Points
The file depends on the DASD core, ECKD SNSS command constant from `dasd_eckd.h`, miscdevice registration, file operations, wait queues, spinlocks, mutexes, EBCDIC-capable bus ids from ccw devices, and kernel timekeeping. It integrates with the broader DASD error path through exported symbols, `device->eer_cqr`, `device->ccw_queue`, `dasd_schedule_device_bh()`, and DASD trigger ids.

## Risks and Test Signals
Risk areas include global `bufferlock` contention across all readers and writers, record eviction while userspace reads partial records, unchecked return values from `dasd_eer_start_record()` in writer paths, very large or invalid `eer_pages` settings, SNSS disable races where an in-flight request must be freed by the callback, and the use of a single global read staging page protected by a mutex. Test signals include open/read/close leak checks, multiple independent readers receiving the same trigger, blocking and nonblocking read behavior, poll wakeups, partial-record reads followed by overwrite producing `-EIO`, enable rejection for non-ECKD or offline devices, SNSS coalescing under repeated state changes, and EER disable while SNSS is in flight.
