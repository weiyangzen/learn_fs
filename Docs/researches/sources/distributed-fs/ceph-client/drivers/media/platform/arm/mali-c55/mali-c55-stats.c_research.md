# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-stats.c

Purpose: Implements the Mali-C55 metadata-capture video node that returns 3A/statistics data to userspace once per frame.

Important APIs/functions: Exports `mali_c55_stats_fill_buffer()`, registration, and unregistration. Internal functions provide meta format ioctls, vb2 queue setup, buffer queueing/return, stream start/stop, and CPU MMIO reads of statistics regions.

Control flow: Queued stats buffers are placed on a list with payload set to `struct mali_c55_stats_buffer`. Stream start gets runtime PM, starts the media pipeline, and may start ISP streaming when all queues are ready. On SOF handling, `mali_c55_stats_fill_buffer()` pops one buffer, stamps sequence/timestamp, copies the 1024-bin histogram and metering config-space data from the just-used ping/pong region, and completes the buffer.

State and persistence: Stats state stores video node, vb2 queue, lock, and queued buffers. No persistent storage; stats are copied from hardware MMIO to userspace buffers.

Dependencies and integration: Uses V4L2 meta capture, vb2 DMA-contig, media controller, runtime PM, core IRQ SOF path, ping/pong config-space selection, and Mali-C55 config UAPI.

Risks: `segments_remaining` and `failed` are initialized but unused, suggesting planned segmented DMA/error handling is incomplete. Stats are read synchronously by CPU in threaded IRQ flow, which can be expensive. If no stats buffer is queued, data is dropped silently.

Test signals: Meta format ioctls, queued/unqueued SOF behavior, sequence alignment with frame-sync and params, ping/pong source correctness, stream start/stop PM balancing, and buffer return on stop.
