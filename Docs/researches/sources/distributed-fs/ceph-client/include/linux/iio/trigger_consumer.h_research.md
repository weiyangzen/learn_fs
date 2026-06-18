<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/trigger_consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/trigger_consumer.h

Purpose: Declares the consumer-side poll function abstraction used by triggered IIO buffers and events.

Important APIs/types/functions: `struct iio_poll_func` stores top half, threaded bottom half, timestamp, trigger, IIO device, IRQ, and name. `iio_alloc_pollfunc()` creates a poll function; `iio_dealloc_pollfunc()` frees it; `iio_pollfunc_store_time()` is a common top half; `iio_trigger_notify_done()` completes trigger processing.

Control flow: Buffer/event setup allocates a poll function, trigger poll invokes top half/thread, driver pushes samples/events, then notifies done.

State/persistence: Poll function state persists while attached to an IIO device/trigger and carries the last timestamp.

Dependencies/integration: Depends on interrupts, IIO trigger provider API, and buffer/event setup helpers.

Risks: Forgetting notify-done or using sleepable code in a hard IRQ top half can deadlock or miss samples.

Test signals: Triggered buffer capture, timestamp top-half behavior, detach cleanup, and threaded handler error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/trigger_consumer.h -->
